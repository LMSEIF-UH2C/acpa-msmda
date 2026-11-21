"""Regression checks for the public research demonstrator."""
import json
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"

def start(language="fr"):
    app = AppTest.from_file(str(APP), default_timeout=25).run()
    if language != "fr":
        app.selectbox[0].set_value(language).run()
    return app

class PublicWebDemoTests(unittest.TestCase):
    def test_each_language_computes(self):
        for language in ("fr", "en", "ar"):
            with self.subTest(language=language):
                app = start(language)
                self.assertFalse(app.exception)
                app.button[0].click().run()
                self.assertFalse(app.exception)
                lang, result = app.session_state["acpa_result"]
                self.assertEqual(lang, language)
                self.assertEqual(result["catalogue_status"], "SYNTHETIC_NOT_EXPERT_EVALUATED")
                self.assertEqual(result["validation_status"], "ILLUSTRATIVE_ONLY")
                self.assertEqual(len(result["recommendations"]), 5)
                self.assertEqual(len(result["alpha"]), 18)
                self.assertAlmostEqual(sum(result["alpha"].values()), 1.0)
                self.assertEqual(len(result["criteria_labels"]), 18)
                self.assertEqual(len(app.get("error")), 0)
                self.assertEqual(len(app.get("json")), 1)
                self.assertTrue(json.dumps(result, ensure_ascii=False, allow_nan=False))

    def test_empty_input_does_not_compute(self):
        app = start()
        app.text_area[0].set_value("   ").run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("error")), 1)
        self.assertNotIn("acpa_result", app.session_state)

    def test_language_change_hides_previous_result(self):
        app = start()
        app.button[0].click().run()
        self.assertEqual(app.session_state["acpa_result"][0], "fr")
        app.selectbox[0].set_value("en").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["acpa_result"][0], "fr")
        self.assertEqual(len(app.get("subheader")), 0)

    def test_input_length_limit(self):
        app = start()
        self.assertEqual(app.text_area[0].proto.max_chars, 1000)

if __name__ == "__main__":
    unittest.main()
