import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from identity_validation_metrics import *
class ValidationMetricsTests(unittest.TestCase):
    def test_sizes(self):
        self.assertEqual(srs_size(349,.10),76)
        self.assertEqual(srs_size(349,.05),184)
    def test_empty(self):
        self.assertIsNone(agreement({}, {},[])["kappa"])
        self.assertIsNone(candidate_yield({},[])["resolved_only_yield"])
    def test_perfect_single_class(self):
        r=agreement({"1":"A"},{"1":"A"},["1"])
        self.assertEqual(r["agreement"],1);self.assertIsNone(r["kappa"])
    def test_uncertain_and_missing(self):
        r=agreement({"1":"UNCERTAIN","2":"A","3":"B"},{"1":"UNCERTAIN","2":"B"},["1","2","3"])
        self.assertEqual(r["paired_complete"],2);self.assertEqual(r["missing_pair"],1);self.assertEqual(r["uncertain_a"],1)
    def test_direction(self):
        r=agreement({"1":"A_CLIENT_OF_B"},{"1":"B_CLIENT_OF_A"},["1"])
        self.assertEqual(r["agreement"],0)
    def test_candidate_bounds(self):
        r=candidate_yield({"1":"SAME_UNIT","2":"DISTINCT_UNIT","3":"UNCERTAIN"},["1","2","3","4"])
        self.assertEqual(r["unresolved"],2);self.assertEqual(r["lower_bound_all_sampled"],.25);self.assertEqual(r["upper_bound_all_sampled"],.75)
    def test_anchor_dedup(self):
        r=reference_capture({"a":["b","c"],"b":["a"]},[("a","b")],["a","b","d"])
        self.assertEqual(r["unique_reference_links"],2);self.assertEqual(r["missed"],1);self.assertEqual(r["reference_conditional_micro_capture"],.5);self.assertEqual(r["reference_conditional_macro_capture"],.75);self.assertEqual(r["anchors_without_discovered_links"],1)
    def test_no_reference(self):
        r=reference_capture({},[],["a"]);self.assertIsNone(r["reference_conditional_micro_capture"])
    def test_future_acceptance(self):
        r=acceptance_metrics({("a","b"):"SAME_UNIT",("a","c"):"DISTINCT_UNIT",("b","c"):"UNCERTAIN"},[("a","c"),("b","c")],[("a","b"),("a","c"),("b","c")])
        self.assertEqual((r["TP"],r["FP"],r["FN"],r["TN"],r["unresolved"]),(0,1,1,0,1))
    def test_invalid(self):
        with self.assertRaises(ValueError):candidate_yield({"x":"SAME_UNIT"},["y"])
        with self.assertRaises(ValueError):reference_capture({"a":["a"]},[],["a"])
        with self.assertRaises(ValueError):acceptance_metrics({("a","b"):"SAME_UNIT",("b","a"):"DISTINCT_UNIT"},[],[("a","b")])
