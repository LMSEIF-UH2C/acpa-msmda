import importlib.util
import pathlib
import unittest
P=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("planner",P/"plan_collection_v03.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PlannerTests(unittest.TestCase):
    def test_union(self):
        q,r=m.build(m.historical(m.ROOT/"tools/catalog/collect_appstore.py"),m.read(P/"query_matrix_v02_proposed.json"))
        self.assertEqual((r["historical_distinct_expressions"],r["modern_distinct_expressions"],r["common_expressions"],r["union_expressions"]),(118,300,20,398))
        self.assertEqual(len(q),1592)
        self.assertEqual(len({x["request_id"] for x in q}),1592)
        self.assertTrue(any(x["term"]=="beep test" for x in q))
    def test_labels_do_not_change_request(self):
        q={"term":"test","country":"ma","limit":200}
        self.assertEqual(m.identity(q),m.identity({**q,"labels":["other"]}))
        self.assertNotEqual(m.identity(q),m.identity({**q,"limit":50}))
        self.assertNotEqual(m.identity(q),m.identity({**q,"country":"fr"}))
    def test_cache_classification(self):
        q={"term":"test","country":"ma","limit":200}
        self.assertEqual(m.summarize([q],{m.identity({**q,"limit":50}):[{}]})["lower_50_snapshot_only"],1)
        self.assertEqual(m.summarize([q],{m.identity(q):[{}]})["exact_200_snapshot"],1)
if __name__=="__main__":unittest.main()
