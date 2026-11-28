"""SILL v2 public export pilot. No automatic identity or eligibility decisions."""
import argparse, collections, csv, datetime, hashlib, json, pathlib, re, unicodedata, urllib.request

URL = "https://code.gouv.fr/sill/api/v2/catalogi.json"
LICENSE = "Licence Ouverte 2.0"
MAX_BYTES = 30 * 1024 * 1024
CATALOG_BLOB = "39b32ebbdf33b49a3fb0bb669f8a0809d0e72995"

def names(value):
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, dict):
        return [v for k,v in value.items() if k in ("fr","en") and isinstance(v,str) and v.strip()]
    if isinstance(value,list):
        return [v for v in value if isinstance(v,str) and v.strip()]
    return []

def norm(value):
    return " ".join(re.findall(r"[^\W_]+",unicodedata.normalize("NFKC",value).casefold()))

def catalog_rows(obj):
    if isinstance(obj,list):
        rows=obj
    elif isinstance(obj,dict):
        candidates=[v for v in obj.values() if isinstance(v,list) and len(v)==2466 and all(isinstance(x,dict) and "name" in x for x in v)]
        if len(candidates)!=1:
            raise ValueError("Cannot unambiguously locate reference catalogue list")
        rows=candidates[0]
    else:
        raise ValueError("Unexpected catalogue type")
    if len(rows)!=2466 or any(not isinstance(r,dict) or not names(r.get("name")) or not isinstance(r.get("id"),(str,int)) for r in rows):
        raise ValueError("Unexpected reference catalogue rows or count")
    if len({str(r["id"]) for r in rows})!=len(rows):
        raise ValueError("Duplicate catalogue IDs")
    return rows

def compare(rows, catalog):
    if not isinstance(rows,list) or not rows:
        raise ValueError("SILL v2 must be a nonempty array")
    if any(not isinstance(r,dict) or type(r.get("id")) is not int or not names(r.get("name")) or not isinstance(r.get("license"),str) for r in rows):
        raise ValueError("SILL v2 required fields missing")
    if len({r["id"] for r in rows})!=len(rows):
        raise ValueError("Duplicate SILL IDs")
    index=collections.defaultdict(set)
    for item in catalog:
        for n in names(item["name"])+names(item.get("aliases")):
            if norm(n): index[norm(n)].add(str(item["id"]))
    result=[]
    for r in rows:
        labels=sorted(set(names(r["name"])))
        probes={norm(n) for n in labels if norm(n)}
        exact=set().union(*(index.get(n,set()) for n in probes))
        partial=set().union(*(ids for key,ids in index.items() if key not in probes and any(" "+n+" " in " "+key+" " or " "+key+" " in " "+n+" " for n in probes))) if probes else set()
        state="NAME_CANDIDATE_REVIEW" if exact else "AMBIGUOUS_NAME_REVIEW" if partial else "NO_NAME_MATCH"
        result.append({"sill_id":r["id"],"names":labels,"active":r.get("dereferencing") is None,"software_license":r["license"],
                       "runtime_platforms":r.get("runtimePlatforms",[]),"categories":r.get("applicationCategories",[]),
                       "exact_catalog_ids":sorted(exact),"partial_match_count":len(partial-exact),"comparison_status":state,"eligibility":"NOT_ASSESSED"})
    return result

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write_json(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--catalog",type=pathlib.Path,required=True)
    a.add_argument("--output",type=pathlib.Path,required=True)
    x=a.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    log={"source":"DINUM SILL","url":URL,"license":LICENSE,"started_utc":utc(),"status":"started","raw_retention":"hash only; raw export not redistributed pending field review"}
    try:
        c=x.catalog.read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(c)).encode()+b"\x00"+c).hexdigest()
        log["catalog_blob"]=blob
        if blob!=CATALOG_BLOB: raise ValueError("Reference catalogue blob differs from frozen baseline")
        catalog=catalog_rows(json.loads(c))
        req=urllib.request.Request(URL,headers={"User-Agent":"ACPA-MSMDA research pilot/0.1","Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=45) as response:
            log.update(http_status=response.status,final_url=response.geturl(),content_type=response.headers.get("Content-Type"),etag=response.headers.get("ETag"),last_modified=response.headers.get("Last-Modified"))
            raw=response.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES: raise ValueError("Export exceeds safety bound")
        log.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        rows=json.loads(raw)
        if isinstance(rows,list):
            log["row_count"]=len(rows)
            log["top_level_field_presence"]=dict(sorted(collections.Counter(k for r in rows if isinstance(r,dict) for k in r).items()))
        result=compare(rows,catalog)
        active=[r for r in result if r["active"]]
        log.update(status="ok",catalog_size=len(catalog),active=len(active),dereferenced=len(result)-len(active),comparison_all=dict(collections.Counter(r["comparison_status"] for r in result)),comparison_active=dict(collections.Counter(r["comparison_status"] for r in active)),note="Nominal candidates only; no confirmed new products or eligibility. Nested related software excluded from catalogue entry counts.")
        write_json(x.output/"sill_product_inventory.json",result)
    except Exception as e:
        log.update(status="error",error_type=type(e).__name__,error=str(e)[:300])
        raise
    finally:
        log["finished_utc"]=utc()
        write_json(x.output/"manifest.json",log)
        print(json.dumps(log,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
