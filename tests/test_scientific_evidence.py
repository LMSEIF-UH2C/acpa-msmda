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

    def test_teacher_information_is_complete_in_three_languages(self):
        evidence=json.loads((ROOT/"data/scientific_evidence.json").read_text(encoding="utf-8"))
        for entry in evidence["instruments"] + evidence["methods"]:
            with self.subTest(entry=entry["id"]):
                self.assertTrue(entry["citation"].strip())
                self.assertEqual(set(entry["teacher_info"]), {"fr", "ar", "en"})
                self.assertTrue(all(v.strip() for v in entry["teacher_info"].values()))
        for entry in evidence["instruments"]:
            self.assertTrue(entry["reference_urls"] or entry["other_reference_urls"])
            self.assertTrue(all(url.startswith("https://") and not url.startswith("https://doi.org/")
                                for url in entry["other_reference_urls"]))

    def test_institutional_battery_and_complementary_groups(self):
        evidence=json.loads((ROOT/"data/scientific_evidence.json").read_text(encoding="utf-8"))
        entries=evidence["instruments"]
        self.assertCountEqual([x["id"] for x in entries if x["group"]=="institutional"],
                              ["leger20","sprint30","saut_horizontal","sargent","medecine_ball","souplesse_assise","souplesse_debout","flamingo","taille","poids","fc_repos"])
        self.assertEqual(sum(x["group"]=="complementary" for x in entries),8)
        self.assertEqual(set(evidence["group_labels"]),{"fr","ar","en"})
        for labels in evidence["group_labels"].values():
            self.assertEqual(len(labels),2)
            self.assertTrue(all(label.strip() for label in labels))
