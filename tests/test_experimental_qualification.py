import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.experimental_qualification import validate,CONSTRAINTS,canonical
from acpa_msmda.experimental_registry import import_snapshot,read_preview
from acpa_msmda.real_catalog import DEFAULT_PATH,load_real_tools

class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"register.sqlite"
        self.doc=json.loads((ROOT/"data/experimental_documentary_leads.json").read_text())
        self.qual=json.loads((ROOT/"data/experimental_qualification_proposals.json").read_text())
    def imp(self,qual=None,day="2026-11-28"):
        return import_snapshot(self.db,DEFAULT_PATH,self.doc,observed_on=day,qualification=qual)
    def test_all_proposals_match_exact_source(self):
        self.assertEqual(len(validate(self.qual,self.doc)),34)
        self.assertEqual({r["review_status"] for r in self.qual["records"]},{"NOT_ASSESSED"})
        self.assertEqual({r["scenario_status"] for r in self.qual["records"]},{"PROPOSED_NOT_TESTED"})
        self.assertEqual({r["proposed_role"] for r in self.qual["records"]},{"DIRECT","COMPLEMENTAIRE","INCERTAIN"})
    def test_upgrade_and_repeat(self):
        before=load_real_tools()
        self.assertEqual(self.imp()["qualification_observations"],0)
        r=self.imp(self.qual)
        self.assertEqual((r["records"],r["observations"],r["qualification_observations"],r["new_qualifications"],r["new_recommendable"]),(2500,2500,34,34,0))
        repeat=self.imp(self.qual)
        self.assertEqual((repeat["new_records"],repeat["new_observations"],repeat["new_qualifications"]),(0,0,0))
        leads=read_preview(self.db)["leads"]
        self.assertEqual(len(leads),34)
        self.assertTrue(all(l["qualification_proposal"]["review_status"]=="NOT_ASSESSED" for l in leads))
        self.assertEqual(before,load_real_tools())
        print("A3_QUALIFICATION "+json.dumps(r,sort_keys=True))
    def test_no_scores_or_automatic_acceptance(self):
        for k,v in (("score",10),("review_status","DIRECT"),("evidence_level","TESTED"),("identity_status","CONFIRMED"),("constraints",dict.fromkeys(CONSTRAINTS,"COMPATIBLE")),("scenario_status","VALIDATED")):
            q=copy.deepcopy(self.qual)
            q["records"][0][k]=v
            with self.assertRaises(ValueError):
                self.imp(q)
        self.assertFalse(self.db.exists())
    def test_source_mismatch(self):
        for k,v in (("url","https://example.org"),("date","2026-11-29"),("record_id","catalog:strava"),("source_report","other")):
            q=copy.deepcopy(self.qual)
            q["records"][0][k]=v
            with self.assertRaises(ValueError):
                validate(q,self.doc)
        q=copy.deepcopy(self.qual)
        q["records"].append(q["records"][0])
        with self.assertRaises(ValueError):
            validate(q,self.doc)
    def test_append_revised_proposal_and_immutable_history(self):
        self.imp(self.qual)
        q=copy.deepcopy(self.qual)
        q["records"][0]["scenario"]="Autre scénario proposé"
        r=self.imp(q)
        self.assertEqual((r["new_qualifications"],r["qualification_observations"]),(1,35))
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM qualification").fetchone()[0],35)
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM qualification")
    def test_changed_source_hides_old_proposal(self):
        self.imp(self.qual)
        self.doc["records"][0]["date"]="2026-11-29"
        self.imp(day="2026-11-29")
        lead=next(x for x in read_preview(self.db)["leads"] if x["id"]=="doc_web:WD01")
        self.assertNotIn("qualification_proposal",lead)
    def test_read_old_schema(self):
        self.imp()
        with sqlite3.connect(self.db) as db:
            db.execute("DROP TABLE qualification")
        self.assertEqual(read_preview(self.db)["qualification_observations"],0)

    def test_same_date_url_changed_payload_hides_stale_proposal(self):
        self.imp(self.qual)
        self.doc["records"][0]["category"]="revised"
        with self.assertRaises(ValueError):
            self.imp(self.qual)
        self.imp()
        lead=next(x for x in read_preview(self.db)["leads"] if x["id"]=="doc_web:WD01")
        self.assertNotIn("qualification_proposal",lead)
        q=copy.deepcopy(self.qual)
        q["records"][0]["source_payload_sha256"]=hashlib.sha256(canonical(self.doc["records"][0]).encode("utf-8")).hexdigest()
        self.assertEqual(self.imp(q)["new_qualifications"],1)
        lead=next(x for x in read_preview(self.db)["leads"] if x["id"]=="doc_web:WD01")
        self.assertEqual(lead["qualification_proposal"]["source_payload_sha256"],q["records"][0]["source_payload_sha256"])

    def test_old_unbound_proposal_preserved_but_not_displayed(self):
        self.imp()
        old=copy.deepcopy(self.qual["records"][0])
        old.pop("source_payload_sha256")
        payload=canonical(old)
        digest=hashlib.sha256(payload.encode()).hexdigest()
        with sqlite3.connect(self.db) as db:
            db.execute("INSERT INTO qualification VALUES (?,?,?,?,?,?)",("qual:old:"+digest,old["record_id"],old["date"],old["url"],digest,payload))
        lead=next(x for x in read_preview(self.db)["leads"] if x["id"]=="doc_web:WD01")
        self.assertNotIn("qualification_proposal",lead)
        self.assertEqual(self.imp(self.qual)["qualification_observations"],35)
        self.assertIn("qualification_proposal",next(x for x in read_preview(self.db)["leads"] if x["id"]=="doc_web:WD01"))
