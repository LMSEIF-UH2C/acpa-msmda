"""Structural coverage check, not curricular or pedagogical validation."""
import csv,json,pathlib
P=pathlib.Path(__file__).resolve().parent
R=P.parent.parent
def read(n):
    with (P/n).open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter=";"))
def validate():
    aps=read("COUVERTURE_APS_V01.csv");fn=read("COUVERTURE_FONCTIONS_V01.csv");ctx=read("COUVERTURE_CONTEXTES_V01.csv")
    old=json.loads((R/"data/aps_specialties.json").read_text(encoding="utf-8"))
    expected=[a["label"] for g in old["groups"] for a in g["activities"]]
    assert [a["aps"] for a in aps if a["origin"]=="ACPA_APS_EXISTANTE_ILLUSTRATIVE"]==expected
    families={f["id"] for f in json.loads((P/"query_matrix.json").read_text(encoding="utf-8"))["families"]}
    codes={r["code"] for r in json.loads((P/"framework_10d97p.json").read_text(encoding="utf-8"))["parameters"]}
    seen=set()
    for a in aps:
        for field in ("direct_family_candidates","complementary_family_candidates"):
            vals=set(a[field].split(","));assert vals<=families;seen.update(vals)
        assert a["status"]=="A_VALIDER_PEDAGOGIQUEMENT"
    for f in fn:
        vals=set(f["family_candidates"].split(","));assert vals<=families;seen.update(vals)
        assert set(f["example_10d97p_codes"].split(","))<=codes
    assert seen==families
    for rows,key in ((aps,"aps"),(fn,"function_id"),(ctx,"context_id")):
        assert len({x[key] for x in rows})==len(rows) and all(all(v.strip() for v in row.values()) for row in rows)
    assert (len(aps),len(fn),len(ctx))==(30,15,12)
    return {"existing_aps_preserved":len(expected),"proposed_extensions":len(aps)-len(expected),"functions":len(fn),"contexts":len(ctx),"families_linked":len(seen),"status":"structural only; all proposals pending expert validation"}
if __name__=="__main__":print(json.dumps(validate(),ensure_ascii=False,indent=2))
