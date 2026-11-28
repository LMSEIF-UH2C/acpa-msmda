"""Validate targeted scenario design and exact lexical/nominal gaps, offline."""
import argparse,collections,csv,hashlib,json,pathlib
from plan_collection_v03 import historical,term_norm
from collect_sill import catalog_rows,names
from identity_graph import unzip,need
from normalize_identity import name_key
P=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def csvrows(n):
    with (P/n).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f,delimiter=";"))
def ix(rows,idkey,labels):
    d=collections.defaultdict(set)
    for r in rows:
        for v in labels(r):
            k=name_key(v)
            if k:d[k].add(str(r[idkey]))
    return d
def matches(labels,index):return set().union(*(index.get(name_key(n),set()) for n in labels))
def main():
    a=argparse.ArgumentParser();a.add_argument("--output",type=pathlib.Path,required=True);a.add_argument("--catalog",type=pathlib.Path,required=True);x=a.parse_args();x.output.mkdir(parents=True,exist_ok=True)
    d=read(P/"COVERAGE_TARGETED_PLAN_V02.json");cases=d["cases"];w=d["witnesses"];ps=d["probes"];modern=read(P/"query_matrix_v02_proposed.json")
    fids={r["function_id"] for r in csvrows("COUVERTURE_FONCTIONS_V01.csv")};kids={r["context_id"] for r in csvrows("COUVERTURE_CONTEXTES_V01.csv")};aps={r["aps"] for r in csvrows("COUVERTURE_APS_V01.csv")};families={r["id"] for r in modern["families"]}
    cids={r["id"] for r in cases};need(len(cids)==len(cases),"Duplicate scenario")
    for c in cases:
        need(c["aps"] in aps and set(c["functions"])<=fids and set(c["contexts"])<=kids and set(c["families"])<=families,"Unknown reference")
        need(c["constraints"] and c["fallback"] and c["verification"] and c["status"]=="PROPOSED_NOT_CURRICULUM_VALIDATED","Missing constraints")
    need(len({r["id"] for r in w})==len(w),"Duplicate witness")
    for r in w:need(set(r["scenarios"])<=cids and r["official_evidence_url"].startswith("https://") and r["limits"] and r["eligibility"]=="NOT_ASSESSED","Witness scope")
    old={term_norm(t) for ts in historical(P.parents[1]/"tools/catalog/collect_appstore.py").values() for t in ts};new={term_norm(t) for f in modern["families"] for ts in f["queries"].values() for t in ts};need(len(old|new)==398,"Lexical frame")
    keys={term_norm(r["term"]) for r in ps};need(len(keys)==len(ps),"Duplicate proposed probe")
    for r in ps:need(r["case_id"] in cids and r["family"] in families and r["language"] in {"en","fr","ar"},"Probe scope")
    lex=[dict(r,exact_historical=term_norm(r["term"]) in old,exact_modern=term_norm(r["term"]) in new) for r in ps]
    b=x.catalog.read_bytes();need(hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()=="39b32ebbdf33b49a3fb0bb669f8a0809d0e72995","Catalogue mismatch")
    rows=catalog_rows(json.loads(b));base=P/"evidence/2026-11-28"
    si=unzip(base/"sill.zip","sill_product_inventory.json","8bb73ecd9d326547bd93a1db570ab37501a5fec25cba61cc10005ba610f7bc27");wi=unzip(base/"wikidata.zip","inventory.json","e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46")
    prior=read(P/"PROSPECTION_WEB_BUREAU_V01.json")["records_detail"]+read(P/"PROSPECTION_MATERIEL_COMMERCIAL_V01.json")["records"]
    indexes={"catalog":ix(rows,"id",lambda r:names(r["name"])+names(r.get("aliases"))),"sill":ix(si,"sill_id",lambda r:r["names"]),"wikidata":ix(wi,"qid",lambda r:r["labels"].values()),"prior_documentary":ix(prior,"id",lambda r:[r["name"]]+r["alias_probes"])}
    results=[{"id":r["id"],"nominal_candidates":{k:len(matches(r["alias_probes"],v)) for k,v in indexes.items()},"status":"NOT_ASSESSED"} for r in w]
    out={"scenarios":len(cases),"functions_covered_in_proposed_design":len(set().union(*(set(c["functions"]) for c in cases))),"contexts_covered_in_proposed_design":len(set().union(*(set(c["contexts"]) for c in cases))),"families_linked_in_proposed_design":len(set().union(*(set(c["families"]) for c in cases))),"probes":len(ps),"probes_exact_absent_from_398":sum(not r["exact_historical"] and not r["exact_modern"] for r in lex),"lexical_results":lex,"witnesses":results,"nominal_match_counts":{k:sum(bool(r["nominal_candidates"][k]) for r in results) for k in indexes},"limitations":"Structural design and documentary declarations, exact name signals only, no confirmed product identity, no new network collection or curriculum validation. No coverage proportion of market. No probes adopted."}
    (x.output/"targeted_coverage.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print("TARGETED_COVERAGE "+json.dumps(out,ensure_ascii=False,separators=(",",":")))
if __name__=="__main__":main()
