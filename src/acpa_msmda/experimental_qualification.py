"""A3 qualification proposals: separate from decisions, ratings and operational recommendations."""
from __future__ import annotations
import hashlib
import json

CONSTRAINTS=("connectivity","cost","equipment","age_privacy","accessibility","physical_safety","morocco_availability")
ROLES={"DIRECT","COMPLEMENTAIRE","NON_PERTINENT","INCERTAIN"}
FIELDS={"record_id","url","date","documented_function","variant","scenario","proposed_role","documented_limits","source_report","evidence_level","scenario_status","review_status","constraints","identity_status","review_origin","source_payload_sha256"}
def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
def validate(manifest, documentary):
    """Return proposals paired with exact admitted source observations; no silent promotion."""
    if not isinstance(manifest,dict) or manifest.get("schema_version")!=2 or not isinstance(manifest.get("records"),list):
        raise ValueError("Invalid qualification manifest")
    leads={r["source"]+":"+r["id"]:r for r in documentary["records"]}
    seen=set()
    result=[]
    for row in manifest["records"]:
        if not isinstance(row,dict) or set(row)!=FIELDS:
            raise ValueError("Invalid qualification fields")
        if any(not isinstance(row[k],str) or not row[k].strip() for k in FIELDS-{"constraints"}):
            raise ValueError("Empty qualification field")
        key=row["record_id"]
        ref=leads.get(key)
        if key in seen or ref is None or (row["url"],row["date"])!=(ref["url"],ref["date"]):
            raise ValueError("Qualification source mismatch")
        if row["source_payload_sha256"] != hashlib.sha256(canonical(ref).encode("utf-8")).hexdigest():
            raise ValueError("Qualification source payload mismatch")
        if row["proposed_role"] not in ROLES or row["review_status"]!="NOT_ASSESSED" or row["scenario_status"]!="PROPOSED_NOT_TESTED":
            raise ValueError("Unapproved assessment")
        if row["evidence_level"]!="PUBLISHER_DECLARATION_REPORTED" or row["identity_status"]!="UNRESOLVED" or row["review_origin"]!="PROJECT_ASSISTANT_EXPLORATORY":
            raise ValueError("Unapproved evidence or identity")
        if row["constraints"]!={k:"UNKNOWN" for k in CONSTRAINTS}:
            raise ValueError("Context compatibility is not verified")
        if row["source_report"]!={"doc_web":"PROSPECTION_WEB_BUREAU_V01.json","doc_target":"PROSPECTION_MATERIEL_COMMERCIAL_V01.json"}[ref["source"]]:
            raise ValueError("Unexpected report")
        seen.add(key)
        payload=canonical(row)
        digest=hashlib.sha256(payload.encode()).hexdigest()
        result.append(("qual:"+key+":"+digest,key,row["date"],row["url"],digest,payload))
    return result
