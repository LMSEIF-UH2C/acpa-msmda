"""Generate blind calibration forms and descriptive agreement; no fabricated judgments."""
import argparse,csv,collections,datetime as dt,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
APPS=("APPLICABLE","SO","A_EXAMINER")
SCORES=("1","2","3","4","5")
PROOFS={"TEST_SCENARIO","AUDIT_DOCUMENTE","DONNEES_EMPIRIQUES"}
FIXED=("review_id","case_id","unit","code","original_label","minimum_evidence","indicator","verification")
FIELDS=FIXED+("applicability","rating","evidence_type","evidence_ref","evidence_date","version_context","reason")
EXPERT_FIELDS=("code","original_label","proposed_unit","minimum_evidence","indicator","verification","decision","fidelite","pertinence","observabilite","unite_proposee","preuve_proposee","ancre_1","ancre_3","ancre_5","justification")
def matrix():
    with (HERE/"OPERATIONNALISATION_10D97P_V01.csv").open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f,delimiter=";"))
def cases():
    return json.loads((HERE/"CALIBRATION_CASES_V01.json").read_text(encoding="utf-8"))
def expected():
    return [dict(review_id=c["id"]+"-"+p["code"],case_id=c["id"],unit=p["proposed_unit"],**{k:p[k] for k in ("code","original_label","minimum_evidence","indicator","verification")})
            for c in cases() for p in matrix() if p["proposed_unit"] in c["units"]]
def write(path,fields,rows):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",delimiter=";");w.writeheader();w.writerows(rows)
def generate(out):
    out.mkdir(parents=True,exist_ok=True);rows=expected()
    for judge in ("A","B"):
        write(out/f"cotation_{judge}.csv",FIELDS,rows)
        write(out/f"expert_{judge}.csv",EXPERT_FIELDS,matrix())
    write(out/"configuration_cas.csv",("case_id","product_or_process","version","platform","settings","test_date","evidence_packet_id","constraints"),[{"case_id":c["id"]} for c in cases()])
    meta={"design":"exploratory calibration, blank forms","cases":len(cases()),"parameters":len(matrix()),"rating_rows_per_judge":len(rows),"expert_rows_per_judge":len(matrix()),"rows_by_case":dict(collections.Counter(x["case_id"] for x in rows)),"file_hashes":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob("*.csv"))}}
    (out/"manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps(meta,ensure_ascii=False,indent=2))
    return meta
def load(path,reference):
    result={}
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f,delimiter=";")
        if tuple(reader.fieldnames or ())!=FIELDS:raise ValueError("Unexpected columns")
        for raw in reader:
            if None in raw or any(v is None for v in raw.values()):raise ValueError("Malformed row")
            i=raw["review_id"]
            if i in result or i not in reference:raise ValueError("Unknown/duplicate ID "+i)
            if any(raw[k]!=reference[i][k] for k in FIXED):raise ValueError("Changed reference "+i)
            row={k:v.strip() for k,v in raw.items()};a=row["applicability"];rating=row["rating"]
            if a not in APPS or not row["reason"]:raise ValueError("Applicability/justification "+i)
            if a=="APPLICABLE":
                if rating not in SCORES+("NR",):raise ValueError("Missing/invalid rating "+i)
            elif rating:raise ValueError("Rating forbidden for SO/uncertain "+i)
            if rating in SCORES:
                if row["evidence_type"]!=row["minimum_evidence"]:raise ValueError("Evidence requirement "+i)
                if not all(row[k] for k in ("evidence_ref","evidence_date","version_context")):raise ValueError("Evidence metadata "+i)
                dt.date.fromisoformat(row["evidence_date"])
            elif row["evidence_type"] and row["evidence_type"] not in PROOFS:raise ValueError("Evidence type "+i)
            result[i]=row
    if set(result)!=set(reference):raise ValueError("Incomplete review")
    return result
def agreement(pairs,labels,ordinal=False):
    n=len(pairs)
    if not n:return None
    count=collections.Counter(pairs);a=collections.Counter(x for x,y in pairs);b=collections.Counter(y for x,y in pairs)
    exact=sum(count[x,x] for x in labels)/n
    w=lambda x,y:abs(int(x)-int(y))/4 if ordinal else int(x!=y)
    obs=sum(count[x,y]*w(x,y) for x in labels for y in labels)/n
    exp=sum(a[x]*b[y]*w(x,y) for x in labels for y in labels)/(n*n)
    return {"n":n,"exact_agreement":exact,"kappa_linear_weighted" if ordinal else "cohen_kappa":None if exp==0 else 1-obs/exp,
            "within_one":sum(abs(int(x)-int(y))<=1 for x,y in pairs)/n if ordinal else None,
            "confusion_A_rows_B_columns":{x:{y:count[x,y] for y in labels} for x in labels}}
def compare(a,b):
    def stats(ids):
        ap=[(a[i]["applicability"],b[i]["applicability"]) for i in ids]
        ratings=[(a[i]["rating"],b[i]["rating"]) for i in ids if a[i]["applicability"]==b[i]["applicability"]=="APPLICABLE" and a[i]["rating"] in SCORES and b[i]["rating"] in SCORES]
        return {"applicability":agreement(ap,APPS),"ordinal":agreement(ratings,SCORES,True),"paired_numeric":len(ratings),"not_paired_numeric":len(ids)-len(ratings),
                "A_status":dict(collections.Counter(a[i]["rating"] or a[i]["applicability"] for i in ids)),
                "B_status":dict(collections.Counter(b[i]["rating"] or b[i]["applicability"] for i in ids))}
    ids=sorted(a)
    return {"overall_descriptive":stats(ids),"by_unit":{u:stats([i for i in ids if a[i]["unit"]==u]) for u in sorted({a[i]["unit"] for i in ids})},
            "by_case":{c:stats([i for i in ids if a[i]["case_id"]==c]) for c in sorted({a[i]["case_id"] for i in ids})},
            "disagreements":[{"review_id":i,"A":[a[i]["applicability"],a[i]["rating"]],"B":[b[i]["applicability"],b[i]["rating"]]} for i in ids if (a[i]["applicability"],a[i]["rating"])!=(b[i]["applicability"],b[i]["rating"])],
            "note":"Exploratory dependent rows within cases and parameters; descriptive only, no naive independent-row CI, no validity conclusion or automatic acceptance. NR/SO/uncertain excluded from ordinal comparison; coverage reported."}
def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
    g=s.add_parser("generate");g.add_argument("--output",type=pathlib.Path,required=True)
    v=s.add_parser("compare");v.add_argument("judge_a",type=pathlib.Path);v.add_argument("judge_b",type=pathlib.Path);v.add_argument("--output",type=pathlib.Path,required=True)
    a=p.parse_args()
    if a.cmd=="generate":generate(a.output)
    else:
        if a.judge_a.resolve()==a.judge_b.resolve():raise ValueError("Two files required")
        ref={x["review_id"]:x for x in expected()}
        result=compare(load(a.judge_a,ref),load(a.judge_b,ref))
        a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":main()
