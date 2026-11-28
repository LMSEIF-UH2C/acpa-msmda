"""Exploratory GitHub repository search, public metadata only; no code or assets downloaded."""
import argparse, collections, datetime as dt, hashlib, json, os, pathlib, time
import urllib.error, urllib.parse, urllib.request

def write(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=pathlib.Path,required=True)
    x=p.parse_args();out=x.output;out.mkdir(parents=True,exist_ok=True)
    matrix=json.loads((pathlib.Path(__file__).parent/"query_matrix.json").read_text(encoding="utf-8"))
    plan=[{"family":f["id"],"term":f["queries"]["en"][0],"q":f["queries"]["en"][0]+" in:name,description,readme is:public","per_page":30,"page":1} for f in matrix["families"]]
    write(out/"plan.json",plan)
    token=os.environ.get("GITHUB_TOKEN")
    if not token:raise ValueError("GITHUB_TOKEN missing")
    headers={"Accept":"application/vnd.github+json","Authorization":"Bearer "+token,"User-Agent":"ACPA-MSMDA-research-pilot","X-GitHub-Api-Version":"2022-11-28"}
    unique={};total=0;errors=0;truncated=0;incomplete=0
    for q in plan:
        time.sleep(7)
        url="https://api.github.com/search/repositories?"+urllib.parse.urlencode({k:q[k] for k in ("q","per_page","page")})
        log={"query":q,"url":url,"time_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=60) as response:
                raw=response.read()
                log["rate_remaining"]=response.headers.get("X-RateLimit-Remaining")
                log["rate_reset"]=response.headers.get("X-RateLimit-Reset")
            data=json.loads(raw);rows=data["items"]
            if not isinstance(rows,list):raise ValueError("Invalid items")
            # Keep raw response for internal audit only; never fetch repository contents.
            (out/(q["family"]+".raw.json")).write_bytes(raw)
            log.update(status="ok",sha256=hashlib.sha256(raw).hexdigest(),returned=len(rows),total_count=data.get("total_count"),incomplete_results=data.get("incomplete_results"))
            total+=len(rows)
            truncated+=int(data.get("total_count",0)>len(rows))
            incomplete+=int(bool(data.get("incomplete_results")))
            for row in rows:unique[row["id"]]=row
        except urllib.error.HTTPError as e:
            errors+=1;log.update(status="error",http_status=e.code,retry_after=e.headers.get("Retry-After"),rate_remaining=e.headers.get("X-RateLimit-Remaining"))
            write(out/(q["family"]+".log.json"),log)
            if e.code in (403,429):break
            continue
        except Exception as e:
            errors+=1;log.update(status="error",error_type=type(e).__name__)
        write(out/(q["family"]+".log.json"),log)
    logs=[json.loads(f.read_text(encoding="utf-8")) for f in out.glob("*.log.json")]
    report={"planned_queries":len(plan),"attempted_queries":len(logs),"successful_queries":sum(l["status"]=="ok" for l in logs),"failed_queries":errors,"unattempted_queries":len(plan)-len(logs),"truncated_queries":truncated,"incomplete_queries":incomplete,"raw_observations":total,"distinct_repository_ids":len(unique),"license_metadata":dict(collections.Counter((row.get("license") or {}).get("spdx_id") or "unknown" for row in unique.values())),"note":"Repository identifiers are not product identifiers. Search ranking, caps, language and incomplete results bias coverage. No eligibility, license verification or code analysis."}
    write(out/"report.json",report);print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors or len(logs)!=len(plan):raise SystemExit(2)
if __name__=="__main__":main()
