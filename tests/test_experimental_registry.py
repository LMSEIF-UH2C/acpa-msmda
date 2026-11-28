import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.experimental_registry import import_snapshot,read_preview
from acpa_msmda.experimental_entry import enabled,label
from acpa_msmda.real_catalog import DEFAULT_PATH,load_real_tools

class A2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"experiment.sqlite"
        self.catalog=Path(self.tmp.name)/"catalog.json"
        self.catalog.write_text(json.dumps({"dataset_type":"REAL_TOOLS_UNSCORED","tools":[{"id":"x","name":"Example"}]}))
        self.manifest={"schema_version":1,"records":[{"source":"doc_web","id":"x","name":"Example","category":"research","kind":"unknown","url":"https://example.org","date":"2026-11-28"}]}
    def run_import(self,day="2026-11-28"):
        return import_snapshot(self.db,self.catalog,self.manifest,observed_on=day)
    def test_idempotency_and_namespace(self):
        a=self.run_import()
        b=self.run_import()
        self.assertEqual((a["new_records"],a["new_observations"]),(2,2))
        self.assertEqual((b["new_records"],b["new_observations"]),(0,0))
        self.assertEqual(b["records"],2)
        self.assertEqual(b["new_recommendable"],0)
    def test_append_observations(self):
        self.run_import()
        b=self.run_import("2026-11-29")
        self.assertEqual((b["new_records"],b["new_observations"],b["observations"]),(0,1,3))
        self.manifest["records"][0]["name"]="Changed"
        c=self.run_import("2026-11-29")
        self.assertEqual((c["new_records"],c["new_observations"]),(0,1))
        self.assertEqual(read_preview(self.db)["leads"][0]["name"],"Changed")
    def test_rollback_on_conflict(self):
        self.run_import()
        self.manifest["records"][0]["kind"]="hardware"
        with self.assertRaises(ValueError):
            self.run_import("2026-11-29")
        self.assertEqual(read_preview(self.db)["observations"],2)
    def test_source_and_fields_rejected(self):
        self.run_import()
        for field,value in (("source","aptoide"),("url","http://example.org"),("date","2026-02-30"),("scores",{"C1":10})):
            original=self.manifest["records"][0].copy()
            self.manifest["records"][0][field]=value
            with self.assertRaises(ValueError):
                self.run_import()
            self.manifest["records"][0]=original
        self.assertEqual(read_preview(self.db)["records"],2)
    def test_immutable_sqlite(self):
        self.run_import()
        with sqlite3.connect(self.db) as db:
            for stmt in ("DELETE FROM record","UPDATE observation SET payload='x'"):
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute(stmt)
    def test_readonly_missing(self):
        with self.assertRaises(sqlite3.Error):
            read_preview(self.db)
        self.assertFalse(self.db.exists())
    def test_default_off(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertFalse(enabled())
        with patch.dict(os.environ,{"ACPA_EXPERIMENTAL_ECOSYSTEM":"true"}):
            self.assertFalse(enabled())
        with patch.dict(os.environ,{"ACPA_EXPERIMENTAL_ECOSYSTEM":"1"}):
            self.assertTrue(enabled())
        self.assertEqual(len({label(k) for k in ("fr","ar","en")}),3)
    def test_frozen_real_pilot(self):
        raw=DEFAULT_PATH.read_bytes()
        rows=load_real_tools()
        manifest=json.loads((ROOT/"data/experimental_documentary_leads.json").read_text())
        a=import_snapshot(self.db,DEFAULT_PATH,manifest,observed_on="2026-11-28")
        b=import_snapshot(self.db,DEFAULT_PATH,manifest,observed_on="2026-11-28")
        self.assertEqual(a["sources"],{"catalog":2466,"doc_web":17,"doc_target":17})
        self.assertEqual((a["records"],a["observations"],a["new_recommendable"]),(2500,2500,0))
        self.assertEqual((b["new_records"],b["new_observations"]),(0,0))
        preview=read_preview(self.db)
        self.assertEqual(len(preview["leads"]),34)
        self.assertTrue(all(x["status"]=="DOCUMENTARY_LEAD_NOT_ASSESSED" for x in preview["leads"]))
        self.assertEqual(load_real_tools(),rows)
        self.assertEqual(DEFAULT_PATH.read_bytes(),raw)
        print("A2_PILOT "+json.dumps(a,sort_keys=True))
