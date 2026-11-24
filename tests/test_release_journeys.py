import sys
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.timetable import generate

class ReleaseJourneys(unittest.TestCase):
    def test_populated_journal(self):
        cycles=[{"number":1,"start":"2026-11-02","end":"2026-11-22","activities":["Triple saut"]}]
        slots=[{"group":"TC1","level":"Lycée","weekday":0,"start_minute":840,"duration":60}]
        entries=generate(cycles,slots,[],[])
        app=AppTest.from_file(str(ROOT/"pages/8_Cahier_Journalier.py"),default_timeout=30)
        app.session_state["acpa_store"]={"journal_cycles":cycles,"journal_entries":entries,"journal_slots":slots}
        app.run()
        self.assertFalse(app.exception,str(app.exception))
        self.assertTrue(any("TC1" in str(w.value) for w in app.warning))
        self.assertEqual(len(app.session_state["acpa_store"]["journal_entries"]),3)
    def test_studio_specialty_three_languages(self):
        for lang in ("fr","ar","en"):
            with self.subTest(lang=lang):
                app=AppTest.from_file(str(ROOT/"pages/5_Studio_Pedagogique.py"),default_timeout=30)
                app.query_params["lang"]=lang
                app.session_state["acpa_store"]={"activity":"Athlétisme","activity_specialty":"Triple saut","level":"Lycée"}
                app.run()
                self.assertFalse(app.exception,str(app.exception))
                self.assertEqual(app.session_state["acpa_store"]["activity_specialty"],"Triple saut")
