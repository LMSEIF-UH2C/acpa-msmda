import json
import hashlib
import sqlite3
import random
from pathlib import Path
import sys
import tempfile
import unittest
from itertools import combinations
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.experimental_ecosystem import GATES,solve_fixture,inspect_real_proposals,inspect_documentary_register,compare_historical_native
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
    def test_incomplete_search_discards_partial_comparators(self):
        # A complete feasible singleton may already have been seen; it is not a final optimum.
        pool=[tool("a",["F04","F06"]),tool("b",["F04"]),tool("c",["F06"])]
        for bound in (1,3,6):
            with self.subTest(bound=bound):
                r=self.runset(pool,max_combinations=bound)
                self.assertEqual(r["status"],"INCOMPLETE_SEARCH")
                self.assertEqual(r["evaluated"],bound)
                for key in ("selected","best_individual","simple_pair","uncovered_required"):
                    self.assertIsNone(r[key])
                self.assertNotIn("best_partial",r)
                self.assertEqual(json.loads(json.dumps(r)),r)
        terminal=self.runset(pool,max_combinations=7)
        self.assertEqual(terminal["status"],"COMPLETE_FIXTURE_SET")
        self.assertEqual(terminal["selected"]["ids"],["a"])
        self.assertIsInstance(terminal["best_individual"],dict)
        self.assertIsInstance(terminal["simple_pair"],dict)
        self.assertEqual(terminal["uncovered_required"],[])
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

    def test_documentary_adapter_exact_lineage(self):
        with tempfile.TemporaryDirectory() as d:
            doc=json.loads((ROOT/"data/experimental_documentary_leads.json").read_text())
            qual=json.loads((ROOT/"data/experimental_qualification_proposals.json").read_text())
            db=Path(d)/"fixture.sqlite"
            import_snapshot(db,DEFAULT_PATH,doc,observed_on="2026-11-28",qualification=qual)
            digest=hashlib.sha256(db.read_bytes()).hexdigest()
            r=inspect_documentary_register(db,ctx())
            self.assertEqual((r["records"],r["linked_proposals"],r["admitted"],r["recommended"]),(34,34,0,[]))
            self.assertFalse(r["coverage_assessed"])
            self.assertEqual(r["uncovered_required"],["F04","F06"])
            self.assertTrue(all(x["status"]=="DOCUMENTARY_PROPOSAL_ONLY" and not x["admissible"]
                                and x["function_ids"] is None and set(x["constraints"].values())=={"UNKNOWN"}
                                for x in r["diagnostics"]))
            self.assertEqual(digest,hashlib.sha256(db.read_bytes()).hexdigest())
            print("A4_DOCUMENTARY_ADAPTER "+json.dumps({"records":r["records"],"linked":r["linked_proposals"],"admitted":r["admitted"]}))
    def test_documentary_adapter_stale_proposal(self):
        with tempfile.TemporaryDirectory() as d:
            doc=json.loads((ROOT/"data/experimental_documentary_leads.json").read_text())
            qual=json.loads((ROOT/"data/experimental_qualification_proposals.json").read_text())
            db=Path(d)/"fixture.sqlite"
            import_snapshot(db,DEFAULT_PATH,doc,observed_on="2026-11-28",qualification=qual)
            doc["records"][0]["name"]+=" (changed local record)"
            import_snapshot(db,DEFAULT_PATH,doc,observed_on="2026-11-28")
            r=inspect_documentary_register(db,ctx())
            self.assertEqual(r["linked_proposals"],33)
            self.assertEqual(sum(x["status"]=="NO_CURRENT_PROPOSAL" for x in r["diagnostics"]),1)
            self.assertEqual(r["admitted"],0)
    def test_documentary_adapter_rejects_tampered_hash(self):
        with tempfile.TemporaryDirectory() as d:
            doc=json.loads((ROOT/"data/experimental_documentary_leads.json").read_text())
            qual=json.loads((ROOT/"data/experimental_qualification_proposals.json").read_text())
            db=Path(d)/"fixture.sqlite"
            import_snapshot(db,DEFAULT_PATH,doc,observed_on="2026-11-28",qualification=qual)
            # Deliberately corrupt disposable test copy; no mutation of real registry.
            with sqlite3.connect(db) as conn:
                conn.execute("DROP TRIGGER no_qualification_update")
                conn.execute("UPDATE qualification SET payload_sha256=? WHERE record_id=?",
                             ("0"*64,qual["records"][0]["record_id"]))
            r=inspect_documentary_register(db,ctx())
            self.assertEqual(r["linked_proposals"],33)
            self.assertEqual(sum(x["status"]=="PROPOSAL_LINEAGE_MISMATCH" for x in r["diagnostics"]),1)
            self.assertEqual(r["recommended"],[])
    def test_historical_native_calls_actual_ranking(self):
        from acpa_msmda.real_catalog import recommend
        digest=hashlib.sha256(DEFAULT_PATH.read_bytes()).hexdigest()
        for text in ("course relais chronometrage sans connexion","basketball video"):
            with self.subTest(context=text):
                native=recommend(text,votes={},path=DEFAULT_PATH)
                r=compare_historical_native(text,catalogue_path=DEFAULT_PATH,expected_sha256=digest,limit=5)
                self.assertEqual(r["matched_count"],len(native["matches"]))
                self.assertEqual([x["id"] for x in r["results"]],[x["id"] for x in native["matches"][:5]])
                self.assertEqual([x["fit"] for x in r["results"]],[x["fit"] for x in native["matches"][:5]])
                self.assertFalse(r["common_pool_comparison"])
                self.assertIsNone(r["coverage"])
                self.assertIsNone(r["constraint_violations"])
                self.assertFalse(r["ranking_validated"])
                print("A4_HISTORICAL_NATIVE "+json.dumps({"context":text,"count":r["matched_count"],"results":r["results"],"catalogue_sha256":digest},ensure_ascii=False))
        self.assertEqual(digest,hashlib.sha256(DEFAULT_PATH.read_bytes()).hexdigest())
    def test_historical_snapshot_and_limit_guard(self):
        digest=hashlib.sha256(DEFAULT_PATH.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            compare_historical_native("course",catalogue_path=DEFAULT_PATH,expected_sha256="0"*64)
        with self.assertRaises(ValueError):
            compare_historical_native("course",catalogue_path=DEFAULT_PATH,expected_sha256=digest,limit=0)

    def _independent_oracle(self, context, candidates):
        # Separate bitmask implementation, not calling any solver internals.
        if context["unsupported_requirements"]:
            return (None,None,None)
        req=set(context["required"])
        valid=[]
        for mask in range(1,1<<len(candidates)):
            items=[t for i,t in enumerate(candidates) if mask & (1<<i)]
            ids=sorted(t["id"] for t in items)
            if len({t["product"] for t in items}) != len(items):
                continue
            if any(t["mode"]!="TEST_FIXTURE" or t["review"]!="FIXTURE_APPROVED"
                   or not t["product"]
                   or any(t["gates"].get(g)!="COMPATIBLE" for g in GATES)
                   or (context["offline"] and t["offline"] is not True)
                   or type(t["cost"]) is not int or t["cost"]<0
                   or t["period"]!=context["period"] or t["currency"]!="MAD"
                   or type(t["load"]) is not int or t["load"]<0
                   or not t["functions"] or not t["device_slots"]
                   or not set(t["requires"]).issubset(ids)
                   or set(t["incompatible"]).intersection(set(ids)-{t["id"]})
                   for t in items):
                continue
            cost=sum(t["cost"] for t in items)
            if cost>context["budget_mad"]:
                continue
            if any(sum(t["device_slots"].get(phase,0) for t in items)>context["devices"]
                   for phase in ("before","during","after")):
                continue
            covered={f for t in items for f in t["functions"]}
            rank=(-len(req & covered),len(items),sum(t["load"] for t in items),cost,ids)
            valid.append((rank,covered))
        def choose(max_n=None,complete=False):
            ranks=[rank for rank,cov in valid if (max_n is None or rank[1]<=max_n)
                   and (not complete or req.issubset(cov))]
            return min(ranks)[-1] if ranks else None
        return choose(1),choose(2),choose(complete=True)

    def _check_common_pool(self, context, candidates):
        observed=self.runset(candidates,context)
        keys=("best_individual","simple_pair","selected")
        ids=tuple(observed[k]["ids"] if observed[k] else None for k in keys)
        self.assertEqual(ids,self._independent_oracle(context,candidates))
        self.assertEqual(observed,self.runset(list(reversed(candidates)),context))
        for k in keys:
            result=observed[k]
            if result is None: continue
            subset=[t for t in candidates if t["id"] in result["ids"]]
            coverage={f for t in subset for f in t["functions"]}
            self.assertEqual(result["covered_required"],sorted(set(context["required"])&coverage))
            self.assertEqual(result["covered_optional"],sorted(set(context["optional"])&coverage))
            self.assertEqual(result["uncovered_required"],sorted(set(context["required"])-coverage))
            self.assertEqual(result["cost_mad"],sum(t["cost"] for t in subset))
            self.assertEqual(result["load"],sum(t["load"] for t in subset))
        return observed

    def test_ten_pedagogical_common_pool_scenarios(self):
        # Conventions from the prospective protocol; all tools and values invented.
        def gate(t,g):
            t["gates"][g]="UNKNOWN"
            return t
        cases=[
            ("S01",ctx(required=["F04","F06","F07"],optional=["F05"]),
             [tool("a",["F04"],device_slots={"before":1}),tool("b",["F06"],device_slots={"during":1}),
              tool("c",["F07"],device_slots={"after":1}),tool("d",["F04","F06","F07"],offline=None)],["a","b","c"]),
            ("S02",ctx(required=["F01","F02","F08","F13"],optional=[],budget_mad=20),
             [tool("a",["F01","F02"],cost=15),tool("b",["F08","F13"],cost=10),
              tool("c",["F01","F02","F08","F13"],offline=None)],None),
            ("S03",ctx(required=["F04","F09","F13"],optional=["F05"]),
             [gate(tool("a",["F04","F09","F13"]),"accessibility"),tool("b",["F04","F09"]),tool("c",["F13"])],["b","c"]),
            ("S04",ctx(required=["F04","F05"],optional=["F07"]),
             [gate(tool("a",["F04","F05","F07"]),"physical_safety"),tool("b",["F04","F05"])],["b"]),
            ("S05",ctx(required=["F03","F06","F07"],optional=["F10"]),
             [gate(tool("a",["F03","F06","F07"]),"age_privacy"),tool("b",["F03","F06"],requires=["c"]),tool("c",["F07"])],["b","c"]),
            ("S06",ctx(required=["F04","F11","F12"],optional=[]),
             [tool("a",["F04","F11","F12"],period="year"),tool("b",["F04","F11","F12"],offline=False),
              tool("c",["F04","F11","F12"],cost=5)],["c"]),
            ("S07",ctx(required=["F02","F08","F15"],optional=[]),
             [tool("a",["F02"],product="same"),tool("b",["F08"],product="same"),
              tool("c",["F15"],incompatible=["b"]),tool("d",["F02","F08"],cost=5)],["c","d"]),
            ("S08",ctx(required=["F03","F06"],optional=["F10"],devices=0),
             [tool("a",["F03","F06"],device_slots={"during":1}),tool("b",["F03"]),tool("c",["F06"])],["b","c"]),
            ("S09",ctx(required=["F01","F10","F14"],optional=[]),
             [tool("a",["F01"],device_slots={"before":1}),tool("b",["F10"],device_slots={"after":1}),
              tool("c",["F14"],device_slots={"after":1}),tool("d",["F10","F14"],device_slots={"after":1},cost=5)],["a","d"]),
            ("S10",ctx(required=["F01","F02","F05","F09"],optional=["F11","F12"],unsupported_requirements=["unmodelled"]),
             [tool("a",["F01","F02","F05","F09"])],None),
        ]
        report=[]
        for case,context,pool,expected in cases:
            with self.subTest(case=case):
                r=self._check_common_pool(context,pool)
                self.assertEqual(r["selected"]["ids"] if r["selected"] else None,expected)
                report.append(dict(case=case,status=r["status"],
                    **{k:r[k] for k in ("best_individual","simple_pair","selected")}))
        print("A4_COMMON_POOL "+json.dumps(report,sort_keys=True))

    def test_full_constraint_oracle_seeded(self):
        rng=random.Random(20261128)
        for trial in range(100):
            n=rng.randint(1,6)
            context=ctx(devices=rng.randint(0,2),budget_mad=rng.randint(0,20),offline=rng.choice([True,False]))
            ids=[str(i) for i in range(n)]
            pool=[]
            for i in ids:
                t=tool(i,rng.sample(["F04","F06","F07"],rng.randint(1,3)),
                       cost=rng.randint(0,10),load=rng.randint(0,4),offline=rng.choice([True,False,None]),
                       device_slots={rng.choice(["before","during","after"]):rng.randint(0,2)},
                       product=rng.choice(ids),requires=rng.sample(ids,rng.randint(0,1)),
                       incompatible=rng.sample(ids,rng.randint(0,1)))
                if rng.random()<0.15: t["gates"][rng.choice(GATES)]="UNKNOWN"
                if rng.random()<0.10: t["period"]="year"
                if rng.random()<0.10: t["review"]="NOT_ASSESSED"
                pool.append(t)
            with self.subTest(trial=trial):
                self._check_common_pool(context,pool)
        print("A4_FULL_ORACLE "+json.dumps({"seed":20261128,"trials":100,"max_candidates":6,"comparators":3}))
