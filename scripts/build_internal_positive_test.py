"""Generate temporary synthetic positive UI fixture, NEVER an operational approval.
Real A3 lineage is exercised, but all compatibility assertions are fabricated.
Only /tmp files; no approved real manifest or public deployment.
"""
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path
import json
import sys
from acpa_msmda.experimental_ecosystem import GATES, inspect_documentary_register
from acpa_msmda.experimental_real_admission import context_digest

def main(db, manifest_path, config_path):
    manifest_path, config_path = Path(manifest_path).resolve(), Path(config_path).resolve()
    if not all(p.parent == Path("/tmp") and p.name.startswith("acpa-test-") for p in (manifest_path, config_path)):
        raise ValueError("Test files must be temporary")
    context={"required":["F14"],"optional":[],"budget_mad":0,"period":"session","devices":1,"offline":True,"unsupported_requirements":[]}
    scenario={"id":"TEST_ONLY_POSITIVE","platform":"TEST_ONLY","data_policy":"No real data","setting":"Synthetic CI acceptance only"}
    d=next(x for x in inspect_documentary_register(db,context)["diagnostics"] if x["id"]=="doc_web:WD07")
    assert d["status"]=="DOCUMENTARY_PROPOSAL_ONLY"
    now=datetime.now(timezone.utc).date()
    candidate={"id":d["id"],"product":"TEST_ONLY_PRODUCT","functions":["F14"],"gates":dict.fromkeys(GATES,"COMPATIBLE"),"offline":True,"cost":0,"currency":"MAD","period":"session","load":1,"device_slots":{"after":1},"requires":[],"incompatible":[]}
    claim=[{"kind":"ACTUAL_TEST","locator":"TEST_ONLY_SYNTHETIC","finding":"Synthetic assertion to exercise UI; NOT actual evidence"}]
    keys={"function:F14"}|{"gate:"+g for g in GATES}|{"cost","load","device_slots","relations","offline"}
    row={"id":d["id"],"source_observation":d["source_observation"],"qualification_observation":d["qualification_observation"],"review_status":"OWNER_APPROVED_INTERNAL","context_sha256":context_digest(context,scenario),"decision_ref":"TEST_ONLY_NO_REAL_OWNER_APPROVAL","reviewed_on":now.isoformat(),"valid_until":(now+timedelta(days=1)).isoformat(),"candidate":candidate,"proofs":dict.fromkeys(keys,claim)}
    manifest_path.write_text(json.dumps({"schema_version":1,"records":[row],"pairs":[]}),encoding="utf-8")
    config_path.write_text(json.dumps({"schema_version":1,"context":context,"scenario":scenario,"manifest_path":str(manifest_path),"manifest_sha256":sha256(manifest_path.read_bytes()).hexdigest()}),encoding="utf-8")

if __name__=="__main__":
    main(*sys.argv[1:])
