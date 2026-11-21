"""Stabilité : ouverture des pages, modèles, mesures signées et sécurité des exports CSV."""
import csv
import io
import json
import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda.scenario_engine import export_scenario_csv, safe_cell
from acpa_msmda.scenario_templates import load_templates, apply_template

PAGES = (
    "2_Performance_Lab.py",
    "3_Espace_Enseignant.py",
    "4_Technologies_Reelles.py",
    "5_Studio_Pedagogique.py",
)


class StabilityTests(unittest.TestCase):
    def test_all_pages_open(self):
        for filename in PAGES:
            with self.subTest(filename=filename):
                app = AppTest.from_file(str(ROOT / "pages" / filename), default_timeout=30).run()
                self.assertFalse(app.exception, str(app.exception))

    def test_template_state_values(self):
        template = load_templates()[0]
        state = {}
        apply_template(template, state)
        self.assertEqual(state["duration"], template["duration"])
        self.assertEqual(state["minutes_0"], template["phases"][0]["minutes"])

    def test_signed_test_metadata(self):
        tests = json.loads((ROOT / "data" / "performance_tests.json").read_text(encoding="utf-8"))["tests"]
        signed = {t["id"] for t in tests if t.get("signed")}
        self.assertEqual(signed, {"souplesse_assise", "souplesse_debout"})

    def test_csv_formula_protection(self):
        risky = ("=", "+", "-", "@", " =SUM(1,2)", chr(9) + "=1+1",
                 chr(13) + "@SUM(1)", chr(0xfeff) + "+1")
        for prefix in risky:
            with self.subTest(prefix=repr(prefix)):
                self.assertTrue(safe_cell(prefix).startswith("'"))
        self.assertEqual(safe_cell("Endurance"), "Endurance")
        self.assertEqual(safe_cell(-4.0), -4.0)
        csv_bytes = export_scenario_csv(
            {"Objectifs": "  =1+1"},
            [{"Phase": "Diagnostic", "Durée (min)": 5,
              "Activité / consignes": chr(9) + "+CMD"}],
        )
        rows = list(csv.reader(io.StringIO(csv_bytes.decode("utf-8-sig"))))
        self.assertEqual(rows[0][1], "'  =1+1")
        self.assertEqual(rows[3][2], "'" + chr(9) + "+CMD")

    def test_studio_widget_defaults_not_conflicting(self):
        source = (ROOT / "pages" / "5_Studio_Pedagogique.py").read_text(encoding="utf-8")
        self.assertIn("st.session_state.setdefault", source)
        self.assertNotIn('value=default,key=f"minutes_{i}"', source)


if __name__ == "__main__":
    unittest.main()
