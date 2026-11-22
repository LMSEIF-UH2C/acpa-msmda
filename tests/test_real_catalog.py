"""Regression tests for real, unscored catalogue."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.real_catalog import load_real_tools,match_pending_tools,match_real_tools,recommend

class RealCatalogueTests(unittest.TestCase):
    def test_scores_only_where_rated(self):
        tools=load_real_tools()
        self.assertGreaterEqual(len(tools),10)
        verified={t["id"] for t in tools if t["evidence_status"] in ("OFFICIAL_SOURCE_FEATURES_ONLY","FEATURES_VERIFIED_ON_OFFICIAL_SITE")}
        self.assertTrue(all(t["criteria_scores"] is None for t in tools if t["id"] in verified))
    def test_endurance_match(self):
        result=match_real_tools("endurance suivi course")
        self.assertIn("strava",{t["id"] for t in result["matches"]})
        self.assertFalse(result["ranking_validated"])
        self.assertIsNone(result["scores"])
    def test_no_false_match(self):
        result=match_real_tools("zzzzxyz")
        self.assertEqual(result["matches"],[])
    def test_recommend_uses_whole_catalogue_and_flags_status(self):
        result=recommend("basket tactique et score")
        self.assertGreater(len(result["matches"]),50)
        self.assertTrue(any(not t["verified"] for t in result["matches"]))
        self.assertTrue(all({"basketball","tactique","score"}&set(t["matched_terms"]) for t in result["matches"]))
        covered=[len(t["matched_terms"]) for t in result["matches"]]
        self.assertEqual(covered,sorted(covered,reverse=True))
        self.assertEqual(recommend("zzzzxyz")["matches"],[])
    def test_recommend_offline_and_votes(self):
        offline=recommend("course endurance sans connexion")["matches"]
        self.assertFalse(any(t["requirement"]=="internet" for t in offline))
        base=recommend("badminton")["matches"]
        last=base[-1]["id"]
        self.assertLess(recommend("badminton",votes={last:3})["matches"].index(next(t for t in recommend("badminton",votes={last:3})["matches"] if t["id"]==last)),len(base)-1)
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


def test_recommend_puts_verified_first_at_equal_coverage():
    matches = recommend("course d'endurance, 35 élèves, sans connexion")["matches"]
    for before, after in zip(matches, matches[1:]):
        if len(before["matched_terms"]) == len(after["matched_terms"]):
            assert before["verified"] or not after["verified"]
    assert [t["name"] for t in matches[:2]] == ["Garmin Connect", "Strava"]


def test_recommend_uses_criteria_scores_and_relevance():
    from acpa_msmda.scoring import relevant
    tools={t["id"]:t for t in load_real_tools()}
    result=recommend("volley score")
    rated=[t for t in result["matches"] if t["criteria_total"] is not None]
    assert rated and all(relevant(t["criteria_scores"]) for t in rated)
    off=[t for t in tools.values() if t.get("criteria_scores") and not relevant(t["criteria_scores"])]
    ids={t["id"] for t in recommend("score basket volley course yoga golf randonnée")["matches"]}
    assert off and not ids.intersection(t["id"] for t in off)
    # À besoins et statut égaux, un meilleur score passe devant.
    m=result["matches"]
    for a,b in zip(m,m[1:]):
        if len(a["matched_terms"])==len(b["matched_terms"]) and a["verified"]==b["verified"]:
            sa=a["criteria_total"] if a["criteria_total"] is not None else 50.0
            sb=b["criteria_total"] if b["criteria_total"] is not None else 50.0
            assert sa>=sb
