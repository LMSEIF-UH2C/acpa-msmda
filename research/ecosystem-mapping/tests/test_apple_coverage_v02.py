import importlib.util
import pathlib
import unittest
P=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("coverage_v02",P/"collect_apple_coverage_v02.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CoverageTests(unittest.TestCase):
    def test_plan(self):
        q=m.plan(m.read(P/"query_matrix.json"),m.read(P/"query_matrix_v02_proposed.json"))
        self.assertEqual(len(q),240)
        self.assertEqual(len({m.digest(x) for x in q}),240)
        self.assertEqual({x["country"] for x in q},{"ma","fr","us","gb"})
        self.assertTrue(all(x["limit"]==50 for x in q))
if __name__=="__main__":unittest.main()
