import unittest

from engine import recommend


class TestACPAEngine(unittest.TestCase):

    def test_low_cardio_limits_intensity(self):
        profile = {
            "mobility": "standard",
            "balance_support": "none",
            "cardio_tolerance": "low",
            "equipment": "mixed",
            "environment": "indoor",
            "objective": "general",
        }

        result = recommend(profile)

        for activity in result["recommendations"]:
            self.assertLessEqual(activity["intensity"], 1)

    def test_no_equipment(self):
        profile = {
            "mobility": "standard",
            "balance_support": "none",
            "cardio_tolerance": "moderate",
            "equipment": "none",
            "environment": "indoor",
            "objective": "general",
        }

        result = recommend(profile)

        for activity in result["recommendations"]:
            self.assertIn("none", activity["equipment"])

    def test_reduced_mobility_rule_is_triggered(self):
        profile = {
            "mobility": "reduced",
            "balance_support": "moderate",
            "cardio_tolerance": "moderate",
            "equipment": "none",
            "environment": "indoor",
            "objective": "general",
        }

        result = recommend(profile)

        rule_ids = [rule["id"] for rule in result["matched_rules"]]
        self.assertIn("R001", rule_ids)

    def test_high_balance_support_excludes_dynamic(self):
        profile = {
            "mobility": "standard",
            "balance_support": "high",
            "cardio_tolerance": "moderate",
            "equipment": "mixed",
            "environment": "indoor",
            "objective": "coordination",
        }

        result = recommend(profile)

        for activity in result["recommendations"]:
            self.assertNotIn("dynamic", activity["tags"])

    def test_recommendations_have_explanations(self):
        profile = {
            "mobility": "reduced",
            "balance_support": "high",
            "cardio_tolerance": "low",
            "equipment": "none",
            "environment": "indoor",
            "objective": "coordination",
        }

        result = recommend(profile)

        self.assertGreater(len(result["recommendations"]), 0)

        for activity in result["recommendations"]:
            self.assertTrue(activity["reasons"])


if __name__ == "__main__":
    unittest.main()
