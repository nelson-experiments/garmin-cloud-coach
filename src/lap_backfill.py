"""Collect private lap records for matched marathon build-ups."""
import json
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

RACES = (date(2024, 9, 15), date(2025, 7, 6), date(2026, 7, 5))


def eligible(activity):
    day = date.fromisoformat(activity["startTimeLocal"][:10])
    return (activity.get("activityType", {}).get("typeKey") == "running"
            and activity.get("distance", 0) >= 10000
            and any(race - timedelta(weeks=24) <= day <= race for race in RACES))


def backfill_laps(api, root="data/history"):
    root = Path(root)
    destination = root / "laps"
    destination.mkdir(parents=True, exist_ok=True)
    activities = {}
    for source in sorted(root.glob("20??-??.json")):
        for activity in json.loads(source.read_text())["activities"]:
            if eligible(activity):
                activities[str(activity["activityId"])] = activity
    for identifier, activity in activities.items():
        target = destination / f"{identifier}.json"
        if target.exists():
            continue
        splits = api.get_activity_splits(identifier)
        if not isinstance(splits, dict) or not isinstance(splits.get("lapDTOs"), list) or not splits["lapDTOs"]:
            raise ValueError(f"No valid laps returned for {identifier}")
        metadata = api.get_activity(identifier)
        if not isinstance(metadata, dict) or not metadata.get("activityId"):
            raise ValueError(f"No valid metadata returned for {identifier}")
        payload = {"generated_at": datetime.now(UTC).isoformat(),
                   "activity": activity, "splits": splits, "metadata": metadata}
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n")
        temporary.replace(target)
        print(f"Archived laps: {identifier}, {len(splits['lapDTOs'])} laps")
        time.sleep(0.3)
