"""Exports PDF du scénario et de l'organisation en ateliers, dans les trois langues."""
import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from acpa_msmda import i18n  # noqa: E402
from acpa_msmda.pdf import organisation_pdf, scenario_pdf  # noqa: E402

ROWS = [{"Phase": "Échauffement", "Durée (min)": 10, "Activité / consignes": "Footing et gammes",
         "Supports": "Plots", "Évaluation / feedback": "Allure régulière"},
        {"Phase": "Retour au calme", "Durée (min)": 5, "Activité / consignes": "Étirements",
         "Supports": "", "Évaluation / feedback": ""}]


class Exports(unittest.TestCase):
    def tearDown(self):
        i18n.use("fr")

    def test_scenario_three_languages(self):
        for lang in ("fr", "en", "ar"):
            i18n.use(lang)
            pdf = scenario_pdf({i18n.t("APS"): i18n.t("Endurance"), i18n.t("Effectif"): 30}, ROWS,
                               {"balanced": False, "used_minutes": 15, "available_minutes": 60,
                                "difference_minutes": -45}, [i18n.t("Précisez les objectifs de la séance.")])
            self.assertTrue(pdf.startswith(b"%PDF"), lang)
            self.assertIn(b"DejaVu", pdf)

    def test_organisation(self):
        for lang in ("fr", "ar"):
            i18n.use(lang)
            pdf = organisation_pdf({i18n.t("Effectif"): 30}, [("Accueil et consignes", 5), ("Ateliers et rotations", 45)],
                                   [8, 8, 7, 7], 11.2, [])
            self.assertTrue(pdf.startswith(b"%PDF"), lang)


class Pages(unittest.TestCase):
    def test_pdf_buttons(self):
        for page, label in (("5_Studio_Pedagogique.py", "Scénario (PDF)"), ("3_Espace_Enseignant.py", "Organisation (PDF)")):
            app = AppTest.from_file(str(ROOT / "pages" / page), default_timeout=60)
            app.session_state["lang"] = "fr"
            app.run()
            self.assertFalse(app.exception, page)
            labels = [b.proto.label for b in app.get("download_button")]
            self.assertIn(label, labels, page)
            self.assertIn("Tableur (CSV)", labels, page)


if __name__ == "__main__":
    unittest.main()
