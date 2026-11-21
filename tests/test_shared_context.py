"""Contexte de séance partagé : le contexte de séance saisi une fois est repris par tous les modules."""
import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import session_context as ctx  # noqa: E402
from acpa_msmda.scenario_templates import load_templates  # noqa: E402

STUDIO = "pages/5_Studio_Pedagogique.py"
PLANNER = "pages/3_Espace_Enseignant.py"
SEARCH = "pages/4_Technologies_Reelles.py"


def app_on(page):
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.switch_page(page).run()
    return app


class ContextModuleTests(unittest.TestCase):
    def test_defaults_and_summary(self):
        session = {}
        self.assertEqual(ctx.get(session, "activity"), "Endurance")
        self.assertIn("30 élèves", ctx.summary(session))

    def test_search_query_uses_phrases_the_engine_recognises(self):
        session = {}
        ctx.put(session, "connectivity", "Aucune")
        self.assertIn("sans connexion", ctx.search_query(session))
        ctx.put(session, "connectivity", "Limitée")
        self.assertIn("connexion instable", ctx.search_query(session))
        ctx.put(session, "connectivity", "Disponible")
        self.assertNotIn("connexion", ctx.search_query(session))

    def test_bind_copies_store_into_widget_state(self):
        session = {}
        ctx.put(session, "activity", "Handball")
        binding = ctx.bind(session, "activity")
        self.assertEqual(session[binding["key"]], "Handball")

    def test_template_values_are_valid_context_options(self):
        for template in load_templates():
            self.assertIn(template["activity"], ctx.APS)
            self.assertIn(template["level"], ctx.LEVELS)


class CrossPageTests(unittest.TestCase):
    def test_activity_chosen_in_studio_appears_in_planner(self):
        app = app_on(STUDIO)
        app.selectbox(key="w:activity").set_value("Gymnastique").run()
        app.number_input(key="w:class_size").set_value(28).run()
        app.switch_page(PLANNER).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="w:activity").value, "Gymnastique")
        self.assertEqual(app.number_input(key="w:class_size").value, 28)

    def test_scenario_survives_a_detour(self):
        app = app_on(STUDIO)
        app.text_area(key="w:action_0").set_value("Course de 6 minutes à allure libre").run()
        app.switch_page(PLANNER).run()
        app.switch_page(STUDIO).run()
        self.assertEqual(app.text_area(key="w:action_0").value, "Course de 6 minutes à allure libre")

    def test_template_feeds_every_module(self):
        template = load_templates()[0]
        app = app_on(STUDIO)
        app.selectbox(key="studio_template").set_value(template["title"]).run()
        next(b for b in app.button if b.label == "Charger le modèle").click().run()
        self.assertFalse(app.exception)
        app.switch_page(PLANNER).run()
        self.assertEqual(app.number_input(key="w:duration").value, template["duration"])
        self.assertEqual(app.selectbox(key="w:level").value, template["level"])

    def test_planner_sends_context_to_search(self):
        app = app_on(PLANNER)
        app.selectbox(key="w:connectivity").set_value("Aucune").run()
        next(b for b in app.button if b.label.startswith("Trouver une technologie")).click().run()
        self.assertFalse(app.exception)
        self.assertIn("sans connexion", app.text_area(key="w:search_context").value)
        self.assertGreater(len(app.expander), 1)

    def test_too_many_workshops_stops_the_plan(self):
        app = app_on(PLANNER)
        app.number_input(key="w:class_size").set_value(3).run()
        app.slider(key="w:workshops").set_value(8).run()
        self.assertGreaterEqual(len(app.error), 1)
        self.assertEqual(len(app.dataframe), 0)


if __name__ == "__main__":
    unittest.main()
