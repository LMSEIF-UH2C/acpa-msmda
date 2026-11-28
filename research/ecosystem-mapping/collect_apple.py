"""Collecte Apple non filtrée, journalisée et reprenable; aucun changement au catalogue."""
import argparse
import collections
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent

def save(path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)

def plan(matrix, mode):
    for family in matrix["families"]:
        for lang, terms in family["queries"].items():
            for term in (terms[:1] if mode == "pilot" else terms):
                countries = [{"ar":"ma","fr":"fr","en":"us"}[lang]] if mode == "pilot" else matrix["countries"]
                for country in countries:
                    yield dict(family=family["id"], language=lang, term=term, country=country,
                               limit=50 if mode == "pilot" else 200)

def key(q):
    return hashlib.sha256(json.dumps(q, sort_keys=True).encode()).hexdigest()[:20]

def fetch(q):
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(
        dict(term=q["term"], country=q["country"], entity="software", limit=q["limit"]))
    last = None
    for attempt in range(3):
        time.sleep(3.5 if attempt == 0 else 10 * attempt)
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                raw = response.read()
            payload = json.loads(raw)
            if not isinstance(payload.get("results"), list):
                raise ValueError("Missing results array")
            return raw, url, attempt + 1, None
        except Exception as exc:
            last = repr(exc)
    return None, url, 3, last

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pilot","full"], default="pilot")
    p.add_argument("--output", type=pathlib.Path, required=True)
    args = p.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    matrix = json.loads((HERE/"query_matrix.json").read_text(encoding="utf-8"))
    queries = list(plan(matrix,args.mode))
    save(out/"plan.json", queries)
    observations = collections.Counter()
    unique = set()
    categories = collections.defaultdict(set)
    missing = collections.Counter()
    failed = capped = 0
    for q in queries:
        k = key(q)
        response_file, log_file = out/(k+".raw.json"), out/(k+".log.json")
        record = {}
        if log_file.exists():
            record = json.loads(log_file.read_text(encoding="utf-8"))
        if record.get("status") != "ok" or not response_file.exists() or hashlib.sha256(response_file.read_bytes()).hexdigest() != record.get("sha256"):
            raw, url, attempts, error = fetch(q)
            record = dict(query=q,url=url,attempts=attempts,time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
            if error:
                record.update(status="error",error=error)
                save(log_file,record)
                failed += 1
                continue
            temp = response_file.with_suffix(".tmp")
            temp.write_bytes(raw)
            temp.replace(response_file)
            record.update(status="ok",sha256=hashlib.sha256(raw).hexdigest())
            save(log_file,record)
        rows = json.loads(response_file.read_bytes())["results"]
        if len(rows) >= q["limit"]:
            capped += 1
        observations[q["family"]] += len(rows)
        for row in rows:
            ident = row.get("trackId")
            if ident is not None:
                unique.add(ident)
                categories[q["family"]].add(ident)
            for field in ("trackId","trackName","sellerName","trackViewUrl","description","artworkUrl100"):
                if not row.get(field):
                    missing[field] += 1
    report = dict(mode=args.mode,planned_queries=len(queries),successful_queries=len(queries)-failed,
                  failed_queries=failed,capped_queries=capped,raw_observations=sum(observations.values()),
                  unique_apple_ids=len(unique),observations_by_family=dict(observations),
                  unique_ids_by_family={k:len(v) for k,v in categories.items()},missing_fields=dict(missing),
                  note="Counts are returned records, not total market coverage. No screening or cross-platform deduplication.")
    save(out/"report.json",report)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if failed:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
