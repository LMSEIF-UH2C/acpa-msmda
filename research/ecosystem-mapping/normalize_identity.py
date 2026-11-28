"""Conservative cross-source identity audit, exploratory only.
Group repeat observations by stable source ID; candidate edges never merge products.
The output is aggregate only. No network requests, catalogue updates or inclusion.
"""
import argparse, collections, hashlib, itertools, json, pathlib, re, unicodedata, random, csv
from urllib.parse import urlsplit
from audit_query_yield import load

def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def name_key(s):
    return " ".join("".join(c if c.isalnum() else " " for c in unicodedata.normalize("NFKC",s).casefold()).split()) if isinstance(s,str) else ""
def repo_url(s):
    try:
        u=urlsplit(s or "")
        if u.scheme not in ("http","https") or u.hostname!="github.com" or u.username or u.password:return ""
        parts=u.path.strip("/").split("/")
        if len(parts)!=2:return ""
        owner,repo=parts
        repo=repo.removesuffix(".git")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+",owner) or not re.fullmatch(r"[A-Za-z0-9_.-]+",repo):return ""
        return (owner+"/"+repo).lower()
    except ValueError:return ""
def localized(v):
    if isinstance(v,dict):return [x for x in v.values() if isinstance(x,str) and x.strip()]
    return [v] if isinstance(v,str) and v.strip() else []

def add(items,source,sid,names=(),publisher=(),package=(),repo=(),phases=(),fork=None):
    if not isinstance(sid,str) or not sid:raise ValueError("Missing stable source ID")
    key=(source,sid)
    x=items.setdefault(key,{"names":set(),"publisher":set(),"package":set(),"repo":set(),"phases":set(),"fork_flags":set()})
    for field,values in (("names",names),("publisher",publisher),("package",package),("repo",repo),("phases",phases)):
        x[field].update(v for v in values if isinstance(v,str) and v.strip())
    if isinstance(fork,bool):x["fork_flags"].add(fork)
    return key

def ingest_apple(root,phase,items):
    verified=load(root,phase)
    for path in sorted(root.glob("*.log.json")):
        log=read(path)
        if log["status"]!="ok":continue
        prefix=path.name.removesuffix(".log.json")
        raw=path.with_name(prefix+".raw.json");facts=path.with_name(prefix+".facts.json")
        if raw.exists() and sha(raw)==log.get("sha256"):rows=read(raw)["results"]
        elif facts.exists() and sha(facts)==log.get("facts_sha256"):rows=read(facts)
        else:raise ValueError("Unverified Apple payload")
        for row in rows:
            if row.get("trackId") is None:raise ValueError("Missing Apple trackId")
            sid=str(row["trackId"])
            if not sid.isdigit():raise ValueError("Invalid Apple ID")
            add(items,"apple",sid,localized(row.get("trackName")),localized(row.get("sellerName")),localized(row.get("bundleId")),phases=[phase])
    return len(verified),sum(x["observations"] for x in verified)

def ingest_fdroid(root,items):
    raw=root/"index-v2.json";report=read(root/"report.json")
    if sha(raw)!=report["sha256"]:raise ValueError("F-Droid hash mismatch")
    packages=read(raw)["packages"]
    for sid,obj in packages.items():
        m=obj.get("metadata",{})
        add(items,"fdroid",sid,localized(m.get("name")),localized(m.get("authorName")),[sid],[repo_url(m.get("sourceCode"))],["fdroid-pilot"])
    if len(packages)!=report["package_ids"]:raise ValueError("F-Droid count mismatch")
    return len(packages)

def ingest_github(root,items):
    total=0;found=set()
    for path in sorted(root.glob("*.log.json")):
        log=read(path)
        if log["status"]!="ok":continue
        raw=path.with_name(path.name.replace(".log.json",".raw.json"))
        if sha(raw)!=log["sha256"]:raise ValueError("GitHub hash mismatch")
        rows=read(raw)["items"]
        if len(rows)!=log["returned"]:raise ValueError("GitHub count mismatch")
        total+=len(rows)
        for row in rows:
            sid=str(row["id"])
            if not sid.isdigit():raise ValueError("Invalid repository ID")
            found.add(sid)
            add(items,"github",sid,localized(row.get("name")),localized((row.get("owner") or {}).get("login")),repo=[repo_url(row.get("html_url"))],phases=["github-pilot"],fork=row.get("fork"))
    report=read(root/"report.json")
    if total!=report["raw_observations"] or len(found)!=report["distinct_repository_ids"]:raise ValueError("GitHub count mismatch")
    return total

def candidates(items,max_group=30):
    """Names are search signals only, never identity. Large groups are explicitly deferred."""
    indexes={"name":collections.defaultdict(set),"identifier_string":collections.defaultdict(set),"repository_url":collections.defaultdict(set)}
    for key,x in items.items():
        for v in x["names"]:
            k=name_key(v)
            if len(k)>=3:indexes["name"][k].add(key)
        for v in x["package"]:
            # Do not collapse case-sensitive identifiers or treat bundle ID as Android package identity.
            if v:indexes["identifier_string"][v].add(key)
        for v in x["repo"]:
            if v:indexes["repository_url"][v].add(key)
    edges=collections.defaultdict(set);deferred=[]
    for rule,index in indexes.items():
        for value,keys in sorted(index.items()):
            if len(keys)<2:continue
            if len(keys)>max_group:
                deferred.append({"rule":rule,"size":len(keys)})
                continue
            for a,b in itertools.combinations(sorted(keys),2):
                edges[(a,b)].add(rule)
    return edges,deferred

def strata_of(pair,rules):
    a,b=pair
    return ("within" if a[0]==b[0] else "cross")+"/"+a[0]+"-"+b[0]+"/"+"+".join(sorted(rules))

def report(items,edges,deferred,observations):
    counts=collections.Counter(k[0] for k in items)
    by_pair=collections.Counter(strata_of(p,rules) for p,rules in edges.items())
    by_rule=collections.Counter(rule for rules in edges.values() for rule in rules)
    return {"source_entities":dict(sorted(counts.items())),"source_entities_total":len(items),
            "observations":observations,"candidate_pairs":len(edges),
            "within_source_pairs":sum(a[0]==b[0] for a,b in edges),
            "cross_source_pairs":sum(a[0]!=b[0] for a,b in edges),
            "pairs_by_signal":dict(sorted(by_rule.items())),"pairs_by_stratum":dict(sorted(by_pair.items())),
            "deferred_large_groups":deferred,"github_fork_flag_true":sum(k[0]=="github" and True in v["fork_flags"] for k,v in items.items()),
            "source_ids_with_multiple_names":dict(sorted(collections.Counter(k[0] for k,v in items.items() if len(v["names"])>1).items())),
            "automatic_cross_id_merges":0,"confirmed_products":None,"historical_full_comparison":False,
            "limitations":["Source-ID grouping is not product deduplication. Repeated source IDs retain observed aliases.","Repository URL links describe code provenance, not necessarily one product. Forks, suites, homonyms and variants require evidence.","Name and identifier-string matches only generate candidates; blocking can miss renamed or translated products.","Groups above 30 are deferred, not excluded. Candidate pairs are not prevalence or accuracy estimates.","No historical raw lists, independent identity judgments, or relevance decisions."]}

def main():
    p=argparse.ArgumentParser()
    for field in ("baseline","expansion","fdroid","github","output"):p.add_argument("--"+field,type=pathlib.Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    items={};bq,bo=ingest_apple(a.baseline,"apple-baseline",items);eq,eo=ingest_apple(a.expansion,"apple-expansion",items)
    fd=ingest_fdroid(a.fdroid,items);gh=ingest_github(a.github,items)
    edges,deferred=candidates(items)
    r=report(items,edges,deferred,{"apple_baseline_queries":bq,"apple_baseline_rows":bo,"apple_expansion_queries":eq,"apple_expansion_rows":eo,"fdroid_index_rows":fd,"github_search_rows":gh})
    # Stratified candidate sample for future independent reviewers. No names/descriptions or judgments exported.
    strata=collections.defaultdict(list)
    for pair,signals in sorted(edges.items()):strata[strata_of(pair,signals)].append(pair)
    rng=random.Random(20261128);sample=[]
    for k,pairs in sorted(strata.items()):
        for pair in rng.sample(pairs,min(10,len(pairs))):
            (sa,ia),(sb,ib)=pair;sample.append({"stratum":k,"source_a":sa,"id_a":ia,"source_b":sb,"id_b":ib,"signals":";".join(sorted(edges[pair]))})
    r["candidate_review_sample"]=len(sample)
    for judge in ("A","B"):
        fields=["review_id","stratum","source_a","id_a","source_b","id_b","signals","decision","evidence_url","evidence_date","justification"]
        with (a.output/("identity_judge_"+judge+".csv")).open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for i,row in enumerate(sample,1):w.writerow({"review_id":f"I{i:04d}",**row})
    (a.output/"report.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
