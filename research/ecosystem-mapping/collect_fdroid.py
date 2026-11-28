"""Pilote F-Droid: lecture de l'index officiel, aucun APK ni modification du catalogue."""
import argparse
import collections
import datetime as dt
import hashlib
import json
import pathlib
import urllib.request

URL = "https://f-droid.org/repo/index-v2.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    report = {"source": URL, "time_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "scope": "F-Droid main repository, current index only; no APKs, no signature verification"}
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "ACPA-MSMDA-research-pilot/0.1"})
        with urllib.request.urlopen(req, timeout=180) as response:
            raw = response.read()
            report["resolved_url"] = response.geturl()
            report["http_status"] = response.status
        data = json.loads(raw)
        packages = data["packages"]
        if not isinstance(packages, dict) or not packages:
            raise ValueError("Missing or empty packages object")
        (out / "index-v2.json").write_bytes(raw)
        categories = collections.Counter()
        missing = collections.Counter()
        for package in packages.values():
            metadata = package.get("metadata", {})
            categories.update(metadata.get("categories") or [])
            for field in ("name", "summary", "description", "license"):
                if not metadata.get(field):
                    missing[field] += 1
        report.update(status="ok", sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                      package_ids=len(packages), source_categories=dict(categories),
                      missing_metadata=dict(missing), repo_timestamp=data.get("repo", {}).get("timestamp"),
                      note="Source categories may overlap. No pedagogical screening, deduplication across sources or efficacy assessment.")
    except Exception as exc:
        report.update(status="error", error=repr(exc))
    (out/"report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "ok":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
