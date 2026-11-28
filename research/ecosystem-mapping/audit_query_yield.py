"""Offline query-yield audit. Counts identifiers, not eligible products.
No network requests, no names/descriptions in report, no automatic exclusions.
"""
import argparse
import collections
import csv
import hashlib
import itertools
import json
import pathlib

def read(p):
    return json.loads(p.read_text(encoding="utf-8"))

def load(root,phase):
    plan=read(root/"plan.json")
    if not isinstance(plan,list):raise ValueError("Expected list plan")
    def key(q):
        return (q["family"],q["language"],q["term"],q["country"],int(q["limit"]))
    logs={}
    for p in sorted(root.glob("*.log.json")):
        log=read(p);k=key(log["query"])
        if k in logs:raise ValueError("Duplicate query log")
        logs[k]=(p,log)
    if len({key(q) for q in plan})!=len(plan):raise ValueError("Duplicate planned query")
    if set(logs)-{key(q) for q in plan}:raise ValueError("Unplanned log")
    rows=[]
    for order,q in enumerate(plan,1):
        k=key(q)
        base={"phase":phase,"order":order,**q,"status":"unattempted","ids":set(),"observations":0,"missing_id":0}
        if k not in logs:rows.append(base);continue
        path,log=logs[k];base.update(status=log["status"],time_utc=log.get("time_utc"),attempts=log.get("attempts"))
        if log["status"]!="ok":rows.append(base);continue
        prefix=path.name.removesuffix(".log.json")
        raw=path.with_name(prefix+".raw.json");facts=path.with_name(prefix+".facts.json")
        if raw.exists() and hashlib.sha256(raw.read_bytes()).hexdigest()==log.get("sha256"):
            data=json.loads(raw.read_bytes())["results"];base["payload"]="raw"
        elif facts.exists() and hashlib.sha256(facts.read_bytes()).hexdigest()==log.get("facts_sha256"):
            data=read(facts);base["payload"]="facts"
        else:raise ValueError(f"Unverified response {path}")
        if not isinstance(data,list) or (log.get("returned") is not None and log["returned"]!=len(data)):raise ValueError("Invalid response count")
        base.update(ids={str(x["trackId"]) for x in data if x.get("trackId") is not None},observations=len(data),missing_id=sum(x.get("trackId") is None for x in data))
        rows.append(base)
    return rows

def metrics(rows):
    ok=[r for r in rows if r["status"]=="ok"]
    frequencies=collections.Counter(i for r in ok for i in r["ids"])
    seen=set();out=[]
    for r in rows:
        ids=r["ids"];new=ids-seen;seen.update(ids)
        out.append({k:v for k,v in r.items() if k!="ids"}|{"unique_ids":len(ids),"new_vs_preceding_queries":len(new),"exclusive_ids_all_observed_queries":sum(frequencies[i]==1 for i in ids),"cumulative_ids":len(seen),"capped":r["status"]=="ok" and r["observations"]>=r["limit"]})
    return out

def groups(rows,fields):
    sets=collections.defaultdict(set);counts=collections.Counter();planned=collections.Counter();raw=collections.Counter();caps=collections.Counter()
    for r in rows:
        k=tuple(r[f] for f in fields);planned[k]+=1
        if r["status"]!="ok":continue
        counts[k]+=1;sets[k].update(r["ids"]);raw[k]+=r["observations"];caps[k]+=int(r["observations"]>=r["limit"])
    freq=collections.Counter(i for v in sets.values() for i in v)
    return [dict(zip(fields,k))|{"planned":planned[k],"successful":counts[k],"observations":raw[k],"unique_ids":len(sets[k]),"exclusive_ids_among_groups":sum(freq[i]==1 for i in sets[k]),"capped":caps[k]} for k in sorted(planned)]

def overlaps(rows):
    # Comparisons within same phase/limit only; no equivalence assumed between 50 and 200.
    ok=[r for r in rows if r["status"]=="ok"]
    result=[]
    for a,b in itertools.combinations(ok,2):
        if a["phase"]!=b["phase"] or a["limit"]!=b["limit"]:continue
        union=a["ids"]|b["ids"];intersection=a["ids"]&b["ids"]
        if not union:continue
        result.append({"phase":a["phase"],"query_a":a["order"],"query_b":b["order"],"term_a":a["term"],"term_b":b["term"],"market_a":a["country"],"market_b":b["country"],"intersection":len(intersection),"union":len(union),"jaccard":len(intersection)/len(union)})
    return sorted(result,key=lambda r:(-r["jaccard"],-r["intersection"],r["phase"],r["query_a"],r["query_b"]))

def write_csv(path,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument("--baseline",type=pathlib.Path,required=True);p.add_argument("--expansion",type=pathlib.Path);p.add_argument("--output",type=pathlib.Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    rows=load(a.baseline,"baseline")
    if a.expansion:rows+=load(a.expansion,"expansion")
    m=metrics(rows);pairs=overlaps(rows)
    ids=lambda rs:set().union(*(r["ids"] for r in rs))
    baseline=ids([r for r in rows if r["phase"]=="baseline"]);extra=ids([r for r in rows if r["phase"]=="expansion"])
    report={"status_counts":dict(collections.Counter(r["status"] for r in rows)),"observations":sum(r["observations"] for r in rows),"unique_ids":len(ids(rows)),"baseline_ids":len(baseline),"expansion_included":bool(a.expansion),"expansion_ids":len(extra) if a.expansion else None,"expansion_additional_ids":len(extra-baseline) if a.expansion else None,"capped_queries":sum(r["capped"] for r in m),"queries_with_zero_new_in_order":sum(r["status"]=="ok" and r["new_vs_preceding_queries"]==0 for r in m),"queries_with_zero_exclusive":sum(r["status"]=="ok" and r["exclusive_ids_all_observed_queries"]==0 for r in m),"pair_count":len(pairs),"nonempty_overlap_pairs":sum(r["intersection"]>0 for r in pairs),"top_overlaps":pairs[:10],"by_family":groups(rows,("phase","family")),"by_market_language":groups(rows,("phase","country","language")),"limitations":["Cumulative marginal gain depends on planned order; exclusive contribution is order-independent on observed successful queries only.","Search terms at limit 50 do not prove absence beyond result cap; no dropping terms based solely on overlap.","Initial pilot confounds market and language; descriptive comparison only.","Identifiers are not relevance or confirmed new products. No elapsed-time claim; fetch latency was not separately measured.","Facts payload hash can be verified, but discarded raw response cannot be independently reconstructed."]}
    write_csv(a.output/"query_metrics.csv",m);write_csv(a.output/"pairwise_jaccard.csv",pairs)
    (a.output/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
