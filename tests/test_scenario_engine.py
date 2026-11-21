import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.scenario_engine import recommend_phase_tools,validate_scenario,export_scenario_csv
class ScenarioTests(unittest.TestCase):
    def test_phase_recommendations_have_sources(self):
        for phase in ("Diagnostic","Mise en activité","Apprentissage","Régulation","Évaluation"):
            self.assertTrue(all(t["source_url"] for t in recommend_phase_tools(phase)))
    def test_offline_excludes_known_online_requirements(self):
        sample=[{"id":"online","name":"Online","category":"Ressources et apprentissage","uses":["ressources"],"source_url":"https://example.org","requirement":"internet","evidence_status":"OFFICIAL_SOURCE_FEATURES_ONLY"}]
        self.assertEqual(recommend_phase_tools("Apprentissage","Aucune",sample),[])
    def test_validation(self):
        self.assertTrue(validate_scenario([{"Durée (min)":10}],10)["balanced"])
        self.assertEqual(validate_scenario([{"Durée (min)":12}],10)["difference_minutes"],2)
    def test_csv(self):
        result=export_scenario_csv({"APS":"Endurance"},[{"Phase":"Diagnostic","Durée (min)":5}])
        self.assertIn("Endurance",result.decode("utf-8-sig"))
if __name__=="__main__":unittest.main()
