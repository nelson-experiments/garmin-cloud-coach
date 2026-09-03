import unittest
from pathlib import Path


PROMPT = Path("DAILY_PUBLISH_TASK_PROMPT.md").read_text(encoding="utf-8")


class DailyPromptContractTests(unittest.TestCase):
    def test_environmental_context_is_required(self):
        for field in (
            "minTemperature",
            "maxTemperature",
            "relative humidity",
            "dew point",
            "cooler conditions",
            "environment",
        ):
            self.assertIn(field, PROMPT)

    def test_heat_does_not_automatically_count_as_non_adherence(self):
        self.assertIn(
            "environmental context, not automatically as poor adherence",
            PROMPT,
        )

    def test_tendon_specific_advice_stays_disabled(self):
        self.assertIn(
            "Do not include posterior-tibial-specific advice unless Nelson reports that symptom again.",
            PROMPT,
        )


if __name__ == "__main__":
    unittest.main()
