"""Separate, append-only experimental technology register.

Only the existing local catalogue and project-authored documentary pointers
are admitted by this prototype. It has no recommendation or promotion API.
External raw sources require a later authorized import policy.
"""
from __future__ import annotations

from contextlib import closing
from datetime import date
import hashlib
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit

from .catalogue_bridge import catalogue_snapshot
from .experimental_qualification import validate as validate_qualification

DOCUMENTARY_SOURCES = {"doc_web", "doc_target"}
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS record(
    id TEXT PRIMARY KEY, source TEXT NOT NULL, native TEXT NOT NULL,
    kind TEXT NOT NULL, UNIQUE(source,native));
CREATE TABLE IF NOT EXISTS observation(
    id TEXT PRIMARY KEY, record_id TEXT NOT NULL REFERENCES record(id),
    observed_on TEXT NOT NULL, locator TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
    payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS qualification(
    id TEXT PRIMARY KEY, record_id TEXT NOT NULL REFERENCES record(id),
    observed_on TEXT NOT NULL, locator TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
    payload TEXT NOT NULL);
"""
def _canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def _sha(obj):
    return hashlib.sha256(_canon(obj).encode("utf-8")).hexdigest()

def _day(value):
    if not isinstance(value,str) or date.fromisoformat(value).isoformat()!=value:
        raise ValueError("Invalid date")
    return value

def _add(db, table, values):
    columns = {"record":("id","source","native","kind"),
               "observation":("id","record_id","observed_on","locator","payload_sha256","payload"),
               "qualification":("id","record_id","observed_on","locator","payload_sha256","payload")}[table]
    previous = db.execute("SELECT "+",".join(columns)+" FROM "+table+" WHERE id=?", (values[0],)).fetchone()
    if previous is not None:
        if tuple(previous)!=tuple(values):
            raise ValueError("Conflicting immutable record or observation")
        return 0
    db.execute("INSERT INTO "+table+" VALUES ("+",".join("?" for _ in values)+")", values)
    return 1

def _documentary_rows(manifest):
    if manifest.get("schema_version")!=1 or not isinstance(manifest.get("records"),list):
        raise ValueError("Unsupported manifest")
    result=[]
    seen=set()
    for row in manifest["records"]:
        if not isinstance(row,dict) or set(row)!={"source","id","name","category","kind","url","date"}:
            raise ValueError("Unexpected documentary fields")
        if any(not isinstance(v,str) or not v.strip() for v in row.values()):
            raise ValueError("Missing documentary field")
        if row["source"] not in DOCUMENTARY_SOURCES:
            raise ValueError("Source not admitted")
        if ":" in row["id"]:
            raise ValueError("Invalid native ID")
        url=urlsplit(row["url"])
        if url.scheme!="https" or not url.hostname or url.username or url.password:
            raise ValueError("Invalid documentary link")
        day=_day(row["date"])
        key=row["source"]+":"+row["id"]
        if key in seen:
            raise ValueError("Duplicate source record")
        seen.add(key)
        payload={k:row[k] for k in ("name","category","url")}
        payload["status"]="DOCUMENTARY_LEAD_NOT_ASSESSED"
        digest=_sha(row)
        result.append(((key,row["source"],row["id"],row["kind"]),
                      ("obs:"+key+":"+day+":"+digest,key,day,row["url"],digest,_canon(payload))))
    return result

def import_snapshot(db_path, catalogue_path, manifest, *, observed_on, qualification=None):
    """One transactional import; same input idempotent, changes append observations."""
    snapshot=catalogue_snapshot(catalogue_path,observed_on=observed_on)
    documentary=_documentary_rows(manifest)
    proposals=[] if qualification is None else validate_qualification(qualification,manifest)
    path=Path(db_path).resolve()
    if path==Path(catalogue_path).resolve():
        raise ValueError("Cannot overwrite catalogue")
    with closing(sqlite3.connect(path)) as db:
        db.executescript(SCHEMA)
        for table in ("record","observation","qualification"):
            for event in ("UPDATE","DELETE"):
                db.execute(f"CREATE TRIGGER IF NOT EXISTS no_{table}_{event.lower()} BEFORE {event} ON {table} BEGIN SELECT RAISE(ABORT,'append only'); END")
        db.commit()
        nr=no=nq=0
        with db:
            db.execute("BEGIN IMMEDIATE")
            for key,r in snapshot["records"].items():
                nr+=_add(db,"record",(key,r["source"],r["source_id"],r["kind_hint"]))
            for key,o in snapshot["observations"].items():
                no+=_add(db,"observation",(key,o["record"],o["date"],o["locator"],o["payload_sha256"],"{}"))
            for record,observation in documentary:
                nr+=_add(db,"record",record)
                no+=_add(db,"observation",observation)
            for proposal in proposals:
                nq+=_add(db,"qualification",proposal)
        return {"new_records":nr,"new_observations":no,"new_qualifications":nq,**_summary(db)}

def _has_qualification(db):
    return db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='qualification'").fetchone() is not None

def _summary(db):
    sources=dict(db.execute("SELECT source,COUNT(*) FROM record GROUP BY source"))
    return {"records":sum(sources.values()),"observations":db.execute("SELECT COUNT(*) FROM observation").fetchone()[0],
            "sources":sources,"documentary_leads":sum(sources.get(s,0) for s in DOCUMENTARY_SOURCES),
            "qualification_observations":db.execute("SELECT COUNT(*) FROM qualification").fetchone()[0] if _has_qualification(db) else 0,
            "new_recommendable":0}

def read_preview(db_path):
    """Read-only, no writes and no legacy score or user/session data."""
    uri=Path(db_path).resolve().as_uri()+"?mode=ro"
    with closing(sqlite3.connect(uri,uri=True)) as db:
        summary=_summary(db)
        rows=db.execute("""SELECT r.id,r.kind,o.observed_on,o.payload,o.payload_sha256 FROM record r
            JOIN observation o ON o.record_id=r.id
            WHERE r.source IN ('doc_web','doc_target')
            AND o.id=(SELECT i.id FROM observation i WHERE i.record_id=r.id ORDER BY i.observed_on DESC,i.rowid DESC LIMIT 1)
            ORDER BY r.id""").fetchall()
        leads=[{"id":r,"kind":k,"date":d,**json.loads(payload)} for r,k,d,payload,_ in rows]
        if _has_qualification(db):
            for lead, (_,_,_,_,source_digest) in zip(leads,rows):
                # Only show the proposal for the currently displayed source observation.
                # A newer observation or changed link requires a new review.
                proposals=db.execute("""SELECT payload FROM qualification WHERE record_id=? AND observed_on=? AND locator=?
                    ORDER BY rowid DESC""",(lead["id"],lead["date"],lead["url"])).fetchall()
                for q in proposals:
                    proposal=json.loads(q[0])
                    if proposal.get("source_payload_sha256")==source_digest:
                        lead["qualification_proposal"]=proposal
                        break
        return {**summary,"leads":leads}
