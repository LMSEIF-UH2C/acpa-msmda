"""Langue conservée quand un fragment Streamlit se relance seul (minuteur du mode terrain)."""
import contextvars
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from acpa_msmda import i18n  # noqa: E402


class FragmentLanguage(unittest.TestCase):
    def test_unset_context_reads_session_language(self):
        def fragment_run():
            with mock.patch.object(i18n, "_session_language", return_value="ar"):
                return i18n.current(), i18n.t("Temps restant")
        self.assertEqual(contextvars.Context().run(fragment_run), ("ar", "الوقت المتبقي"))

    def test_outside_streamlit_defaults_to_french(self):
        self.assertEqual(contextvars.Context().run(i18n.current), "fr")

    def test_explicit_choice_wins(self):
        def run():
            i18n.use("en")
            with mock.patch.object(i18n, "_session_language", return_value="ar"):
                return i18n.current()
        self.assertEqual(contextvars.Context().run(run), "en")

    def test_timer_page_uses_fragments(self):
        source = (Path(__file__).resolve().parents[1] / "pages" / "6_Mode_Terrain.py").read_text(encoding="utf-8")
        self.assertIn("st.fragment(run_every=1)", source)


if __name__ == "__main__":
    unittest.main()
