"""Banque visuelle du Laboratoire : couverture des 32 épreuves, licences, sécurité des SVG, affichage facultatif."""
import json
import re
import sys
import unittest
from pathlib import Path

from PIL import Image
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from acpa_msmda import visual_bank  # noqa: E402

TESTS = {x["id"] for x in json.loads((ROOT / "data/performance_tests.json").read_text(encoding="utf-8"))["tests"]}
MANIFEST = visual_bank.manifest()
SPECIFIC = {x["id"] for x in MANIFEST["lab_specific"]}
GENERIC = {x["id"] for x in MANIFEST["lab_generic"]}


class Coverage(unittest.TestCase):
    def test_all_32_tests_kept_and_covered_once(self):
        self.assertEqual(len(TESTS), 32)
        self.assertEqual(SPECIFIC | GENERIC, TESTS)
        self.assertFalse(SPECIFIC & GENERIC)
        self.assertEqual((len(SPECIFIC), len(GENERIC)), (14, 18))
        self.assertIn("handgrip", GENERIC)              # handgrip conservé, sans illustration

    def test_every_test_has_a_visual_entry(self):
        for test_id in TESTS:
            visual = visual_bank.visual_for(test_id)
            self.assertIsNotNone(visual, test_id)
            self.assertTrue(visual.note, test_id)


class Licences(unittest.TestCase):
    def test_pictograms_present_credited_unmodified(self):
        for icon in MANIFEST["icons"]:
            with self.subTest(icon=icon["id"]):
                self.assertTrue((ROOT / icon["path"]).is_file())
                self.assertEqual(icon["license"], "CC-BY-SA-4.0")
                self.assertFalse(icon["modified"])
                self.assertIn("openmoji", icon["source"])
        self.assertTrue(any("CC BY-SA 4.0" in line for line in visual_bank.credits()))

    def test_svg_have_no_script_or_external_resource(self):
        bad = re.compile(r"<script|<foreignObject|\son[a-z]+\s*=|(xlink:)?href\s*=\s*[\"']https?:", re.IGNORECASE)
        for svg in (ROOT / "assets/visual-bank/pictograms").glob("*.svg"):
            self.assertIsNone(bad.search(svg.read_text(encoding="utf-8")), svg.name)

    def test_external_references_not_hotlinked(self):
        source = (ROOT / "src/acpa_msmda/visual_bank.py").read_text(encoding="utf-8")
        self.assertNotIn("wikimedia.org", source)
        self.assertNotIn("requests", source)


class Illustrations(unittest.TestCase):
    def test_accepted_illustrations_are_present_and_light(self):
        for test_id in sorted(SPECIFIC):
            with self.subTest(test_id=test_id):
                path = visual_bank.visual_for(test_id).path
                self.assertTrue(path.is_file(), f"Illustration manquante : {path.name}")
                with Image.open(path) as image:
                    self.assertEqual(image.format, "JPEG")
                    self.assertGreaterEqual(image.width, 300)
                    self.assertGreaterEqual(image.height, 200)
                    image.verify()
                self.assertLess(path.stat().st_size, 500_000)


class Page(unittest.TestCase):
    def lab(self, test_id, lang="fr"):
        app = AppTest.from_file(str(ROOT / "pages/2_Performance_Lab.py"), default_timeout=60)
        app.session_state["lang"] = lang
        app.session_state["acpa_store"] = {"lab_test": test_id, "lab_domain": "Tous"}
        return app.run()

    def test_pictogram_shown_with_disclaimer_and_credit(self):
        app = self.lab("handgrip")
        self.assertFalse(app.exception)
        captions = " ".join(c.value for c in app.caption)
        self.assertIn("Pictogramme de famille", captions)
        self.assertIn("OpenMoji", captions)

    def test_missing_illustration_never_blocks(self):
        visual = visual_bank.visual_for("sprint30")
        original = visual_bank.Visual.available
        try:
            visual_bank.Visual.available = property(lambda self: False)
            app = self.lab("sprint30")
            self.assertFalse(app.exception)
            self.assertNotIn("Illustration pédagogique", [e.label for e in app.expander])
            self.assertTrue(any("Protocole" in c.value for c in app.caption))
        finally:
            visual_bank.Visual.available = original
        self.assertEqual(visual.kind, "illustration")

    def test_arabic(self):
        app = self.lab("shirado", "ar")
        self.assertFalse(app.exception)
        self.assertTrue(any("رمز يدل على عائلة الاختبار" in c.value for c in app.caption))


if __name__ == "__main__":
    unittest.main()
