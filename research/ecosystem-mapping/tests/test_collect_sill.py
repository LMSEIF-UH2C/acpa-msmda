import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from collect_sill import compare,norm,catalog_rows
class SillTest(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(norm("  Open—Board "), "open board")
    def test_exact_alias_and_localized_name(self):
        r=compare([{"id":1,"name":{"fr":"Outil","en":"Tool"},"license":"MIT"}],[{"id":"a","name":"Other","aliases":["Tool"]}])
        self.assertEqual(r[0]["exact_catalog_ids"],["a"])
    def test_partial_not_identity(self):
        r=compare([{"id":1,"name":"Tracker","license":"MIT"}],[{"id":"a","name":"GPS Tracker"}])
        self.assertEqual(r[0]["comparison_status"],"AMBIGUOUS_NAME_REVIEW")
    def test_dereferenced_and_absent(self):
        r=compare([{"id":1,"name":"Zeta","license":"MIT","dereferencing":{"time":"x"}}],[{"id":"a","name":"Other"}])
        self.assertFalse(r[0]["active"])
        self.assertEqual(r[0]["comparison_status"],"NO_NAME_MATCH")
    def test_duplicate_rejected(self):
        r={"id":1,"name":"X","license":"MIT"}
        with self.assertRaises(ValueError): compare([r,r],[])
    def test_invalid_schema_rejected(self):
        with self.assertRaises(ValueError): compare({"softwares":[]},[])
        with self.assertRaises(ValueError): catalog_rows([])
