"""Global conservative candidate audit of eight archived source spaces.
No network, no source metadata publication, no automatic identity decisions.
"""
import argparse,collections,hashlib,itertools,json,pathlib,tempfile
from integrate_legacy import extract,build,read,ARCHIVES
from normalize_identity import ingest_apple,ingest_fdroid,ingest_github,name_key,repo_url,localized,candidates
from identity_graph import pilot,unzip,need
from collect_sill import names,catalog_rows
from identity_registry import canon,digest
P=pathlib.Path(__file__).resolve().parent
LEGACY={"apple","fdroid","github"}
def add(index,rule,key,rid):
    if key:index[rule][key].add(rid)
def pair(a,b):return tuple(sorted((a,b)))
def namespace(r):return r.split(":",1)[0]
def stratum(p):return "/".join(sorted(namespace(x) for x in p))
def block(p):
    a,b=map(namespace,p)
    if (a in LEGACY)!=(b in LEGACY):return "between_blocks"
    return "legacy" if a in LEGACY else "recent"
def make_index():return collections.defaultdict(lambda:collections.defaultdict(set))
def collect(index,rid,labels=(),ids=(),urls=()):
    for s in labels:
        k=name_key(s)
        add(index,"name" if len(k)>=3 else "short_name",k,rid)
    for s in ids:
        if isinstance(s,str) and s.strip():add(index,"identifier_string",s,rid)
    for s in urls:add(index,"repository_url",repo_url(s),rid)
def compare(index,cap=30):
    edges=collections.defaultdict(set);deferred=[];short=[]
    for rule,keys in sorted(index.items()):
        for value,rs in sorted(keys.items()):
            by=collections.Counter(namespace(r) for r in rs)
            possible=sum(a*b for a,b in itertools.combinations(by.values(),2))
            if not possible:continue
            if rule=="short_name" or len(rs)>cap:
                row={"rule":rule,"size":len(rs),"cross_source_pairs_upper_bound":possible,"source_counts":dict(sorted(by.items()))}
                (short if rule=="short_name" else deferred).append(row);continue
            for a,b in itertools.combinations(sorted(rs),2):
                if namespace(a)!=namespace(b):edges[pair(a,b)].add(rule)
    return edges,deferred,short
def main():
    a=argparse.ArgumentParser()
    for n in ("catalog","archives","output"):a.add_argument("--"+n,type=pathlib.Path,required=True)
    x=a.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        root=pathlib.Path(tmp);extract(x.archives,root);data,old=build(root)
        items={}
        ingest_apple(root/"baseline","apple-baseline",items);ingest_apple(root/"expansion","apple-expansion",items);ingest_fdroid(root/"fdroid",items);ingest_github(root/"github",items)
    need(len(items)==9237 and old["candidate_pairs"]==669,"Legacy mismatch")
    g=pilot(x.catalog)
    need(len(g.records)==3719 and len(g.observations)==3721,"Recent mismatch")
    ridset=set(g.records)|{s+":"+i for s,i in items};need(len(ridset)==12956,"Namespace mismatch")
    index=make_index()
    for (s,i),v in items.items():
        collect(index,s+":"+i,v["names"],v["package"],["https://github.com/"+r for r in v["repo"] if r])
    # Only explicitly named technical-ID fields and exact root GitHub URLs are used.
    # No arbitrary strings, fuzzy URL matching or guesses from IDs in catalogue.
    rows=catalog_rows(json.loads(x.catalog.read_bytes()))
    field_counts=collections.Counter()
    idfields=("bundleId","bundle_id","packageName","package_name","android_package")
    urlfields=("official_url","officialUrl","website","url","sourceCode","source_code","repository_url","github_url")
    for r in rows:
        ids=[];urls=[]
        for f in idfields+urlfields:
            v=r.get(f)
            if isinstance(v,str) and v.strip():
                field_counts[f]+=1
                (ids if f in idfields else urls).append(v)
        collect(index,"catalog:"+str(r["id"]),names(r["name"])+names(r.get("aliases")),ids,urls)
    base=P/"evidence/2026-11-28"
    si=unzip(base/"sill.zip","sill_product_inventory.json","8bb73ecd9d326547bd93a1db570ab37501a5fec25cba61cc10005ba610f7bc27")
    wi=unzip(base/"wikidata.zip","inventory.json","e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46")
    for r in si:collect(index,"sill:"+str(r["sill_id"]),r["names"])
    for r in wi:collect(index,"wikidata:"+r["qid"],r["labels"].values())
    for s,rows in (("doc_web",read(P/"PROSPECTION_WEB_BUREAU_V01.json")["records_detail"]),("doc_target",read(P/"PROSPECTION_MATERIEL_COMMERCIAL_V01.json")["records"])):
        for r in rows:
            collect(index,s+":"+r["id"],[r["name"]]+r["alias_probes"],urls=[r.get("official_url") or r["official_evidence_url"]])
    edges,deferred,short=compare(index)
    previous_legacy={pair(a,b) for a,b,v in data["legacy_candidate"] if namespace(a)!=namespace(b)}
    previous_recent={pair(v["a"],v["b"]) for v in g.assertions.values() if v["relation"]=="NAME_CANDIDATE"}
    need(len(previous_legacy)==13 and len(previous_recent)==45,"Prior edge mismatch")
    previous=previous_legacy|previous_recent
    current=set(edges);union=current|previous
    new=current-previous
    coverage={}
    for rule,keys in index.items():
        coverage[rule]=dict(collections.Counter(namespace(r) for r in set().union(*keys.values()))) if keys else {}
    bypair=collections.Counter(stratum(p) for p in new)
    need(all(set(p)<=ridset for p in union),"Missing endpoint")
    result={"source_records":len(ridset),"source_spaces":8,"archives_verified":6,"cross_source_generated":len(current),"previous_cross_source_candidates":len(previous),"previous_regenerated":len(current&previous),"previous_not_regenerated_preserved":len(previous-current),"cross_source_union":len(union),"new_candidates":len(new),"new_between_blocks":sum(block(p)=="between_blocks" for p in new),"new_by_block":dict(collections.Counter(block(p) for p in new)),"new_by_source_pair":dict(sorted(bypair.items())),"new_by_signal":dict(collections.Counter(s for p in new for s in edges[p])),"new_multi_signal":sum(len(edges[p])>1 for p in new),"legacy_within_source_preserved":656,"coverage_by_signal":coverage,"catalog_explicit_field_counts":dict(field_counts),"deferred_groups":deferred,"short_name_groups":short,"deferred_pair_upper_bound":sum(r["cross_source_pairs_upper_bound"] for r in deferred),"short_pair_upper_bound":sum(r["cross_source_pairs_upper_bound"] for r in short),"candidate_manifest_sha256":digest([{"a":p[0],"b":p[1],"signals":sorted(edges.get(p,set())),"prior":p in previous} for p in sorted(union)]),"confirmed_products":None,"automatic_merges":0,"limitations":"Exact names including aliases and documentary probes; explicit identifier strings and exact GitHub root URLs only. Names and code links are signals, not identity. Deferred/short pair counts may overlap and do not measure missed links. Previously imported 656 within-source candidates retained, no new within-source scan. No fuzzy matching, external link verification, human judgments or recall estimate. No raw names or IDs in public report."}
    (x.output/"global_identity_report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GLOBAL_IDENTITY "+canon(result))
if __name__=="__main__":main()
