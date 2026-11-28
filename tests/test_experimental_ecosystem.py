import json
from pathlib import Path
import sys
import tempfile
import unittest
from itertools import combinations
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.experimental_ecosystem import GATES,solve_fixture,inspect_real_proposals
from acpa_msmda.experimental_registry import import_snapshot,read_preview
from acpa_msmda.real_catalog import DEFAULT_PATH

def ctx(**kw):
    return dict({"required":["F04","F06"],"optional":["F07"],"budget_mad":100,"period":"session","devices":1,"offline":True,"unsupported_requirements":[]},**kw)
def tool(id,functions,**kw):
    return dict({"id":id,"product":id,"mode":"TEST_FIXTURE","review":"FIXTURE_APPROVED","gates":dict.fromkeys(GATES,"COMPATIBLE"),"offline":True,"cost":0,"period":"session","currency":"MAD","load":1,"device_slots":{"during":0},"functions":functions,"requires":[],"incompatible":[]},**kw)
class EcosystemTests(unittest.TestCase):
    def runset(self,items,c=None,**kw):
        return solve_fixture(c or ctx(),items,**kw)
    def test_offline(self):
        r=self.runset([tool("a",["F04","F06"],offline=False),tool("b",["F04"],offline=None)])
        self.assertEqual(r["excluded"],dict.fromkeys(["a","b"],"OFFLINE_NOT_ESTABLISHED"))
    def test_complementary(self):
        r=self.runset([tool("a",["F04"]),tool("b",["F06"])])
        self.assertEqual(r["selected"]["ids"],["a","b"])
        self.assertEqual(r["best_individual"]["uncovered_required"],["F06"])
    def test_parsimony(self):
        r=self.runset([tool("a",["F04"]),tool("b",["F06"]),tool("c",["F04","F06"],load=8)])
        self.assertEqual(r["selected"]["ids"],["c"])
    def test_total_budget(self):
        r=self.runset([tool("a",["F04"],cost=60),tool("b",["F06"],cost=60)])
        self.assertIsNone(r["selected"])
        self.assertEqual(r["combination_rejections"]["TOTAL_BUDGET"],1)
    def test_cost_unknown(self):
        r=self.runset([tool("a",["F04"],cost=None),tool("b",["F06"],period="year")])
        self.assertEqual(len(r["excluded"]),2)
    def test_dependency(self):
        r=self.runset([tool("a",["F04","F06"],requires=["b"])])
        self.assertIsNone(r["selected"])
    def test_pair_and_devices(self):
        a,b=tool("a",["F04"],device_slots={"during":1}),tool("b",["F06"],device_slots={"during":1})
        self.assertIsNone(self.runset([a,b])["selected"])
        b["device_slots"]={"after":1}
        self.assertIsNotNone(self.runset([a,b])["selected"])
        b["incompatible"]=["a"]
        self.assertIsNone(self.runset([a,b])["selected"])
    def test_safety(self):
        t=tool("a",["F04","F06"])
        t["gates"]["physical_safety"]="UNKNOWN"
        self.assertIsNone(self.runset([t])["selected"])
    def test_privacy(self):
        t=tool("a",["F04","F06"])
        t["gates"]["age_privacy"]="UNKNOWN"
        self.assertIsNone(self.runset([t])["selected"])
    def test_identity(self):
        a,b=tool("a",["F04"],product="same"),tool("b",["F06"],product="same")
        self.assertIsNone(self.runset([a,b])["selected"])
    def test_stale(self):
        t=tool("a",["F04","F06"])
        t["gates"]["source_current"]="UNKNOWN"
        self.assertIsNone(self.runset([t])["selected"])
    def test_real_register(self):
        with tempfile.TemporaryDirectory() as d:
            doc=json.loads((ROOT/"data/experimental_documentary_leads.json").read_text())
            qual=json.loads((ROOT/"data/experimental_qualification_proposals.json").read_text())
            db=Path(d)/"fixture.sqlite"
            import_snapshot(db,DEFAULT_PATH,doc,observed_on="2026-11-28",qualification=qual)
            leads=read_preview(db)["leads"]
            r=inspect_real_proposals(leads)
            self.assertEqual((r["records"],r["admitted"],r["recommended"]),(34,0,[]))
            print("A4_REAL_BOUNDARY "+json.dumps(r,sort_keys=True))
    def test_determinism(self):
        a,b=tool("a",["F04","F06"]),tool("b",["F04","F06"])
        self.assertEqual(self.runset([a,b]),self.runset([b,a]))
    def test_bound(self):
        r=self.runset([tool("a",["F04"]),tool("b",["F06"])],max_combinations=1)
        self.assertEqual(r["status"],"INCOMPLETE_SEARCH")
        self.assertIsNone(r["selected"])
    def test_small_oracle(self):
        # Independent explicit oracle for cost and coverage on a bounded fixture.
        pool=[tool("a",["F04"],cost=2),tool("b",["F06"],cost=3),tool("c",["F04","F06"],cost=7),tool("d",["F06"],cost=1)]
        for budget in range(9):
            feasible=[]
            for mask in range(1,1<<len(pool)):
                selected=[t for i,t in enumerate(pool) if mask>>i&1]
                if sum(t["cost"] for t in selected)<=budget and {"F04","F06"}<=set(f for t in selected for f in t["functions"]):
                    feasible.append((len(selected),sum(t["load"] for t in selected),sum(t["cost"] for t in selected),[t["id"] for t in selected]))
            result=self.runset(pool,ctx(budget_mad=budget))["selected"]
            self.assertEqual(None if result is None else result["ids"],min(feasible)[3] if feasible else None)
    def test_comparators(self):
        r=self.runset([tool("a",["F04"]),tool("b",["F06"]),tool("c",["F07"])])
        self.assertEqual(r["simple_pair"]["ids"],r["selected"]["ids"])
        self.assertEqual(r["selected"]["covered_optional"],[])
    def test_unknown_requirement(self):
        self.assertEqual(self.runset([tool("a",["F04","F06"])],ctx(unsupported_requirements=["other"]))["status"],"UNSUPPORTED_REQUIREMENT")
    def test_unapproved(self):
        self.assertIsNone(self.runset([tool("a",["F04","F06"],review="NOT_ASSESSED")])["selected"])
