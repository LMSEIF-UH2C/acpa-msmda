"""Retrospective replay of fixed vs cumulative vs adaptive Apple search.
The full observed snapshot is the evaluation frame, not market coverage.
No network or product eligibility decisions.
"""
import argparse,collections,hashlib,json,pathlib,tempfile,zipfile
from audit_query_yield import load
from plan_collection_v03 import identity
from identity_registry import canon,digest
P=pathlib.Path(__file__).resolve().parent
ARCHIVES={"baseline":"7ae8e6d9b0bff727a2bfd322b30fb0f66d3aa0b8ae2ecda4cf82c764c7c50a4d","expansion":"98657812ca3201aba2a0d9ad392d828db1600bef2ab32b387565e227339ba471"}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read_archive(path,out,phase):
    need(hashlib.sha256(path.read_bytes()).hexdigest()==ARCHIVES[phase],"Archive mismatch")
    with zipfile.ZipFile(path) as z:
        need(z.testzip() is None and len(z.namelist())==len(set(z.namelist())),"ZIP integrity")
        for e in z.infolist():
            q=pathlib.PurePosixPath(e.filename)
            need(not q.is_absolute() and ".." not in q.parts and ((e.external_attr>>16)&0o170000)!=0o120000,"Unsafe archive")
        z.extractall(out)
    return load(out,phase)
def ids(rows):return set().union(*(r["ids"] for r in rows if r["status"]=="ok"))
def stratum(r):return (r["family"],r["language"],r["country"],r["limit"])
def key(r):return identity(r)
def cap(r):return r["status"]=="ok" and r["observations"]>=r["limit"]
def guards(baseline,rows):
    family=collections.Counter(r["family"] for r in baseline+rows)
    sizes=collections.Counter(stratum(r) for r in rows)
    pre_caps={stratum(r) for r in baseline if cap(r) or r["status"]!="ok" or r["missing_id"]}
    # Schedule-only protection, no future response is examined.
    protected={k for k,n in sizes.items() if family[k[0]]<12 or k[1]=="ar" or n<6 or k in pre_caps}
    ordinal=collections.Counter();holdouts=set()
    for r in rows:
        k=stratum(r);ordinal[k]+=1
        if sizes[k]>=4 and ordinal[k]%4==0:holdouts.add(key(r))
    return protected,holdouts
def simulate(baseline,rows,threshold,window,minimum=3):
    protected,holdouts=guards(baseline,rows)
    seen=ids(baseline);selected=[];skipped=[];states=collections.defaultdict(lambda:{"attempted":0,"low":0,"suspended":False,"guarded":False})
    events=collections.Counter();by=collections.defaultdict(collections.Counter);trace=[]
    # This loop does not inspect unexecuted responses before deciding.
    for r in rows:
        k=stratum(r);st=states[k];held=key(r) in holdouts
        guard=k in protected or st["guarded"]
        if st["suspended"] and not guard and not held:
            skipped.append(r);by[r["family"]]["skipped"]+=1;trace.append({"id":key(r),"action":"defer"});continue
        selected.append(r);st["attempted"]+=1;by[r["family"]]["attempted"]+=1
        new=r["ids"]-seen if r["status"]=="ok" else set()
        seen.update(new);by[r["family"]]["new_ids"]+=len(new)
        adverse=r["status"]!="ok" or cap(r) or bool(r["missing_id"])
        if adverse:
            st["guarded"]=True;st["low"]=0;st["suspended"]=False;events["adverse_guard"]+=1
        elif held:
            events["control_calls"]+=1;events["control_new_ids"]+=len(new)
            if st["suspended"] and len(new)>threshold:
                st["suspended"]=False;st["low"]=0;events["reopened_by_control"]+=1
            elif not st["suspended"]:st["low"]=0
        else:
            st["low"]=st["low"]+1 if len(new)<=threshold else 0
            if not guard and st["attempted"]>=minimum and st["low"]>=window and not st["suspended"]:
                st["suspended"]=True;events["suspensions"]+=1
        trace.append({"id":key(r),"action":"control" if held else "execute","gain":len(new),"status":r["status"],"suspended_after":st["suspended"]})
    full=ids(baseline+rows);lost=full-seen
    # Counterfactual assessment uses previously hidden responses only now.
    for r in skipped:
        by[r["family"]]["lost_ids_in_skipped_response"]+=len(r["ids"]&lost)
    lost_family={f:len(ids([r for r in skipped if r["family"]==f])&lost) for f in sorted({r["family"] for r in skipped})}
    matched=ids(baseline+rows[:len(selected)])
    return {"threshold":threshold,"window":window,"minimum_attempted_per_stratum":minimum,"new_calls":len(selected),"deferred_queries":len(skipped),"retained_observed_ids":len(seen),"lost_observed_ids":len(lost),"observed_coverage":len(seen)/len(full) if full else None,"matched_budget_fixed_prefix_ids":len(matched),"difference_vs_fixed_prefix":len(seen)-len(matched),"protected_strata":len(protected),"total_strata":len({stratum(r) for r in rows}),"scheduled_controls":len(holdouts),"events":dict(events),"skipped_capped":sum(cap(r) for r in skipped),"skipped_non_ok":sum(r["status"]!="ok" for r in skipped),"lost_ids_by_family_nonadditive":lost_family,"by_family":{f:dict(c) for f,c in sorted(by.items())},"trace_sha256":digest(trace)}
def main():
    a=argparse.ArgumentParser()
    for n in ("archives","output"):a.add_argument("--"+n,type=pathlib.Path,required=True)
    x=a.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        root=pathlib.Path(t);b=read_archive(x.archives/"baseline.zip",root/"baseline","baseline");e=read_archive(x.archives/"expansion.zip",root/"expansion","expansion")
    B,E=ids(b),ids(e);full=B|E
    need(len(b)==48 and len(e)==240 and len(B)==1435 and len(E)==2362 and len(full)==3709,"Frozen snapshot mismatch")
    need(all(r["limit"]==50 and r["status"]=="ok" for r in b+e),"Incompatible observation frame")
    need(len({key(r) for r in b+e})==288,"Physical query duplicate, plan requires explicit reconciliation")
    freq=collections.Counter(i for r in b+e for i in r["ids"])
    fams={f:ids([r for r in b+e if r["family"]==f]) for f in sorted({r["family"] for r in b+e})}
    ff=collections.Counter(i for vs in fams.values() for i in vs)
    by_family=[{"family":f,"queries":sum(r["family"]==f for r in b+e),"observed_ids":len(v),"exclusive_among_families":sum(ff[i]==1 for i in v),"capped":sum(cap(r) for r in b+e if r["family"]==f)} for f,v in fams.items()]
    result={"scope":"Apple two archived pilots, limit 50, descriptive retrospective replay; no new network","baseline_queries":len(b),"expansion_queries":len(e),"baseline_ids":len(B),"expansion_ids":len(E),"common_ids":len(B&E),"union_ids":len(full),"additional_ids":len(E-B),"observations":sum(r["observations"] for r in b+e),"capped_queries":sum(cap(r) for r in b+e),"valid_empty_queries":sum(not r["ids"] and r["observations"]==0 for r in b+e),"unique_physical_queries":len({key(r) for r in b+e}),"zero_exclusive_queries":sum(not any(freq[i]==1 for i in r["ids"]) for r in b+e),"by_family":by_family,"comparators":{"restart_fixed":{"hypothetical_new_calls":288,"observed_ids":3709},"cumulative_fixed":{"hypothetical_new_calls":240,"reused_archived_queries":48,"observed_ids":3709,"additional_ids":len(E-B),"reuse_condition":"Only if snapshot date, fields, rights and exact scope compatible; not actual saved calls or time."}},"adaptive_scenarios":[simulate(b,e,t,w) for t in (0,2,5,10,20) for w in (2,3)],"limitations":"Replay on known observations, not prospective validation. Same fixed order and frozen corpus, no relevance or rare-product truth labels, no inference beyond limit 50. Cache hypothetical, rights and temporal compatibility not established. No threshold selected. Control queries in same pilot are not independent external validation. Lost family counts may overlap. No actual latency or cost estimates."}
    (x.output/"saturation_comparison.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SATURATION_COMPARISON "+canon(result))
if __name__=="__main__":main()
