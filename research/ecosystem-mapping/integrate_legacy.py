"""Offline integration of archived legacy source IDs; no product merges."""
import argparse,collections,hashlib,json,pathlib,sqlite3,zipfile
from identity_graph import pilot,need
from identity_registry import Register,canon,digest
from normalize_identity import ingest_apple,ingest_fdroid,ingest_github,candidates,report
from audit_query_yield import load
P=pathlib.Path(__file__).resolve().parent
ARCHIVES={"baseline":"7ae8e6d9b0bff727a2bfd322b30fb0f66d3aa0b8ae2ecda4cf82c764c7c50a4d","expansion":"98657812ca3201aba2a0d9ad392d828db1600bef2ab32b387565e227339ba471","fdroid":"9348a5cee92d30e3621c75a543c2b4ac25900995bbda536734597617819fea85","github":"7e1ce5956d457f121bbc832f6171f77697ca783772092c294a023cbb079ec082"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def extract(root,output):
    for name,h in ARCHIVES.items():
        path=root/(name+".zip");need(sha(path)==h,"ZIP mismatch "+name)
        with zipfile.ZipFile(path) as z:
            need(z.testzip() is None and len(z.namelist())==len(set(z.namelist())),"CRC or duplicate path")
            for entry in z.infolist():
                q=pathlib.PurePosixPath(entry.filename)
                need(not q.is_absolute() and ".." not in q.parts and not ((entry.external_attr>>16)&0o170000)==0o120000,"Unsafe archive path")
            z.extractall(output/name)
def build(root):
    items={}
    bq,bo=ingest_apple(root/"baseline","apple-baseline",items)
    eq,eo=ingest_apple(root/"expansion","apple-expansion",items)
    fd=ingest_fdroid(root/"fdroid",items);gh=ingest_github(root/"github",items)
    edges,deferred=candidates(items)
    old=report(items,edges,deferred,{"apple_baseline_queries":bq,"apple_baseline_rows":bo,"apple_expansion_queries":eq,"apple_expansion_rows":eo,"fdroid_index_rows":fd,"github_search_rows":gh})
    need(old["source_entities"]=={"apple":3709,"fdroid":5057,"github":471} and len(edges)==669 and old["cross_source_pairs"]==13 and old["within_source_pairs"]==656 and deferred==[{"rule":"repository_url","size":63}],"Legacy audit drift")
    sources=[("apple",{"kind":"store","locator":"https://apps.apple.com/"}),("fdroid",{"kind":"index","locator":"https://f-droid.org/"}),("github",{"kind":"repository_index","locator":"https://github.com/"})]
    records=[]
    for (s,i),v in sorted(items.items()):
        k=s+":"+i
        # Full metadata stays in source archives, not in this projection.
        records.append((k,s,{"source":s,"source_id":i,"kind_hint":"repository" if s=="github" else "unknown","phases":sorted(v["phases"])}))
    obs=[]
    def add(s,sid,phase,file,row,h,date):
        k=s+":"+sid;oid="legacy:"+phase+":"+file+":"+str(row)
        obs.append((oid,k,{"record":k,"date":date,"locator":phase+"/"+file+"#row="+str(row),"payload_sha256":h}))
    for phase in ("baseline","expansion"):
        rootp=root/phase
        load(rootp,phase)
        for f in sorted(rootp.glob("*.log.json")):
            l=read(f)
            if l["status"]!="ok":continue
            raw=f.with_name(f.name.replace(".log.json",".raw.json"));facts=f.with_name(f.name.replace(".log.json",".facts.json"))
            if raw.exists() and sha(raw)==l.get("sha256"):payload=raw;rows=read(raw)["results"]
            else:payload=facts;rows=read(facts);need(sha(facts)==l["facts_sha256"],"Facts hash")
            h=sha(payload);date=(l.get("time_utc") or "2026-11-28")[:10]
            for i,r in enumerate(rows):add("apple",str(r["trackId"]),phase,payload.name,i,h,date)
    f=root/"fdroid"/"index-v2.json";h=sha(f)
    for i,sid in enumerate(read(f)["packages"]):add("fdroid",sid,"fdroid",f.name,i,h,"2026-11-28")
    for f in sorted((root/"github").glob("*.log.json")):
        l=read(f)
        if l["status"]!="ok":continue
        raw=f.with_name(f.name.replace(".log.json",".raw.json"));h=sha(raw)
        for i,r in enumerate(read(raw)["items"]):add("github",str(r["id"]),"github",raw.name,i,h,(l.get("time_utc") or "2026-11-28")[:10])
    need(len(obs)==12524 and len({o[0] for o in obs})==12524,"Observation mismatch")
    signals=[]
    for (a,b),rules in sorted(edges.items()):
        x,y=sorted((":".join(a),":".join(b)))
        signals.append((x,y,{"signals":sorted(rules),"status":"REVIEW_REQUIRED","origin":"legacy_v01","proof":"https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46133860479"}))
    return {"source":sources,"record":records,"observation":obs,"legacy_candidate":signals},old
def setup(r):
    with r.db:
        r.db.executescript("""
        CREATE TABLE IF NOT EXISTS legacy_candidate(a TEXT NOT NULL REFERENCES record(id), b TEXT NOT NULL REFERENCES record(id), payload TEXT NOT NULL, PRIMARY KEY(a,b), CHECK(a<b));
        CREATE TABLE IF NOT EXISTS integration_checkpoint(id TEXT PRIMARY KEY, manifest_hash TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS no_legacy_candidate_update BEFORE UPDATE ON legacy_candidate BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS no_legacy_candidate_delete BEFORE DELETE ON legacy_candidate BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS no_checkpoint_update BEFORE UPDATE ON integration_checkpoint BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS no_checkpoint_delete BEFORE DELETE ON integration_checkpoint BEGIN SELECT RAISE(ABORT,'immutable'); END;
        """)
def verify(r,data):
    for table,rows in data.items():
        for row in rows:
            if table=="legacy_candidate":
                got=r.db.execute("SELECT payload FROM legacy_candidate WHERE a=? AND b=?",row[:2]).fetchone()
            else:
                got=r.db.execute(f"SELECT payload FROM {table} WHERE id=?",(row[0],)).fetchone()
            need(got is not None and got[0]==canon(row[-1]),"Readback mismatch "+table)
def integrate(r,data,fail=False):
    setup(r);m=digest(data);key="legacy-v01"
    with r.db:
        r.db.execute("BEGIN IMMEDIATE")
        prev=r.db.execute("SELECT manifest_hash,payload FROM integration_checkpoint WHERE id=?",(key,)).fetchone()
        if prev:
            need(prev[0]==m and prev[1]==canon({"counts":{k:len(v) for k,v in data.items()}}),"Checkpoint mismatch")
            verify(r,data);return "already_integrated"
        for table,rows in data.items():
            n=2 if table=="source" else 3
            r.db.executemany(f"INSERT INTO {table} VALUES ("+",".join("?"*n)+")",[(*row[:-1],canon(row[-1])) for row in rows])
            if fail and table=="record":raise RuntimeError("Injected interruption")
        verify(r,data)
        r.db.execute("INSERT INTO integration_checkpoint VALUES (?,?,?)",(key,m,canon({"counts":{k:len(v) for k,v in data.items()}})))
    return "integrated"
def main():
    a=argparse.ArgumentParser();a.add_argument("--catalog",type=pathlib.Path,required=True);a.add_argument("--archives",type=pathlib.Path,required=True);a.add_argument("--output",type=pathlib.Path,required=True);x=a.parse_args()
    x.output.mkdir(parents=True,exist_ok=True)
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        root=pathlib.Path(temp);extract(x.archives,root);data,old=build(root)
    path=x.output/"integrated.sqlite";need(not path.exists(),"Refuse overwrite")
    g=pilot(x.catalog);r=Register(path,True);r.load(g)
    for s,rows in (("doc_web",read(P/"PROSPECTION_WEB_BUREAU_V01.json")["records_detail"]),("doc_target",read(P/"PROSPECTION_MATERIEL_COMMERCIAL_V01.json")["records"])):
        for row in rows:
            k=s+":"+row["id"];ent="provisional:"+k
            r.add_entity(ent,g.records[k]["kind_hint"],row["name"])
            r.append("attachment:"+k,{"category":"attachment","a":k,"b":ent,"relation":"REFERS_TO","state":"PROPOSED","evidence":["proof:"+k],"rationale":"Documentary hypothesis only; no adjudicated identity.","decision":None,"date":"2026-11-28","actor":"pilot_import"},0)
    before=r.audit()
    expected=read(P/"AUDIT_IDENTITY_REGISTRY_V03.json")
    need(all(before[k]==expected[k] for k in ("tables","chain_head","states","confirmed_attachments","current_assertions")),"V0.3 base drift")
    # Simulate interruption of atomic legacy import; no partial rows or marker may survive.
    try:integrate(r,data,True)
    except RuntimeError as e:need(str(e)=="Injected interruption","Unexpected interruption")
    else:raise ValueError("Fault not injected")
    need(r.audit()==before and r.db.execute("SELECT count(*) FROM integration_checkpoint").fetchone()[0]==0,"Rollback failed")
    need(integrate(r,data)=="integrated","Import failed");after=r.audit();r.close()
    r=Register(path);need(integrate(r,data)=="already_integrated","Resume failed");need(r.audit()==after,"Resume changed register");verify(r,data)
    counts=dict(r.db.execute("SELECT source_id,count(*) FROM record GROUP BY source_id").fetchall())
    n=r.db.execute("SELECT count(*) FROM legacy_candidate").fetchone()[0];r.close()
    need(sum(counts.values())==12956 and after["tables"]["observation"]==16245 and n==669,"Integrated totals")
    result={"register":after,"v03_base_verified":True,"source_counts":counts,"legacy_records":9237,"legacy_observations":12524,"legacy_candidates":n,"legacy_cross":old["cross_source_pairs"],"legacy_within":old["within_source_pairs"],"legacy_signals":old["pairs_by_signal"],"deferred":old["deferred_large_groups"],"existing_candidate_edges":45,"new_cross_block_matching":"NOT_RUN","archives_verified":4,"rollback_verified":True,"resume_verified":True,"checkpoint_manifest":digest(data),"confirmed_products":None,"database_sha256":sha(path),"limitations":"Distinct namespaces, not unique products. Legacy signals separate from nominal edges; no new cross-block matching or human adjudication. Local snapshot, not production; DB not uploaded. Date fallback for some historical observations is audit date, not source timestamp."}
    (x.output/"integration_report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("INTEGRATION_RESULT "+canon(result))
if __name__=="__main__":main()
