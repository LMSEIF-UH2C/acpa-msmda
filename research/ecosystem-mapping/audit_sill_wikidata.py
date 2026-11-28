"""Independent implementation of archival checks. No requests to original sources."""
import argparse,base64,collections,hashlib,json,pathlib,re,unicodedata,zipfile
P=pathlib.Path(__file__).resolve().parent
DIGESTS={"sill":"8bb73ecd9d326547bd93a1db570ab37501a5fec25cba61cc10005ba610f7bc27","wikidata":"e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46","failure":"fae8f68b11fadc359838894220d03ab743a75217470d247f7ad086673f4500c9"}
def require(ok,msg):
    if not ok: raise ValueError(msg)
def sha(b): return hashlib.sha256(b).hexdigest()
def verify_zip(path,expected):
    b=path.read_bytes();require(sha(b)==expected,"ZIP digest mismatch")
    z=zipfile.ZipFile(path)
    require(z.testzip() is None,"CRC error")
    require(len(z.namelist())==len(set(z.namelist())),"Duplicate archive path")
    return z
def read(z,n):return json.loads(z.read(n))
def normalized(s):
    return " ".join(re.findall(r"[^\W_]+",unicodedata.normalize("NFKC",s).casefold()))
def label_values(v):
    if isinstance(v,str):return [v]
    if isinstance(v,list):return [s for s in v if isinstance(s,str)]
    if isinstance(v,dict):return [s for k,s in v.items() if k in ("en","fr") and isinstance(s,str)]
    return []
def make_index(rows,idkey,namekey,aliases=False):
    idx=collections.defaultdict(set)
    for r in rows:
        for name in label_values(r[namekey])+(label_values(r.get("aliases")) if aliases else []):
            k=normalized(name)
            if k:idx[k].add(str(r[idkey]))
    return idx
def matches(labels,idx):
    return set().union(*(idx.get(normalized(v),set()) for v in labels))
def audit(sill,wd,fail,catalog,witnesses):
    require(set(sill.namelist())=={"manifest.json","sill_product_inventory.json"},"SILL files unexpected")
    require(set(fail.namelist())=={"manifest.json"},"Failure files unexpected")
    sf=read(fail,"manifest.json");require(sf["status"]=="error" and "500" in sf["error"],"Failure mismatch")
    sm=read(sill,"manifest.json");si=read(sill,"sill_product_inventory.json")
    require(sm["status"]=="ok" and sm["row_count"]==len(si)==len({r["sill_id"] for r in si})==672,"SILL IDs")
    allowed={"sill_id","names","active","software_license","runtime_platforms","categories","exact_catalog_ids","partial_match_count","comparison_status","eligibility"}
    require(all(set(r)==allowed and r["eligibility"]=="NOT_ASSESSED" and type(r["active"]) is bool and all(isinstance(s,str) for s in r["names"]+r["runtime_platforms"]+r["categories"]) for r in si),"SILL projection scope")
    ci=make_index(catalog,"id","name",True);sx=make_index(si,"sill_id","names")
    status=collections.Counter();active=collections.Counter()
    for r in si:
        labels={normalized(s) for s in r["names"] if normalized(s)}
        exact=matches(labels,ci)
        partial=set()
        for key,ids in ci.items():
            if key in labels:continue
            for n in labels:
                if " "+n+" " in " "+key+" " or " "+key+" " in " "+n+" ":partial.update(ids)
        state="NAME_CANDIDATE_REVIEW" if exact else "AMBIGUOUS_NAME_REVIEW" if partial else "NO_NAME_MATCH"
        require(exact==set(r["exact_catalog_ids"]) and len(partial-exact)==r["partial_match_count"] and state==r["comparison_status"],"SILL nominal mismatch")
        status[state]+=1
        if r["active"]:active[state]+=1
    require(dict(status)==sm["comparison_all"] and dict(active)==sm["comparison_active"] and sum(active.values())==sm["active"]==615,"SILL aggregates")
    wm=read(wd,"manifest.json");wi=read(wd,"inventory.json")
    plan=json.loads((P/"WIKIDATA_PLAN_V01.json").read_text())
    logs=wm["by_query"]
    require(len(logs)==len(plan)==10 and all(l["status"]=="ok" for l in logs),"WD query count/status")
    require(set(wd.namelist())=={"manifest.json","inventory.json"}|{e["family"]+suffix for e in plan for suffix in (".rq",".raw.json")},"WD files unexpected")
    found={};observations=0;caps=0
    for entry,l in zip(plan,logs):
        require(all(l[k]==v for k,v in entry.items()),"WD plan mismatch")
        f=entry["family"];query=wd.read(f+".rq").decode();require("wdt:P31 wd:"+entry["qid"] in query and "LIMIT 101" in query,"WD query mismatch")
        raw=wd.read(f+".raw.json");require(sha(raw)==l["sha256"] and len(raw)==l["bytes"],"WD payload hash/size")
        obj=json.loads(raw);require(set(obj["head"]["vars"])=={"item","en","fr","ar"},"WD field scope")
        ids=set()
        for b in obj["results"]["bindings"]:
            require(set(b)<= {"item","en","fr","ar"},"Unexpected WD fields")
            match=re.fullmatch(r"https?://www.wikidata.org/entity/(Q[1-9][0-9]*)",b["item"]["value"])
            require(match is not None and b["item"]["type"]=="uri","Invalid QID")
            q=match.group(1);ids.add(q)
            rec=found.setdefault(q,{"labels":{},"families":set()});rec["families"].add(f)
            for lang in ("en","fr","ar"):
                if lang in b:
                    label=b[lang]["value"]
                    require(b[lang].get("xml:lang")==lang and isinstance(label,str),"Invalid WD label")
                    require(rec["labels"].get(lang,label)==label,"Conflicting label")
                    rec["labels"][lang]=label
        require(len(ids)==l["unique_qids"]<=101 and l["cap_reached"]==(len(ids)==101),"WD counts")
        observations+=len(ids);caps+=len(ids)==101
    require(len(wi)==len({r["qid"] for r in wi})==len(found)==wm["distinct_qids"]==547,"WD union")
    overlap=collections.Counter();labels=collections.Counter()
    wix=collections.defaultdict(set)
    for r in wi:
        require(set(r)=={"qid","labels","families","catalog_name_candidates","sill_name_candidates","eligibility"} and r["eligibility"]=="NOT_ASSESSED","WD projection scope")
        q=r["qid"];v=found[q]
        require(r["labels"]==v["labels"] and set(r["families"])==v["families"],"WD inventory mismatch")
        c=matches(v["labels"].values(),ci);s=matches(v["labels"].values(),sx)
        require(c==set(r["catalog_name_candidates"]) and s==set(r["sill_name_candidates"]),"WD matching mismatch")
        overlap[(bool(c),bool(s))]+=1;labels.update(v["labels"].keys())
        for n in v["labels"].values():wix[normalized(n)].add(q)
    require(observations==wm["observations"]==549 and caps==wm["capped_queries"]==2,"WD totals")
    require(dict(labels)==wm["label_coverage"] and sum(n for (c,s),n in overlap.items() if c)==wm["with_catalog_name_candidates"] and sum(n for (c,s),n in overlap.items() if s)==wm["with_sill_name_candidates"] and overlap[(True,True)]==wm["with_both"],"WD aggregates")
    witness=[]
    for w in witnesses:
        a=w["alias_probes"]
        witness.append({"id":w["id"],"name":w["name"],"catalog_ids":sorted(matches(a,ci)),"sill_ids":sorted(matches(a,sx)),"wikidata_qids":sorted(matches(a,wix))})
    return {"sill_count":len(si),"sill_active":sum(active.values()),"sill_status":dict(status),"sill_nominal_rows_checked":len(si),"wikidata_payload_hashes_checked":len(logs),"wikidata_qids":len(found),"wikidata_observations":observations,"wikidata_caps":caps,"wikidata_nominal_rows_checked":len(wi),"wikidata_labels":dict(labels),"overlap":{"catalog_only":overlap[(True,False)],"sill_only":overlap[(False,True)],"both":overlap[(True,True)],"neither":overlap[(False,False)]},"witnesses":witness,"witness_nominal_counts":{k:sum(bool(w[k]) for w in witness) for k in ("catalog_ids","sill_ids","wikidata_qids")},"failure_preserved":True,"limitations":"Independent code implementation, not independent human reviewer. SILL original HTTP body not archived; SHA of original body cannot be recalculated. Witness sample purposive, name candidates only; no recall or eligibility."}
def main():
    a=argparse.ArgumentParser()
    for n in ("sill","wikidata","failure","catalog","output"):a.add_argument("--"+n,type=pathlib.Path,required=True)
    x=a.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    b=x.catalog.read_bytes();blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
    require(blob=="39b32ebbdf33b49a3fb0bb669f8a0809d0e72995","Catalogue blob")
    obj=json.loads(b);c=obj if isinstance(obj,list) else next(v for v in obj.values() if isinstance(v,list) and len(v)==2466 and all(isinstance(i,dict) and "name" in i for i in v))
    require(len(c)==2466 and len({str(i["id"]) for i in c})==2466,"Catalogue count")
    with verify_zip(x.sill,DIGESTS["sill"]) as s,verify_zip(x.wikidata,DIGESTS["wikidata"]) as w,verify_zip(x.failure,DIGESTS["failure"]) as f:
        result=audit(s,w,f,c,json.loads((P/"PROSPECTION_WEB_BUREAU_V01.json").read_text())["records_detail"])
    result["catalog_blob"]=blob;result["zip_digests"]=DIGESTS
    (x.output/"audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("AUDIT_RESULT "+json.dumps(result,ensure_ascii=False,separators=(",",":")))
    # Emit exact already scope-checked ZIPs in small chunks for connector-based archival.
    for key in DIGESTS:
        payload=base64.b64encode(getattr(x,key).read_bytes()).decode()
        for i in range(0,len(payload),3000):
            print("ARCHIVE_B64 "+key+" "+str(i//3000)+" "+payload[i:i+3000])
if __name__=="__main__":main()
