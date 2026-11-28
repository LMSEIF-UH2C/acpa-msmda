"""Agreement of locked, independent screening decisions; no generated ratings."""
import argparse
import collections
import csv
import json
import pathlib

LABELS = ("DIRECT", "COMPLEMENTAIRE", "NON_PERTINENT", "INCERTAIN")
INCLUDED = {"DIRECT", "COMPLEMENTAIRE"}

def load(path):
    rows = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            ident = row["review_id"]
            if not ident or ident in rows:
                raise ValueError("Missing or duplicate review_id")
            label = row["decision"].strip().upper()
            if label not in LABELS:
                raise ValueError(f"{ident}: decision missing or invalid")
            if not row["reason"].strip():
                raise ValueError(f"{ident}: justification required")
            if label in INCLUDED and not row["usage_eps"].strip():
                raise ValueError(f"{ident}: EPS scenario required")
            if label != "INCERTAIN" and not (row["evidence_url"].strip() and row["evidence_date"].strip()):
                raise ValueError(f"{ident}: source and date required")
            rows[ident] = {**row, "decision": label}
    if not rows:
        raise ValueError("Empty review")
    return rows

def agreement(pairs, labels):
    pairs = list(pairs)
    if not pairs:
        raise ValueError("Empty pair set")
    n = len(pairs)
    counts = collections.Counter(pairs)
    a = collections.Counter(x for x,y in pairs)
    b = collections.Counter(y for x,y in pairs)
    observed = sum(counts[x,x] for x in labels) / n
    expected = sum(a[x]*b[x] for x in labels) / (n*n)
    return {"n": n, "observed_agreement": observed, "expected_agreement": expected,
            "cohen_kappa": None if expected == 1 else (observed-expected)/(1-expected),
            "confusion_A_rows_B_columns": {x:{y:counts[x,y] for y in labels} for x in labels}}

def compare(a,b):
    if set(a)!=set(b):
        raise ValueError("Review IDs differ")
    for i in a:
        if any(a[i][k]!=b[i][k] for k in ("source","source_id")):
            raise ValueError(f"{i}: source identities differ")
    pairs = [(a[i]["decision"],b[i]["decision"]) for i in sorted(a)]
    # For binary analysis, uncertain cases are not treated as exclusions.
    determinate = [(x,y) for x,y in pairs if "INCERTAIN" not in (x,y)]
    binary = [("INCLUDE" if x in INCLUDED else "EXCLUDE","INCLUDE" if y in INCLUDED else "EXCLUDE") for x,y in determinate]
    return {"four_class":agreement(pairs,LABELS),
            "binary_determinate_only":agreement(binary,("INCLUDE","EXCLUDE")) if binary else None,
            "binary_omitted_uncertain":len(pairs)-len(binary),
            "disagreements":[{"review_id":i,"A":a[i]["decision"],"B":b[i]["decision"]} for i in sorted(a) if a[i]["decision"]!=b[i]["decision"]],
            "note":"Descriptive agreement on stratified calibration sample, not a population estimate. False negatives require independent adjudication; agreement does not establish validity."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("judge_a",type=pathlib.Path);p.add_argument("judge_b",type=pathlib.Path)
    p.add_argument("--output",type=pathlib.Path,required=True)
    x=p.parse_args()
    if x.judge_a.resolve()==x.judge_b.resolve(): raise ValueError("Two independent files required")
    report=compare(load(x.judge_a),load(x.judge_b))
    x.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
