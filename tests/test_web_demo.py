"""Accueil et recherche de technologies : parcours réels exécutés avec AppTest."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
SEARCH_PAGE = ROOT / "pages" / "4_Technologies_Reelles.py"


def start(path=APP, lang="fr"):
    app = AppTest.from_file(str(path), default_timeout=30)
    if lang:
        app.session_state["lang"] = lang
    return app.run()


def button(app, label):
    return next(b for b in app.button if b.label == label)


class HomeTests(unittest.TestCase):
    def test_load_without_counters(self):
        app = start()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)

    def test_four_task_links(self):
        app = start()
        self.assertFalse(app.exception)
        self.assertEqual([b.label for b in app.button if b.key and b.key.startswith("guided_")],
                         ["Préparer une séance", "Évaluer une classe", "Trouver un outil",
                          "Préparer une séance sans connexion"])
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from acpa_msmda.ui import MODULES
        links = [e.proto.label for e in app.get("page_link")]
        self.assertIn("Organiser les ateliers", links)
        self.assertEqual([label for label in links if label != "Organiser les ateliers"],
                         [m.short for m in MODULES])

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

    def test_catalogue_shows_every_fiche_and_marks_pending_ones(self):
        app = start(SEARCH_PAGE)
        app.text_input[0].set_value("Testmoz").run()
        self.assertTrue(any(e.label.startswith("Testmoz") for e in app.expander))
        self.assertTrue(any("Fonctions non vérifiées en séance" in c.value for c in app.caption))
        app.toggle[0].set_value(False).run()  # l'enseignant peut se limiter aux fiches vérifiées
        self.assertFalse(any(e.label.startswith("Testmoz") for e in app.expander))
        self.assertTrue(any("Activez l'interrupteur" in i.value for i in app.info))

    def test_recommendations_cover_the_whole_catalogue(self):
        app = start(SEARCH_PAGE)
        app.text_area[0].input("basket tactique et score").run()
        next(b for b in app.button if b.label == "Voir les suggestions").click().run()
        self.assertFalse(app.exception)
        labels = [e.label for e in app.expander]
        self.assertTrue(any("· À vérifier" in label for label in labels))
        self.assertTrue(any("applications correspondent" in m.value for m in app.markdown))
        more = next(b for b in app.button if b.label.startswith("Afficher"))
        before = sum("/100" in label for label in labels)
        more.click().run()
        after = sum("/100" in e.label for e in app.expander)
        self.assertEqual(after, before + 10)

    def test_max_length(self):
        self.assertEqual(start(SEARCH_PAGE).text_area[0].proto.max_chars, 1000)


if __name__ == "__main__":
    unittest.main()
