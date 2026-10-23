import unittest
from src.lap_backfill import eligible


class LapSelectionTests(unittest.TestCase):
    def test_matched_windows_and_distance(self):
        activity = {"startTimeLocal": "2026-07-05 06:00:00",
                    "activityType": {"typeKey": "running"}, "distance": 42000}
        self.assertTrue(eligible(activity))
        activity["startTimeLocal"] = "2026-07-06 06:00:00"
        self.assertFalse(eligible(activity))
        activity["startTimeLocal"] = "2026-01-18 06:00:00"
        activity["distance"] = 10000
        self.assertTrue(eligible(activity))
        activity["distance"] = 9999
        self.assertFalse(eligible(activity))
