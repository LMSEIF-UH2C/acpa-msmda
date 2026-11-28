"""Bounded WDQS pilot, direct P31 only; QIDs are observations, not verified products."""
import argparse,collections,hashlib,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from collect_sill import norm,names,catalog_rows,CATALOG_BLOB,utc,write_json
P=pathlib.Path(__file__).resolve().parent
ENDPOINT="https://query.wikidata.org/sparql"
USER_AGENT="ACPA-MSMDA-research/0.1 (https://github.com/LMSEIF-UH2C/acpa-msmda)"
MAX_BYTES=5*1024*1024
def query(qid,limit):
    if not re.fullmatch(r"Q[1-9][0-9]*",qid) or limit!=101: raise ValueError("Invalid plan")
    return f"""PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?item ?en ?fr ?ar WHERE {{
  {{ SELECT DISTINCT ?item WHERE {{ ?item wdt:P31 wd:{qid} . }} ORDER BY ?item LIMIT {limit} }}
  OPTIONAL {{ ?item rdfs:label ?en . FILTER(LANG(?en)="en") }}
  OPTIONAL {{ ?item rdfs:label ?fr . FILTER(LANG(?fr)="fr") }}
  OPTIONAL {{ ?item rdfs:label ?ar . FILTER(LANG(?ar)="ar") }}
}} ORDER BY ?item"""
def parse(raw):
    obj=json.loads(raw); rows=obj["results"]["bindings"]; out={}
    if not isinstance(rows,list): raise ValueError("Invalid bindings")
    for b in rows:
        uri=b["item"]["value"]; match=re.fullmatch(r"https?://www.wikidata.org/entity/(Q[1-9][0-9]*)",uri)
        if not match or b["item"]["type"]!="uri": raise ValueError("Unexpected item URI")
        q=match.group(1); vals=out.setdefault(q,{})
        for lang in ("en","fr","ar"):
            if lang in b:
                value=b[lang]["value"]
                if not isinstance(value,str) or b[lang].get("xml:lang")!=lang: raise ValueError("Invalid label")
                if lang in vals and vals[lang]!=value: raise ValueError("Conflicting label")
                vals[lang]=value
    if len(out)>101: raise ValueError("Unexpected limit")
    return out
def index_catalog(catalog):
    idx=collections.defaultdict(set)
    for r in catalog:
        for s in names(r["name"])+names(r.get("aliases")):
            if norm(s): idx[norm(s)].add(str(r["id"]))
    return idx
def index_sill(rows):
    if len(rows)!=672 or len({r["sill_id"] for r in rows})!=672: raise ValueError("SILL baseline mismatch")
    idx=collections.defaultdict(set)
    for r in rows:
        for s in r["names"]:
            if norm(s): idx[norm(s)].add(str(r["sill_id"]))
    return idx
def candidates(labels,idx):
    return sorted(set().union(*(idx.get(norm(s),set()) for s in labels.values() if norm(s))))
def main():
    a=argparse.ArgumentParser()
    for k in ("catalog","sill","output"): a.add_argument("--"+k,type=pathlib.Path,required=True)
    x=a.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    plan=json.loads((P/"WIKIDATA_PLAN_V01.json").read_text())
    c=x.catalog.read_bytes();blob=hashlib.sha1(b"blob "+str(len(c)).encode()+b"\x00"+c).hexdigest()
    if blob!=CATALOG_BLOB: raise ValueError("Catalogue blob mismatch")
    ci=index_catalog(catalog_rows(json.loads(c)));si=index_sill(json.loads(x.sill.read_bytes()))
    logs=[];items={};start=time.monotonic();stop=None
    for entry in plan:
        family=entry["family"]; q=query(entry["qid"],entry["limit"])
        (x.output/(family+".rq")).write_text(q,encoding="utf-8")
        log={**entry,"started_utc":utc(),"status":"not_executed"}
        if stop or time.monotonic()-start>38:
            stop=stop or "wall_budget";log["reason"]=stop;logs.append(log);continue
        try:
            url=ENDPOINT+"?"+urllib.parse.urlencode({"query":q,"format":"json"})
            req=urllib.request.Request(url,headers={"Accept":"application/sparql-results+json","User-Agent":USER_AGENT})
            with urllib.request.urlopen(req,timeout=15) as resp:
                log.update(http_status=resp.status,final_url=resp.geturl(),content_type=resp.headers.get("Content-Type"))
                raw=resp.read(MAX_BYTES+1)
            if len(raw)>MAX_BYTES: raise ValueError("Response too large")
            (x.output/(family+".raw.json")).write_bytes(raw)
            log.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            found=parse(raw); cap=len(found)==101
            # Keep all 101 observations; reaching the cap signals unknown remaining population.
            log.update(status="ok",unique_qids=len(found),cap_reached=cap)
            for qid,labels in found.items():
                item=items.setdefault(qid,{"qid":qid,"labels":{},"families":[]})
                for lang,label in labels.items():
                    if lang in item["labels"] and item["labels"][lang]!=label: raise ValueError("Cross-query label conflict")
                    item["labels"][lang]=label
                item["families"].append(family)
        except Exception as e:
            log.update(status="error",error_type=type(e).__name__,error=str(e)[:300])
            if isinstance(e,urllib.error.HTTPError): log.update(http_status=e.code,retry_after=e.headers.get("Retry-After"))
            stop="stop_after_error"
        log["finished_utc"]=utc();logs.append(log)
        if not stop: time.sleep(2)
    for item in items.values():
        item["catalog_name_candidates"]=candidates(item["labels"],ci)
        item["sill_name_candidates"]=candidates(item["labels"],si)
        item["eligibility"]="NOT_ASSESSED"
    summary={"endpoint":ENDPOINT,"license":"CC0","catalog_blob":blob,"sill_baseline_count":672,"planned":len(plan),"status_counts":dict(collections.Counter(l["status"] for l in logs)),
      "by_query":logs,"observations":sum(l.get("unique_qids",0) for l in logs if l["status"]=="ok"),"distinct_qids":len(items),"capped_queries":sum(l.get("cap_reached",False) for l in logs),
      "with_catalog_name_candidates":sum(bool(i["catalog_name_candidates"]) for i in items.values()),"with_sill_name_candidates":sum(bool(i["sill_name_candidates"]) for i in items.values()),"with_both":sum(bool(i["catalog_name_candidates"]) and bool(i["sill_name_candidates"]) for i in items.values()),
      "label_coverage":{l:sum(l in i["labels"] for i in items.values()) for l in ("en","fr","ar")},"note":"Direct P31 only; nominal matches not identity; SILL QIDs not in prior projection; no inferred source independence or eligibility."}
    write_json(x.output/"inventory.json",sorted(items.values(),key=lambda i:i["qid"]))
    write_json(x.output/"manifest.json",summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if summary["status_counts"].get("ok",0)!=len(plan): raise SystemExit(2)
if __name__=="__main__":main()
