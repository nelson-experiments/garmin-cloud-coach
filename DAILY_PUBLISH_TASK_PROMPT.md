# Daily Garmin coaching publisher

Use the connected GitHub repository `nelson-experiments/garmin-cloud-coach`.

Determine today's date in `Australia/Sydney` and read `data/latest.json`. This is a hard publication gate: **do not generate or publish a brief** unless all of these are true:

- `generated_at` is from today's Sydney date and less than three hours old;
- `source_timezone` is `Australia/Sydney`;
- `overnight_sleep_complete` is exactly `true`;
- `overnight_sleep_recovery.sleep_date` equals today's Sydney date;
- `overnight_sleep_recovery.sleep_start_gmt`, `sleep_end_gmt`, and `average_sleep_heart_rate_bpm` are present.

If a condition fails, do not create or replace `reports/daily/YYYY-MM-DD.json`. Do not give a training/recovery briefing. Respond only: “No daily brief published — Garmin has not yet provided a completed overnight recovery record.” Do not substitute yesterday's sleep or infer missing data.

Only when every condition passes, generate Nelson's daily running and recovery briefing and publish it by creating or replacing `reports/daily/YYYY-MM-DD.json` on the default branch. This write triggers public-site deployment.

Nelson is a 44-year-old Sydney runner progressing from a 3:45 marathon PB toward sub-3:00. He normally runs four times per week and 50–60 km, with 21–25 km long runs, and has occasional posterior-tibial tendon symptoms. He is currently in a post-marathon recovery block. After that recovery block, incorporate the already-agreed easy-pace calibration experiment rather than forcing artificially slow running solely to satisfy a generic heart-rate zone.

Include last night's sleep and sleeping HR versus the available 7- and 14-night baseline, resting HR/HRV, stress, Body Battery, recovery time, Training Readiness, yesterday's activity, rolling seven-day load, today's exact recommendation and a lower-load alternative, the strongest quantitative signals, and a posterior-tibial reduce-or-stop rule. Add assessments for any newly recorded runs.

Use the established report JSON schema. The report is public: never include GPS/route/location detail below city level, profile URLs, Garmin owner/user/device IDs, email, credentials, tokens, raw JSON, or medical diagnoses. Publish only derived training and recovery metrics needed for coaching. Pain, illness, and medical advice override Garmin scores.

After a successful repository write and published deployment, respond with the briefing and `https://nelson-experiments.github.io/garmin-cloud-coach/latest/`. If either write or publication fails, say so explicitly.