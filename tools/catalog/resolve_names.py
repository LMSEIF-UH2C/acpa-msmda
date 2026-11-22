import json, re, time, unicodedata, urllib.parse, urllib.request, sys
def norm(t):
    t = unicodedata.normalize("NFKD", (t or "").replace("\xa0", " ").casefold()); t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", t).strip()
def core(n):
    n = n.replace("\xa0", " "); n = re.split(r"\s[:\-–—|]\s|:\s", n)[0]
    return norm(re.sub(r"\(.*?\)", "", n))
rows = json.load(open(sys.argv[1])); out = []
for i, r in enumerate(rows):
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode({"term": r["nom"], "entity": "software", "country": "us", "limit": 15})
    res = []
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as h: res = json.load(h)["results"]; break
        except Exception: time.sleep(10 * (attempt + 1))
    m = [x for x in res if core(x["trackName"]) == core(r["nom"]) and (x.get("userRatingCount") or 0) >= 20]
    if m:
        b = max(m, key=lambda x: x.get("userRatingCount") or 0)
        out.append({"row": r, "app": {"trackId": b["trackId"], "name": b["trackName"], "seller": b.get("sellerName"),
                    "url": b["trackViewUrl"].split("?")[0], "genre": b.get("primaryGenreName"), "ratings": b.get("userRatingCount") or 0,
                    "description": (b.get("description") or "")[:300], "contentAdvisoryRating": b.get("contentAdvisoryRating")}})
    if i % 50 == 0:
        print(i, len(out), flush=True); json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False)
    time.sleep(3.1)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False); print("fini", len(out), flush=True)
