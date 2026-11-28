import pathlib,sys,tempfile,unittest,csv
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P))
from calibration_10d97p import *
class TestCalibration(unittest.TestCase):
    def test_design(self):
        rows=expected();self.assertEqual(len(rows),361);self.assertEqual(len({r["review_id"] for r in rows}),361)
        self.assertEqual({r["code"] for r in rows},{p["code"] for p in matrix()})
    def test_blank_forms(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d);m=generate(out)
            self.assertEqual(m["rating_rows_per_judge"],361)
            self.assertEqual((out/"cotation_A.csv").read_bytes(),(out/"cotation_B.csv").read_bytes())
            with self.assertRaises(ValueError):load(out/"cotation_A.csv",{x["review_id"]:x for x in expected()})
    def test_kappa(self):
        self.assertEqual(agreement([("1","1"),("5","5")],SCORES,True)["kappa_linear_weighted"],1)
        self.assertIsNone(agreement([("3","3")],SCORES,True)["kappa_linear_weighted"])
        self.assertEqual(agreement([("1","5"),("5","1")],SCORES,True)["kappa_linear_weighted"],-1)
    def test_missing_not_score(self):
        ref=expected()[0];a=dict(ref,applicability="APPLICABLE",rating="NR");b=dict(ref,applicability="SO",rating="")
        self.assertIsNone(compare({ref["review_id"]:a},{ref["review_id"]:b})["overall_descriptive"]["ordinal"])
    def test_reject_score_without_evidence(self):
        ref=expected()[0]
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/"a.csv";write(p,FIELDS,[dict(ref,applicability="APPLICABLE",rating="5",reason="test")])
            with self.assertRaises(ValueError):load(p,{ref["review_id"]:ref})
    def test_valid_synthetic_fixture(self):
        ref=expected()[0]
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/"a.csv";write(p,FIELDS,[dict(ref,applicability="APPLICABLE",rating="4",reason="synthetic fixture",evidence_type=ref["minimum_evidence"],evidence_ref="fixture",evidence_date="2026-11-28",version_context="fixture")])
            self.assertEqual(load(p,{ref["review_id"]:ref})[ref["review_id"]]["rating"],"4")
    def test_nonapplicable_score_forbidden(self):
        ref=expected()[0]
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/"a.csv";write(p,FIELDS,[dict(ref,applicability="SO",rating="3",reason="test")])
            with self.assertRaises(ValueError):load(p,{ref["review_id"]:ref})
if __name__=="__main__":unittest.main()
