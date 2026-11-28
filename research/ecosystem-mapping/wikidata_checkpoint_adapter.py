"""Bounded live WDQS checkpoint adapter, four frozen direct P31 requests.
Only CC0 structured results. No retry, no redirects, no new collection after an error.
"""
import argparse,base64,collections,datetime,hashlib,json,os,pathlib,re,time
import urllib.request,urllib.parse,urllib.error
from checkpoint_blocks import block,recover,digest,read,save
from collect_wikidata import query,parse,ENDPOINT,MAX_BYTES
P=pathlib.Path(__file__).resolve().parent
MODE="wikidata-cc0-checkpoint-v01"
PLAN_FILE=P/"WIKIDATA_CHECKPOINT_PLAN_V01.json"
USER_AGENT="ACPA-MSMDA-research-checkpoint/0.1 (https://github.com/LMSEIF-UH2C/acpa-msmda)"
def require(ok,msg):
    if not ok:raise ValueError(msg)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def identity(q):return digest({k:q[k] for k in ("source","family","qid","limit","relation","endpoint","query_sha256")})
def plan():
    rows=read(PLAN_FILE)
    require(len(rows)==4,"Expected four fixed requests")
    approved={e["family"]:e for e in read(P/"WIKIDATA_PLAN_V01.json")}
    out=[]
    for r in rows:
        require(r==approved[r["family"]],"Plan differs from approved class")
        q=query(r["qid"],r["limit"])
        e={**r,"source":"wikidata","endpoint":ENDPOINT,"query_sha256":hashlib.sha256(q.encode()).hexdigest()}
        e["request_id"]=identity(e);out.append(e)
    validate(out);return out
def validate(rows):
    require(isinstance(rows,list) and len(rows)==4,"Invalid plan size")
    ids=[]
    for r in rows:
        require(r["source"]=="wikidata" and r["endpoint"]==ENDPOINT and r["relation"]=="P31 direct" and r["limit"]==101,"Invalid source scope")
        q=query(r["qid"],r["limit"]);require(hashlib.sha256(q.encode()).hexdigest()==r["query_sha256"],"Query digest mismatch")
        i=identity(r);require(i==r["request_id"],"Request ID mismatch");ids.append(i)
    require(len(set(ids))==len(ids),"Duplicate requests");return ids
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None
def provider(opener=None,sleep=time.sleep,clock=time.monotonic):
    if opener is None:opener=urllib.request.build_opener(NoRedirect()).open
    def fetch(r):
        q=query(r["qid"],r["limit"]);require(hashlib.sha256(q.encode()).hexdigest()==r["query_sha256"],"Unexpected query")
        url=ENDPOINT+"?"+urllib.parse.urlencode({"query":q,"format":"json"})
        sleep(4);start=clock();meta={"started_utc":utc(),"request_url":url,"query_sha256":r["query_sha256"],"attempts":1,"minimum_pause_seconds":4}
        def finish(status,payload):return status,meta|payload|{"finished_utc":utc(),"network_elapsed_seconds":max(0,clock()-start)}
        try:
            req=urllib.request.Request(url,headers={"Accept":"application/sparql-results+json","User-Agent":USER_AGENT})
            with opener(req,timeout=15) as resp:
                require(resp.status==200 and resp.geturl()==url,"Unexpected endpoint/status")
                raw=resp.read(MAX_BYTES+1)
            require(len(raw)<=MAX_BYTES,"Response too large")
            obj=json.loads(raw);require(set(obj["head"]["vars"])=={"item","en","fr","ar"},"Unexpected response fields")
            require(all(set(b)<={"item","en","fr","ar"} for b in obj["results"]["bindings"]),"Unexpected bindings")
            found=parse(raw)
            return finish("ok",{"http_status":200,"response_sha256":hashlib.sha256(raw).hexdigest(),"response_bytes":len(raw),"raw_b64":base64.b64encode(raw).decode(),"returned":len(found),"cap_reached":len(found)==r["limit"]})
        except urllib.error.HTTPError as e:
            return finish("blocked" if e.code in (401,403,429) else "error",{"http_status":e.code,"retry_after":e.headers.get("Retry-After") if e.headers else None})
        except Exception as e:return finish("error",{"error_type":type(e).__name__})
    return fetch
def checked_records(out):
    rows=plan();records=recover(rows,out,MODE,validate)
    for r in records.values():
        if r["status"]!="ok":continue
        p=r["payload"];raw=base64.b64decode(p["raw_b64"],validate=True)
        require(len(raw)==p["response_bytes"] and hashlib.sha256(raw).hexdigest()==p["response_sha256"],"Raw response corrupted")
        require(len(parse(raw))==p["returned"],"Reparse count mismatch")
    return records
def hashes(out):
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob("*.record.json"))}
def stage(out,n):
    rows=plan();ids=validate(rows);out.mkdir(parents=True,exist_ok=True)
    if n==1:
        require(not list(out.iterdir()),"Stage 1 must start empty")
        report=block(rows,out,provider(),2,mode=MODE,validator=validate,stop_on_error=True)
        recs=checked_records(out);save(out/"handoff.json",{"stage":1,"plan_sha256":digest(rows),"records_sha256":hashes(out),"progress":report,"runner":os.environ.get("RUNNER_NAME"),"job":os.environ.get("GITHUB_JOB"),"run_id":os.environ.get("GITHUB_RUN_ID")})
        print("WD_STAGE1 "+json.dumps(report,sort_keys=True));return
    before=read(out/"handoff.json");require(before["plan_sha256"]==digest(rows),"Plan mismatch")
    require(before["run_id"]==os.environ.get("GITHUB_RUN_ID") and before["job"]!=os.environ.get("GITHUB_JOB"),"Not a different job in same run")
    require(before["records_sha256"]==hashes(out),"Transfer hash mismatch")
    initial=checked_records(out)
    if not (len(initial)==2 and set(initial)==set(ids[:2]) and all(r["status"]=="ok" for r in initial.values())):
        print("WD_RESUME_STOP "+json.dumps({"reason":"first block incomplete or blocked; no new requests","progress":before["progress"]}))
        return
    report=block(rows,out,provider(),2,mode=MODE,validator=validate,stop_on_error=True)
    require(all(hashes(out).get(k)==v for k,v in before["records_sha256"].items()),"Prior record modified")
    recs=checked_records(out);save(out/"resume.json",{"stage":2,"job":os.environ.get("GITHUB_JOB"),"runner":os.environ.get("RUNNER_NAME"),"run_id":os.environ.get("GITHUB_RUN_ID"),"prior_records_unchanged":True,"progress":report,"records_sha256":hashes(out)})
    print("WD_STAGE2 "+json.dumps(report,sort_keys=True))
def audit(out):
    rows=plan();ids=validate(rows);recs=checked_records(out);before=read(out/"handoff.json")
    require(all(hashes(out).get(k)==v for k,v in before["records_sha256"].items()),"First block modified")
    if not (out/"resume.json").exists():
        result={"status":"STOPPED_AFTER_FIRST_BLOCK","first":before["progress"],"final_records":len(recs),"second_network_attempts":0}
    else:
        after=read(out/"resume.json");require(after["records_sha256"]==hashes(out),"Final transfer hash mismatch")
        require(after["job"]!=before["job"] and after["run_id"]==before["run_id"],"Job provenance mismatch")
        first=before["progress"];second=after["progress"]
        require(first["new_attempts"]==2 and second["reused_successes"]==2 and second["new_attempts"]<=2,"Invalid resume count")
        seen=set();obs=0;per=[]
        for i in ids:
            if i not in recs:continue
            r=recs[i];p=r["payload"];found=set(parse(base64.b64decode(p["raw_b64"]))) if r["status"]=="ok" else set()
            per.append({"family":r["query"]["family"],"status":r["status"],"http_status":p.get("http_status"),"returned":p.get("returned"),"cap_reached":p.get("cap_reached"),"network_elapsed_seconds":p.get("network_elapsed_seconds"),"new_qids_in_order":len(found-seen),"started_utc":p["started_utc"],"finished_utc":p["finished_utc"]});seen|=found;obs+=len(found)
        # A third job replays the completed checkpoint offline; provider must never be called.
        offline=None
        if second["complete_success"]:
            def forbidden(q):raise AssertionError("Network replay forbidden")
            offline=block(rows,out,forbidden,4,mode=MODE,validator=validate,stop_on_error=True)
            require(offline["new_attempts"]==0 and offline["reused_successes"]==4,"Unexpected repeat")
        result={"status":"SUCCESS" if offline else "STOPPED_AFTER_SECOND_BLOCK","first":first,"second":second,"offline_replay":offline,"first_job":before["job"],"second_job":after["job"],"audit_job":os.environ.get("GITHUB_JOB"),"runner_labels":[before["runner"],after["runner"],os.environ.get("RUNNER_NAME")],"first_records_unchanged":True,"final_records":len(recs),"observations":obs,"distinct_qids":len(seen),"repeated_qid_observations":obs-len(seen),"per_query":per,"plan_sha256":digest(rows),"checkpoint_manifest_sha256":digest(hashes(out))}
    result["scope"]="Live sequential Wikidata only; different hosted jobs; no claims of reproducibility of mutable remote results, no automatic product merge."
    save(out/"cross_runner_audit.json",result);print("WD_CROSS_RUNNER "+json.dumps(result,sort_keys=True))
def main():
    a=argparse.ArgumentParser();a.add_argument("--output",type=pathlib.Path,required=True);a.add_argument("--stage",choices=["1","2","audit"],required=True);a.add_argument("--approved-bounded-pilot",action="store_true");x=a.parse_args()
    if x.stage=="audit":audit(x.output)
    else:
        require(x.approved_bounded_pilot,"Explicit bounded pilot required");stage(x.output,int(x.stage))
if __name__=="__main__":main()
