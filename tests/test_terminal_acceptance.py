import csv
import io
import sys
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import session_context as ctx, i18n
from acpa_msmda.pdf import scenario_pdf
from acpa_msmda.scenario_engine import export_scenario_csv, validate_scenario

class TerminalAcceptanceTests(unittest.TestCase):
    def test_context_confirmation(self):
        app = AppTest.from_file(str(ROOT / "pages/5_Studio_Pedagogique.py"), default_timeout=60)
        app.session_state["acpa_store"] = {"activity":"Endurance","level":"Collège","class_size":30,
            "connectivity":"Disponible","objectives":"Mon objectif","scenario_context_pending":
            "Basketball, lycée, 40 élèves, sans connexion"}
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["acpa_store"]["activity"], "Endurance")
        app.button(key="accept_search_context").click().run()
        self.assertFalse(app.exception)
        state = app.session_state["acpa_store"]
        self.assertEqual((state["activity"],state["level"],state["class_size"],state["connectivity"]),
                         ("Basketball","Lycée",40,"Aucune"))
        self.assertEqual(state["objectives"], "Mon objectif")
        self.assertIsNone(state["scenario_context_pending"])

    def test_ambiguous_context(self):
        self.assertNotIn("activity", ctx.context_proposal("Basketball ou football"))
        self.assertNotIn("class_size", ctx.context_proposal("Basketball 40"))
        self.assertEqual(ctx.context_proposal("basketball, connexion instable")["connectivity"], "Limitée")
        self.assertEqual(ctx.context_proposal("Triple saut, lycée, 35 élèves")["activity_specialty"], "Triple saut")

    def test_real_exports_three_languages(self):
        for lang in ("fr","ar","en"):
            with self.subTest(lang=lang):
                i18n.use(lang)
                metadata = {i18n.t("APS"):i18n.t("Basketball"),i18n.t("Effectif"):40}
                rows = [{"Phase":"Apprentissage","Durée (min)":60,
                         "Activité / consignes":i18n.t("Basketball"),
                         "Supports":"TestTool-ACPA", "Évaluation / feedback":"=1+1"}]
                result = list(csv.reader(io.StringIO(export_scenario_csv(metadata,rows).decode("utf-8-sig"))))
                self.assertIn("TestTool-ACPA",result[-1])
                self.assertIn("'=1+1",result[-1])
                pdf = scenario_pdf(metadata,rows,validate_scenario(rows,60),[])
                self.assertTrue(pdf.startswith(b"%PDF-"))
                self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
                self.assertGreater(len(pdf),1000)
        i18n.use("fr")
