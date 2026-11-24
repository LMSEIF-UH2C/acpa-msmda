import sys
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.ui import arabic_font_css

class ClosureTests(unittest.TestCase):
    def test_local_plex(self):
        for name in ("IBMPlexSansArabic-Regular.ttf","IBMPlexSansArabic-Medium.ttf","IBMPlexSansArabic-SemiBold.ttf","IBMPlexSansArabic-Bold.ttf"):
            self.assertEqual((ROOT/"assets/fonts"/name).read_bytes()[:4],b"\x00\x01\x00\x00")
        self.assertTrue((ROOT/"assets/fonts/IBM-Plex-OFL.txt").is_file())
        self.assertEqual(arabic_font_css().count("data:font/ttf;base64,"),4)
    def test_manual_assessment(self):
        app=AppTest.from_file(str(ROOT/"pages/9_Evaluation_Technologie.py"),default_timeout=30).run()
        self.assertFalse(app.exception)
        submit=next(b for b in app.button if b.label=="Enregistrer mon évaluation")
        submit.click().run()
        self.assertTrue(app.error)
        app.text_input(key="assessment_name").set_value("Outil fictif")
        next(a for a in app.text_area if a.label=="Sources et observations").set_value("Observation fictive")
        app.selectbox(key="ind_C1").select(8)
        app.selectbox(key="ind_C2").select("SO")
        next(b for b in app.button if b.label=="Enregistrer mon évaluation").click().run()
        self.assertFalse(app.exception)
        saved=app.session_state["acpa_store"]["independent_assessment"]
        self.assertEqual(saved["scores"]["C1"],8)
        self.assertEqual(saved["scores"]["C2"],"SO")
        self.assertEqual(saved["scores"]["C3"],"NR")

    def test_context_first(self):
        app=AppTest.from_file(str(ROOT/"pages/9_Evaluation_Technologie.py"),default_timeout=30).run()
        self.assertFalse(app.exception)
        app.text_area(key="w:evaluation_context").set_value("Endurance, 35 élèves, sans connexion, budget limité").run()
        app.button(key="analyze_context").click().run()
        self.assertFalse(app.exception)
        self.assertIn("sans connexion",app.session_state["acpa_store"]["analyzed_context"])
        self.assertTrue(any(b.key=="context_to_explore" for b in app.button))
        app.text_area(key="w:evaluation_context").set_value("Basketball").run()
        self.assertFalse(any(b.key=="context_to_explore" for b in app.button))
