"""Regression tests for real, unscored catalogue."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.real_catalog import load_real_tools,match_pending_tools,match_real_tools

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
    def test_no_internet_tool_when_offline(self):
        online=match_real_tools("gymnastique ressources")["matches"]
        self.assertTrue(any(t["requirement"]=="internet" for t in online))
        offline=match_real_tools("gymnastique ressources sans connexion")["matches"]
        self.assertFalse(any(t["requirement"]=="internet" for t in offline))
    def test_pending_leads_bridge_french_words_and_follow_votes(self):
        leads=match_pending_tools("chronométrage vitesse")
        self.assertTrue(leads)
        self.assertTrue(all(t["evidence_status"]=="OFFICIAL_LINK_ADDED_PENDING_FEATURE_REVIEW" for t in leads))
        self.assertTrue(all({"stopwatch","timer","lap","sprint","speed"}&set(t["matched_terms"]) for t in leads))
        last=leads[-1]["id"]
        self.assertEqual(match_pending_tools("chronométrage vitesse",votes={last:3})[0]["id"],last)
        self.assertEqual(match_pending_tools("zzzzxyz"),[])
if __name__=="__main__":
    unittest.main()
