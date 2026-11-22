"""Vérifie qu'une application candidate existe : site officiel joignable et nom présent sur la page.

Entrée : TSV catégorie<TAB>nom<TAB>url. Sortie : JSON des résultats (accepté / rejeté + raison).
Règle stricte : le nom principal (sans la partie entre parenthèses) doit apparaître tel quel,
après normalisation (casse, accents, ponctuation), dans le titre ou le texte de la page.
"""
import concurrent.futures as cf
import json
import re
import sys
import unicodedata
import urllib.request
import ssl

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def core_name(name: str) -> str:
    return norm(re.sub(r"\(.*?\)", "", name))


def check(row):
    category, name, url = row
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr,en;q=0.8"})
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            status = resp.status
            final = resp.geturl()
            body = resp.read(600_000).decode("utf-8", "ignore")
    except Exception as exc:  # noqa: BLE001
        code = getattr(exc, "code", None)
        return {"category": category, "name": name, "url": url, "ok": False, "reason": f"inaccessible ({code or type(exc).__name__})"}
    title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    title_text = norm(title.group(1)) if title else ""
    page = norm(re.sub(r"<[^>]+>", " ", body))
    target = core_name(name)
    found = f" {target} " in f" {title_text} " or f" {target} " in f" {page} "
    return {"category": category, "name": name, "url": url, "final_url": final, "status": status,
            "ok": bool(found), "reason": "nom trouvé sur la page" if found else "nom absent de la page",
            "title": title.group(1).strip()[:120] if title else ""}


def main(path, out):
    rows = [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8") if l.strip()]
    with cf.ThreadPoolExecutor(max_workers=24) as pool:
        results = list(pool.map(check, rows))
    json.dump(results, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = sum(r["ok"] for r in results)
    print(f"{ok} acceptées / {len(results)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
