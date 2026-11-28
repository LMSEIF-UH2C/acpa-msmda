"""Sensitivity analysis of discovery curves on observed verified searches.
No stopping decision, API access, or inference about unobserved products.
"""
import argparse
import collections
import json
import math
import pathlib
import random
import statistics
from audit_query_yield import load

def quantile(values,p):
    v=sorted(values)
    x=(len(v)-1)*p
    a,b=math.floor(x),math.ceil(x)
    return v[a]+(x-a)*(v[b]-v[a])

def summarize(values):
    return {"median":statistics.median(values),"p05":quantile(values,.05),"p95":quantile(values,.95)}

def curve(rows,draws=500,seed=20261128):
    ok=[r for r in rows if r["status"]=="ok"]
    universe=set().union(*(r["ids"] for r in ok))
    base={"planned_queries":len(rows),"successful_queries":len(ok),"observed_ids":len(universe),"capped_queries":sum(r["observations"]>=r["limit"] for r in ok),"status_counts":dict(collections.Counter(r["status"] for r in rows))}
    if not ok or not universe:
        return base|{"curve":[],"leave_one_out":[]}
    rng=random.Random(seed)
    steps=[[] for _ in ok];gains=[[] for _ in ok]
    for _ in range(draws):
        order=ok[:];rng.shuffle(order);seen=set()
        for k,r in enumerate(order):
            before=len(seen);seen.update(r["ids"])
            steps[k].append(len(seen)/len(universe))
            gains[k].append(len(seen)-before)
    frequency=collections.Counter(i for r in ok for i in r["ids"])
    omitted=[{"order":r["order"],"term":r["term"],"market":r["country"],"language":r["language"],"unique_loss":sum(frequency[i]==1 for i in r["ids"]),"loss_fraction":sum(frequency[i]==1 for i in r["ids"])/len(universe)} for r in ok]
    return base|{"curve":[{"queries":i+1,"observed_coverage":summarize(steps[i]),"marginal_ids":summarize(gains[i])} for i in range(len(ok))],"leave_one_out":omitted}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=pathlib.Path,required=True)
    p.add_argument("--expansion",type=pathlib.Path)
    p.add_argument("--output",type=pathlib.Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    rows=load(a.baseline,"baseline")
    if a.expansion:rows+=load(a.expansion,"expansion")
    grouped=collections.defaultdict(list)
    for row in rows:
        grouped[(row["phase"],"all")].append(row)
        grouped[(row["phase"],row["family"])].append(row)
    report={"draws":500,"seed":20261128,"groups":{"/".join(k):curve(v) for k,v in sorted(grouped.items())},"limitations":["Reference is the union of observed successful queries only, not the actual market or relevant-app universe.","Random permutations describe order sensitivity; quantile bands are not confidence intervals.","No automatic stopping threshold. Leave-one-out excludes exactly one observed query, not all related queries.","Small family samples and caps preclude saturation claims; language and market are confounded in initial pilot.","No inclusion decisions or API calls. Independent prospective coverage controls remain necessary."]}
    (a.output/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    for k,v in report["groups"].items():
        if k.endswith("/all") and v["curve"]:
            n=v["successful_queries"];indices=sorted({max(1,math.ceil(n*x))-1 for x in (.25,.5,.75,.9,1)})
            print(json.dumps({"group":k,"planned":v["planned_queries"],"successful":n,"observed_ids":v["observed_ids"],"capped":v["capped_queries"],"checkpoints":[v["curve"][i] for i in indices],"largest_single_query_loss":max(x["unique_loss"] for x in v["leave_one_out"])},ensure_ascii=False))
if __name__=="__main__":main()
