"""Regression tests for real, unscored catalogue."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.real_catalog import load_real_tools,match_real_tools

class RealCatalogueTests(unittest.TestCase):
    def test_no_real_scores(self):
        tools=load_real_tools()
        self.assertGreaterEqual(len(tools),10)
        self.assertTrue(all(t["criteria_scores"] is None for t in tools))
    def test_endurance_match(self):
        result=match_real_tools("endurance suivi course")
        self.assertIn("strava",{t["id"] for t in result["matches"]})
        self.assertFalse(result["ranking_validated"])
        self.assertIsNone(result["scores"])
    def test_no_false_match(self):
        result=match_real_tools("zzzzxyz")
        self.assertEqual(result["matches"],[])
    def test_internet_caution(self):
        result=match_real_tools("gymnastique ressources sans connexion")
        self.assertTrue(any("Connexion requise" in c for t in result["matches"] for c in t["cautions"]))
if __name__=="__main__":
    unittest.main()
