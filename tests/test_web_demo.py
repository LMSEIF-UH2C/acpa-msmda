"""Smoke tests for the public Streamlit research demonstrator."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


class PublicWebDemoTests(unittest.TestCase):
    def test_loads_and_computes_synthetic_ranking(self):
        app = AppTest.from_file(str(APP), default_timeout=20).run()
        self.assertFalse(app.exception)
        app.form_submit_button[0].click().run()
        self.assertFalse(app.exception)

        language, result = app.session_state["acpa_result"]
        self.assertEqual(language, "fr")
        self.assertEqual(result["catalogue_status"], "SYNTHETIC_NOT_EXPERT_EVALUATED")
        self.assertEqual(result["validation_status"], "ILLUSTRATIVE_ONLY")
        self.assertEqual(len(result["recommendations"]), 5)
        self.assertEqual(len(result["alpha"]), 18)
        self.assertAlmostEqual(sum(result["alpha"].values()), 1.0)


if __name__ == "__main__":
    unittest.main()
