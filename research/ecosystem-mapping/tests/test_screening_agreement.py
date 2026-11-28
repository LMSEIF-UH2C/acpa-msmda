import importlib.util
import pathlib
import unittest
P=pathlib.Path(__file__).resolve().parents[1]/"screening_agreement.py"
spec=importlib.util.spec_from_file_location("screening_agreement",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AgreementTests(unittest.TestCase):
    def test_perfect(self):
        self.assertEqual(m.agreement([("a","a"),("b","b")],("a","b"))["cohen_kappa"],1)
    def test_chance(self):
        self.assertEqual(m.agreement([("a","a"),("a","b"),("b","a"),("b","b")],("a","b"))["cohen_kappa"],0)
    def test_degenerate(self):
        self.assertIsNone(m.agreement([("a","a")],("a","b"))["cohen_kappa"])
    def test_uncertain(self):
        def row(d):return {"source":"apple","source_id":"123","decision":d}
        r=m.compare({"R1":row("INCERTAIN")},{"R1":row("DIRECT")})
        self.assertEqual(r["binary_omitted_uncertain"],1)
        self.assertIsNone(r["binary_determinate_only"])
    def test_id_mismatch(self):
        with self.assertRaises(ValueError):m.compare({"R1":{}},{"R2":{}})
if __name__=="__main__":unittest.main()
