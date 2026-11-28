"""A5 native BORIS export test, distinct from failed upstream CLI.
Protocol: PLAN_RETEST_BORIS_EXPORT_NATIF_V01.md. No student data.
"""
import csv
import hashlib
import io
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path
import sys
import traceback

UPSTREAM = "01143a7bd3ba9375cda03539d76d3e56391e8084"
OBS = "observation #1"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ms(x):
    v = Decimal(str(x)) * 1000
    if not v.is_finite() or v != v.to_integral_value():
        raise ValueError("Expected integer milliseconds")
    return int(v)

def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    project = root / "tests/files/test.boris"
    out = output / "actual-native-export.csv"
    if out.exists():
        raise FileExistsError("Refuse stale export")
    digest = sha(project)
    report = {"source_commit": UPSTREAM, "project_sha256": digest, "route": "UNMODIFIED_NATIVE_EXPORT_NOT_CLI",
              "observation": OBS, "interval_seconds": [0, 60], "subjects": ["subject1", "subject2"],
              "behaviors": ["p", "s"], "status": "NOT_COMPLETED"}
    try:
        from boris import config as cfg, export_observation, project_functions, version
        report["boris_version"] = version.__version__
        _, changed, pj, message = project_functions.open_project_json(str(project))
        report["loader"] = {"changed_in_memory": changed, "message": str(message)}
        if "error" in pj:
            raise RuntimeError(str(pj["error"]))
        parameters = {cfg.SELECTED_SUBJECTS: ["subject1", "subject2"], cfg.SELECTED_BEHAVIORS: ["p", "s"],
                      "time": cfg.TIME_ARBITRARY_INTERVAL, cfg.START_TIME: Decimal(0), cfg.END_TIME: Decimal(60)}
        ok, message = export_observation.export_tabular_events(
            pj, parameters, OBS, pj[cfg.OBSERVATIONS][OBS], pj[cfg.ETHOGRAM], str(out), "csv")
        report["native_return"] = {"ok": bool(ok), "message": str(message)}
        if not ok or not out.is_file() or out.stat().st_size == 0:
            raise RuntimeError("Native function did not produce a nonempty successful export")
        report["export_sha256"] = sha(out)
        rows = list(csv.reader(io.StringIO(out.read_text(encoding="utf-8-sig"), newline="")))
        if not rows:
            raise ValueError("Empty CSV")
        header = rows[0]
        report["header"] = header
        required = {"Observation id", "Time", "Subject", "Behavior", "Behavior type"}
        if not required <= set(header) or len(set(header)) != len(header):
            raise ValueError("Unexpected native schema")
        if any(len(row) != len(header) for row in rows[1:]):
            raise ValueError("Nonrectangular export")
        records = [dict(zip(header, row)) for row in rows[1:]]
        original = json.loads(project.read_text(encoding="utf-8"), parse_float=Decimal)["observations"][OBS]["events"]
        expected = [(ms(t), s, b) for t, s, b, *_ in original]
        actual = [(ms(r["Time"]), r["Subject"], r["Behavior"]) for r in records]
        report["source_event_count"], report["actual_event_count"] = len(expected), len(actual)
        report["event_match"] = Counter(expected) == Counter(actual)
        if len(expected) != 8 or not report["event_match"] or any(r["Observation id"] != OBS for r in records):
            raise AssertionError("Event identity, time or count mismatch")
        pending = {}
        intervals = []
        for r in sorted(records, key=lambda r: ms(r["Time"])):
            key = (r["Subject"], r["Behavior"])
            t, status = ms(r["Time"]), r["Behavior type"].strip().upper()
            if status == "START":
                if key in pending:
                    raise ValueError("Duplicate start")
                pending[key] = t
            elif status == "STOP":
                if key not in pending:
                    raise ValueError("Unpaired stop")
                start = pending.pop(key)
                if t < start:
                    raise ValueError("Negative interval")
                intervals.append([key[0], key[1], start, t, t-start])
            else:
                raise ValueError("Unexpected behavior type: " + status)
        report["intervals_ms"] = intervals
        expected_intervals = [["subject1","s",3300,7750,4450],["subject1","s",9900,16200,6300],
                              ["subject1","s",18350,24475,6125],["subject2","s",38425,46100,7675]]
        if pending or sorted(intervals) != sorted(expected_intervals):
            raise AssertionError("State interval mismatch")
        report["totals_ms"] = {s: sum(r[4] for r in intervals if r[0] == s) for s in ("subject1","subject2")}
        if report["totals_ms"] != {"subject1":16875,"subject2":7675}:
            raise AssertionError("Duration mismatch")
        report["status"] = "PASS_NATIVE_EXPORT_ONLY"
    except Exception as exc:
        report["status"] = "FAIL_OR_BLOCKED"
        report["error"] = repr(exc)
        (output/"native-traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
    finally:
        report["source_unchanged"] = sha(project) == digest
        if not report["source_unchanged"]:
            report["status"] = "FAIL_SOURCE_CHANGED"
        (output/"native-results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("A5_BORIS_NATIVE " + json.dumps(report), flush=True)
        if not report["source_unchanged"]:
            raise AssertionError("Original project modified")

if __name__ == "__main__":
    run(*sys.argv[1:])
