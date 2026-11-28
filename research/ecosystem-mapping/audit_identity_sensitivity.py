"""P2-07: offline sensitivity and native listing correspondence, no identity decisions."""
import argparse,collections,itertools,json,pathlib,re,tempfile
from urllib.parse import urlsplit
from integrate_legacy import extract,build,read
from normalize_identity import ingest_apple,ingest_fdroid,ingest_github,candidates,name_key,localized
from global_identity import make_index,collect,compare,pair,namespace
from identity_graph import pilot,unzip,need
from collect_sill import names,catalog_rows
from identity_registry import canon,digest
from audit_residual_identity import parse_link
P=pathlib.Path(__file__).resolve().parent
CAPS=(10,20,30,60,63,100)
def native_link(v):
    """A source_url listing candidate; not a product identity."""
    result=parse_link(v)
    if not result or result[0] not in {"apple","fdroid"}:return None
    u=urlsplit(v.strip())
    if result[0]=="apple" and not re.fullmatch(r"/(?:[a-zA-Z]{2}/)?app/(?:[^/]+/)?id[0-9]+/?",u.path):return None
    if result[0]=="fdroid" and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+",result[1]):return None
    return result
def link_edges(rows,items):
    """Only same namespace native identifiers; no cross-store string equivalence."""
    groups=collections.defaultdict(set);hits={};fields=collections.defaultdict(collections.Counter)
    for r in rows:
        k=native_link(r.get("source_url"))
        if k is None:continue
        rid="catalog:"+str(r["id"]);groups[k].add(rid)
        # Store/origin corroboration is metadata, not a substitute for source ID.
        for f in ("store","origin"):
            v=r.get(f)
            fields[k[0]+"/"+f][str(v) if isinstance(v,(str,int)) else "missing_or_nonscalar"]+=1
        if k in items:hits[pair(rid,":".join(k))]=k[0]
    return hits,groups,fields
def name_overlap(a,b):
    return bool({name_key(v) for v in a if name_key(v)} & {name_key(v) for v in b if name_key(v)})
def sensitivity(index,items):
    out=[]
    baseline=set(compare(index,30)[0]);old=set(candidates(items,30)[0])
    for c in CAPS:
        es,d,short=compare(index,c);le,ld=candidates(items,c)
        current=set(es);legacy=set(le)
        out.append({"cap":c,"global_cross_pairs":len(current),"global_new_vs_30":len(current-baseline),"global_lost_vs_30":len(baseline-current),"global_deferred_cross_groups":len(d),"legacy_pairs":len(legacy),"legacy_new_vs_30":len(legacy-old),"legacy_lost_vs_30":len(old-legacy),"legacy_cross":sum(a[0]!=b[0] for a,b in legacy),"legacy_deferred_groups":ld})
    return out
def legacy_groups(items):
    ix=collections.defaultdict(set)
    for k,v in items.items():
        for url in v["repo"]:ix[url].add(k)
    old=set(candidates(items,30)[0]);out=[]
    for url,ids in sorted(ix.items()):
        if len(ids)<=30:continue
        ps=set(itertools.combinations(sorted(ids),2))
        names_by_id={k:{name_key(n) for n in items[k]["names"] if name_key(n)} for k in ids}
        name_pairs=sum(bool(names_by_id[a]&names_by_id[b]) for a,b in ps)
        pubs={k:{name_key(n) for n in items[k]["publisher"] if name_key(n)} for k in ids}
        publisher_pairs=sum(bool(pubs[a]&pubs[b]) for a,b in ps)
        out.append({"group_sha256":digest(url),"size":len(ids),"source_counts":dict(collections.Counter(k[0] for k in ids)),"pair_upper_bound":len(ps),"already_candidate":len(ps&old),"additional_if_expanded":len(ps-old),"pairs_with_shared_normalized_name":name_pairs,"pairs_with_shared_publisher_label":publisher_pairs,"ids_with_publisher_label":sum(bool(v) for v in pubs.values()),"distinct_native_ids":len(ids),"status":"DEFERRED_REVIEW_REQUIRED"})
    return out
def main():
    a=argparse.ArgumentParser()
    for n in ("catalog","archives","output"):a.add_argument("--"+n,type=pathlib.Path,required=True)
    x=a.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        root=pathlib.Path(tmp);extract(x.archives,root);items={}
        ingest_apple(root/"baseline","apple-baseline",items);ingest_apple(root/"expansion","apple-expansion",items)
        ingest_fdroid(root/"fdroid",items);ingest_github(root/"github",items)
    old_edges,old_deferred=candidates(items,30)
    need(len(items)==9237 and len(old_edges)==669,"Legacy audit mismatch")
    g=pilot(x.catalog);rows=catalog_rows(json.loads(x.catalog.read_bytes()));base=P/"evidence/2026-11-28"
    index=make_index()
    for (s,i),v in items.items():collect(index,s+":"+i,v["names"],v["package"],["https://github.com/"+r for r in v["repo"] if r])
    for r in rows:collect(index,"catalog:"+str(r["id"]),names(r["name"])+names(r.get("aliases")))
    si=unzip(base/"sill.zip","sill_product_inventory.json","8bb73ecd9d326547bd93a1db570ab37501a5fec25cba61cc10005ba610f7bc27")
    wi=unzip(base/"wikidata.zip","inventory.json","e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46")
    for r in si:collect(index,"sill:"+str(r["sill_id"]),r["names"])
    for r in wi:collect(index,"wikidata:"+r["qid"],r["labels"].values())
    for s,ds in (("doc_web",read(P/"PROSPECTION_WEB_BUREAU_V01.json")["records_detail"]),("doc_target",read(P/"PROSPECTION_MATERIEL_COMMERCIAL_V01.json")["records"])):
        for r in ds:collect(index,s+":"+r["id"],[r["name"]]+r["alias_probes"],urls=[r.get("official_url") or r["official_evidence_url"]])
    es,_,_=compare(index,30)
    previous={pair(":".join(a),":".join(b)) for a,b in old_edges if a[0]!=b[0]}|{pair(v["a"],v["b"]) for v in g.assertions.values() if v["relation"]=="NAME_CANDIDATE"}
    union=set(es)|previous
    before=digest([{"a":p[0],"b":p[1],"signals":sorted(es.get(p,set())),"prior":p in previous} for p in sorted(union)])
    need(before==read(P/"AUDIT_GLOBAL_IDENTITY_V01.json")["candidate_manifest_sha256"],"Prior manifest mismatch")
    hits,groups,fields=link_edges(rows,items)
    cat={str(r["id"]):r for r in rows};by=collections.defaultdict(collections.Counter)
    for k,ids in groups.items():
        by[k[0]]["distinct_listing_ids"]+=1;by[k[0]]["catalog_rows_with_strict_link"]+=len(ids)
        by[k[0]]["catalog_duplicate_listing_groups"]+=int(len(ids)>1)
        by[k[0]]["catalog_pairs_same_listing"]+=len(ids)*(len(ids)-1)//2
        if k not in items:by[k[0]]["catalog_rows_not_observed_in_pilots"]+=len(ids)
    for p,s in hits.items():
        by[s]["native_listing_pairs"]+=1
        by[s]["already_in_candidate_union"]+=int(p in union)
        by[s]["new_native_listing_pairs"]+=int(p not in union)
        cid=next(i.split(":",1)[1] for i in p if namespace(i)=="catalog")
        sid=next(i.split(":",1)[1] for i in p if namespace(i)==s)
        r=cat[cid];v=items[(s,sid)]
        by[s]["shared_normalized_name"]+=int(name_overlap(names(r["name"])+names(r.get("aliases")),v["names"]))
        by[s]["shared_publisher_label"]+=int(name_overlap(localized(r.get("publisher")),v["publisher"]))
    short=set()
    for rs in index["short_name"].values():
        for a,b in itertools.combinations(sorted(rs),2):
            if namespace(a)!=namespace(b):short.add(pair(a,b))
    out={"scope":"12956 records; source_url listing syntax, six verified archives, frozen catalogue; exploratory","prior_manifest_verified":True,"prior_union":len(union),"native_listing_pairs":len(hits),"native_listing_overlap_prior":len(set(hits)&union),"new_native_listing_pairs":len(set(hits)-union),"extended_union":len(union|set(hits)),"listing_by_namespace":{s:dict(c) for s,c in sorted(by.items())},"metadata_field_distributions":{k:dict(v) if len(v)<=15 else {"distinct_values":len(v),"counts_suppressed":True} for k,v in sorted(fields.items())},"sensitivity":sensitivity(index,items),"deferred_repository_groups":legacy_groups(items),"short_cross_pairs":len(short),"short_cross_pairs_already_preserved":len(short&union),"extended_candidate_manifest_sha256":digest([{"pair":list(p),"prior":p in union,"native_listing":hits.get(p)} for p in sorted(union|set(hits))]),"automatic_merges":0,"confirmed_products":None,"limitations":"Same listing identifier only, not product identity; source_url may be stale or refer to a different entry, no live URL checks. Strict syntax may omit valid alternate paths. Names and publisher labels are supporting signals only. No human truth labels, no recall or precision. Threshold analysis on fixed observed pilots, not optimized threshold. Deferred group expansion is a sensitivity scenario, not adopted."}
    (x.output/"sensitivity_report.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("IDENTITY_SENSITIVITY "+canon(out))
if __name__=="__main__":main()
