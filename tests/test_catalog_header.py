"""L'en-tête descriptif du catalogue réel concorde avec ses fiches."""
import json
import unittest
from collections import Counter
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "data" / "real_tools_catalog.json"


class CatalogHeaderTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.tools = self.data["tools"]

    def test_counts_match_entries(self):
        status = Counter(t["evidence_status"] for t in self.tools)
        self.assertEqual(self.data["total"], len(self.tools))
        self.assertEqual(self.data["total"], 2466)
        self.assertEqual(self.data["status_counts"], dict(status))
        self.assertEqual(self.data["feature_verified_count"], status["FEATURES_VERIFIED_ON_OFFICIAL_SITE"])
        self.assertEqual(self.data["source_links_added"], sum(bool(t.get("source_url")) for t in self.tools))
        self.assertEqual(self.data["criteria_method_counts"],
                         dict(Counter(t["criteria_method"] for t in self.tools)))

    def test_notice_does_not_claim_validation(self):
        notice = self.data["notice"]
        self.assertIn("ne sont pas des mesures validées", notice)
        self.assertNotIn("Seules les fiches", notice)


if __name__ == "__main__":
    unittest.main()
