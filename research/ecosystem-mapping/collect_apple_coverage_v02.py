"""Exploratory crossed-market coverage of additional V0.2 expressions.
Only factual metadata and response hashes are archived; no icons or descriptions are published.
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
FIELDS = ("trackId","bundleId","trackName","sellerName","trackViewUrl","primaryGenreName","version","currentVersionReleaseDate","price","currency","contentAdvisoryRating")

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path,obj):
    temp=path.with_suffix(".tmp")
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
    temp.replace(path)

def plan(old,new):
    original={(f["id"],lang,term) for f in old["families"] for lang,terms in f["queries"].items() for term in terms}
    extra=[(f["id"],lang,term) for f in new["families"] for lang,terms in f["queries"].items() for term in terms if (f["id"],lang,term) not in original]
    if len(extra)!=60 or len(set(extra))!=60:
        raise ValueError("Expected 60 distinct additional expressions")
    return [{"family":f,"language":lang,"term":term,"country":country,"limit":50} for f,lang,term in extra for country in new["countries"]]

def digest(q):
    return hashlib.sha256(json.dumps(q,sort_keys=True).encode()).hexdigest()[:20]

def fetch(q):
    url="https://itunes.apple.com/search?"+urllib.parse.urlencode({"term":q["term"],"country":q["country"],"entity":"software","limit":q["limit"]})
    for attempt in range(1,4):
        time.sleep(4 if attempt==1 else 12*attempt)
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"ACPA-MSMDA-research-coverage/0.2"})
            with urllib.request.urlopen(req,timeout=30) as response:
                raw=response.read()
            data=json.loads(raw)
            rows=data["results"]
            if not isinstance(rows,list) or data.get("resultCount")!=len(rows):
                raise ValueError("Unexpected search payload")
            return {"status":"ok","url":url,"attempts":attempt,"response_sha256":hashlib.sha256(raw).hexdigest(),"response_bytes":len(raw),"returned":len(rows)}, [{k:row[k] for k in FIELDS if k in row} for row in rows]
        except urllib.error.HTTPError as exc:
            if exc.code in (403,429):
                return {"status":"blocked","url":url,"attempts":attempt,"http_status":exc.code,"retry_after":exc.headers.get("Retry-After")}, []
            last={"http_status":exc.code}
        except Exception as exc:
            last={"error_type":type(exc).__name__}
    return {"status":"error","url":url,"attempts":3,**last}, []

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=pathlib.Path,required=True)
    p.add_argument("--baseline",type=pathlib.Path,required=True)
    args=p.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    old=read(HERE/"query_matrix.json");new=read(HERE/"query_matrix_v02_proposed.json")
    queries=plan(old,new);save(out/"plan.json",queries)
    baseline=set()
    for log in sorted(args.baseline.glob("*.log.json")):
        record=read(log)
        if record["status"]!="ok":continue
        raw=log.with_name(log.name.replace(".log.json",".raw.json")).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=record["sha256"]:raise ValueError("Baseline hash mismatch")
        baseline.update(str(row["trackId"]) for row in json.loads(raw)["results"] if row.get("trackId") is not None)
    if len(baseline)!=1435:raise ValueError("Unexpected original Apple pilot size")
    ids=set();by_cell=collections.defaultdict(set);by_family=collections.defaultdict(set);by_term=collections.defaultdict(set)
    counts=collections.Counter();total=0;capped=0
    for q in queries:
        k=digest(q);record_path=out/(k+".log.json");facts_path=out/(k+".facts.json")
        if record_path.exists() and facts_path.exists():
            record=read(record_path)
            if record.get("status")=="ok" and record.get("facts_sha256")==hashlib.sha256(facts_path.read_bytes()).hexdigest():
                rows=read(facts_path)
            else:record={}
        else:record={}
        if not record:
            record,rows=fetch(q);record.update(query=q,time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
            if record["status"]=="ok":
                save(facts_path,rows);record["facts_sha256"]=hashlib.sha256(facts_path.read_bytes()).hexdigest()
            save(record_path,record)
        counts[record["status"]]+=1
        if record["status"]=="blocked":break
        if record["status"]!="ok":continue
        total+=len(rows);capped+=int(len(rows)>=q["limit"])
        found={str(row["trackId"]) for row in rows if row.get("trackId") is not None}
        ids.update(found);by_cell[(q["language"],q["country"])].update(found);by_family[q["family"]].update(found);by_term[(q["family"],q["language"],q["term"])].update(found)
    report={"phase":"exploratory additional terms only","planned_queries":len(queries),"attempted_queries":sum(counts.values()),"status_counts":dict(counts),"unattempted_queries":len(queries)-sum(counts.values()),"capped_queries":capped,"raw_observations":total,"distinct_apple_ids":len(ids),"baseline_ids":len(baseline),"overlap_baseline":len(ids&baseline),"additional_ids_vs_baseline":len(ids-baseline),"combined_ids":len(ids|baseline),"by_language_market":{"/".join(k):{"ids":len(v),"additional_vs_baseline":len(v-baseline)} for k,v in sorted(by_cell.items())},"by_family":{k:{"ids":len(v),"additional_vs_baseline":len(v-baseline)} for k,v in sorted(by_family.items())},"by_term":[{"family":k[0],"language":k[1],"term":k[2],"ids":len(v),"additional_vs_baseline":len(v-baseline)} for k,v in sorted(by_term.items())],"note":"Factual metadata only, raw responses hashed but not retained for this expansion to limit redistribution. No relevance screening. Search yield and ranking vary over time; no exhaustive coverage or causal country comparison."}
    save(out/"report.json",report);print(json.dumps(report,ensure_ascii=False,indent=2))
    if counts["ok"]!=len(queries):raise SystemExit(2)

if __name__=="__main__":main()
