import pathlib,sys,unittest
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P))
from saturation_sensitivity import curve,quantile
def row(i,ids,status="ok"):
    return {"order":i,"term":str(i),"country":"ma","language":"fr","ids":set(ids),"status":status,"limit":50,"observations":len(ids)}
class Tests(unittest.TestCase):
    def test_disjoint(self):
        r=curve([row(1,"ab"),row(2,"cd")],20)
        self.assertEqual(r["curve"][0]["observed_coverage"]["median"],.5)
        self.assertEqual(r["curve"][-1]["observed_coverage"]["median"],1)
        self.assertEqual([x["unique_loss"] for x in r["leave_one_out"]],[2,2])
    def test_overlap(self):
        r=curve([row(1,"ab"),row(2,"bc")],20)
        self.assertEqual([x["unique_loss"] for x in r["leave_one_out"]],[1,1])
    def test_failed(self):
        r=curve([row(1,"ab"),row(2,"","error")],20)
        self.assertEqual((r["planned_queries"],r["successful_queries"]),(2,1))
    def test_empty(self):
        self.assertEqual(curve([row(1,"")])["curve"],[])
    def test_quantile(self):
        self.assertEqual(quantile([0,10],.5),5)
if __name__=="__main__":unittest.main()
