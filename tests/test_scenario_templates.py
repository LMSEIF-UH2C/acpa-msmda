import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.scenario_templates import load_templates,apply_template,scenario_checks
class TemplateTests(unittest.TestCase):
    def test_templates_are_consistent(self):
        self.assertGreaterEqual(len(load_templates()),4)
    def test_apply_template(self):
        state={}
        apply_template(load_templates()[0],state)
        self.assertEqual(state["duration"],60)
        self.assertEqual(state["minutes_2"],30)
        self.assertTrue(state["evaluation_2"])
    def test_checks(self):
        rows=[{"Phase":"Diagnostic","Durée (min)":5,"Activité / consignes":"","Évaluation / feedback":""}]
        self.assertEqual(len(scenario_checks(rows,"")),3)
if __name__=="__main__":unittest.main()
