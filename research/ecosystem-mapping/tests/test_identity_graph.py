import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from identity_graph import Graph
D={"judge_a":"A","judge_b":"B","arbitrator":"C","decision_date":"2026-11-28","reference":"synthetic-only"}
class GraphTest(unittest.TestCase):
    def setUp(self):
        self.g=Graph();self.g.source("a","store","example");self.g.source("b","store","example")
        self.a=self.g.record("a","123");self.b=self.g.record("b","123")
        self.g.proof("p","https://example.org/evidence","2026-11-28","adjudication")
        for k in ("X","Y","Z"):self.g.entity(k,"software",k)
    def accepted(self,k,a,r,b):self.g.link(k,a,r,b,"ADJUDICATED",["p"],"synthetic",D)
    def test_source_namespace(self):self.assertNotEqual(self.a,self.b)
    def test_repeat_record(self):self.assertEqual(self.g.record("a","123"),self.a);self.assertEqual(len(self.g.records),2)
    def test_observations(self):
        self.g.observe("o1",self.a,"2026-11-28","q1");self.g.observe("o2",self.a,"2026-11-28","q2")
        self.assertEqual(len(self.g.observations),2);self.assertEqual(len(self.g.records),2)
    def test_name_no_merge(self):
        self.g.link("c",self.a,"NAME_CANDIDATE",self.b,"REVIEW_REQUIRED");self.assertEqual(self.g.identity_groups(),[])
    def test_missing_endpoint(self):
        with self.assertRaises(ValueError):self.g.link("c",self.a,"NAME_CANDIDATE","missing")
    def test_missing_proof(self):
        with self.assertRaises(ValueError):self.g.link("c","X","SAME_PRODUCT","Y","ADJUDICATED")
    def test_record_merge_rejected(self):
        with self.assertRaises(ValueError):self.accepted("c",self.a,"SAME_PRODUCT",self.b)
    def test_distinct_roles(self):
        d={**D,"judge_b":"A"}
        with self.assertRaises(ValueError):self.g.link("c","X","SAME_PRODUCT","Y","ADJUDICATED",["p"],"synthetic",d)
    def test_adjudicated_group(self):
        self.accepted("c","X","SAME_PRODUCT","Y");self.assertEqual(self.g.identity_groups(),[["X","Y"]])
    def test_transitive_conflict(self):
        self.accepted("a","X","SAME_PRODUCT","Y");self.accepted("b","Y","SAME_PRODUCT","Z")
        self.g.link("c","X","DISTINCT_PRODUCT","Z","UNCERTAIN")
        with self.assertRaises(ValueError):self.g.validate()
    def test_component_never_merge(self):
        self.g.link("a","X","COMPONENT_OF","Y","PROPOSED");self.assertEqual(self.g.identity_groups(),[])
        self.accepted("b","X","SAME_PRODUCT","Y")
        with self.assertRaises(ValueError):self.g.validate()
    def test_hardware_software_merge_rejected(self):
        self.g.entity("H","hardware","sensor")
        with self.assertRaises(ValueError):self.accepted("c","X","SAME_PRODUCT","H")
    def test_variant_client_fork(self):
        self.g.link("a","X","VARIANT_OF","Y");self.g.link("b","Y","CLIENT_OF","Z");self.g.link("c","Z","FORK_OF","X")
        self.assertEqual(self.g.identity_groups(),[])
    def test_directional_cycle(self):
        self.accepted("a","X","COMPONENT_OF","Y");self.accepted("b","Y","COMPONENT_OF","X")
        with self.assertRaises(ValueError):self.g.validate()
    def test_rename_is_not_automatic(self):
        self.g.link("a","X","RENAMED_FROM","Y");self.assertEqual(self.g.identity_groups(),[])
    def test_duplicate_symmetric(self):
        self.g.link("a","X","NAME_CANDIDATE","Y")
        with self.assertRaises(ValueError):self.g.link("b","Y","NAME_CANDIDATE","X")
