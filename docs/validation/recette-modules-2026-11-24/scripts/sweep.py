"""Balayage : chaque page x langue x appareil. Relève exceptions, alertes d'erreur, débordement horizontal,
direction du texte, mots français résiduels en AR/EN, et capture d'écran."""
import asyncio, json, re, sys
from playwright.async_api import async_playwright
BASE = "http://localhost:8599/"
PAGES = ["", "Technologies_Reelles", "Studio_Pedagogique", "Espace_Enseignant", "Performance_Lab", "Mode_Terrain",
         "Evaluation_Formative", "Cahier_Journalier", "Evaluation_Technologie", "Espace_EPS"]
FR_WORDS = re.compile(r"\b(séance|élèves|Choisissez|Ajouter|Enregistrer|Télécharger|Évaluation|Activité|Niveau|Objectifs|Supprimer|Durée)\b")
async def visit(ctx, name, path, lang, device):
    pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    await pg.goto(f"{BASE}{path}?lang={lang}"); await pg.wait_for_timeout(7000)
    info = await pg.evaluate("""() => ({
      exc: [...document.querySelectorAll('[data-testid="stException"]')].map(e=>e.innerText.slice(0,300)),
      err: [...document.querySelectorAll('[data-testid="stAlertContentError"]')].map(e=>e.innerText.slice(0,200)),
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      dir: getComputedStyle(document.querySelector('[data-testid="stMainBlockContainer"]')||document.body).direction,
      text: (document.querySelector('[data-testid="stMainBlockContainer"]')||document.body).innerText})""")
    leaks = sorted(set(FR_WORDS.findall(info["text"]))) if lang != "fr" else []
    await pg.screenshot(path=f"/home/claude/work/recette/shots/{device}_{lang}_{name}.png", full_page=False)
    await pg.close()
    return {"page": name, "lang": lang, "device": device, "exceptions": info["exc"], "errors": info["err"],
            "overflow_px": info["overflow"], "direction": info["dir"], "fr_leaks": leaks, "js_errors": errs,
            "chars": len(info["text"])}
async def main():
    out = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for device, opts in (("desktop", {"viewport": {"width": 1366, "height": 900}}), ("iphone", p.devices["iPhone 13"])):
            ctx = await b.new_context(**opts)
            for lang in ("fr", "ar", "en"):
                for path in PAGES:
                    out.append(await visit(ctx, path or "Accueil", path, lang, device))
                    r = out[-1]; flag = "!!" if (r["exceptions"] or r["errors"] or r["overflow_px"] > 2 or r["fr_leaks"] or r["js_errors"]) else "ok"
                    print(flag, device, lang, r["page"], r["direction"], r["overflow_px"], r["fr_leaks"], r["exceptions"][:1], r["errors"][:1], r["js_errors"][:1], flush=True)
            await ctx.close()
        await b.close()
    json.dump(out, open("/home/claude/work/recette/sweep.json", "w"), ensure_ascii=False, indent=1)
asyncio.run(main())
