# Garmin cloud coach

Runs in GitHub Actions, collects a minimal read-only snapshot from Garmin Connect, and commits `data/latest.json` to a **private** repository for a ChatGPT scheduled coaching task to read.

## Setup

1. Create a new private GitHub repository and upload this folder.
2. In **Settings → Actions → General**, set workflow permissions to **Read and write**.
3. In **Settings → Secrets and variables → Actions**, add `GARMIN_EMAIL`, `GARMIN_PASSWORD`, and optionally `GARMIN_TOKENS_B64` (a base64-encoded JSON token store). Use a dedicated Garmin password and never commit credentials or tokens.
4. Run **Actions → Refresh Garmin coach snapshot → Run workflow**. Confirm `data/latest.json` was created, then connect that private repository to ChatGPT's GitHub app.
5. Create the weekly scheduled task with the prompt in `COACH_TASK_PROMPT.md`. Schedule it for Sunday 7 pm Australia/Sydney, after the collector's daily refresh.

## Authentication note

Garmin's supported Connect developer APIs are enterprise-only. This project instead uses the community `garminconnect` client, which relies on Garmin's private Connect endpoints and can break when Garmin changes sign-in. It is read-only. If Garmin enables MFA or invalidates sessions, update the repository secret with a freshly generated token store, or use the official API if you obtain enterprise approval.

## What is collected

42 days of activities and daily summaries, plus today's sleep, heart-rate, training-readiness, training-status and race-prediction data. The coaching prompt should treat metrics as decision support, not medical advice.
