"""Targeted audit of residual recent-block pairs and catalogue field structure.
No new matching against legacy archives; no product identity decisions.
"""
import argparse,collections,itertools,json,pathlib,re
from urllib.parse import urlsplit,parse_qs
from global_identity import make_index,collect,compare,pair,namespace
from identity_graph import pilot,unzip,need
from collect_sill import names,catalog_rows
from identity_registry import canon,digest
P=pathlib.Path(__file__).resolve().parent
def walk(v,path=()):
    if isinstance(v,dict):
        for k,x in v.items():yield from walk(x,path+(k,))
    elif isinstance(v,list):
        for x in v:yield from walk(x,path+("[]",))
    else:yield path,v
def parse_link(v):
    if not isinstance(v,str):return None
    try:u=urlsplit(v.strip())
    except ValueError:return None
    if u.scheme not in ("http","https") or not u.hostname or u.username or u.password:return None
    host=u.hostname.lower();parts=u.path.strip("/").split("/")
    if host in ("apps.apple.com","itunes.apple.com"):
        m=re.search(r"/id([0-9]+)(?:/|$)",u.path)
        if m:return "apple",m.group(1)
    if host=="play.google.com" and u.path=="/store/apps/details":
        q=parse_qs(u.query).get("id",[])
        if len(q)==1 and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+",q[0]):return "google_play",q[0]
    if host in ("f-droid.org","www.f-droid.org"):
        m=re.fullmatch(r"/(?:[a-zA-Z-]+/)?packages/([A-Za-z][A-Za-z0-9_.]+)/?",u.path)
        if m:return "fdroid",m.group(1)
    if host=="github.com" and len(parts)==2 and all(re.fullmatch(r"[A-Za-z0-9_.-]+",x) for x in parts):
        return "github_repository_url","/".join(parts).removesuffix(".git").lower()
    return "other_url",None
def field_audit(rows):
    top=collections.Counter();paths=collections.defaultdict(set);typed=collections.defaultdict(set);per_record=collections.defaultdict(set);technical=collections.defaultdict(set);kinds=collections.Counter()
    idfields={"bundleid","bundle_id","packagename","package_name","android_package","trackid","track_id","appid","app_id","repository_id","repositoryid"}
    for r in rows:
        rid=str(r["id"]);top.update(r.keys())
        for path,v in walk(r):
            key=".".join(path);leaf=path[-1].casefold() if path else ""
            if isinstance(v,str) and v.strip():
                if leaf in idfields:technical[key].add(rid)
                link=parse_link(v)
                if link:
                    paths[key].add(rid);kind,val=link;typed[(key,kind)].add(rid);kinds[kind]+=1
                    if val:per_record[(rid,kind)].add(val)
            elif type(v) is int and leaf in idfields:technical[key].add(rid)
    return {"top_level_field_presence":dict(sorted(top.items())),"url_paths_record_counts":{k:len(v) for k,v in sorted(paths.items())},"url_path_type_record_counts":{k+" | "+t:len(v) for (k,t),v in sorted(typed.items())},"recognized_link_occurrences":dict(kinds),"recognized_link_records_by_type":dict(collections.Counter(t for r,t in per_record)),"multi_identifier_records_by_type":dict(collections.Counter(t for (r,t),v in per_record.items() if len(v)>1)),"explicit_identifier_field_record_counts":{k:len(v) for k,v in sorted(technical.items())},"limitations":"URL syntax only; links may be evidence, store listings, dependencies or obsolete. Do not treat nested links as official product identity or convert catalogue IDs by guess. Counts of paths/types can overlap."}
def main():
    a=argparse.ArgumentParser();a.add_argument("--catalog",type=pathlib.Path,required=True);a.add_argument("--output",type=pathlib.Path,required=True);x=a.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    g=pilot(x.catalog);rows=catalog_rows(json.loads(x.catalog.read_bytes()));base=P/"evidence/2026-11-28"
    si=unzip(base/"sill.zip","sill_product_inventory.json","8bb73ecd9d326547bd93a1db570ab37501a5fec25cba61cc10005ba610f7bc27")
    wi=unzip(base/"wikidata.zip","inventory.json","e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46")
    idx=make_index()
    for r in rows:collect(idx,"catalog:"+str(r["id"]),names(r["name"])+names(r.get("aliases")))
    for r in si:collect(idx,"sill:"+str(r["sill_id"]),r["names"])
    for r in wi:collect(idx,"wikidata:"+r["qid"],r["labels"].values())
    for s,ds in (("doc_web",json.loads((P/"PROSPECTION_WEB_BUREAU_V01.json").read_text())["records_detail"]),("doc_target",json.loads((P/"PROSPECTION_MATERIEL_COMMERCIAL_V01.json").read_text())["records"])):
        for r in ds:collect(idx,s+":"+r["id"],[r["name"]]+r["alias_probes"],urls=[r.get("official_url") or r["official_evidence_url"]])
    edges,deferred,short=compare(idx)
    prior={pair(v["a"],v["b"]) for v in g.assertions.values() if v["relation"]=="NAME_CANDIDATE"}
    need(len(prior)==45,"Prior recent mismatch")
    missing=prior-set(edges)
    details=[]
    for p in sorted(missing):
        signals=[{"rule":rule,"key_length":len(key),"group_size":len(rs)} for rule,groups in idx.items() for key,rs in groups.items() if set(p)<=rs]
        reason="SHORT_NAME" if any(s["rule"]=="short_name" for s in signals) else "LARGE_GROUP" if any(s["group_size"]>30 for s in signals) else "NORMALIZATION_OR_PROJECTION_DIFFERENCE"
        details.append({"pair_sha256":digest(list(p)),"source_pair":"/".join(sorted(map(namespace,p))),"reason":reason,"common_signal_metadata":signals,"status":"PRESERVED_REVIEW_REQUIRED"})
    prev=json.loads((P/"AUDIT_GLOBAL_IDENTITY_V01.json").read_text())
    need(len(missing)==prev["previous_not_regenerated_preserved"] and len(prior&set(edges))==43,"Residual discrepancy not fully reconciled")
    shortpairs=set()
    for key,rs in idx["short_name"].items():
        for a,b in itertools.combinations(sorted(rs),2):
            if namespace(a)!=namespace(b):shortpairs.add(pair(a,b))
    result={"recent_records":len(g.records),"legacy_not_replayed":True,"recent_prior_pairs":len(prior),"recent_regenerated":len(prior&set(edges)),"missing_previous_pairs":details,"short_cross_pairs":len(shortpairs),"short_pairs_previously_preserved":len(shortpairs&prior),"short_groups":short,"field_audit":field_audit(rows),"automatic_merges":0,"identity_adjudicated":0,"next":"Review candidate link fields semantically, then sensitivity analysis and independent sampling. No change to the earlier candidate union."}
    (x.output/"residual_identity_report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RESIDUAL_IDENTITY "+canon(result))
if __name__=="__main__":main()
