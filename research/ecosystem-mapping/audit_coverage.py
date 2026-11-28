"""Offline coverage audit from the exact archived candidate plan and two pilot ZIPs.
Usage: python audit_coverage.py plan.zip baseline.zip expansion.zip
Outputs counts only; no redistribution of third-party payloads.
"""
import sys,zipfile,json,hashlib,collections
def read(z,n):return json.loads(z.read(n))
def key(q):return q["term"],q["country"]
def audit(plan_path,baseline_path,expansion_path):
    with zipfile.ZipFile(plan_path) as z:
        if z.testzip():raise ValueError("Corrupt plan ZIP")
        p=read(z,"candidate_plan.json")
    plans={key(r):r for r in p}
    if len(plans)!=len(p) or any(r["limit"]!=200 or r["entity"]!="software" for r in p):raise ValueError("Invalid candidate plan")
    obs={}
    for path in (baseline_path,expansion_path):
        with zipfile.ZipFile(path) as z:
            if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError("Corrupt or duplicate ZIP entry")
            plan=read(z,"plan.json");logs={}
            for n in z.namelist():
                if not n.endswith(".log.json"):continue
                l=read(z,n);q=l["query"];k=key(q)
                if k in logs or k in obs or k not in plans or q["limit"]!=50 or l["status"]!="ok":raise ValueError("Unexpected log")
                suffix=".raw.json" if "sha256" in l else ".facts.json"
                raw=z.read(n.replace(".log.json",suffix))
                if hashlib.sha256(raw).hexdigest()!=l.get("sha256",l.get("facts_sha256")):raise ValueError("Hash mismatch")
                a=json.loads(raw)
                if isinstance(a,dict):a=a["results"]
                if not isinstance(a,list) or len(a)!=l.get("returned",len(a)):raise ValueError("Count mismatch")
                if not any(x["origin"]=="modern" and x["family"]==q["family"] and x["language"]==q["language"] for x in plans[k]["labels"]):raise ValueError("Label mismatch")
                obs[k]=len(a);logs[k]=q
            if len(plan)!=len(logs) or {key(q):q for q in plan}!=logs:raise ValueError("Plan/log mismatch")
    fam=collections.defaultdict(lambda:[0,0,0,0]);cell=collections.defaultdict(lambda:[0,0,0,0]);hist=collections.Counter()
    for k,r in plans.items():
        for l in r["labels"]:
            if l["origin"]=="modern":
                for d,idx in [(fam,l["family"]),(cell,l["language"]+"/"+r["country"])]:
                    d[idx][0]+=1
                    if k in obs:
                        d[idx][1]+=1;d[idx][2]+=obs[k]==0;d[idx][3]+=obs[k]>=50
            elif l["origin"]=="historical":
                hist["planned"]+=1;hist["observed"]+=k in obs
    return {"columns":["planned","verified_limit50","empty","capped50"],"family":dict(sorted(fam.items())),"language_market":dict(sorted(cell.items())),"historical_labels":dict(hist),"union_planned":len(plans),"observed_limit50":len(obs),"union_not_observed_in_pilots":len(plans)-len(obs),"observed_limit200":0,"note":"Query plan execution, not market or relevant-product coverage"}
if __name__=="__main__":print(json.dumps(audit(*sys.argv[1:]),ensure_ascii=False,indent=2))
