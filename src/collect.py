"""Read-only Garmin Connect snapshot for a cloud-based running coach."""
import base64, json, os
from datetime import date, timedelta
from pathlib import Path
from garminconnect import Garmin

TODAY = date.today()
START = TODAY - timedelta(days=42)

def token_json(name):
    value = os.getenv(name)
    return base64.b64decode(value).decode() if value else None

def call(api, name, *args):
    method = getattr(api, name, None)
    if not method: return None
    try: return method(*args)
    except Exception as exc: return {"unavailable": str(exc)}

def main():
    tokens = token_json("GARMIN_TOKENS_B64")
    api = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
    api.login(tokenstore=tokens)
    start, end, today = START.isoformat(), TODAY.isoformat(), TODAY.isoformat()
    snapshot = {
      "generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
      "window": {"start": start, "end": end},
      "activities": call(api, "get_activities_by_date", start, end),
      "daily_summaries": [call(api, "get_user_summary", (START + timedelta(days=i)).isoformat()) for i in range(43)],
      "sleep": call(api, "get_sleep_data", today),
      "heart_rate": call(api, "get_heart_rates", today),
      "training_readiness": call(api, "get_training_readiness", today),
      "training_status": call(api, "get_training_status", today),
      "race_predictions": call(api, "get_race_predictions"),
    }
    Path("data").mkdir(exist_ok=True)
    Path("data/latest.json").write_text(json.dumps(snapshot, indent=2, default=str) + "\n")

if __name__ == "__main__": main()
