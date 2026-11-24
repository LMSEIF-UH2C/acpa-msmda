import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.curriculum import profiles, validate_projects, export_projects, import_projects

class CurriculumTests(unittest.TestCase):
    def setUp(self):
        self.cycles=[{"number":1,"start":"2026-09-07","end":"2026-10-17","activities":["Triple saut"]}]
        self.project={"group":"TC1","cycle":1,"level":"Lycée","profile":"MA","grade":"TC","module":"","institutional":"","reference":"","diagnostic":"Observation initiale","target":"Coordination des bonds","progression":"","assessment":""}
    def test_levels(self):
        self.assertEqual([g["id"] for g in profiles()[0]["levels"]],["1AC","2AC","3AC","TC","1BAC","2BAC"])
    def test_roundtrip(self):
        self.assertEqual(import_projects(export_projects([self.project],self.cycles),self.cycles),[self.project])
    def test_invalid(self):
        for p in (dict(self.project,grade="1AC"),dict(self.project,cycle=2),dict(self.project,institutional="Texte sans source")):
            with self.assertRaises(ValueError):
                validate_projects([p],self.cycles)
        with self.assertRaises(ValueError):
            validate_projects([self.project,self.project],self.cycles)
