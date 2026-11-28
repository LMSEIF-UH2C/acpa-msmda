"""Known-item retrieval check on archived sources. Not independent recall estimation."""
import argparse,collections,json,pathlib
from normalize_identity import ingest_apple,ingest_fdroid,ingest_github
P=pathlib.Path(__file__).resolve().parent
def check(items,targets):
    result=[]
    for w in targets:
        s,k=w["source"],w["key"]
        if s not in ("apple","fdroid","github"):raise ValueError("Unknown source")
        matches=sorted([sid for (source,sid),v in items.items() if source==s and (k in v["repo"] if s=="github" else sid==k)])
        result.append({**w,"status":"FOUND_EXACT" if len(matches)==1 else "AMBIGUOUS" if matches else "NOT_OBSERVED","matched_source_ids":matches,
                       "phases":sorted(set().union(*(items[(s,sid)]["phases"] for sid in matches)))})
    return {"results":result,"by_source":{s:dict(collections.Counter(x["status"] for x in result if x["source"]==s)) for s in sorted({x["source"] for x in result})},
            "by_status":dict(collections.Counter(x["status"] for x in result)),"note":"Purposive retrospective known-item sample; not an independent holdout or a recall estimate. Source-specific IDs/repository links only. Not observed does not mean unavailable, irrelevant or excluded."}
def main():
    a=argparse.ArgumentParser()
    for n in ("baseline","expansion","fdroid","github","output"):a.add_argument("--"+n,type=pathlib.Path,required=True)
    x=a.parse_args();items={}
    ingest_apple(x.baseline,"apple-baseline",items);ingest_apple(x.expansion,"apple-expansion",items)
    ingest_fdroid(x.fdroid,items);ingest_github(x.github,items)
    targets=json.loads((P/"KNOWN_ITEM_WITNESSES_V01.json").read_text(encoding="utf-8"))
    if len({t["id"] for t in targets})!=len(targets):raise ValueError("Duplicate witness")
    r=check(items,targets);r["source_entities"]=len(items)
    x.output.mkdir(parents=True,exist_ok=True);(x.output/"report.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
