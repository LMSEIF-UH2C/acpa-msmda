import pathlib,sys,tempfile,unittest,sqlite3
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from identity_graph import Graph
from identity_registry import Register
D={"judge_a":"A","judge_b":"B","arbitrator":"C","decision_date":"2026-11-28","reference":"synthetic"}
class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/"test.sqlite";self.r=Register(self.path,True)
        g=Graph();g.source("s","test","synthetic");g.record("s","a","software");g.observe("o","s:a","2026-11-28","synthetic")
        g.proof("p","https://example.org/proof","2026-11-28","publisher");g.proof("q","https://example.org/arbitration","2026-11-28","adjudication")
        for k,t in [("X","software"),("Y","software"),("Z","hardware"),("V","variant"),("C","client"),("P","platform")]:g.entity(k,t,k)
        self.r.load(g)
    def tearDown(self):self.r.close();self.tmp.cleanup()
    def v(self,a="s:a",b="X",rel="REFERS_TO",cat="attachment",state="PROPOSED",proofs=None):
        return {"a":a,"b":b,"relation":rel,"category":cat,"state":state,"evidence":proofs or ["p"],"rationale":"synthetic","date":"2026-11-28","actor":"test","decision":D if state in {"ADJUDICATED","REJECTED","WITHDRAWN"} else None}
    def test_reopen(self):
        self.r.append("a",self.v(),0);s=self.r.audit();self.r.close();self.r=Register(self.path);self.assertEqual(s,self.r.audit())
    def test_stale_revision(self):
        self.r.append("a",self.v(),0)
        with self.assertRaises(ValueError):self.r.append("a",self.v(),0)
    def test_history_and_conflicting_evidence(self):
        self.r.append("a",self.v(),0);self.r.append("a",self.v(state="UNCERTAIN",proofs=["p","q"]),1)
        self.assertEqual(len(self.r.history("a")),2)
        with self.assertRaises(ValueError):self.r.append("a",self.v(proofs=["q"]),2)
    def test_no_mutation(self):
        self.r.append("a",self.v(),0)
        with self.assertRaises(sqlite3.IntegrityError):self.r.db.execute("UPDATE event SET payload='{}'")
        with self.assertRaises(sqlite3.IntegrityError):self.r.db.execute("DELETE FROM event")
    def test_missing_endpoint(self):
        with self.assertRaises(ValueError):self.r.append("a",self.v(b="missing"),0)
    def test_type_attachment(self):
        with self.assertRaises(ValueError):self.r.append("a",self.v(b="Z",state="ADJUDICATED",proofs=["p","q"]),0)
    def test_two_accepted_attachments_rollback(self):
        self.r.append("a",self.v(state="ADJUDICATED",proofs=["p","q"]),0)
        with self.assertRaises(ValueError):self.r.append("b",self.v(b="Y",state="ADJUDICATED",proofs=["p","q"]),0)
        self.assertEqual(self.r.audit()["tables"]["event"],1)
    def test_variant_relation(self):
        self.r.append("a",self.v("V","X","VARIANT_OF","relation","ADJUDICATED",["p","q"]),0)
        with self.assertRaises(ValueError):self.r.append("b",self.v("X","V","VARIANT_OF","relation","ADJUDICATED",["p","q"]),0)
    def test_client_type(self):
        self.r.append("a",self.v("C","P","CLIENT_OF","relation","ADJUDICATED",["p","q"]),0)
        with self.assertRaises(ValueError):self.r.append("b",self.v("C","Z","CLIENT_OF","relation","ADJUDICATED",["p","q"]),0)
    def test_multi_relations(self):
        self.r.append("a",self.v("C","P","CLIENT_OF","relation"),0);self.r.append("b",self.v("C","P","REQUIRES","relation"),0)
        self.assertEqual(self.r.audit()["current_assertions"],2)
    def test_rejected_history(self):
        self.r.append("a",self.v(),0);self.r.append("a",self.v(state="REJECTED",proofs=["p","q"]),1)
        self.assertEqual(len(self.r.history("a")),2);self.assertEqual(self.r.audit()["confirmed_attachments"],0)
    def test_reopen_rejected_requires_arbitration(self):
        self.r.append("a",self.v(state="REJECTED",proofs=["p","q"]),0)
        with self.assertRaises(ValueError):self.r.append("a",self.v(state="PROPOSED",proofs=["p","q"]),1)
    def test_missing_arbitration(self):
        with self.assertRaises(ValueError):self.r.append("a",self.v(state="ADJUDICATED"),0)
    def test_immutable_endpoints(self):
        self.r.append("a",self.v(),0)
        with self.assertRaises(ValueError):self.r.append("a",self.v(b="Y"),1)
    def test_chain_detects_tampering(self):
        self.r.append("a",self.v(),0);self.r.db.execute("DROP TRIGGER no_event_update");self.r.db.execute("UPDATE event SET hash='bad'");self.r.db.commit()
        with self.assertRaises(ValueError):self.r.audit()
