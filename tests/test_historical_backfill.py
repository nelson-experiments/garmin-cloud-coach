import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from src.historical_backfill import backfill, month_windows


class BackfillTests(unittest.TestCase):
    def test_windows_include_leap_day_and_partial_month(self):
        self.assertEqual(list(month_windows(date(2024, 2, 1), date(2024, 3, 2))),
                         [("2024-02-01", "2024-02-29"), ("2024-03-01", "2024-03-02")])

    def test_deduplication_and_resume(self):
        class API:
            calls = 0
            def get_activities_by_date(self, start, end):
                self.calls += 1
                return [{"activityId": 1}, {"activityId": 1}]
        api = API()
        with tempfile.TemporaryDirectory() as root:
            backfill(api, root, date(2024, 1, 31))
            backfill(api, root, date(2024, 1, 31))
            self.assertEqual(api.calls, 1)
            self.assertEqual(len(json.loads((Path(root) / "2024-01.json").read_text())["activities"]), 1)

    def test_failure_does_not_write_checkpoint(self):
        class API:
            def get_activities_by_date(self, start, end):
                return {"unavailable": "failure"}
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                backfill(API(), root, date(2024, 1, 31))
            self.assertEqual(list(Path(root).iterdir()), [])
