"""P2-08: prospective validation statistics; no real judgments bundled.
All counts are descriptive unless the approved sampling design supports inference.
"""
import collections,math
def require(ok,msg):
    if not ok:raise ValueError(msg)
def ratio(n,d):return n/d if d else None
def srs_size(population,half_width,z=1.959963984540054,p=.5):
    require(type(population) is int and population>0 and 0<half_width<1 and 0<p<1 and z>0,"Invalid design")
    n0=z*z*p*(1-p)/(half_width**2)
    return min(population,math.ceil(population*n0/(population-1+n0)))
def agreement(a,b,expected_ids):
    """Exact nominal agreement; uncertain is a legitimate code, blank is missing."""
    ids=set(expected_ids)
    require(set(a)<=ids and set(b)<=ids,"Unexpected review ID")
    require(all(isinstance(v,str) for v in list(a.values())+list(b.values())),"Codes must be strings")
    pairs=[(a.get(k,"").strip(),b.get(k,"").strip()) for k in sorted(ids)]
    complete=[(x,y) for x,y in pairs if x and y]
    n=len(complete);m=collections.Counter(complete);ca=collections.Counter(x for x,y in complete);cb=collections.Counter(y for x,y in complete)
    po=ratio(sum(x==y for x,y in complete),n)
    pe=sum(ca[k]*cb[k] for k in set(ca)|set(cb))/n**2 if n else None
    kappa=(po-pe)/(1-pe) if n and pe<1 else None
    return {"expected":len(ids),"paired_complete":n,"missing_pair":len(ids)-n,"uncertain_a":ca["UNCERTAIN"],"uncertain_b":cb["UNCERTAIN"],"agreement":po,"kappa":kappa,"confusion":[{"a":x,"b":y,"n":v} for (x,y),v in sorted(m.items())]}
def candidate_yield(outcomes,expected_ids):
    """Adjudicated candidate same-unit yield, not classifier accuracy.
    Missing and UNCERTAIN stay unresolved, with worst-case bounds.
    """
    ids=set(expected_ids);require(set(outcomes)<=ids,"Unexpected candidate ID")
    require(all(v in {"SAME_UNIT","DISTINCT_UNIT","UNCERTAIN"} for v in outcomes.values()),"Invalid adjudicated label")
    c=collections.Counter(outcomes.values());yes=c["SAME_UNIT"];no=c["DISTINCT_UNIT"];unresolved=len(ids)-yes-no
    return {"sampled":len(ids),"same_unit":yes,"distinct_unit":no,"unresolved":unresolved,"resolved_only_yield":ratio(yes,yes+no),"lower_bound_all_sampled":ratio(yes,len(ids)),"upper_bound_all_sampled":ratio(yes+unresolved,len(ids))}
def pair(a,b):
    require(isinstance(a,str) and isinstance(b,str) and a and b and a!=b,"Invalid pair")
    return tuple(sorted((a,b)))
def reference_capture(reference,generated,anchors):
    """Recall conditional on independent, adjudicated links actually discovered.
    Never treats undiscovered links as true negatives or complete truth.
    reference: mapping anchor -> distinct known same-unit counterpart IDs;
    anchors: all prespecified anchor IDs, even if no link found.
    """
    require(set(reference)<=set(anchors),"Unexpected anchor")
    cand={pair(*p) for p in generated}
    refs=set();per=[]
    for a in sorted(set(anchors)):
        ps={pair(a,b) for b in reference.get(a,[])}
        refs.update(ps);hit=len(ps&cand)
        per.append({"anchor":a,"reference_links":len(ps),"captured":hit,"missed":len(ps)-hit,"capture":ratio(hit,len(ps))})
    eligible=[r["capture"] for r in per if r["capture"] is not None]
    hit=len(refs&cand)
    return {"anchors":len(per),"anchors_with_reference_links":len(eligible),"anchors_without_discovered_links":len(per)-len(eligible),"unique_reference_links":len(refs),"captured":hit,"missed":len(refs)-hit,"reference_conditional_micro_capture":ratio(hit,len(refs)),"reference_conditional_macro_capture":ratio(sum(eligible),len(eligible)),"per_anchor":per}
def acceptance_metrics(reference,accepted,expected_pairs):
    """Optional future fusion decision evaluation on fixed adjudicated pair frame.
    Unresolved labels are excluded, and explicitly counted.
    """
    universe={pair(*p) for p in expected_pairs};positive={pair(*p) for p in accepted}
    require(positive<=universe,"Unexpected predicted pair")
    refs={}
    for p,v in reference.items():
        key=pair(*p);require(key in universe and key not in refs and v in {"SAME_UNIT","DISTINCT_UNIT","UNCERTAIN"},"Invalid reference")
        refs[key]=v
    counts=collections.Counter()
    for p in universe:
        v=refs.get(p,"UNCERTAIN")
        if v=="UNCERTAIN":counts["unresolved"]+=1;continue
        counts[("TP" if p in positive else "FN") if v=="SAME_UNIT" else ("FP" if p in positive else "TN")]+=1
    return {**{k:counts[k] for k in ("TP","FP","FN","TN","unresolved")},"precision_resolved":ratio(counts["TP"],counts["TP"]+counts["FP"]),"recall_resolved":ratio(counts["TP"],counts["TP"]+counts["FN"])}
