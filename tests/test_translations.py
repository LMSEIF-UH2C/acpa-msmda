"""Langues de l'interface : table de traduction complète, choix de la langue, arabe de droite à gauche,
et demandes équivalentes en français, arabe et anglais traitées de la même façon."""
import re
import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from acpa_msmda import i18n  # noqa: E402
from acpa_msmda.context_engine import detect_language, normalize_text  # noqa: E402
from acpa_msmda.keywords import keywords_in, mentions_offline  # noqa: E402

APP = ROOT / "app.py"
PLACEHOLDER = re.compile(r"\{(\w*)\}")


class TableTests(unittest.TestCase):
    def test_translation_cache_refreshes_when_file_changes(self):
        import tempfile
        import json
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "translations.json"
            with patch.object(i18n, "PATH", path):
                path.write_text(json.dumps({"test": {"ar": "first"}}), encoding="utf-8")
                self.assertEqual(i18n.table()["test"]["ar"], "first")
                path.write_text(json.dumps({"test": {"ar": "updated translation"}}), encoding="utf-8")
                self.assertEqual(i18n.table()["test"]["ar"], "updated translation")


    def test_every_interface_text_has_arabic_and_english(self):
        import i18n_strings

        self.assertFalse(i18n_strings.missing())

    def test_placeholders_kept(self):
        for source, versions in i18n.table().items():
            for lang in ("ar", "en"):
                self.assertEqual(sorted(PLACEHOLDER.findall(versions[lang])), sorted(PLACEHOLDER.findall(source)),
                                 f"{lang}: {source}")

    def test_no_dash_separator(self):
        for source, versions in i18n.table().items():
            for text in versions.values():
                self.assertNotIn("—", text, source)

    def test_t_follows_language(self):
        for lang, expected in (("fr", "Supprimer"), ("ar", "حذف"), ("en", "Delete")):
            i18n.use(lang)
            self.assertEqual(i18n.t("Supprimer"), expected)
        i18n.use("ar")
        self.assertEqual(i18n.t("{n} élèves", n=30), "30 تلميذًا")
        self.assertTrue(i18n.is_rtl())
        i18n.use("fr")
        self.assertFalse(i18n.is_rtl())


class QueryTests(unittest.TestCase):
    SAME = (
        ("course d'endurance avec chronomètre pour une classe de 35 élèves sans connexion",
         "جري المداومة بالميقاتية لقسم من 35 تلميذا بدون انترنت",
         "endurance running with a stopwatch for a class of 35 pupils offline"),
        ("basketball : former des équipes et compter les points",
         "كرة السلة: تكوين الفرق وتسجيل النقاط",
         "basketball: make teams and keep score"),
        ("échauffement et étirements en gymnastique",
         "الإحماء والتمدد في الجمباز",
         "warm-up and stretching in gymnastics"),
    )

    def test_language_detected(self):
        for fr, ar, en in self.SAME:
            self.assertEqual((detect_language(fr), detect_language(ar), detect_language(en)), ("fr", "ar", "en"))

    def test_arabic_normalisation(self):
        self.assertEqual(normalize_text("الجري"), normalize_text("جري"))
        self.assertEqual(normalize_text("كرة"), normalize_text("كره"))
        self.assertEqual(normalize_text("وتسجيل"), normalize_text("تسجيل"))
        self.assertEqual(normalize_text("وثب").strip(), "وثب")

    def test_same_needs_in_three_languages(self):
        for fr, ar, en in self.SAME:
            self.assertEqual(keywords_in(fr), keywords_in(ar), ar)
            self.assertEqual(keywords_in(fr), keywords_in(en), en)
            self.assertEqual(mentions_offline(fr), mentions_offline(ar))

    def test_same_suggestions_in_three_languages(self):
        from acpa_msmda.real_catalog import recommend

        for fr, ar, en in self.SAME:
            top_fr, top_ar, top_en = ([m for m in recommend(q)["matches"][:5]] for q in (fr, ar, en))
            self.assertTrue(top_fr, fr)
            self.assertEqual([m["name"] for m in top_fr], [m["name"] for m in top_en], en)
            # En arabe, une application à interface arabe peut remonter : c'est la seule différence admise.
            arabic_ui = {m["name"] for m in top_ar if (m.get("store") or {}).get("has_ar")}
            self.assertEqual({m["name"] for m in top_fr} - {m["name"] for m in top_ar} == set() or bool(arabic_ui), True, ar)
            self.assertLessEqual({m["name"] for m in top_ar} - {m["name"] for m in top_fr}, arabic_ui, ar)


class PickerTests(unittest.TestCase):
    def test_first_screen_asks_for_language(self):
        app = AppTest.from_file(str(APP), default_timeout=30).run()
        self.assertFalse(app.exception)
        labels = [b.label for b in app.button]
        for name in i18n.LANGUAGES.values():
            self.assertIn(name, labels)
        self.assertEqual(len(app.get("page_link")), 0)
        styles = [m.value for m in app.markdown]
        self.assertTrue(any("font-family:IBM Plex Sans Arabic;" in s and "unicode-range:U+0600-06FF" in s for s in styles))
        self.assertFalse(any("direction:rtl" in s for s in styles))

    def test_choosing_arabic_switches_interface(self):
        app = AppTest.from_file(str(APP), default_timeout=30).run()
        next(b for b in app.button if b.label == "العربية").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["lang"], "ar")
        self.assertIn("ماذا تريد أن تفعل؟", [s.value for s in app.subheader])
        self.assertTrue(any('direction:rtl' in m.value for m in app.markdown))

    def test_home_descriptions_in_three_languages(self):
        from acpa_msmda.ui import TECH_EVAL, SEARCH, STUDIO, EPS_SPACE
        for lang in ("fr", "ar", "en"):
            with self.subTest(lang=lang):
                app = AppTest.from_file(str(APP), default_timeout=30)
                app.session_state["lang"] = lang
                app.run()
                self.assertFalse(app.exception)
                captions = [c.value for c in app.caption]
                for module in (TECH_EVAL, SEARCH, STUDIO, EPS_SPACE):
                    expected = module.summary if lang == "fr" else i18n.table()[module.summary][lang]
                    self.assertIn(expected, captions)
                    if lang != "fr":
                        self.assertNotIn(module.summary, captions)

    def test_switching_back_to_french(self):
        app = AppTest.from_file(str(APP), default_timeout=30)
        app.session_state["lang"] = "en"
        app.run()
        self.assertIn("What would you like to do?", [s.value for s in app.subheader])
        next(b for b in app.button if b.label == "Français").click().run()
        self.assertIn("Que voulez-vous faire ?", [s.value for s in app.subheader])

    def test_untouched_defaults_follow_language(self):
        from acpa_msmda.session_context import CONTEXT_DEFAULTS, TEXT_DEFAULTS, refresh_text_defaults, store

        session = {}
        data = store(session)
        data["equipment"] = CONTEXT_DEFAULTS["equipment"]
        data["objectives"] = "Mon objectif à moi"
        i18n.use("ar")
        refresh_text_defaults(session)
        self.assertEqual(data["equipment"], i18n.t(CONTEXT_DEFAULTS["equipment"]))
        self.assertNotEqual(data["equipment"], CONTEXT_DEFAULTS["equipment"])
        self.assertEqual(data["objectives"], "Mon objectif à moi")
        i18n.use("fr")
        refresh_text_defaults(session)
        self.assertEqual(data["equipment"], CONTEXT_DEFAULTS["equipment"])
        self.assertIn("equipment", TEXT_DEFAULTS)


if __name__ == "__main__":
    unittest.main()
