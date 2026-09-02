import unittest

from src.collect import completed_overnight, sleep_recovery_summary


class SleepRecoveryTests(unittest.TestCase):
    DATE = "2026-09-03"

    def test_completed_record_requires_same_date_times_and_heart_rate(self):
        record = {
            "sleep_date": self.DATE,
            "sleep_start_gmt": "2026-09-02T13:02:00.0",
            "sleep_end_gmt": "2026-09-02T21:01:00.0",
            "average_sleep_heart_rate_bpm": 51,
        }
        self.assertTrue(completed_overnight(record, self.DATE))

        for key in ("sleep_start_gmt", "sleep_end_gmt", "average_sleep_heart_rate_bpm"):
            incomplete = dict(record)
            incomplete[key] = None
            self.assertFalse(completed_overnight(incomplete, self.DATE))

        self.assertFalse(completed_overnight(record, "2026-09-04"))

    def test_avg_heart_rate_alias_is_captured(self):
        summary = sleep_recovery_summary(
            {
                "dailySleepDTO": {
                    "calendarDate": self.DATE,
                    "sleepStartTimestampGMT": "2026-09-02T13:02:00.0",
                    "sleepEndTimestampGMT": "2026-09-02T21:01:00.0",
                    "avgHeartRate": 51,
                }
            },
            self.DATE,
        )
        self.assertEqual(summary["average_sleep_heart_rate_bpm"], 51)
        self.assertTrue(completed_overnight(summary, self.DATE))


if __name__ == "__main__":
    unittest.main()
