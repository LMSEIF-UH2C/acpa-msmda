import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class LabLibraryTests(unittest.TestCase):
    def test_documentary_entries_do_not_enter_measurement_registry(self):
        library = json.loads((ROOT / "data/lab_library.json").read_text(encoding="utf-8"))
        tests = json.loads((ROOT / "data/performance_tests.json").read_text(encoding="utf-8"))["tests"]
        entries = [i for g in library["groups"] for i in g["entries"]]
        ids = [i["id"] for i in entries]
        self.assertEqual(len(ids), 83)
        self.assertEqual(len(set(ids)), len(ids))
        self.assertFalse(set(ids) & {i["id"] for i in tests})
        self.assertEqual(len(tests), 32)
        for group in library["groups"]:
            self.assertEqual(set(group["label"]), {"fr", "ar", "en"})
        for item in entries:
            self.assertEqual(item["status"], "documentary_lead")
            self.assertIn(item["level"], {"complementary", "specialist"})
            self.assertTrue(item["url"].startswith("https://"))
            self.assertTrue(item["citation"].strip())
