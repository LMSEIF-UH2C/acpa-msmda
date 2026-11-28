"""Offline plan: preserve historical vocabulary, deduplicate exact HTTP queries.
No network access or catalogue changes. A query limit is part of its identity.
"""
import argparse
import ast
import collections
import hashlib
import json
import pathlib
import unicodedata

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def historical(path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="QUERIES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("Historical QUERIES missing")

def term_norm(s):
    return unicodedata.normalize("NFC",s).strip()

def request_key(q):
    return (term_norm(q["term"]),q["country"],"software",int(q["limit"]))

def identity(q):
    return hashlib.sha256(json.dumps(request_key(q),ensure_ascii=False).encode()).hexdigest()

def build(old,new):
    vocabulary=collections.defaultdict(set)
    modern_terms=set();old_terms=set()
    for f in new["families"]:
        for lang,terms in f["queries"].items():
            for t in terms:
                t=term_norm(t);modern_terms.add(t);vocabulary[t].add(("modern",f["id"],lang))
    for family,terms in old.items():
        for t in terms:
            t=term_norm(t);old_terms.add(t);vocabulary[t].add(("historical",family,"en"))
    queries=[]
    for term,labels in sorted(vocabulary.items()):
        for country in new["countries"]:
            q={"term":term,"country":country,"entity":"software","limit":200,"labels":[{"origin":a,"family":b,"language":c} for a,b,c in sorted(labels)]}
            q["request_id"]=identity(q);queries.append(q)
    if len({q["request_id"] for q in queries})!=len(queries):
        raise ValueError("Duplicate request")
    return queries,{"historical_distinct_expressions":len(old_terms),"modern_distinct_expressions":len(modern_terms),"common_expressions":len(old_terms&modern_terms),"historical_not_exactly_repeated":len(old_terms-modern_terms),"union_expressions":len(vocabulary),"markets":new["countries"],"candidate_requests":len(queries),"note":"Candidate union before validation; no requirement to execute all requests, no app count target. Semantically similar terms are not assumed equivalent."}

def audit_cache(roots):
    verified=collections.defaultdict(list)
    failures=[]
    for root in roots:
        for path in sorted(root.rglob("*.log.json")):
            try:
                log=read(path)
                if log.get("status")!="ok":continue
                q=log["query"];k=identity(q)
                prefix=path.name.removesuffix(".log.json")
                raw=path.with_name(prefix+".raw.json")
                facts=path.with_name(prefix+".facts.json")
                if raw.exists() and hashlib.sha256(raw.read_bytes()).hexdigest()==log.get("sha256"):
                    rows=json.loads(raw.read_bytes())["results"];kind="raw"
                elif facts.exists() and hashlib.sha256(facts.read_bytes()).hexdigest()==log.get("facts_sha256"):
                    rows=read(facts);kind="facts"
                else:
                    raise ValueError("No verified payload")
                if not isinstance(rows,list):raise ValueError("Invalid rows")
                if log.get("returned") is not None and len(rows)!=log["returned"]:raise ValueError("Row count mismatch")
                verified[k].append({"kind":kind,"date":log.get("time_utc"),"rows":len(rows),"ids":sorted({str(x["trackId"]) for x in rows if x.get("trackId") is not None}),"log":str(path)})
            except Exception as e:
                failures.append({"log":str(path),"error":str(e)})
    return verified,failures

def summarize(queries,verified):
    exact=lower_only=missing=0
    for q in queries:
        if identity(q) in verified:
            exact+=1;q["cache_status"]="exact_snapshot_available"
        elif identity({**q,"limit":50}) in verified:
            lower_only+=1;q["cache_status"]="exploratory_50_only"
        else:
            missing+=1;q["cache_status"]="no_verified_snapshot"
    return {"exact_200_snapshot":exact,"lower_50_snapshot_only":lower_only,"no_verified_snapshot":missing,
            "note":"Exact snapshots are eligible for reuse only after date, rights, fields and protocol checks; 50 is not interchangeable with 200. No HTTP calls made."}

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=pathlib.Path,required=True);p.add_argument("--cache",type=pathlib.Path,action="append",default=[])
    x=p.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    queries,report=build(historical(ROOT/"tools/catalog/collect_appstore.py"),read(HERE/"query_matrix_v02_proposed.json"))
    cache,errors=audit_cache(x.cache)
    report.update(summarize(queries,cache),cache_errors=errors,cache_roots=[str(y) for y in x.cache])
    for name,obj in (("candidate_plan.json",queries),("report.json",report)):
        (x.output/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(2)
if __name__=="__main__":main()
