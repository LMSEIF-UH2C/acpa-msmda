"""Catalogue checks: distinct real entries, source honesty, no invented scores."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.real_catalog import load_real_tools,match_real_tools
class CatalogueIntegrityTests(unittest.TestCase):
    def test_unique_identifiers_and_names(self):
        items=load_real_tools()
        self.assertGreaterEqual(len(items),200)
        self.assertEqual(len(items),len({t["id"] for t in items}))
        self.assertEqual(len(items),len({t["name"].casefold() for t in items}))
    def test_no_unverified_scoring(self):
        self.assertTrue(all(t.get("criteria_scores") is None for t in load_real_tools()))
    def test_recommendations_are_documented(self):
        for query in ("video analyse","endurance course","gymnastique video"):
            for t in match_real_tools(query)["matches"]:
                self.assertTrue(t["source_url"])
                self.assertIn(t["evidence_status"],("OFFICIAL_SOURCE_FEATURES_ONLY","FEATURES_VERIFIED_ON_OFFICIAL_SITE"))
    def test_pending_entries_are_not_suggested(self):
        pending={t["id"] for t in load_real_tools() if t["evidence_status"]=="PENDING_SOURCE_VERIFICATION"}
        for query in ("video analyse","endurance course"):
            self.assertFalse(pending.intersection({t["id"] for t in match_real_tools(query)["matches"]}))
if __name__=="__main__":unittest.main()
