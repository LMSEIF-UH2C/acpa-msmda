import json, time, urllib.request, sys
apps = json.load(open(sys.argv[1]))
pool = [a for a in apps if a["ratings"] >= int(sys.argv[3])]
details = {}
ids = [a["trackId"] for a in pool]
for i in range(0, len(ids), 150):
    chunk = ids[i:i + 150]
    url = "https://itunes.apple.com/lookup?country=us&id=" + ",".join(map(str, chunk))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                for res in json.load(r)["results"]:
                    details[res["trackId"]] = {"description": res.get("description", "")[:4000],
                                               "genres": res.get("genres", []), "sellerUrl": res.get("sellerUrl"),
                                               "minimumOsVersion": res.get("minimumOsVersion"),
                                               "contentAdvisoryRating": res.get("contentAdvisoryRating")}
            break
        except Exception:
            time.sleep(10 * (attempt + 1))
    time.sleep(3.2)
    print(i, len(details), flush=True)
json.dump({str(k): v for k, v in details.items()}, open(sys.argv[2], "w"), ensure_ascii=False)
