"""Accueil et recherche de technologies : parcours réels exécutés avec AppTest."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
SEARCH_PAGE = ROOT / "pages" / "4_Technologies_Reelles.py"


def start(path=APP):
    return AppTest.from_file(str(path), default_timeout=30).run()


def button(app, label):
    return next(b for b in app.button if b.label == label)


class HomeTests(unittest.TestCase):
    def test_load_without_counters(self):
        app = start()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)

    def test_four_task_buttons(self):
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from acpa_msmda.ui import TASKS
        labels = [b.label for b in start().button]
        for module in TASKS:
            self.assertIn(module.title, labels)

    def test_navigation_targets_exist(self):
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from acpa_msmda.ui import MODULES
        for module in MODULES:
            if module.path:
                self.assertTrue((ROOT / module.path).is_file(), module.path)


class SearchPageTests(unittest.TestCase):
    def test_empty_search_warns(self):
        app = start(SEARCH_PAGE)
        button(app, "Voir les suggestions").click().run()
        self.assertFalse(app.exception)
        self.assertGreaterEqual(len(app.warning), 1)

    def test_context_search_shows_documented_tools(self):
        app = start(SEARCH_PAGE)
        app.text_area[0].set_value("endurance course").run()
        button(app, "Voir les suggestions").click().run()
        self.assertFalse(app.exception)
        titles = [e.label for e in app.expander]
        self.assertTrue(any(t.startswith("Strava") for t in titles))

    def test_results_survive_rerun(self):
        app = start(SEARCH_PAGE)
        app.text_area[0].set_value("endurance course").run()
        button(app, "Voir les suggestions").click().run()
        app.text_input[0].set_value("Kinovea").run()
        self.assertTrue(any(e.label.startswith("Strava") for e in app.expander))

    def test_catalogue_hides_pending_fiches_by_default(self):
        app = start(SEARCH_PAGE)
        app.text_input[0].set_value("Testmoz").run()
        self.assertFalse(any(e.label.startswith("Testmoz") for e in app.expander))
        app.toggle[0].set_value(True).run()
        self.assertTrue(any(e.label.startswith("Testmoz") for e in app.expander))

    def test_hidden_fiches_are_explained(self):
        app = start(SEARCH_PAGE)
        self.assertTrue(any("en cours de documentation" in c.value for c in app.caption))
        app.text_input[0].set_value("Testmoz").run()
        self.assertTrue(any("Activez l'interrupteur" in i.value for i in app.info))

    def test_max_length(self):
        self.assertEqual(start(SEARCH_PAGE).text_area[0].proto.max_chars, 1000)


if __name__ == "__main__":
    unittest.main()
