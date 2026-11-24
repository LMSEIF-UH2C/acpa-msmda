import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.real_catalog import load_real_tools
from acpa_msmda.scenario_templates import apply_template,load_templates

class HandoffTests(unittest.TestCase):
    def test_exact_catalogue_target(self):
        tool=load_real_tools()[3]
        app=AppTest.from_file(str(ROOT/"pages/9_Evaluation_Technologie.py"),default_timeout=30)
        app.session_state["acpa_store"]={"evaluation_target":tool["id"]}
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="eval_selected").value,tool["id"])
    def test_assignment_and_removal(self):
        tool=next(x for x in load_real_tools() if x.get("source_url") and x.get("requirement")!="internet")
        app=AppTest.from_file(str(ROOT/"pages/5_Studio_Pedagogique.py"),default_timeout=30)
        app.session_state["acpa_store"]={"scenario_tool_candidate":tool["id"]}
        app.run()
        self.assertFalse(app.exception)
        app.selectbox(key="candidate_phase").select(2).run()
        app.button(key="assign_candidate").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["acpa_store"]["scenario_phase_tools"]["2"],tool["id"])
        app.button(key="remove_phase_tool_2").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["acpa_store"]["scenario_phase_tools"],{})
    def test_template_resets_stale_context(self):
        state={"acpa_store":{"activity_specialty":"Triple saut","scenario_phase_tools":{"2":"tool"}}}
        apply_template(load_templates()[0],state)
        self.assertNotIn("activity_specialty",state["acpa_store"])
        self.assertNotIn("scenario_phase_tools",state["acpa_store"])
