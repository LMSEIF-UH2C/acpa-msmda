import json
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"sprint30", "saut_horizontal", "medecine_ball", "sargent",
            "souplesse_assise", "front_plank", "killy", "handgrip"}


class LabIllustrationTests(unittest.TestCase):
    def test_priority_images_are_present_and_readable(self):
        registry = json.loads((ROOT / "data/performance_tests.json").read_text(encoding="utf-8"))
        self.assertTrue(EXPECTED <= {x["id"] for x in registry["tests"]})
        for test_id in sorted(EXPECTED):
            with self.subTest(test_id=test_id):
                path = ROOT / "assets/lab" / (test_id + ".jpg")
                self.assertTrue(path.is_file(), f"Missing required illustration: {path.name}")
                with Image.open(path) as image:
                    self.assertEqual(image.format, "JPEG")
                    self.assertGreaterEqual(image.width, 300)
                    self.assertGreaterEqual(image.height, 200)
                    image.verify()
                self.assertLess(path.stat().st_size, 500_000)
