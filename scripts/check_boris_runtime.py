"""Execute pinned BORIS CLI on upstream public test project; validate actual output.
No student data. Do not substitute stored reference data for generated export.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from decimal import Decimal

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(root, output):
    root=Path(root).resolve()
    output=Path(output).resolve()
    output.mkdir(parents=True,exist_ok=True)
    project=root/"tests/files/test.boris"
    cmd=[sys.executable,"-m","boris.boris_cli","-p",str(project),"-o","observation #1","--command","export_events","csv"]
    report={"source_commit":"01143a7bd3ba9375cda03539d76d3e56391e8084","project_sha256":sha(project),"command":cmd,"status":"NOT_COMPLETED"}
    try:
        with tempfile.TemporaryDirectory() as d:
            proc=subprocess.run(cmd,cwd=d,text=True,capture_output=True,timeout=120)
            (output/"cli.stdout.txt").write_text(proc.stdout,encoding="utf-8")
            (output/"cli.stderr.txt").write_text(proc.stderr,encoding="utf-8")
            report["returncode"]=proc.returncode
            paths=list(Path(d).glob("*.csv"))
            report["generated_files"]=[p.name for p in paths]
            if proc.returncode!=0 or len(paths)!=1 or paths[0].stat().st_size==0:
                raise RuntimeError("Expected one nonempty actual export")
            raw=paths[0].read_bytes()
            exported=output/"actual-export.csv"
            exported.write_bytes(raw)
            report["export_sha256"]=sha(exported)
            rows=list(csv.reader(raw.decode("utf-8-sig").splitlines()))
            header_index=next((i for i,r in enumerate(rows) if {"Time","Subject","Behavior","Status"}<=set(r)),None)
            if header_index is None:
                report["headers_observed"]=rows[:3]
                raise ValueError("Unrecognized actual export schema")
            header=rows[header_index]
            records=[dict(zip(header,r)) for r in rows[header_index+1:] if any(r)]
            report["header"]=header
            report["header_index"]=header_index
            report["rows"]=len(records)
            original=json.loads(project.read_text(encoding="utf-8"))["observations"]["observation #1"]["events"]
            # The project has eight state events. Compare every event, not just totals.
            expected=[(Decimal(str(t)),s,b) for t,s,b,*_ in original]
            actual=[(Decimal(r["Time"]),r["Subject"],r["Behavior"]) for r in records]
            report["source_event_count"]=len(expected)
            report["actual_event_count"]=len(actual)
            if sorted(actual)!=sorted(expected):
                raise AssertionError("Actual events differ from full project source")
            pending={}
            totals={}
            for r in records:
                key=(r["Subject"],r["Behavior"],r.get("Modifiers",""))
                time=Decimal(r["Time"])
                status=r["Status"].upper()
                if status=="START":
                    if key in pending: raise ValueError("Duplicate start")
                    pending[key]=time
                elif status=="STOP":
                    if key not in pending: raise ValueError("Unpaired stop")
                    duration=time-pending.pop(key)
                    if duration<0: raise ValueError("Negative duration")
                    totals[key[0]]=totals.get(key[0],Decimal(0))+duration
                else:
                    raise ValueError("Unexpected state event status")
            if pending: raise ValueError("Unpaired start")
            report["duration_totals_seconds"]={k:str(v) for k,v in totals.items()}
            if totals!={"subject1":Decimal("16.875"),"subject2":Decimal("7.675")}:
                raise AssertionError("Duration mismatch")
            report["status"]="PASS_ACTUAL_BORIS_EXPORT"
    except Exception as exc:
        report["status"]="FAIL_OR_BLOCKED"
        report["error"]=str(exc)
        raise
    finally:
        (output/"results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        print("A5_BORIS_RUNTIME "+json.dumps(report),flush=True)

if __name__=="__main__":
    run(*sys.argv[1:])
