"""Archive Garmin activity splits, newest first, across the full activity history."""
import json
import time
from datetime import UTC, datetime
from pathlib import Path

PAGE_SIZE = 100
MAX_ATTEMPTS = 50


def backfill_laps(api, root="data/history", max_attempts=MAX_ATTEMPTS):
    """Resume from existing files; retry failed activities on a later refresh.

    Pagination covers activity types and dates beyond the monthly summary archive.
    A bounded number of split requests protects the normal snapshot refresh.
    """
    destination = Path(root) / "laps"
    destination.mkdir(parents=True, exist_ok=True)
    failures_path = destination / "_retry.json"
    try:
        failures = json.loads(failures_path.read_text()) if failures_path.exists() else {}
        if not isinstance(failures, dict):
            failures = {}
    except (ValueError, OSError):
        failures = {}
    now = datetime.now(UTC).timestamp()
    offset = 0
    attempts = 0
    seen = set()
    while attempts < max_attempts:
        activities = api.get_activities(offset, PAGE_SIZE)
        if not isinstance(activities, list):
            raise ValueError("Invalid activity page")
        if not activities:
            break
        for activity in activities:
            if not isinstance(activity, dict) or not activity.get("activityId"):
                raise ValueError("Activity page contains a missing ID")
            identifier = str(activity["activityId"])
            if identifier in seen:
                continue
            seen.add(identifier)
            target = destination / f"{identifier}.json"
            if target.exists():
                failures.pop(identifier, None)
                continue
            if failures.get(identifier, 0) > now:
                continue
            attempts += 1
            try:
                splits = api.get_activity_splits(identifier)
                # An empty lap list is a valid response for some activity types.
                if not isinstance(splits, dict) or not isinstance(splits.get("lapDTOs"), list):
                    raise ValueError("Invalid split response")
                metadata = api.get_activity(identifier)
                if not isinstance(metadata, dict) or not metadata.get("activityId"):
                    raise ValueError("Invalid activity metadata")
                payload = {"generated_at": datetime.now(UTC).isoformat(),
                           "activity": activity, "splits": splits, "metadata": metadata}
                temporary = target.with_suffix(".tmp")
                temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n")
                temporary.replace(target)
                failures.pop(identifier, None)
                print(f"Archived splits: {identifier}, {len(splits['lapDTOs'])} laps")
            except Exception:
                # Do not log API exception text: it may contain credentials.
                failures[identifier] = now + 86400
                print(f"Splits unavailable for {identifier}; will retry.")
            finally:
                temporary_retry = failures_path.with_suffix(".tmp")
                temporary_retry.write_text(json.dumps(failures, indent=2) + "\n")
                temporary_retry.replace(failures_path)
                time.sleep(0.3)
            if attempts >= max_attempts:
                break
        if len(activities) < PAGE_SIZE:
            break
        offset += len(activities)
    print(f"Split collection attempted {attempts} activities this refresh.")
