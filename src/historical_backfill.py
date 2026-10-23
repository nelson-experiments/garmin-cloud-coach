"""Resumable, private Garmin activity archive; never touches latest.json."""
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path


def month_windows(start, end):
    while start <= end:
        following = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        last = min(end, following - timedelta(days=1))
        yield start.isoformat(), last.isoformat()
        start = last + timedelta(days=1)


def backfill(api, root="data/history", end=None):
    """Checkpoint complete months. API failures must not masquerade as empty months."""
    end = end or date.today()
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for start, stop in month_windows(date(2024, 1, 1), end):
        target = root / f"{start[:7]}.json"
        if target.exists():
            existing = json.loads(target.read_text())
            if existing.get("window", {}).get("end") == stop:
                continue
        activities = api.get_activities_by_date(start, stop)
        if not isinstance(activities, list):
            raise ValueError(f"Invalid activity response for {start[:7]}")
        unique = {}
        for activity in activities:
            if not isinstance(activity, dict) or not activity.get("activityId"):
                raise ValueError(f"Missing activity ID for {start[:7]}")
            unique[str(activity["activityId"])] = activity
        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "window": {"start": start, "end": stop},
            "activities": sorted(unique.values(), key=lambda a: a.get("startTimeGMT", "")),
        }
        temp = target.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, indent=2, default=str) + "\n")
        temp.replace(target)
        print(f"Archived {start[:7]}: {len(unique)} activities")
