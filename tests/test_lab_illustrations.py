"""Banque visuelle du Laboratoire : couverture des 32 épreuves, licences, sécurité des SVG, provenance des
illustrations, textes alternatifs FR/AR/EN et affichage facultatif."""
import hashlib
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

    def test_illustrations_licensed_cc_by_within_rights_held(self):
        for entry in MANIFEST["lab_specific"]:
            with self.subTest(test_id=entry["id"]):
                self.assertEqual(entry["license"], "CC-BY-4.0")
                self.assertIn("droits détenus", entry["license_scope"])
        self.assertTrue((ROOT / "assets/visual-bank/LICENCE-ILLUSTRATIONS.md").is_file())
        self.assertTrue(any("CC BY 4.0" in line for line in visual_bank.credits()))
        notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
        for licence in ("MIT", "CC BY 4.0", "CC BY-SA 4.0"):
            self.assertIn(licence, notice)

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


class Provenance(unittest.TestCase):
    """Fichiers conformes au registre ; empreinte d'origine conservée ; retouches limitées aux images documentées."""
    EVIDENCE = ROOT / "docs/validation/banque-visuelle-2026-11-25"

    def delivered(self):
        return {e["id"]: e for e in json.loads((self.EVIDENCE / "remise/manifest.json").read_text(encoding="utf-8"))}

    def test_files_match_record_and_delivery(self):
        delivered = self.delivered()
        for entry in MANIFEST["lab_specific"]:
            with self.subTest(test_id=entry["id"]):
                path = ROOT / entry["path"]
                data = path.read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
                self.assertEqual(len(data), entry["bytes"])
                with Image.open(path) as image:
                    self.assertEqual(image.size, (entry["width"], entry["height"]))
                origin = delivered[entry["id"]]
                self.assertEqual((entry["width"], entry["height"]), (origin["width"], origin["height"]))
                self.assertEqual((entry["source_sha256"], entry["source_bytes"]), (origin["sha256"], origin["bytes"]))
                self.assertEqual(entry["status"], "accepted_by_user_imported")
                self.assertIn("non normative", entry["scientific_status"])
                if entry["retouch"] == "aucune":
                    self.assertEqual(entry["sha256"], entry["source_sha256"])
                else:
                    self.assertNotEqual(entry["sha256"], entry["source_sha256"])
                    self.assertTrue((ROOT / entry["retouch_evidence"]).is_file())

    def test_delivery_evidence_kept(self):
        delivery = MANIFEST["lab_delivery"]
        self.assertRegex(delivery["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(delivery["files"], 14)
        evidence = ROOT / delivery["evidence"]
        self.assertTrue((evidence / "README.md").is_file())
        received = {k: v["sha256"] for k, v in self.delivered().items()}
        self.assertEqual(received, {e["id"]: e["source_sha256"] for e in MANIFEST["lab_specific"]})
        self.assertNotIn("handgrip", received)

    def test_retouch_limited_to_documented_images(self):
        stats = json.loads((self.EVIDENCE / "retouche/stats.json").read_text(encoding="utf-8"))
        zones = json.loads((self.EVIDENCE / "retouche/zones_logos.json").read_text(encoding="utf-8"))
        retouched = {e["id"] for e in MANIFEST["lab_specific"] if e["retouch"] != "aucune"}
        self.assertEqual(retouched, {"ruffier", "sargent", "medecine_ball", "saut_horizontal", "front_plank", "killy"})
        self.assertEqual(set(stats), retouched)
        self.assertEqual(set(zones), retouched)
        for entry in MANIFEST["lab_specific"]:
            if entry["id"] in stats:
                with self.subTest(test_id=entry["id"]):
                    record = stats[entry["id"]]
                    self.assertEqual((record["sha256"], record["source_sha256"]), (entry["sha256"], entry["source_sha256"]))
                    self.assertLess(record["outside_mask_mean_abs_diff"], 1.0)   # hors masque : bruit de réencodage

    def test_no_stray_file_in_lab_folder(self):
        self.assertEqual({p.name for p in (ROOT / "assets/lab").iterdir()}, {i + ".jpg" for i in SPECIFIC})


class TextAlternatives(unittest.TestCase):
    TRANSLATIONS = json.loads((ROOT / "data/translations.json").read_text(encoding="utf-8"))

    def test_every_illustration_has_a_translated_text_alternative(self):
        for entry in MANIFEST["lab_specific"]:
            with self.subTest(test_id=entry["id"]):
                fr = entry["alt"]
                self.assertIn("Matériel représenté : ", fr)
                ar, en = self.TRANSLATIONS[fr]["ar"], self.TRANSLATIONS[fr]["en"]
                self.assertIn("العتاد الظاهر في الرسم: ", ar)
                self.assertIn("Equipment shown: ", en)
                self.assertRegex(ar, r"[\u0600-\u06FF]")
                for text in (fr, ar, en):
                    self.assertNotIn("\u2014", text)       # pas de tiret cadratin

    def test_sprint_caption_states_timing_nuance(self):
        fr = next(e["alt"] for e in MANIFEST["lab_specific"] if e["id"] == "sprint30")
        self.assertIn("Nuance de chronométrage", fr)
        self.assertIn("premier mouvement", fr)
        self.assertIn("ligne d'arrivée", fr)
        self.assertIn("خط الوصول", self.TRANSLATIONS[fr]["ar"])
        self.assertIn("finish line", self.TRANSLATIONS[fr]["en"])

    def test_ruffier_labels_reproduced_in_three_languages(self):
        fr = next(e["alt"] for e in MANIFEST["lab_specific"] if e["id"] == "ruffier")
        for text in (fr, self.TRANSLATIONS[fr]["ar"], self.TRANSLATIONS[fr]["en"]):
            for label in ("P1", "P2", "P3", "30", "45"):
                self.assertIn(label, text)


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

    def test_illustration_with_text_alternative_and_disclaimer(self):
        app = self.lab("sargent")
        self.assertFalse(app.exception)
        self.assertIn("Illustration pédagogique", [e.label for e in app.expander])
        captions = [c.value for c in app.caption]
        self.assertTrue(any(c.startswith("Le long d'une toise murale") for c in captions))
        self.assertTrue(any("non normative" in c for c in captions))
        self.assertTrue(any("CC BY 4.0" in c for c in captions))         # crédit et licence des illustrations

    def test_ruffier_legend_in_arabic_and_english(self):
        for lang, label in (("ar", "نبض القلب في الراحة"), ("en", "P1, resting heart rate")):
            with self.subTest(lang=lang):
                app = self.lab("ruffier", lang)
                self.assertFalse(app.exception)
                self.assertTrue(any(label in c.value for c in app.caption))


if __name__ == "__main__":
    unittest.main()
