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
    return _resource_reason(t,c)

def _resource_reason(t,c):
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
    return _solve(context,candidates,max_combinations=max_combinations,reason_fn=_reason,
                  pair_fn=None,mode="TEST_FIXTURE_ONLY",complete_status="COMPLETE_FIXTURE_SET")

def _solve(context,candidates,*,max_combinations,reason_fn,pair_fn,mode,complete_status):
    req,opt=_context(context)
    if not _natural(max_combinations) or max_combinations==0:
        raise ValueError("Invalid search bound")
    if not isinstance(candidates,list) or any(not isinstance(t,dict) or not isinstance(t.get("id"),str) or not t["id"] for t in candidates):
        raise ValueError("Invalid candidates")
    if len({t["id"] for t in candidates})!=len(candidates):
        raise ValueError("Duplicate candidate IDs")
    out={"mode":mode,"status":"NO_COMPLETE_SET","selected":None,"best_individual":None,"simple_pair":None,"excluded":{},"combination_rejections":{},"evaluated":0,"uncovered_required":sorted(req)}
    if context["unsupported_requirements"]:
        out["status"]="UNSUPPORTED_REQUIREMENT"
        return out
    pool=[]
    for t in sorted(candidates,key=lambda t:t["id"]):
        reason=reason_fn(t,context)
        if reason: out["excluded"][t["id"]]=reason
        else: pool.append(t)
    best=None
    partial=None
    for n in range(1,len(pool)+1):
        for items in combinations(pool,n):
            if out["evaluated"]>=max_combinations:
                out["status"]="INCOMPLETE_SEARCH"
                # A prefix of the search cannot establish an optimum or definitive coverage.
                for key in ("selected", "best_individual", "simple_pair", "uncovered_required"):
                    out[key]=None
                return out
            out["evaluated"]+=1
            reason=_combination(items,context)
            if reason is None and pair_fn is not None:
                reason=pair_fn(items)
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
        out["status"]=complete_status
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

def inspect_documentary_register(db_path, context):
    """Read current A3 observations, validate their exact local lineage, and abstain.
    
    No documentary record can be converted to a solver fixture or a real
    candidate. No inference of F01–F15, hard constraints or independent review.
    """
    from .experimental_registry import read_preview
    from .experimental_qualification import canonical, validate, CONSTRAINTS
    import hashlib
    req, opt = _context(context)
    leads = read_preview(db_path, include_provenance=True)["leads"]
    result = inspect_real_proposals(leads)
    result.update({"required":sorted(req), "optional":sorted(opt),
                   "uncovered_required":sorted(req), "coverage_assessed":False,
                   "unsupported_requirements":list(context["unsupported_requirements"]),
                   "diagnostics":[]})
    for lead in leads:
        source, native = lead["id"].split(":",1)
        row = dict(source=source,id=native,name=lead["name"],category=lead["category"],
                   kind=lead["kind"],url=lead["url"],date=lead["date"])
        digest = hashlib.sha256(canonical(row).encode("utf-8")).hexdigest()
        obs = lead["source_observation"]
        valid_source = (obs["sha256"] == digest and obs["locator"] == row["url"]
                        and obs["id"] == "obs:"+lead["id"]+":"+row["date"]+":"+digest)
        proposal = lead.get("qualification_proposal")
        qobs = lead.get("qualification_observation")
        status = "SOURCE_LINEAGE_MISMATCH" if not valid_source else "NO_CURRENT_PROPOSAL"
        linked = False
        if valid_source and proposal is not None:
            try:
                validated = validate({"schema_version":2,"records":[proposal]},
                                     {"records":[row]})[0]
                linked = (qobs == {"id":validated[0],"sha256":validated[4]})
            except (ValueError, KeyError, TypeError):
                linked = False
            status = "DOCUMENTARY_PROPOSAL_ONLY" if linked else "PROPOSAL_LINEAGE_MISMATCH"
        result["diagnostics"].append({
            "id":lead["id"], "source_observation":obs,
            "qualification_observation":qobs if linked else None,
            "status":status, "documented_function":proposal["documented_function"] if linked else None,
            "proposed_role":proposal["proposed_role"] if linked else None,
            "review_status":"NOT_ASSESSED" if linked else "UNKNOWN",
            "identity_status":"UNRESOLVED" if linked else "UNKNOWN",
            "constraints":dict.fromkeys(CONSTRAINTS,"UNKNOWN"),
            "function_ids":None, "admissible":False,
            "reasons":[status,"INDEPENDENT_REVIEW_REQUIRED","CONTEXT_EVIDENCE_REQUIRED",
                       "FUNCTION_MAPPING_NOT_VALIDATED","IDENTITY_NOT_RESOLVED"]})
    result["linked_proposals"] = sum(d["status"]=="DOCUMENTARY_PROPOSAL_ONLY" for d in result["diagnostics"])
    return result

def compare_historical_native(context_text, *, catalogue_path, expected_sha256, limit=5):
    """Call the actual legacy ranking with neutral votes on exact snapshot bytes.
    
    Native scores/keywords are descriptive, not comparable coverage or evidence.
    No conversion of historic ranks to admissible tools; no claim of superiority.
    """
    import hashlib
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from .real_catalog import recommend
    if not isinstance(context_text,str) or not context_text.strip():
        raise ValueError("Context text required")
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError("Limit must be 1..50")
    raw = Path(catalogue_path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError("Historical catalogue snapshot hash mismatch")
    with TemporaryDirectory() as tmp:
        frozen = Path(tmp)/"catalogue.json"
        frozen.write_bytes(raw)
        native = recommend(context_text, votes={}, path=frozen)
    matches = native["matches"]
    return {"mode":"HISTORICAL_NATIVE_DESCRIPTIVE_ONLY","catalogue_sha256":digest,
            "context_text":context_text,"votes":"NEUTRAL","method":native["method"],
            "ranking_validated":native["ranking_validated"],"matched_count":len(matches),
            "limit":limit,"context_flags":native["context_flags"],
            "results":[{"rank":i,"id":t["id"],"fit":t["fit"],
                        "matched_terms":t["matched_terms"],"verified_features":t["verified"]}
                       for i,t in enumerate(matches[:limit],1)],
            "common_pool_comparison":False,"coverage":None,"cost_mad":None,
            "constraint_violations":None,"load":None,
            "limitation":"NO_VALIDATED_COMMON_FUNCTION_MAPPING_OR_CONTEXT_EVIDENCE"}
