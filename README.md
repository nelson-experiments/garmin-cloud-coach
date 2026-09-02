# Garmin cloud coach

Runs in GitHub Actions, collects a read-only snapshot from Garmin Connect, and commits `data/latest.json` to a **private** repository for a ChatGPT scheduled coaching task to read. The task writes a privacy-filtered coaching report back to the repository, which is rendered as a public historical site.

## Setup

1. Create a new private GitHub repository and upload this folder.
2. In **Settings → Actions → General**, set workflow permissions to **Read and write**.
3. In **Settings → Secrets and variables → Actions**, add `GARMIN_EMAIL`, `GARMIN_PASSWORD`, and optionally `GARMIN_TOKENS_B64` (a base64-encoded JSON token store). Use a dedicated Garmin password and never commit credentials or tokens.
4. Run **Actions → Refresh Garmin coach snapshot → Run workflow**. Confirm `data/latest.json` was created, then connect that private repository to ChatGPT's GitHub app.
5. Create the weekly scheduled task with the prompt in `COACH_TASK_PROMPT.md`.
6. Create or update the daily scheduled task with `DAILY_PUBLISH_TASK_PROMPT.md`, scheduled for 8:00 am Australia/Sydney after the 7:45 am Garmin refresh.
7. In **Settings → Pages**, select **GitHub Actions** as the publishing source. The public site keeps `latest/`, dated daily reports, run pages, and an archive while the raw repository remains private.

## Authentication note

Garmin's supported Connect developer APIs are enterprise-only. This project instead uses the community `garminconnect` client, which relies on Garmin's private Connect endpoints and can break when Garmin changes sign-in. It is read-only. If Garmin enables MFA or invalidates sessions, update the repository secret with a freshly generated token store, or use the official API if you obtain enterprise approval.

## What is collected and published

The private snapshot contains 42 days of activities and daily summaries, plus today's sleep, heart-rate, training-readiness, training-status and race-prediction data. `src/build_site.py` explicitly selects the few metrics used on the public pages and excludes coordinates, routes and profile fields. Coaching prompts treat metrics as decision support, not medical advice.
