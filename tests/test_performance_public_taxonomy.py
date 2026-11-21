"""Public-facing Performance Lab must not expose research-document taxonomies."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PublicPerformanceTaxonomyTests(unittest.TestCase):
    def test_no_provenance_filters_or_labels(self):
        page=(ROOT/"pages"/"2_Performance_Lab.py").read_text(encoding="utf-8")
        for forbidden in ("Circulaire 2358/25","Thèse","Collection","**Origine :**","protocoles de thèse"):
            self.assertNotIn(forbidden,page)
        self.assertIn('st.selectbox("Domaine"',page)
    def test_sources_retained_in_internal_registry(self):
        import json
        tests=json.loads((ROOT/"data"/"performance_tests.json").read_text(encoding="utf-8"))["tests"]
        self.assertTrue(all("source" in t for t in tests))
if __name__=="__main__":unittest.main()
