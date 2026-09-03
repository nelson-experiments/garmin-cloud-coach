import unittest

from src.build_site import report_body


class ReportAdherenceRenderingTests(unittest.TestCase):
    def test_previous_day_adherence_is_rendered(self):
        report = {
            "date": "2026-09-04",
            "status": "current",
            "headline": "Test brief",
            "summary": "Test summary",
            "yesterday": {
                "title": "Easy run",
                "summary": "A run was recorded.",
                "adherence_verdict": "mostly_followed",
                "prescribed": "20–25 minutes easy.",
                "completed": "27 minutes easy.",
                "adherence_assessment": "The purpose was followed with a small duration difference.",
                "adherence_evidence": ["27 minutes completed versus 20–25 prescribed."],
                "adherence_caveats": ["Garmin cannot verify perceived effort."],
            },
            "recommendation": {},
        }

        rendered = report_body(report)

        self.assertIn("Plan adherence: Mostly Followed", rendered)
        self.assertIn("20–25 minutes easy.", rendered)
        self.assertIn("27 minutes easy.", rendered)
        self.assertIn("Garmin cannot verify perceived effort.", rendered)

    def test_legacy_report_without_adherence_still_renders(self):
        rendered = report_body({
            "date": "2026-09-03",
            "headline": "Legacy brief",
            "summary": "Legacy report.",
            "yesterday": {"title": "Rest", "summary": "No activity."},
            "recommendation": {},
        })

        self.assertNotIn("Plan adherence:", rendered)


if __name__ == "__main__":
    unittest.main()
