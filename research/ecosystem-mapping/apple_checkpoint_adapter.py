"""Apple adapter for the checkpoint engine. No network calls on import.
Live use requires an approved plan, storage and explicit CLI acknowledgement.
Archive minimal factual metadata only, not raw commercial descriptions or images.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from checkpoint_blocks import block,read,validate_plan

ENDPOINT="https://itunes.apple.com/search"
FIELDS=("trackId","bundleId","trackName","sellerName","trackViewUrl","primaryGenreName","version","currentVersionReleaseDate","price","currency","contentAdvisoryRating")
MARKETS={"ma","fr","us","gb"}
MAX_BYTES=32*1024*1024

def validate_query(q):
    if q.get("entity")!="software" or q.get("country") not in MARKETS or type(q.get("limit")) is not int or not 1<=q["limit"]<=200:
        raise ValueError("Invalid Apple query")
    if not isinstance(q.get("term"),str) or not q["term"].strip():
        raise ValueError("Empty term")

def provider(opener=urllib.request.urlopen,sleep=time.sleep,clock=time.monotonic):
    def fetch(q):
        validate_query(q)
        url=ENDPOINT+"?"+urllib.parse.urlencode({k:q[k] for k in ("term","country","entity","limit")})
        start=clock()
        sleep(4)
        started=dt.datetime.now(dt.timezone.utc).isoformat()
        network_start=clock()
        base={"url":url,"started_utc":started,"attempts":1,"minimum_pause_seconds":4}
        def result(status,payload):
            return status,base|payload|{"network_elapsed_seconds":max(0,clock()-network_start),"total_elapsed_seconds":max(0,clock()-start)}
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"ACPA-MSMDA-research-checkpoint/0.3","Accept":"application/json"})
            with opener(req,timeout=30) as response:
                # A redirected endpoint is not silently accepted.
                parsed=urllib.parse.urlsplit(response.geturl())
                if parsed.scheme!="https" or parsed.hostname!="itunes.apple.com" or parsed.path!="/search":
                    raise ValueError("Unexpected response endpoint")
                raw=response.read(MAX_BYTES+1)
                if len(raw)>MAX_BYTES:raise ValueError("Response exceeds safety limit")
            obj=json.loads(raw)
            rows=obj["results"]
            if not isinstance(rows,list) or type(obj.get("resultCount")) is not int or obj["resultCount"]!=len(rows) or len(rows)>q["limit"]:
                raise ValueError("Invalid response count")
            if any(not isinstance(row,dict) for row in rows):
                raise ValueError("Invalid result row")
            facts=[{k:row[k] for k in FIELDS if k in row} for row in rows]
            return result("ok",{"response_sha256":hashlib.sha256(raw).hexdigest(),"response_bytes":len(raw),"returned":len(rows),"capped":len(rows)==q["limit"],"missing_track_id":sum(row.get("trackId") is None for row in rows),"facts":facts,"raw_retained":False})
        except urllib.error.HTTPError as exc:
            return result("blocked" if exc.code in (401,403,429) else "error",{"http_status":exc.code,"retry_after":exc.headers.get("Retry-After") if exc.headers else None})
        except Exception as exc:
            return result("error",{"error_type":type(exc).__name__})
    return fetch

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plan",type=pathlib.Path,required=True);p.add_argument("--output",type=pathlib.Path,required=True)
    p.add_argument("--budget",type=int,required=True)
    p.add_argument("--approved-plan",action="store_true",help="Confirm approved plan, access, storage and absence of other Apple jobs")
    a=p.parse_args()
    if not a.approved_plan:raise SystemExit("Live access not authorized: approval flag required")
    if not 1<=a.budget<=25:raise SystemExit("Exploratory block budget must be 1–25")
    plan=read(a.plan);validate_plan(plan)
    for q in plan:validate_query(q)
    report=block(plan,a.output,provider(),a.budget,mode="apple-facts-v03")
    if report["blocked"] or report["status_counts"].get("error",0):raise SystemExit(2)

if __name__=="__main__":main()
