import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from saturation_comparison import simulate,guards
def row(i,vs,lang="en",family="motor",status="ok",cap=False):
    return {"family":family,"language":lang,"country":"ma","limit":50,"term":"q"+str(i),"status":status,"ids":set(vs),"observations":50 if cap else len(vs),"missing_id":0}
class ReplayTests(unittest.TestCase):
    def test_zero_loss_suspension(self):
        b=[row(i,{"a"}) for i in range(6)]
        r=[row(i,{"a"}) for i in range(6,18)]
        x=simulate(b,r,0,2);self.assertGreater(x["deferred_queries"],0);self.assertEqual(x["lost_observed_ids"],0)
    def test_protect_arabic(self):
        b=[row(i,{"a"},lang="ar") for i in range(6)]
        r=[row(i,{"a"},lang="ar") for i in range(6,18)]
        self.assertEqual(simulate(b,r,20,2)["deferred_queries"],0)
    def test_protect_sparse(self):
        b=[row(i,{"a"}) for i in range(10)]
        r=[row(i,{"a"}) for i in range(10,15)]
        self.assertEqual(simulate(b,r,20,2)["deferred_queries"],0)
    def test_protect_baseline_cap(self):
        b=[row(i,{"a"},cap=i==0) for i in range(6)]
        r=[row(i,{"a"}) for i in range(6,18)]
        self.assertEqual(simulate(b,r,20,2)["deferred_queries"],0)
    def test_future_outcome_not_used(self):
        b=[row(i,{"a"}) for i in range(6)]
        r=[row(i,{"a"}) for i in range(6,18)]
        x=simulate(b,r,0,2)
        r[4]["ids"]={"a","lost"};r[4]["observations"]=2
        y=simulate(b,r,0,2)
        self.assertEqual(x["new_calls"],y["new_calls"]);self.assertEqual(y["lost_observed_ids"],1)
    def test_control_reopens(self):
        b=[row(i,{"a"}) for i in range(6)]
        r=[row(i,{"a"}) for i in range(6,18)]
        r[3]["ids"]={"a","b"};r[3]["observations"]=2
        self.assertGreaterEqual(simulate(b,r,0,2)["events"].get("reopened_by_control",0),1)
    def test_observed_error_guards(self):
        b=[row(i,{"a"}) for i in range(6)]
        r=[row(i,{"a"}) for i in range(6,18)]
        r[0]["status"]="error";r[0]["ids"]=set()
        self.assertEqual(simulate(b,r,20,2)["deferred_queries"],0)
