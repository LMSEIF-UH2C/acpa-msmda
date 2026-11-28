"""Exploratory persistent identity register. Never merge source records.
SQLite is a local audit snapshot, not a production catalogue or a tamper-proof service.
"""
import argparse,collections,csv,hashlib,json,pathlib,sqlite3
from identity_graph import pilot,Graph,TYPES,REL,STATES,SYMMETRIC,valid_date,need
P=pathlib.Path(__file__).resolve().parent
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def digest(x):return hashlib.sha256(canon(x).encode()).hexdigest()
SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE source(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE record(id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source(id), payload TEXT NOT NULL);
CREATE TABLE observation(id TEXT PRIMARY KEY, record_id TEXT NOT NULL REFERENCES record(id), payload TEXT NOT NULL);
CREATE TABLE entity(id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL);
CREATE TABLE proof(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE event(seq INTEGER PRIMARY KEY, stream TEXT NOT NULL, revision INTEGER NOT NULL, previous TEXT NOT NULL, hash TEXT NOT NULL UNIQUE, payload TEXT NOT NULL, UNIQUE(stream,revision));
CREATE TRIGGER no_event_update BEFORE UPDATE ON event BEGIN SELECT RAISE(ABORT,'append only'); END;
CREATE TRIGGER no_event_delete BEFORE DELETE ON event BEGIN SELECT RAISE(ABORT,'append only'); END;
"""
# Rules constrain accepted entity-level claims, not initial record-level candidate observations.
STRUCTURE={
 "VARIANT_OF":({"variant"},{"product","software","platform","hardware","system"}),
 "CLIENT_OF":({"client"},{"platform","system","software"}),
 "COMPONENT_OF":({"component","hardware","software","client","variant"},{"system","platform","product","software","hardware"}),
 "SOURCE_CODE_OF":({"repository"},{"software","component","client","platform","product"}),
 "FORK_OF":({"repository","software","component","platform","product"},{"repository","software","component","platform","product"}),
 "SUCCESSOR_OF":({"product","software","hardware","platform","system"},{"product","software","hardware","platform","system"}),
 "RENAMED_FROM":({"product","software","hardware","platform","system"},{"product","software","hardware","platform","system"}),
}
ACTIVE={"PROPOSED","REVIEW_REQUIRED","UNCERTAIN","ADJUDICATED"}
class Register:
    def __init__(self,path,create=False):
        self.db=sqlite3.connect(path)
        self.db.row_factory=sqlite3.Row;self.db.execute("PRAGMA foreign_keys=ON")
        if create:
            self.db.executescript(SCHEMA)
            for table in ("source","record","observation","entity","proof"):
                self.db.executescript(f"CREATE TRIGGER no_{table}_update BEFORE UPDATE ON {table} BEGIN SELECT RAISE(ABORT,'immutable snapshot'); END; CREATE TRIGGER no_{table}_delete BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT,'immutable snapshot'); END;")
    def close(self):self.db.close()
    def load(self,g):
        with self.db:
            for k,v in g.sources.items():self.db.execute("INSERT INTO source VALUES (?,?)",(k,canon(v)))
            for k,v in g.records.items():self.db.execute("INSERT INTO record VALUES (?,?,?)",(k,v["source"],canon(v)))
            for k,v in g.observations.items():self.db.execute("INSERT INTO observation VALUES (?,?,?)",(k,v["record"],canon(v)))
            for k,v in g.entities.items():self.db.execute("INSERT INTO entity VALUES (?,?,?)",(k,v["kind"],canon(v)))
            for k,v in g.evidence.items():self.db.execute("INSERT INTO proof VALUES (?,?)",(k,canon(v)))
        for k,v in g.assertions.items():
            self.append("relation:"+k,{"category":"relation",**v,"date":"2026-11-28","actor":"import_v02"},0)
    def lookup(self,table,key):
        need(table in {"source","record","observation","entity","proof"},"Invalid table")
        r=self.db.execute(f"SELECT payload FROM {table} WHERE id=?",(key,)).fetchone()
        return json.loads(r[0]) if r else None
    def add_entity(self,key,kind,label):
        need(kind in TYPES and bool(label) and not self.lookup("record",key),"Invalid entity")
        with self.db:self.db.execute("INSERT INTO entity VALUES (?,?,?)",(key,kind,canon({"kind":kind,"label":label,"status":"PROVISIONAL"})))
    def add_proof(self,key,url,date,kind):
        g=Graph();g.proof(key,url,date,kind)
        with self.db:self.db.execute("INSERT INTO proof VALUES (?,?)",(key,canon(g.evidence[key])))
    def history(self,stream):
        return [json.loads(r[0]) for r in self.db.execute("SELECT payload FROM event WHERE stream=? ORDER BY revision",(stream,))]
    def current(self):
        return {r["stream"]:json.loads(r["payload"]) for r in self.db.execute("SELECT e.* FROM event e JOIN (SELECT stream,MAX(revision) rev FROM event GROUP BY stream) x ON e.stream=x.stream AND e.revision=x.rev")}
    def check_payload(self,v):
        need(v.get("category") in {"attachment","relation"} and v.get("state") in ACTIVE|{"REJECTED","WITHDRAWN"},"Invalid event")
        need(valid_date(v.get("date")) and isinstance(v.get("actor"),str) and v["actor"].strip() and isinstance(v.get("rationale"),str) and v["rationale"].strip(),"Missing event provenance")
        proofs=v.get("evidence");need(isinstance(proofs,list) and bool(proofs) and len(proofs)==len(set(proofs)) and all(self.lookup("proof",i) for i in proofs),"Missing proof")
        a,b=v.get("a"),v.get("b");need(a!=b,"Same endpoint")
        if v["category"]=="attachment":
            ra=self.lookup("record",a);eb=self.lookup("entity",b)
            need(ra and eb,"Attachment must link record to entity")
            need(v.get("relation")=="REFERS_TO","Invalid attachment relation")
            if v["state"]=="ADJUDICATED":need(ra["kind_hint"] in ("unknown",eb["kind"]),"Attachment type conflict")
        else:
            ea,eb=self.lookup("entity",a),self.lookup("entity",b)
            need((ea or self.lookup("record",a)) and (eb or self.lookup("record",b)) and v.get("relation") in REL,"Invalid relation endpoints")
            if v["relation"] in SYMMETRIC:need(a<b,"Noncanonical symmetric relation")
            if v["state"]=="ADJUDICATED":
                need(ea and eb and v["relation"]!="NAME_CANDIDATE","Accepted relation requires typed entities")
                if v["relation"] in STRUCTURE:
                    ka,kb=STRUCTURE[v["relation"]];need(ea["kind"] in ka and eb["kind"] in kb,"Invalid relation types")
                if v["relation"] in {"FORK_OF","SUCCESSOR_OF","RENAMED_FROM"}:need(ea["kind"]==eb["kind"],"Incompatible type")
        if v["state"] in {"ADJUDICATED","REJECTED","WITHDRAWN"}:
            d=v.get("decision");need(isinstance(d,dict) and set(d)=={"judge_a","judge_b","arbitrator","decision_date","reference"} and all(isinstance(x,str) and x.strip() for x in d.values()) and valid_date(d["decision_date"]) and len({d["judge_a"],d["judge_b"],d["arbitrator"]})==3,"Arbitration required")
            need(any(self.lookup("proof",i)["kind"]=="adjudication" for i in proofs),"Missing arbitration proof")
    def check_current(self):
        cur=self.current();g=Graph();targets=collections.defaultdict(set)
        for r in self.db.execute("SELECT id,payload FROM entity"):
            v=json.loads(r["payload"]);g.entity(r["id"],v["kind"],v["label"])
        for r in self.db.execute("SELECT id,payload FROM proof"):
            v=json.loads(r["payload"]);g.proof(r["id"],v["url"],v["date"],v["kind"])
        seen=set()
        for k,v in cur.items():
            if v["state"] not in ACTIVE:continue
            key=(v["category"],v["a"],v["relation"],v["b"]);need(key not in seen,"Duplicate active assertion");seen.add(key)
            if v["category"]=="attachment" and v["state"]=="ADJUDICATED":targets[v["a"]].add(v["b"])
            if v["category"]=="relation" and v["a"] in g.entities and v["b"] in g.entities:
                g.link(k,v["a"],v["relation"],v["b"],v["state"],v["evidence"],v["rationale"],v.get("decision"))
        need(all(len(v)<=1 for v in targets.values()),"Multiple accepted attachments; unresolved")
        g.validate()
        # A mixed hierarchy cycle is also disallowed in accepted component and variant links.
        adj=collections.defaultdict(list)
        for v in cur.values():
            if v["state"]=="ADJUDICATED" and v["relation"] in {"COMPONENT_OF","VARIANT_OF"}:adj[v["a"]].append(v["b"])
        visiting=set();done=set()
        def visit(n):
            need(n not in visiting,"Mixed hierarchy cycle")
            if n in done:return
            visiting.add(n)
            for m in adj.get(n,[]):visit(m)
            visiting.remove(n);done.add(n)
        for n in list(adj):visit(n)
    def append(self,stream,v,expected_revision):
        self.check_payload(v)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            prev=self.db.execute("SELECT seq,hash FROM event ORDER BY seq DESC LIMIT 1").fetchone()
            last=self.db.execute("SELECT revision,payload FROM event WHERE stream=? ORDER BY revision DESC LIMIT 1",(stream,)).fetchone()
            actual=last["revision"] if last else 0
            need(actual==expected_revision,"Stale revision")
            if last:
                old=json.loads(last["payload"])
                need(all(old[k]==v[k] for k in ("category","a","b","relation")),"Cannot change assertion identity")
                need(v["date"]>=old["date"],"Backdated revision")
                need(set(old["evidence"])<=set(v["evidence"]),"Preserve prior evidence")
                if old["state"] in {"ADJUDICATED","REJECTED","WITHDRAWN"}:
                    need(v["state"] in {"ADJUDICATED","REJECTED","WITHDRAWN"} and v.get("decision"),"Reopening needs arbitration")
            seq=prev["seq"]+1 if prev else 1;previous=prev["hash"] if prev else "0"*64
            rev=actual+1;h=digest([seq,stream,rev,previous,v])
            self.db.execute("INSERT INTO event VALUES (?,?,?,?,?,?)",(seq,stream,rev,previous,h,canon(v)))
            self.check_current()
        return rev
    def audit(self):
        need(self.db.execute("PRAGMA integrity_check").fetchone()[0]=="ok","DB integrity")
        need(not self.db.execute("PRAGMA foreign_key_check").fetchall(),"Foreign keys")
        previous="0"*64;rev={};seq=0
        for r in self.db.execute("SELECT * FROM event ORDER BY seq"):
            v=json.loads(r["payload"]);seq+=1
            need(r["seq"]==seq and r["previous"]==previous and r["revision"]==rev.get(r["stream"],0)+1 and r["hash"]==digest([seq,r["stream"],r["revision"],previous,v]),"Event chain broken")
            self.check_payload(v);previous=r["hash"];rev[r["stream"]]=r["revision"]
        self.check_current()
        return {"tables":{t:self.db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("source","record","observation","entity","proof","event")},"current_assertions":len(rev),"chain_head":previous,"states":dict(collections.Counter(v["state"] for v in self.current().values())),"confirmed_attachments":sum(v["category"]=="attachment" and v["state"]=="ADJUDICATED" for v in self.current().values()),"confirmed_product_count":None}
def make_kit(g,output):
    # Four complex documentary proposals plus six purposeful non-candidates. No reference answers.
    cases=[("complex",v["a"],v["b"]) for v in g.assertions.values() if v["relation"]!="NAME_CANDIDATE"]
    cases += [("outside_imported_candidates",a,b) for a,b in [
        ("doc_target:T05","doc_target:T06"),("doc_target:T07","doc_target:T03"),
        ("doc_target:T08","doc_target:T09"),("doc_target:T12","doc_web:WD02"),
        ("doc_web:WD05","doc_web:WD06"),("doc_web:WD07","doc_web:WD11")]]
    cand={frozenset((v["a"],v["b"])) for v in g.assertions.values() if v["relation"]=="NAME_CANDIDATE"}
    need(len({frozenset((a,b)) for _,a,b in cases})==10,"Duplicate case")
    fields=["review_id","source_a","id_a","source_b","id_b","locator_a","locator_b","type_a","type_b","primary_relation","additional_relations","evidence_urls","evidence_date","justification","uncertainty"]
    def locator(r):
        obs=next(v for v in g.observations.values() if v["record"]==r)
        if r.startswith("wikidata:"):return "https://www.wikidata.org/wiki/"+r.split(":",1)[1]
        if r.startswith("catalog:"):return "data/real_tools_catalog.json#id="+r.split(":",1)[1]
        return obs["locator"]
    rows=[]
    for i,(stratum,a,b) in enumerate(cases,1):
        need(a in g.records and b in g.records,"Missing case")
        if stratum=="outside_imported_candidates":need(frozenset((a,b)) not in cand,"Not outside candidates")
        sa,ia=a.split(":",1);sb,ib=b.split(":",1)
        rows.append(dict(review_id=f"R{i:03d}",source_a=sa,id_a=ia,source_b=sb,id_b=ib,locator_a=locator(a),locator_b=locator(b)))
    for judge in ("A","B"):
        with (output/f"relational_judge_{judge}.csv").open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    (output/"relational_strata.json").write_text(canon({f"R{i:03d}":s for i,(s,a,b) in enumerate(cases,1)})+"\n",encoding="utf-8")
    return {"cases":len(rows),"complex":4,"outside_imported_candidates":6,"judges_blank_identical":(output/"relational_judge_A.csv").read_bytes()==(output/"relational_judge_B.csv").read_bytes()}
def main():
    a=argparse.ArgumentParser();a.add_argument("--catalog",type=pathlib.Path,required=True);a.add_argument("--output",type=pathlib.Path,required=True);x=a.parse_args()
    x.output.mkdir(parents=True,exist_ok=True);g=pilot(x.catalog);path=x.output/"identity_registry.sqlite"
    need(not path.exists(),"Refuse overwrite of audit DB")
    r=Register(path,True);r.load(g)
    for s,rows in (("doc_web",json.loads((P/"PROSPECTION_WEB_BUREAU_V01.json").read_text())["records_detail"]),("doc_target",json.loads((P/"PROSPECTION_MATERIEL_COMMERCIAL_V01.json").read_text())["records"])):
        for row in rows:
            k=s+":"+row["id"];ent="provisional:"+k
            r.add_entity(ent,g.records[k]["kind_hint"],row["name"])
            r.append("attachment:"+k,{"category":"attachment","a":k,"b":ent,"relation":"REFERS_TO","state":"PROPOSED","evidence":["proof:"+k],"rationale":"Documentary hypothesis only; no adjudicated identity.","decision":None,"date":"2026-11-28","actor":"pilot_import"},0)
    before=r.audit();r.close()
    r=Register(path);after=r.audit();r.close();need(before==after,"Reopen mismatch")
    report={**after,"reopen_verified":True,"database_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"kit":make_kit(g,x.output),"scope":"Five spaces V0.2; 34 provisional documentary entities, not unique confirmed products. No prior Apple/F-Droid/GitHub ingestion. No real judgments."}
    (x.output/"registry_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("REGISTRY_RESULT "+canon(report))
if __name__=="__main__":main()
