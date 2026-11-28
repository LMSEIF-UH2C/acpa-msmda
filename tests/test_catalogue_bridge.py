"""A1: legacy compatibility and the metadata-only cumulative projection."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda.catalogue_bridge import catalogue_snapshot, load_legacy_rows
from acpa_msmda.real_catalog import DEFAULT_PATH, load_real_tools


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "catalog.json"
        self.rows = [
            {"id": "a", "name": "Same", "criteria_scores": {"C6": "NR"},
             "evidence_status": "PENDING_SOURCE_VERIFICATION"},
            {"id": "b", "name": "Same", "criteria_scores": {"C6": 10},
             "evidence_status": "FEATURES_VERIFIED_ON_OFFICIAL_SITE"},
        ]
        self.write(self.rows)

    def write(self, rows):
        self.path.write_text(json.dumps({"dataset_type": "REAL_TOOLS_UNSCORED",
                                         "tools": rows}), encoding="utf-8")

    def snap(self, day="2026-11-28"):
        return catalogue_snapshot(self.path, observed_on=day)

    def test_legacy_roundtrip(self):
        self.assertEqual(load_legacy_rows(self.path), self.rows)
        self.assertEqual(load_real_tools(self.path), self.rows)

    def test_homonyms_never_merge(self):
        s = self.snap()
        self.assertEqual(set(s["records"]), {"catalog:a", "catalog:b"})
        self.assertEqual(len(s["observations"]), 2)
        self.assertEqual(s["entities"], {})
        self.assertEqual(s["assertions"], {})

    def test_no_promoted_evidence_or_scores(self):
        s = self.snap()
        self.assertEqual(s["evidence"], {})
        self.assertNotIn("criteria_scores", json.dumps(s))
        self.assertNotIn("FEATURES_VERIFIED", json.dumps(s))
        self.assertNotIn("Same", json.dumps(s))

    def test_deterministic_and_nonmutating(self):
        raw = self.path.read_bytes()
        self.assertEqual(self.snap(), self.snap())
        self.assertEqual(self.path.read_bytes(), raw)
        self.assertEqual(self.snap()["snapshot"]["sha256"], hashlib.sha256(raw).hexdigest())

    def test_update_preserves_record_identity(self):
        old = self.snap()
        self.rows[0]["criteria_scores"]["C6"] = 7
        self.write(self.rows)
        new = self.snap()
        self.assertEqual(old["records"], new["records"])
        self.assertFalse(set(old["observations"]) & set(new["observations"]))
        def row_hash(s, key):
            return next(v["payload_sha256"] for v in s["observations"].values() if v["record"] == key)
        self.assertNotEqual(row_hash(old, "catalog:a"), row_hash(new, "catalog:a"))
        self.assertEqual(row_hash(old, "catalog:b"), row_hash(new, "catalog:b"))

    def test_repeat_on_different_day(self):
        a, b = self.snap(), self.snap("2026-11-29")
        self.assertEqual(a["records"], b["records"])
        self.assertFalse(set(a["observations"]) & set(b["observations"]))

    def test_duplicate_rejected(self):
        self.write([self.rows[0], self.rows[0]])
        for fn in (lambda: load_real_tools(self.path), self.snap):
            with self.assertRaises(ValueError):
                fn()

    def test_invalid_id_rejected(self):
        for bad in (None, "", " ", 12):
            self.write([{"id": bad}])
            with self.assertRaises(ValueError):
                self.snap()

    def test_bad_date(self):
        for day in ("20261128", "2026-02-30", None):
            with self.assertRaises(ValueError):
                self.snap(day)

    def test_wrong_catalogue_type(self):
        self.path.write_text('{"dataset_type":"SYNTHETIC","tools":[]}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.snap()

    def test_frozen_real_catalogue(self):
        raw = DEFAULT_PATH.read_bytes()
        git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
        self.assertEqual(git_blob, "39b32ebbdf33b49a3fb0bb669f8a0809d0e72995")
        expected = json.loads(raw.decode("utf-8"))["tools"]
        self.assertEqual(load_real_tools(), expected)
        snapshot = catalogue_snapshot(DEFAULT_PATH, observed_on="2026-11-28")
        self.assertEqual(len(expected), 2466)
        self.assertEqual(len(snapshot["records"]), 2466)
        self.assertEqual(len(snapshot["observations"]), 2466)
        self.assertEqual(set(snapshot["records"]), {"catalog:" + r["id"] for r in expected})
        self.assertEqual(snapshot["entities"], {})
        self.assertEqual(DEFAULT_PATH.read_bytes(), raw)
        print("A1_CATALOGUE_SNAPSHOT " + json.dumps(snapshot["snapshot"], sort_keys=True))
