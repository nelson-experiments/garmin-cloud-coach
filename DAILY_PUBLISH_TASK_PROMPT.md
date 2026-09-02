# Daily Garmin coaching publisher

Use the connected GitHub repository `nelson-experiments/garmin-cloud-coach`.

Read `data/latest.json` and determine today's calendar date in `Australia/Sydney`. Generate Nelson's daily running and recovery briefing, then publish it by creating or replacing `reports/daily/YYYY-MM-DD.json` on the default branch. This repository write is the intended action: it triggers the public site deployment. Do not merely return the JSON in chat.

Nelson is a 44-year-old Sydney runner progressing from a 3:45 marathon PB toward sub-3:00. He normally runs four times per week and 50–60 km, with 21–25 km long runs, and has occasional posterior-tibial tendon symptoms. He is currently in a post-marathon recovery block. After that recovery block, incorporate the already-agreed easy-pace calibration experiment rather than forcing artificially slow running solely to satisfy a generic heart-rate zone.

First verify `generated_at`. If the snapshot is more than 36 hours old, set `status` to `stale`, clearly say the data is stale, and give only conservative general advice. Otherwise:

1. Assess last night's sleep, sleeping heart rate versus the recent 14-night range where available, resting HR/HRV, stress, Body Battery, recovery time and Training Readiness.
2. Summarise yesterday's activity and the rolling seven-day load.
3. Give today's exact session or rest recommendation, plus an alternative.
4. Identify the two or three quantitative signals driving the recommendation.
5. Add a clear reduce-or-stop rule for posterior-tibial symptoms.
6. Add a `run_assessments` entry for every run since the previous daily report that does not already have an assessment. Use the Garmin `activityId` only as `activity_id`.

Write valid UTF-8 JSON with this shape:

```json
{
  "date": "YYYY-MM-DD",
  "generated_at": "ISO-8601 timestamp",
  "snapshot_generated_at": "ISO-8601 timestamp copied from the snapshot",
  "status": "current or stale",
  "headline": "short, decision-oriented headline",
  "summary": "two or three concise sentences",
  "recovery": [
    {"label": "Sleep", "value": "7h 30m", "context": "comparison or interpretation", "status": "good, watch, alert, or neutral"}
  ],
  "yesterday": {"title": "short activity title", "summary": "activity and load interpretation"},
  "recommendation": {
    "title": "exact session or Rest",
    "details": ["duration, intensity, terrain and other execution details"],
    "alternative": "lower-load alternative",
    "reduce_or_stop": "specific symptom rule"
  },
  "signals": [
    {"label": "signal name", "value": "quantitative value", "interpretation": "why it matters today"}
  ],
  "caveats": ["missing, stale or contradictory Garmin data"],
  "run_assessments": [
    {
      "activity_id": "Garmin activityId as a string",
      "summary": "one-sentence run summary",
      "assessment": "concise coaching interpretation",
      "signals": [{"label": "metric", "value": "value", "interpretation": "meaning"}]
    }
  ]
}
```

Privacy boundary: the report will be public. Never include latitude, longitude, route or location detail below city level, profile URLs, Garmin owner/user/device IDs, email addresses, credentials, tokens, raw JSON, or medical diagnoses. Only publish derived training and recovery metrics needed for coaching. Do not infer illness or injury. Pain, illness and medical advice override Garmin scores.

After the repository write succeeds, respond in this chat with the briefing and link to `https://nelson-experiments.github.io/garmin-cloud-coach/latest/`. If the write fails or requires approval, say so explicitly and do not claim publication succeeded.
