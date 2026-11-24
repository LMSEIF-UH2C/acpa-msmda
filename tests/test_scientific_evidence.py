import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class EvidenceTests(unittest.TestCase):
    def test_registry_covers_all_instruments(self):
        tests=json.loads((ROOT/"data/performance_tests.json").read_text(encoding="utf-8"))["tests"]
        evidence=json.loads((ROOT/"data/scientific_evidence.json").read_text(encoding="utf-8"))
        entries=evidence["instruments"]
        self.assertCountEqual([x["id"] for x in entries],[x["id"] for x in tests])
        for entry in entries:
            self.assertEqual(entry["protocol_status"],"to_confirm")
            self.assertEqual(entry["empirical_status"],"not_assessed_for_current_implementation")
            self.assertTrue(entry["limitations"])
            self.assertTrue(all(url.startswith("https://doi.org/") for url in entry["reference_urls"]))
