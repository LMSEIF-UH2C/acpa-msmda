"""Checkpoint/resume engine for approved, fixed plans; fixture mode only in CI.
No external requests in this proof. Production integration is a separate gate.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import time
from plan_collection_v03 import identity

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def read(p):return json.loads(p.read_text(encoding="utf-8"))
def save(p,obj):
    t=p.with_suffix(".tmp");t.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8");t.replace(p)

def validate_plan(plan):
    if not isinstance(plan,list) or not plan:raise ValueError("Empty or invalid plan")
    ids=[identity(q) for q in plan]
    if len(set(ids))!=len(ids):raise ValueError("Duplicate request identity")
    if any(q.get("request_id")!=i or q.get("entity")!="software" for q,i in zip(plan,ids)):
        raise ValueError("Request identity mismatch")
    return ids

def recover(plan,out,mode,validator=validate_plan):
    ids=validator(plan)
    manifest={"schema":1,"mode":mode,"plan_sha256":digest(plan)}
    path=out/"manifest.json"
    if path.exists():
        if read(path)!=manifest:raise ValueError("Checkpoint belongs to another plan or mode")
    elif list(out.glob("*.record.json")):
        raise ValueError("Records without manifest")
    else:save(path,manifest)
    records={}
    expected=dict(zip(ids,plan))
    for p in sorted(out.glob("*.record.json")):
        rec=read(p);i=rec["request_id"]
        if i not in expected or p.name!=i+".record.json" or i in records:raise ValueError("Unexpected checkpoint record")
        if rec["query"]!=expected[i] or rec["mode"]!=mode:raise ValueError("Checkpoint query mismatch")
        payload=rec["payload"]
        if digest(payload)!=rec["payload_sha256"]:raise ValueError("Corrupted checkpoint payload")
        if digest({k:v for k,v in rec.items() if k!="record_sha256"})!=rec["record_sha256"]:raise ValueError("Corrupted checkpoint record")
        if rec["status"] not in ("ok","error","blocked"):raise ValueError("Unknown status")
        records[i]=rec
    return records

def block(plan,out,provider,budget,mode="fixture",validator=validate_plan,stop_on_error=False):
    if budget<1:raise ValueError("Positive request budget required")
    out.mkdir(parents=True,exist_ok=True)
    records=recover(plan,out,mode,validator)
    reused=sum(x["status"]=="ok" for x in records.values())
    attempts=0
    # A blocked response is a hard stop, not an invitation to retry.
    blocked=any(x["status"]=="blocked" for x in records.values())
    halted=stop_on_error and any(x["status"]=="error" for x in records.values())
    for q in plan:
        if blocked or halted or attempts>=budget:break
        i=q["request_id"]
        if i in records:continue # errors require explicit documented adjudication; do not silently retry
        start=time.monotonic()
        status,payload=provider(q)
        if status not in ("ok","error","blocked"):raise ValueError("Invalid provider status")
        rec={"request_id":i,"query":q,"mode":mode,"status":status,"payload":payload,"payload_sha256":digest(payload),"elapsed_seconds":time.monotonic()-start}
        rec["record_sha256"]=digest(rec)
        save(out/(i+".record.json"),rec)
        records[i]=rec;attempts+=1
        if status=="blocked":blocked=True
        if stop_on_error and status=="error":halted=True
    counts=collections.Counter(x["status"] for x in records.values())
    report={"mode":mode,"planned":len(plan),"new_attempts":attempts,"reused_successes":reused,"recorded":len(records),"status_counts":dict(counts),"unattempted":len(plan)-len(records),"blocked":blocked,"complete_success":counts["ok"]==len(plan)}
    save(out/"progress.json",report);print(json.dumps(report,indent=2))
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument("--plan",type=pathlib.Path,required=True);p.add_argument("--output",type=pathlib.Path,required=True);p.add_argument("--budget",type=int,required=True)
    a=p.parse_args()
    # Entirely synthetic response; never mixed with observed records.
    block(read(a.plan),a.output,lambda q:("ok",{"synthetic":True,"ids":[q["request_id"][:12]]}),a.budget)
if __name__=="__main__":main()
