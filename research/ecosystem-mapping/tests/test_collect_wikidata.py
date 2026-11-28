import json,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from collect_wikidata import query,parse,candidates,index_catalog,index_sill
class WDTest(unittest.TestCase):
    def test_query(self):
        self.assertIn("wdt:P31 wd:Q694007",query("Q694007",101))
        self.assertIn("LIMIT 101",query("Q694007",101))
        with self.assertRaises(ValueError): query("Q1 .",101)
    def test_parse(self):
        b={"item":{"type":"uri","value":"http://www.wikidata.org/entity/Q2"},"fr":{"type":"literal","xml:lang":"fr","value":"Nom"}}
        raw=json.dumps({"results":{"bindings":[b,b]}})
        self.assertEqual(parse(raw),{"Q2":{"fr":"Nom"}})
    def test_empty(self):
        self.assertEqual(parse('{"results":{"bindings":[]}}'),{})
    def test_bad_uri(self):
        with self.assertRaises(ValueError): parse('{"results":{"bindings":[{"item":{"type":"uri","value":"http://example.org/Q1"}}]}}')
    def test_name_not_identity(self):
        idx=index_catalog([{"id":"a","name":"Open Board","aliases":["OpenBoard"]}])
        self.assertEqual(candidates({"en":"OpenBoard"},idx),["a"])
        self.assertEqual(candidates({"en":"Board"},idx),[])
    def test_sill_baseline(self):
        with self.assertRaises(ValueError): index_sill([])
