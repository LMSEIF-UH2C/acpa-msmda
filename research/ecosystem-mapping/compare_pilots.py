"""Audit des deux pilotes et tirage exploratoire reproductible; aucun ajout catalogue."""
import argparse, collections, csv, hashlib, json, pathlib, random, re
from urllib.parse import urlsplit

def read(p):
    return json.loads(p.read_text(encoding="utf-8"))

def loc(v):
    if isinstance(v,dict):
        return v.get("fr") or v.get("en-US") or next(iter(v.values()),"")
    return v or ""

def historical_ids(tools):
    a,f=set(),set()
    for t in tools:
        i=t.get("id","")
        if i.startswith("ios-") and i[4:].isdigit(): a.add(i[4:])
        if i.startswith("fd-"): f.add(i[3:])
        if i.startswith("apt-"): f.add(i[4:])
        u=urlsplit(t.get("source_url") or "")
        if u.hostname=="apps.apple.com":
            m=re.search(r"/id(\d+)(?:/|$)",u.path)
            if m:a.add(m.group(1))
        if u.hostname=="f-droid.org":
            m=re.search(r"/packages/([^/]+)",u.path)
            if m:f.add(m.group(1))
    return a,f

def main():
    p=argparse.ArgumentParser()
    for k in ("apple","fdroid","catalog","output"):p.add_argument("--"+k,type=pathlib.Path,required=True)
    x=p.parse_args(); x.output.mkdir(parents=True,exist_ok=True)
    hist=read(x.catalog)["tools"]; ha,hf=historical_ids(hist)
    apple={}
    for log in sorted(x.apple.glob("*.log.json")):
        v=read(log)
        if v["status"]!="ok":continue
        raw=log.with_name(log.name.replace(".log.json",".raw.json")).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=v["sha256"]:raise ValueError("Apple hash mismatch")
        for row in json.loads(raw)["results"]:
            if row.get("trackId") is None:continue
            ident=str(row["trackId"])
            item=apple.setdefault(ident,dict(source="apple",source_id=ident,name=row.get("trackName",""),url=row.get("trackViewUrl",""),categories=set()))
            item["categories"].add(v["query"]["family"])
    raw=(x.fdroid/"index-v2.json").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=read(x.fdroid/"report.json")["sha256"]:raise ValueError("F-Droid hash mismatch")
    fd={}
    for ident,pkg in json.loads(raw)["packages"].items():
        m=pkg.get("metadata",{})
        fd[ident]=dict(source="fdroid",source_id=ident,name=loc(m.get("name")),url="https://f-droid.org/packages/"+ident+"/",categories=set(m.get("categories") or []))
    signal={"Science & Education","Sports & Health","Navigation","Workout","Stopwatch","Timer","Educational Game","Messaging","Voice & Video Chat","Text to Speech","Translation & Dictionary","Calendar & Agenda"}
    groups=collections.defaultdict(list)
    for src,items,old in (("apple",apple,ha),("fdroid",fd,hf)):
        for ident,item in sorted(items.items()):
            # Signal sert seulement à stratifier; aucun rejet.
            hit=bool(item["categories"] & signal) if src=="fdroid" else bool(item["categories"] & {"motor","video","measurement","tactics","orientation"})
            strata=(src,"present" if ident in old else "not_matched","signal" if hit else "other")
            groups[strata].append(item)
    rng=random.Random(20261128)
    selected=[]; strata_counts={}
    for k,rows in sorted(groups.items()):
        n=min(20,len(rows)); sample=rng.sample(rows,n);selected.extend(sample)
        strata_counts["/".join(k)]=dict(population=len(rows),sample=n)
    rng.shuffle(selected)
    fields=["review_id","source","source_id","name","url","decision","usage_eps","functions","conditions","evidence_url","evidence_date","reason"]
    for judge in ("A","B"):
        with (x.output/f"judge_{judge}.csv").open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for i,item in enumerate(selected,1):
                row={k:item[k] for k in ("source","source_id","name","url")}
                # Neutralize spreadsheet formulas in external metadata.
                row={k:("'"+v if isinstance(v,str) and v.lstrip().startswith(("=","+","-","@")) else v) for k,v in row.items()}
                w.writerow(dict(review_id=f"R{i:04d}",**row))
    report=dict(historical_rows=len(hist),apple_ids=len(apple),fdroid_ids=len(fd),
                apple_exact_match=len(set(apple)&ha),apple_not_matched=len(set(apple)-ha),
                fdroid_exact_match=len(set(fd)&hf),fdroid_not_matched=len(set(fd)-hf),
                sample_size=len(selected),strata=strata_counts,
                note="Not matched means no exact platform ID found, not confirmed new product. No fuzzy merges or eligibility decisions.")
    (x.output/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
