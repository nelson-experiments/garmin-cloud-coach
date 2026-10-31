import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.lap_backfill import backfill_laps


class API:
    def __init__(self):
        self.calls = []

    def get_activities(self, start, limit):
        return [{"activityId": i} for i in range(1, 4)][start:start + limit]

    def get_activity_splits(self, identifier):
        self.calls.append(identifier)
        if identifier == "1":
            raise RuntimeError("temporary failure")
        return {"lapDTOs": []}

    def get_activity(self, identifier):
        return {"activityId": identifier}


class LapBackfillTests(unittest.TestCase):
    @patch("src.lap_backfill.time.sleep")
    def test_bounded_resume_empty_laps_and_deferred_failures(self, _sleep):
        with tempfile.TemporaryDirectory() as root:
            api = API()
            backfill_laps(api, root, max_attempts=2)
            self.assertEqual(api.calls, ["1", "2"])
            backfill_laps(api, root, max_attempts=2)
            self.assertEqual(api.calls, ["1", "2", "3"])
            self.assertTrue((Path(root) / "laps/2.json").exists())
            self.assertTrue((Path(root) / "laps/3.json").exists())
