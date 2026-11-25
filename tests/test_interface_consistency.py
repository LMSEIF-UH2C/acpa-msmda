"""Cohérence de l'interface : mêmes titres partout, pas d'emoji, pas de compteurs publics."""
import re
import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda.ui import MODULES  # noqa: E402

SOURCES = [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py")), ROOT / "src" / "acpa_msmda" / "ui.py"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⏩-⏺⭐⭕]")
JARGON = ("Performance Lab", "Studio pédagogique", "Espace enseignant", "moteur ACPA", "Prototype",
          "Version pilote", "Présélection contextuelle", "Références répertoriées")


class InterfaceConsistencyTests(unittest.TestCase):
    def test_tab_bar_centred_and_never_animated(self):
        """Régression Streamlit 1.52 : l'animation d'entrée annulait le centrage de la barre d'onglets fixe."""
        from acpa_msmda import ui
        self.assertIn(".st-key-tabbar{position:fixed;left:50%;transform:translateX(-50%)", ui._CSS)
        self.assertIn(".st-key-tabbar{animation:none!important}", ui._CSS)
        self.assertLess(ui._CSS.index("@keyframes rise"), ui._CSS.index(".st-key-tabbar{animation:none!important}"))

    def test_no_emoji_in_interface_code(self):
        for path in SOURCES:
            with self.subTest(file=path.name):
                self.assertIsNone(EMOJI.search(path.read_text(encoding="utf-8")))

    def test_material_icons_only(self):
        for module in MODULES:
            self.assertTrue(module.icon.startswith(":material/"), module.key)

    def test_page_titles_match_navigation(self):
        for module in MODULES:
            if not module.path:
                continue
            with self.subTest(page=module.path):
                app = AppTest.from_file(str(ROOT / module.path), default_timeout=30).run()
                self.assertFalse(app.exception)
                self.assertEqual(app.title[0].value, module.title)

    def test_no_public_counters_or_internal_jargon(self):
        for module in MODULES:
            if not module.path:
                continue
            app = AppTest.from_file(str(ROOT / module.path), default_timeout=30).run()
            self.assertEqual(len(app.metric), 0, module.path)
            visible = " ".join(e.value for e in [*app.title, *app.caption, *app.markdown, *app.info, *app.warning])
            for word in JARGON:
                self.assertNotIn(word, visible, (module.path, word))


if __name__ == "__main__":
    unittest.main()
