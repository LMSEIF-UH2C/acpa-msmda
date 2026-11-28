import importlib.util
import pathlib
import unittest
P=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("yield_audit",P/"audit_query_yield.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(order,ids,status="ok"):
    return dict(phase="baseline",order=order,family="motor",language="en",term=str(order),country="ma",limit=50,status=status,ids=set(ids),observations=len(ids),missing_id=0)
class YieldTests(unittest.TestCase):
    def test_marginal_exclusive(self):
        r=m.metrics([row(1,"abc"),row(2,"bcd"),row(3,"", "error")])
        self.assertEqual([x["new_vs_preceding_queries"] for x in r],[3,1,0])
        self.assertEqual([x["exclusive_ids_all_observed_queries"] for x in r],[1,1,0])
        self.assertEqual(r[-1]["cumulative_ids"],4)
    def test_jaccard(self):
        p=m.overlaps([row(1,"abc"),row(2,"bcd")])
        self.assertEqual(p[0]["jaccard"],.5)
    def test_empty(self):
        self.assertEqual(m.overlaps([row(1,""),row(2,"")]),[])
    def test_group_counts_failed(self):
        g=m.groups([row(1,"abc"),row(2,"","error")],("family",))[0]
        self.assertEqual((g["planned"],g["successful"],g["unique_ids"]),(2,1,3))
if __name__=="__main__":unittest.main()
