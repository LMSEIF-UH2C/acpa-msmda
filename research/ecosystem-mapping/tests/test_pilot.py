import importlib.util
import json
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("collector",ROOT/"collect_apple.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class MatrixTests(unittest.TestCase):
    def test_counts_and_unique_keys(self):
        matrix = json.loads((ROOT/"query_matrix.json").read_text(encoding="utf-8"))
        for mode,count in (("pilot",48),("full",960)):
            plan = list(module.plan(matrix,mode))
            self.assertEqual(len(plan),count)
            self.assertEqual(len({module.key(q) for q in plan}),count)
    def test_framework(self):
        params = json.loads((ROOT/"framework_10d97p.json").read_text(encoding="utf-8"))["parameters"]
        self.assertEqual(len(params),97)
        self.assertEqual(len({p["code"] for p in params}),97)
if __name__ == "__main__":
    unittest.main()
