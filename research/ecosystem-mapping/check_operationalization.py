"""Structural checks only; no evidence or ratings invented."""
import csv,json,pathlib
P=pathlib.Path(__file__).resolve().parent
def validate():
    orig=json.loads((P/"framework_10d97p.json").read_text(encoding="utf-8"))["parameters"]
    with (P/"OPERATIONNALISATION_10D97P_V01.csv").open(encoding="utf-8",newline="") as f:rows=list(csv.DictReader(f,delimiter=";"))
    assert len(rows)==len(orig)==97
    assert len({r["code"] for r in rows})==97
    assert [(r["code"],r["original_label"]) for r in rows]==[(r["code"],r["label"]) for r in orig]
    units={"PRODUIT_VARIANTE","USAGE_PEDAGOGIQUE","PROCESSUS_CADRE","SYSTEME_ECOSYSTEME"}
    proofs={"TEST_SCENARIO","AUDIT_DOCUMENTE","DONNEES_EMPIRIQUES"}
    for r in rows:
        assert r["proposed_unit"] in units and r["minimum_evidence"] in proofs
        assert r["indicator"].strip() and r["verification"].strip() and r["status"]=="PROPOSE_A_VALIDER"
        assert int(r["original_page"])==2+(int(r["code"].split("_")[0][1:])-1)//2
    from collections import Counter
    return {"parameters":len(rows),"units":dict(Counter(r["proposed_unit"] for r in rows)),"evidence_types":dict(Counter(r["minimum_evidence"] for r in rows)),"status":"structural checks passed, not scientific validation"}
if __name__=="__main__":print(json.dumps(validate(),ensure_ascii=False,indent=2))
