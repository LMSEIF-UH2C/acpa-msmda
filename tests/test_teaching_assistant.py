import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.teaching_assistant import suggestions

class AssistantTests(unittest.TestCase):
    def test_context(self):
        r=suggestions("Endurance","Collège","Aucune","Apprentissage")
        self.assertEqual(r["mode"],"rule_based")
        self.assertFalse(r["institutional_validation"])
        self.assertTrue(all(s["activity"]=="Endurance" and s["level"]=="Collège" for s in r["situations"]))
        self.assertTrue(all(t["source_url"] for t in r["tools"]))
        self.assertLessEqual(len(r["tools"]),3)
    def test_invalid_context(self):
        with self.assertRaises(ValueError):
            suggestions("unknown","Collège","Aucune","Apprentissage")
