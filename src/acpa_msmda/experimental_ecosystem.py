"""A4 isolated decision prototype. Fictional test fixtures only.
No real operational recommendation or scientific score is produced.
"""
from itertools import combinations

FUNCTIONS=frozenset(f"F{i:02}" for i in range(1,16))
GATES=("connectivity","equipment","age_privacy","accessibility","physical_safety","morocco_availability","identity","source_current","transfer")
def _natural(x):
    return type(x) is int and x>=0
def _functions(x):
    if not isinstance(x,(list,tuple,set,frozenset)) or not all(isinstance(v,str) and v in FUNCTIONS for v in x):
        raise ValueError("Invalid function IDs")
    return set(x)
def _ids(x):
    if not isinstance(x,(list,tuple)) or not all(isinstance(v,str) and v for v in x):
        raise ValueError("Invalid IDs")
    return set(x)
def _context(c):
    if not isinstance(c,dict) or set(c)!={"required","optional","budget_mad","period","devices","offline","unsupported_requirements"}:
        raise ValueError("Invalid context")
    req,opt=_functions(c["required"]),_functions(c["optional"])
    if not req or req&opt or not _natural(c["budget_mad"]) or not _natural(c["devices"]) or type(c["offline"]) is not bool or not isinstance(c["period"],str) or not c["period"]:
        raise ValueError("Invalid context values")
    if not isinstance(c["unsupported_requirements"],list):
        raise ValueError("Invalid unsupported requirements")
    return req,opt
def _reason(t,c):
    if t.get("mode")!="TEST_FIXTURE" or t.get("review")!="FIXTURE_APPROVED":
        return "UNASSESSED_REAL_OR_UNAPPROVED"
    if not isinstance(t.get("product"),str) or not t["product"]:
        return "IDENTITY_UNKNOWN"
    gates=t.get("gates")
    if not isinstance(gates,dict) or set(gates)!=set(GATES) or any(gates[k]!="COMPATIBLE" for k in GATES):
        return "CRITICAL_CONSTRAINT_NOT_ESTABLISHED"
    if c["offline"] and t.get("offline") is not True:
        return "OFFLINE_NOT_ESTABLISHED"
    if not _natural(t.get("cost")) or t.get("period")!=c["period"] or t.get("currency")!="MAD":
        return "COST_NOT_COMPARABLE"
    if t["cost"]>c["budget_mad"]:
        return "INDIVIDUAL_BUDGET"
    if not _natural(t.get("load")) or not isinstance(t.get("device_slots"),dict) or not t["device_slots"] or not all(isinstance(k,str) and k in {"before","during","after"} and _natural(v) for k,v in t["device_slots"].items()):
        return "RESOURCE_UNKNOWN"
    if any(v>c["devices"] for v in t["device_slots"].values()):
        return "INDIVIDUAL_DEVICE_LIMIT"
    try:
        if not _functions(t.get("functions")):
            return "NO_FUNCTION"
        _ids(t.get("requires")); _ids(t.get("incompatible"))
    except ValueError:
        return "INVALID_FUNCTION_OR_RELATION"
    return None
def _combination(items,c):
    keys={t["id"] for t in items}
    if len({t["product"] for t in items})!=len(items):
        return "DUPLICATE_PRODUCT"
    if any(not _ids(t["requires"])<=keys for t in items):
        return "MISSING_DEPENDENCY"
    if any(_ids(t["incompatible"]) & (keys-{t["id"]}) for t in items):
        return "INCOMPATIBLE_PAIR"
    if sum(t["cost"] for t in items)>c["budget_mad"]:
        return "TOTAL_BUDGET"
    if any(sum(t["device_slots"].get(slot,0) for t in items)>c["devices"] for slot in ("before","during","after")):
        return "SIMULTANEOUS_DEVICE_LIMIT"
    return None
def _result(items,req,opt):
    covered=set().union(*(_functions(t["functions"]) for t in items))
    return {"ids":[t["id"] for t in items],"covered_required":sorted(req&covered),"covered_optional":sorted(opt&covered),
            "uncovered_required":sorted(req-covered),"cost_mad":sum(t["cost"] for t in items),"load":sum(t["load"] for t in items),
            "roles":{t["id"]:sorted(_functions(t["functions"])&(req|opt)) for t in items}}
def solve_fixture(context,candidates,*,max_combinations=10000):
    """Enumerate bounded feasible sets; minimize count, load, cost, then IDs.
    All returned combinations are synthetic, never a real recommendation.
    """
    req,opt=_context(context)
    if not _natural(max_combinations) or max_combinations==0:
        raise ValueError("Invalid search bound")
    if not isinstance(candidates,list) or any(not isinstance(t,dict) or not isinstance(t.get("id"),str) or not t["id"] for t in candidates):
        raise ValueError("Invalid candidates")
    if len({t["id"] for t in candidates})!=len(candidates):
        raise ValueError("Duplicate candidate IDs")
    out={"mode":"TEST_FIXTURE_ONLY","status":"NO_COMPLETE_SET","selected":None,"best_individual":None,"simple_pair":None,"excluded":{},"combination_rejections":{},"evaluated":0,"uncovered_required":sorted(req)}
    if context["unsupported_requirements"]:
        out["status"]="UNSUPPORTED_REQUIREMENT"
        return out
    pool=[]
    for t in sorted(candidates,key=lambda t:t["id"]):
        reason=_reason(t,context)
        if reason: out["excluded"][t["id"]]=reason
        else: pool.append(t)
    best=None
    partial=None
    for n in range(1,len(pool)+1):
        for items in combinations(pool,n):
            if out["evaluated"]>=max_combinations:
                out["status"]="INCOMPLETE_SEARCH"
                out["selected"]=None
                return out
            out["evaluated"]+=1
            reason=_combination(items,context)
            if reason:
                counts=out["combination_rejections"]
                counts[reason]=counts.get(reason,0)+1
                continue
            r=_result(items,req,opt)
            rank=(-len(r["covered_required"]),n,r["load"],r["cost_mad"],tuple(r["ids"]))
            if partial is None or rank<partial[0]: partial=(rank,r)
            if n==1 and (out["best_individual"] is None or rank<out["best_individual"][0]): out["best_individual"]=(rank,r)
            if n<=2 and (out["simple_pair"] is None or rank<out["simple_pair"][0]): out["simple_pair"]=(rank,r)
            if not r["uncovered_required"] and (best is None or rank<best[0]): best=(rank,r)
    for key in ("best_individual","simple_pair"):
        if out[key] is not None: out[key]=out[key][1]
    if best:
        out["status"]="COMPLETE_FIXTURE_SET"
        out["selected"]=best[1]
        out["uncovered_required"]=[]
    elif partial:
        out["uncovered_required"]=partial[1]["uncovered_required"]
        out["best_partial"]=partial[1]
    return out
def inspect_real_proposals(leads):
    """No promotion pathway exists in this prototype."""
    return {"mode":"REAL_DOCUMENTARY_ONLY","status":"NO_OPERATIONAL_RECOMMENDATION",
            "records":len(leads),"admitted":0,"recommended":[],
            "reason":"INDEPENDENT_REVIEW_AND_CONTEXT_EVIDENCE_REQUIRED"}
