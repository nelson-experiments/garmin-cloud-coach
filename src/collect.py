"""Read-only Garmin Connect snapshot for a cloud-based running coach."""
import base64
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SYDNEY = ZoneInfo("Australia/Sydney")


def get_path(value, *path):
    """Return a nested dict value, or None when Garmin omits that field."""
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def sleep_recovery_summary(sleep, sleep_date):
    """Expose the completed overnight HR signal and its source timestamps."""
    daily = get_path(sleep, "dailySleepDTO") or sleep
    spo2 = get_path(daily, "spo2SleepSummary") or {}
    return {
        "sleep_date": get_path(daily, "calendarDate") or sleep_date,
        "sleep_start_gmt": get_path(daily, "sleepStartTimestampGMT"),
        "sleep_end_gmt": get_path(daily, "sleepEndTimestampGMT"),
        "average_sleep_heart_rate_bpm": (
            get_path(daily, "averageHeartRate")
            or get_path(daily, "averageHR")
            or get_path(daily, "avgHeartRate")
            or get_path(spo2, "averageHR")
        ),
        "resting_heart_rate_bpm": (
            get_path(daily, "restingHeartRate")
            or get_path(sleep, "restingHeartRate")
        ),
    }


def completed_overnight(summary, expected_date):
    """Return true only when Garmin has finalised the requested night's sleep."""
    try:
        heart_rate = float(summary["average_sleep_heart_rate_bpm"])
    except (KeyError, TypeError, ValueError):
        return False
    return (
        summary.get("sleep_date") == expected_date
        and summary.get("sleep_start_gmt") is not None
        and summary.get("sleep_end_gmt") is not None
        and heart_rate > 0
    )


def token_json(name):
    value = os.getenv(name)
    return base64.b64decode(value).decode() if value else None


def call(api, name, *args):
    method = getattr(api, name, None)
    if not method:
        return None
    try:
        return method(*args)
    except Exception as exc:
        return {"unavailable": str(exc)}


def main() -> bool:
    # Import lazily so the pure validation functions stay independently testable.
    from garminconnect import Garmin

    # Garmin calendar dates are local-day dates. The record ending this morning
    # is dated with today's Sydney date, not the runner's UTC date.
    today = datetime.now(SYDNEY).date()
    start_date = today - timedelta(days=42)
    tokens = token_json("GARMIN_TOKENS_B64")
    api = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
    api.login(tokenstore=tokens)

    start, end, today_text = start_date.isoformat(), today.isoformat(), today.isoformat()
    sleep = call(api, "get_sleep_data", today_text)
    overnight = sleep_recovery_summary(sleep, today_text)

    # An unfinished record is normal before Garmin has completed its overnight
    # processing. It is not a workflow error: preserve the last valid snapshot
    # and let the next scheduled retry try again.
    if not completed_overnight(overnight, today_text):
        print(
            "Garmin has not finalised the Sydney overnight record for "
            f"{today_text}; preserving the previous valid snapshot."
        )
        return False

    recent_sleep_recovery = [overnight]
    for offset in range(1, 15):
        sleep_date = (today - timedelta(days=offset)).isoformat()
        recent_sleep_recovery.append(
            sleep_recovery_summary(call(api, "get_sleep_data", sleep_date), sleep_date)
        )

    snapshot = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_timezone": "Australia/Sydney",
        "window": {"start": start, "end": end},
        "overnight_sleep_complete": True,
        "activities": call(api, "get_activities_by_date", start, end),
        "daily_summaries": [
            call(api, "get_user_summary", (start_date + timedelta(days=i)).isoformat())
            for i in range(43)
        ],
        "sleep": sleep,
        "overnight_sleep_recovery": overnight,
        "recent_sleep_recovery": recent_sleep_recovery,
        "heart_rate": call(api, "get_heart_rates", today_text),
        "training_readiness": call(api, "get_training_readiness", today_text),
        "training_status": call(api, "get_training_status", today_text),
        "race_predictions": call(api, "get_race_predictions"),
    }
    Path("data").mkdir(exist_ok=True)
    Path("data/latest.json").write_text(json.dumps(snapshot, indent=2, default=str) + "\n")
    return True


if __name__ == "__main__":
    main()
