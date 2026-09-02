# Published coaching reports

`daily/YYYY-MM-DD.json` contains the privacy-filtered coaching interpretation produced by the scheduled ChatGPT Work task. The static-site build publishes only these derived reports and selected run metrics; it never copies `data/latest.json`, coordinates, routes, profile data, or Garmin credentials into the public artifact.

Daily report files are immutable historical records except when the same day's task corrects or completes a report after delayed Garmin synchronization.
