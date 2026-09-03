"""Build the public, privacy-filtered Garmin coaching archive."""

from __future__ import annotations

import html
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "latest.json"
REPORTS = ROOT / "reports" / "daily"
OUTPUT = ROOT / "_site"
SYDNEY = ZoneInfo("Australia/Sydney")


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def pace(speed_mps: Any) -> str:
    try:
        seconds = round(1000 / float(speed_mps))
    except (TypeError, ValueError, ZeroDivisionError):
        return "—"
    return f"{seconds // 60}:{seconds % 60:02d}/km"


def duration(seconds_value: Any) -> str:
    try:
        seconds = round(float(seconds_value))
    except (TypeError, ValueError):
        return "—"
    hours, rem = divmod(seconds, 3600)
    minutes = rem // 60
    return f"{hours}h {minutes:02d}m" if hours else f"{minutes} min"


def kilometres(metres: Any) -> str:
    try:
        return f"{float(metres) / 1000:.2f} km"
    except (TypeError, ValueError):
        return "—"


def local_activity_date(activity: dict[str, Any]) -> str:
    value = str(activity.get("startTimeLocal") or "")
    return value[:10] if len(value) >= 10 else "unknown-date"


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def load_reports() -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for path in sorted(REPORTS.glob("*.json"), reverse=True):
        report = load_json(path, None)
        if isinstance(report, dict) and report.get("date"):
            reports.append(report)
    return reports


def running_activities(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    values = snapshot.get("activities")
    if not isinstance(values, list):
        return []
    runs = [
        item for item in values
        if isinstance(item, dict)
        and (item.get("activityType") or {}).get("typeKey") in {"running", "trail_running"}
    ]
    return sorted(runs, key=lambda item: str(item.get("startTimeLocal") or ""), reverse=True)


def render_items(items: Any, css_class: str = "") -> str:
    if not isinstance(items, list) or not items:
        return ""
    cls = f' class="{esc(css_class)}"' if css_class else ""
    return f"<ul{cls}>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def metric_cards(items: Any) -> str:
    if not isinstance(items, list):
        return ""
    cards = []
    for item in items:
        if not isinstance(item, dict):
            continue
        state = str(item.get("status") or "neutral")
        cards.append(
            f'<article class="metric {esc(state)}"><span>{esc(item.get("label"))}</span>'
            f'<strong>{esc(item.get("value") or "—")}</strong>'
            f'<small>{esc(item.get("context"))}</small></article>'
        )
    return '<div class="metrics">' + "".join(cards) + "</div>" if cards else ""


def signal_cards(items: Any) -> str:
    if not isinstance(items, list):
        return ""
    cards = []
    for item in items:
        if not isinstance(item, dict):
            continue
        cards.append(
            '<article class="signal">'
            f'<div><span>{esc(item.get("label"))}</span><strong>{esc(item.get("value"))}</strong></div>'
            f'<p>{esc(item.get("interpretation"))}</p></article>'
        )
    return '<div class="signals">' + "".join(cards) + "</div>" if cards else ""


def page(title: str, body: str, relative_root: str = "./") -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>{esc(title)} · Nelson's Run Brief</title>
<link rel="stylesheet" href="{relative_root}assets/styles.css"></head>
<body><header class="topbar"><a class="brand" href="{relative_root}">Nelson's Run Brief</a>
<nav><a href="{relative_root}latest/">Latest</a><a href="{relative_root}archive/">Archive</a></nav></header>
<main>{body}</main><footer>Training guidance, not medical advice. Pain and illness override device scores.</footer></body></html>"""


def report_body(report: dict[str, Any]) -> str:
    date = esc(report.get("date"))
    status = str(report.get("status") or "current")
    recovery = metric_cards(report.get("recovery"))
    yesterday = report.get("yesterday") if isinstance(report.get("yesterday"), dict) else {}
    recommendation = report.get("recommendation") if isinstance(report.get("recommendation"), dict) else {}
    caveats = render_items(report.get("caveats"), "caveats")
    adherence_verdict = str(yesterday.get("adherence_verdict") or "").replace("_", " ").title()
    adherence = ""
    if adherence_verdict:
        evidence = render_items(yesterday.get("adherence_evidence"))
        adherence_caveats = render_items(yesterday.get("adherence_caveats"), "caveats")
        adherence = f"""
<div class="adherence"><h3>Plan adherence: {esc(adherence_verdict)}</h3>
<p><strong>Prescribed:</strong> {esc(yesterday.get('prescribed'))}</p>
<p><strong>Completed:</strong> {esc(yesterday.get('completed'))}</p>
<p>{esc(yesterday.get('adherence_assessment'))}</p>
{evidence}{adherence_caveats}</div>"""
    return f"""
<section class="hero"><div><p class="eyebrow">Daily briefing · {date}</p><h1>{esc(report.get('headline') or 'Daily training brief')}</h1>
<p class="lede">{esc(report.get('summary'))}</p></div><span class="status {esc(status)}">{esc(status)}</span></section>
<section><h2>Recovery dashboard</h2>{recovery or '<p>No recovery metrics were available.</p>'}</section>
<section class="split"><article><h2>Yesterday</h2><h3>{esc(yesterday.get('title') or 'No run recorded')}</h3><p>{esc(yesterday.get('summary'))}</p>{adherence}</article>
<article class="prescription"><h2>Today</h2><h3>{esc(recommendation.get('title') or 'Awaiting recommendation')}</h3>
{render_items(recommendation.get('details'))}<p><strong>Alternative:</strong> {esc(recommendation.get('alternative'))}</p>
<p class="stop"><strong>Reduce or stop:</strong> {esc(recommendation.get('reduce_or_stop'))}</p></article></section>
<section><h2>Signals driving the decision</h2>{signal_cards(report.get('signals'))}</section>
{f'<section><h2>Data notes</h2>{caveats}</section>' if caveats else ''}
<p class="updated">Coaching interpretation generated {esc(report.get('generated_at'))}; snapshot {esc(report.get('snapshot_generated_at'))}.</p>"""


def run_assessments(reports: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for report in reversed(reports):
        values = report.get("run_assessments")
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, dict) and item.get("activity_id") is not None:
                result[str(item["activity_id"])] = item
    return result


def run_body(activity: dict[str, Any], assessment: dict[str, Any] | None) -> str:
    activity_id = str(activity.get("activityId") or "")
    date = local_activity_date(activity)
    title = activity.get("activityName") or "Run"
    metrics = [
        ("Distance", kilometres(activity.get("distance"))),
        ("Time", duration(activity.get("duration"))),
        ("Average pace", pace(activity.get("averageSpeed"))),
        ("Average HR", f"{activity.get('averageHR')} bpm" if activity.get("averageHR") is not None else "—"),
        ("Training load", f"{float(activity.get('activityTrainingLoad')):.0f}" if activity.get("activityTrainingLoad") is not None else "—"),
        ("Training effect", str(activity.get("trainingEffectLabel") or "—").replace("_", " ").title()),
    ]
    metric_html = "".join(f'<article class="metric neutral"><span>{esc(k)}</span><strong>{esc(v)}</strong></article>' for k, v in metrics)
    if assessment:
        narrative = f"""<section><h2>Coach's assessment</h2><p class="lede">{esc(assessment.get('summary'))}</p>
<p>{esc(assessment.get('assessment'))}</p>{signal_cards(assessment.get('signals'))}</section>"""
    else:
        narrative = '<section><h2>Coach\'s assessment</h2><p>This run predates the published coaching archive. Its privacy-filtered metrics are retained for history.</p></section>'
    return f"""<section class="hero"><div><p class="eyebrow">Run · {esc(date)}</p><h1>{esc(title)}</h1>
<p class="lede">A privacy-filtered record from Garmin activity {esc(activity_id)}.</p></div></section>
<section><div class="metrics">{metric_html}</div></section>{narrative}
<p><a href="../../daily/{esc(date)}/">View that day's briefing →</a></p>"""


def archive_body(reports: list[dict[str, Any]], runs: list[dict[str, Any]]) -> str:
    daily = "".join(
        f'<li><a href="../daily/{esc(r.get("date"))}/"><strong>{esc(r.get("date"))}</strong><span>{esc(r.get("headline"))}</span></a></li>'
        for r in reports
    ) or "<li>No daily briefings published yet.</li>"
    recent_runs = "".join(
        f'<li><a href="../runs/{esc(r.get("activityId"))}/"><strong>{esc(local_activity_date(r))}</strong>'
        f'<span>{esc(r.get("activityName") or "Run")} · {esc(kilometres(r.get("distance")))}</span></a></li>'
        for r in runs
    ) or "<li>No runs available.</li>"
    return f"""<section class="hero compact"><div><p class="eyebrow">History</p><h1>Briefing archive</h1>
<p class="lede">Permanent daily briefings and privacy-filtered run records.</p></div></section>
<section class="split archive"><article><h2>Daily briefs</h2><ul class="archive-list">{daily}</ul></article>
<article><h2>Runs</h2><ul class="archive-list">{recent_runs}</ul></article></section>"""


def write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main() -> None:
    snapshot = load_json(SNAPSHOT, {})
    reports = load_reports()
    runs = running_activities(snapshot)
    assessments = run_assessments(reports)
    shutil.rmtree(OUTPUT, ignore_errors=True)
    (OUTPUT / "assets").mkdir(parents=True)
    shutil.copy(ROOT / "site" / "styles.css", OUTPUT / "assets" / "styles.css")

    if reports:
        latest = reports[0]
        latest_body = report_body(latest)
        write_page(OUTPUT / "index.html", page(str(latest.get("headline") or "Latest briefing"), latest_body, "./"))
        write_page(OUTPUT / "latest" / "index.html", page("Latest briefing", latest_body, "../"))
        for report in reports:
            report_date = str(report["date"])
            write_page(OUTPUT / "daily" / report_date / "index.html", page(report_date, report_body(report), "../../"))
    else:
        generated = parse_time(snapshot.get("generated_at"))
        age = "unknown"
        if generated:
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=UTC)
            age = f"{(datetime.now(UTC) - generated.astimezone(UTC)).total_seconds() / 3600:.1f} hours"
        pending = f"""<section class="hero"><div><p class="eyebrow">Setup complete</p><h1>Your first briefing is pending</h1>
<p class="lede">The latest Garmin snapshot is {esc(age)} old. The scheduled coach will publish the first interpretation here.</p></div></section>"""
        write_page(OUTPUT / "index.html", page("Briefing pending", pending, "./"))
        write_page(OUTPUT / "latest" / "index.html", page("Briefing pending", pending, "../"))

    for activity in runs:
        activity_id = str(activity.get("activityId") or "")
        if activity_id:
            write_page(OUTPUT / "runs" / activity_id / "index.html", page(str(activity.get("activityName") or "Run"), run_body(activity, assessments.get(activity_id)), "../../"))
    write_page(OUTPUT / "archive" / "index.html", page("Archive", archive_body(reports, runs), "../"))
    (OUTPUT / ".nojekyll").write_text("")


if __name__ == "__main__":
    main()
