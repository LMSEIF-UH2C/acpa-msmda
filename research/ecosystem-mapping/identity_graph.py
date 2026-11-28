"""Exploratory identity graph; candidates never merge source records."""
import argparse,collections,datetime,hashlib,json,pathlib,re,zipfile
P=pathlib.Path(__file__).resolve().parent
TYPES={"product","system","hardware","software","platform","component","variant","client","repository","unknown"}
REL={"SAME_PRODUCT","DISTINCT_PRODUCT","VARIANT_OF","CLIENT_OF","COMPONENT_OF","SOURCE_CODE_OF","FORK_OF","SUCCESSOR_OF","RENAMED_FROM","COMPATIBLE_WITH","REQUIRES","NAME_CANDIDATE"}
STATES={"PROPOSED","REVIEW_REQUIRED","UNCERTAIN","ADJUDICATED"}
# Direction is subject -> object. Symmetric relations are normalized independently.
SYMMETRIC={"SAME_PRODUCT","DISTINCT_PRODUCT","COMPATIBLE_WITH","NAME_CANDIDATE"}
NON_IDENTITY={"DISTINCT_PRODUCT","VARIANT_OF","CLIENT_OF","COMPONENT_OF","SOURCE_CODE_OF","FORK_OF","SUCCESSOR_OF","REQUIRES"}
# Variant and product entities remain separate graph nodes even if they share a product.
IDENTITY_TYPES={"product","software","platform","hardware","system"}
def need(condition,msg):
    if not condition: raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def jsonread(path):return json.loads(path.read_text(encoding="utf-8"))
def valid_date(s):
    try:return datetime.date.fromisoformat(s).isoformat()==s
    except (ValueError,TypeError):return False
def stable(namespace,sid):
    need(isinstance(sid,str) and bool(sid.strip()),"Empty source id")
    return namespace+":"+sid
class Graph:
    def __init__(self):
        self.sources={};self.records={};self.observations={};self.entities={};self.evidence={};self.assertions={}
    def source(self,key,kind,locator):
        need(key not in self.sources,"Duplicate source")
        self.sources[key]={"kind":kind,"locator":locator}
    def record(self,source,sid,kind="unknown"):
        need(source in self.sources and kind in TYPES,"Invalid record")
        k=stable(source,sid)
        if k not in self.records:self.records[k]={"source":source,"source_id":sid,"kind_hint":kind}
        else:need(self.records[k]["kind_hint"]==kind,"Conflicting record kind")
        return k
    def observe(self,key,record,date,locator,digest=None):
        need(key not in self.observations and record in self.records and valid_date(date),"Invalid observation")
        need(digest is None or re.fullmatch(r"[0-9a-f]{64}",digest),"Invalid digest")
        self.observations[key]={"record":record,"date":date,"locator":locator,"payload_sha256":digest}
    def entity(self,key,kind,label):
        need(key not in self.entities and key not in self.records and kind in TYPES and bool(label),"Invalid entity")
        self.entities[key]={"kind":kind,"label":label,"status":"PROVISIONAL"}
        return key
    def proof(self,key,url,date,kind):
        need(key not in self.evidence and url.startswith("https://") and valid_date(date),"Invalid evidence")
        need(kind in {"publisher","independent","adjudication","source_projection","synthetic"},"Invalid proof type")
        self.evidence[key]={"url":url,"date":date,"kind":kind}
    def link(self,key,a,rel,b,state="PROPOSED",proofs=(),rationale="",decision=None):
        need(key not in self.assertions and a!=b and rel in REL and state in STATES,"Invalid relation")
        nodes=set(self.records)|set(self.entities)
        need(a in nodes and b in nodes,"Missing endpoint")
        need(all(i in self.evidence for i in proofs),"Missing evidence")
        if rel in SYMMETRIC:a,b=sorted((a,b))
        need(not any((v["a"],v["relation"],v["b"])==(a,rel,b) for v in self.assertions.values()),"Duplicate relation")
        if state=="ADJUDICATED":
            need(rel!="NAME_CANDIDATE" and proofs and rationale.strip() and isinstance(decision,dict),"Adjudication evidence required")
            need(set(decision)=={"judge_a","judge_b","arbitrator","decision_date","reference"} and valid_date(decision["decision_date"]) and all(isinstance(decision[x],str) and decision[x].strip() for x in decision),"Invalid adjudication metadata")
            need(len({decision["judge_a"],decision["judge_b"],decision["arbitrator"]})==3,"Independent roles required")
            need(any(self.evidence[i]["kind"]=="adjudication" for i in proofs),"Missing adjudication proof")
            if rel=="SAME_PRODUCT":
                need(a in self.entities and b in self.entities and self.entities[a]["kind"]==self.entities[b]["kind"] and self.entities[a]["kind"] in IDENTITY_TYPES,"Identity cannot collapse source records, components or variants")
        self.assertions[key]={"a":a,"relation":rel,"b":b,"state":state,"evidence":list(proofs),"rationale":rationale,"decision":decision}
    def identity_groups(self):
        """Only adjudicated same-product edges can propose groups; refuse contradictions globally."""
        parent={k:k for k in self.entities}
        def root(k):
            while parent[k]!=k:k=parent[k]
            return k
        for v in self.assertions.values():
            if v["state"]=="ADJUDICATED" and v["relation"]=="SAME_PRODUCT":
                a,b=root(v["a"]),root(v["b"])
                if a!=b:parent[b]=a
        for v in self.assertions.values():
            if v["relation"] in NON_IDENTITY and v["a"] in parent and v["b"] in parent and root(v["a"])==root(v["b"]):
                # unresolved contradictions also block grouping, not only accepted negatives
                raise ValueError("Identity group contradiction: "+v["relation"])
        groups=collections.defaultdict(list)
        for k in parent:groups[root(k)].append(k)
        return sorted(sorted(g) for g in groups.values() if len(g)>1)
    def validate(self):
        self.identity_groups()
        # cycles in accepted directed structural links are invalid for these hierarchical predicates.
        for rel in ("VARIANT_OF","COMPONENT_OF","FORK_OF","SUCCESSOR_OF","RENAMED_FROM"):
            adj=collections.defaultdict(list)
            for v in self.assertions.values():
                if v["state"]=="ADJUDICATED" and v["relation"]==rel:adj[v["a"]].append(v["b"])
            visiting=set();done=set()
            def walk(n):
                if n in visiting:raise ValueError("Directed cycle: "+rel)
                if n in done:return
                visiting.add(n)
                for m in adj.get(n,[]):walk(m)
                visiting.remove(n);done.add(n)
            for n in list(adj):walk(n)
    def export(self):
        self.validate()
        return {k:getattr(self,k) for k in ("sources","records","observations","entities","evidence","assertions")}
def unzip(path,name,expected):
    b=path.read_bytes();need(sha(b)==expected,"ZIP hash mismatch")
    with zipfile.ZipFile(path) as z:
        need(z.testzip() is None,"CRC mismatch")
        return json.loads(z.read(name))
def pilot(catalog_path):
    g=Graph()
    for s,kind,loc in [("catalog","local_snapshot","data/real_tools_catalog.json"),("sill","institutional","https://code.gouv.fr/sill/"),("wikidata","semantic","https://www.wikidata.org/"),("doc_web","documentary","PROSPECTION_WEB_BUREAU_V01.json"),("doc_target","documentary","PROSPECTION_MATERIEL_COMMERCIAL_V01.json")]:g.source(s,kind,loc)
    b=catalog_path.read_bytes();blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
    need(blob=="39b32ebbdf33b49a3fb0bb669f8a0809d0e72995","catalog mismatch")
    c=json.loads(b);c=c if isinstance(c,list) else next(v for v in c.values() if isinstance(v,list) and len(v)==2466 and all(isinstance(i,dict) and "name" in i for i in v))
    need(len(c)==2466,"catalog count")
    for r in c:
        k=g.record("catalog",str(r["id"]));g.observe("obs:"+k,k,"2026-11-28","catalog snapshot checked",None)
    base=P/"evidence/2026-11-28"
    si=unzip(base/"sill.zip","sill_product_inventory.json","8bb73ecd9d326547bd93a1db570ab37501a5fec25cba61cc10005ba610f7bc27")
    wi=unzip(base/"wikidata.zip","inventory.json","e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46")
    wm=unzip(base/"wikidata.zip","manifest.json","e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46")
    sm=unzip(base/"sill.zip","manifest.json","8bb73ecd9d326547bd93a1db570ab37501a5fec25cba61cc10005ba610f7bc27")
    wdlogs={r["family"]:r for r in wm["by_query"]}
    need(len(si)==672 and len(wi)==547,"Source count")
    for r in si:
        k=g.record("sill",str(r["sill_id"]));g.observe("obs:"+k,k,"2026-11-28","SILL archived projection")
    for r in wi:
        k=g.record("wikidata",r["qid"])
        for family in r["families"]:
            g.observe("obs:"+k+":"+family,k,"2026-11-28",family+".raw.json",wdlogs[family]["sha256"])
    web=jsonread(P/"PROSPECTION_WEB_BUREAU_V01.json")["records_detail"]
    target=jsonread(P/"PROSPECTION_MATERIEL_COMMERCIAL_V01.json")["records"]
    kinds={"systeme":"system","materiel":"hardware","logiciel":"software","plateforme":"platform","composant":"component","variante_logicielle":"variant","logiciel_client":"client"}
    for s,rows in (("doc_web",web),("doc_target",target)):
        for r in rows:
            kind=kinds[r["unit"]] if s=="doc_target" else "unknown"
            k=g.record(s,r["id"],kind)
            url=r.get("official_url") or r["official_evidence_url"]
            date=r.get("observed_date") or r["date"]
            g.observe("obs:"+k,k,date,url);g.proof("proof:"+k,url,date,"publisher")
    g.proof("catalog_comparison","https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46140698351","2026-11-28","source_projection")
    g.proof("sill_wd_comparison","https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46140045337","2026-11-28","source_projection")
    n=0
    def candidate(a,b,proof):
        nonlocal n
        n+=1;g.link("candidate:"+str(n),a,"NAME_CANDIDATE",b,"REVIEW_REQUIRED",[proof],"Nom, famille, composant ou variante : signal seulement.")
    for r in si:
        for cid in r["exact_catalog_ids"]:candidate(stable("sill",str(r["sill_id"])),stable("catalog",str(cid)),"sill_wd_comparison")
    for r in wi:
        for s,field in (("catalog","catalog_name_candidates"),("sill","sill_name_candidates")):
            for cid in r[field]:candidate(stable("wikidata",r["qid"]),stable(s,str(cid)),"sill_wd_comparison")
    for r in web:
        for cid in r["exact_name_matches"]:
            # Earlier register stores identifiers or objects; reject unsupported representation.
            ident=cid["id"] if isinstance(cid,dict) else cid
            candidate(stable("doc_web",r["id"]),stable("catalog",str(ident)),"proof:"+stable("doc_web",r["id"]))
    for r in jsonread(P/"AUDIT_PROSPECTION_MATERIEL_COMMERCIAL_V01.json")["rows"]:
        for s,ids in r["candidates"].items():
            for cid in ids:candidate(stable("doc_target",r["id"]),stable(s,str(cid)),"catalog_comparison")
    # Documentary proposals, not independent adjudications; a contested compatibility stays uncertain.
    proposals=[
      ("r1","doc_target:T02","COMPATIBLE_WITH","doc_target:T01","UNCERTAIN",["proof:doc_target:T02"],"Documentation compatible selon version; contradiction apparente sur synchronisation."),
      ("r2","doc_target:T15","VARIANT_OF","doc_web:WD03","PROPOSED",["proof:doc_target:T15","proof:doc_web:WD03"],"Tracker Online et Tracker OSP; continuité à arbitrer."),
      ("r3","doc_target:T16","CLIENT_OF","wikidata:Q190434","PROPOSED",["proof:doc_target:T16"],"Moodle App client; cible QID candidate, identité à arbitrer."),
      ("r4","doc_target:T16","CLIENT_OF","catalog:moodle","PROPOSED",["proof:doc_target:T16"],"Moodle App client; fiche catalogue à contrôler.")
    ]
    for k,a,rel,b,state,proof,why in proposals:g.link(k,a,rel,b,state,proof,why)
    g.validate()
    return g
def main():
    a=argparse.ArgumentParser();a.add_argument("--catalog",type=pathlib.Path,required=True);a.add_argument("--output",type=pathlib.Path,required=True);x=a.parse_args()
    g=pilot(x.catalog);x.output.mkdir(parents=True,exist_ok=True)
    # Do not publish source IDs/links en masse: output aggregate + four documentary proposals only.
    report={"sources":len(g.sources),"source_records":dict(collections.Counter(v["source"] for v in g.records.values())),"records_total":len(g.records),"observations_total":len(g.observations),"observations_by_source":dict(collections.Counter(g.records[v["record"]]["source"] for v in g.observations.values())),"candidate_edges":sum(v["relation"]=="NAME_CANDIDATE" for v in g.assertions.values()),"candidate_by_source_pair":dict(collections.Counter("/".join(sorted([g.records[v["a"]]["source"],g.records[v["b"]]["source"]])) for v in g.assertions.values() if v["relation"]=="NAME_CANDIDATE")),"documentary_proposals":[v for v in g.assertions.values() if v["relation"]!="NAME_CANDIDATE"],"adjudicated_relations":sum(v["state"]=="ADJUDICATED" for v in g.assertions.values()),"confirmed_product_count":None,"identity_groups":g.identity_groups(),"scope":"Catalog + SILL + Wikidata + two documentary pilots. Earlier Apple/F-Droid/GitHub identity pilot remains separate; no sum of products."}
    (x.output/"identity_graph_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("IDENTITY_GRAPH "+json.dumps(report,ensure_ascii=False,separators=(",",":")))
if __name__=="__main__":main()
