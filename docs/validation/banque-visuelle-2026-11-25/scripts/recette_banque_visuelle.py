"""Recette mobile de la banque visuelle du Laboratoire (iPhone 13 émulé, Chromium sans interface).

Usage : python recette_banque_visuelle.py <dossier_de_sortie> [url_de_base]
Pour chaque cas : sélection de l'épreuve, ouverture du volet d'illustration, contrôle du chargement de l'image,
de l'absence de débordement horizontal, des légendes, du sens d'écriture, des erreurs et des requêtes externes.
"""
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

OUT = Path(sys.argv[1])
BASE = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8599"
EXPANDER = {"fr": "Illustration pédagogique", "ar": "رسم توضيحي تربوي", "en": "Educational illustration"}
CASES = [
    ("fr", "sargent", "Saut vertical Sargent", "illustration"),
    ("ar", "ruffier", "اختبار روفيي-ديكسون", "illustration"),
    ("en", "medecine_ball", "3 kg medicine-ball throw", "illustration"),
    ("ar", "souplesse_assise", "المرونة من الجلوس", "illustration"),
    ("fr", "handgrip", "Force de préhension (handgrip)", "pictogramme"),
    ("en", "killy", "Killy test", "illustration"),
]


async def choose_test(page, label):
    select = page.locator("div[class*='st-key-'][class*='lab_test'] [data-baseweb=select]").first
    await select.click()
    await page.wait_for_timeout(500)
    await page.keyboard.insert_text(label)
    await page.wait_for_timeout(700)
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(3500)


async def run_case(browser, devices, lang, test_id, label, kind):
    context = await browser.new_context(**devices["iPhone 13"])
    page = await context.new_page()
    errors, external = [], set()
    page.on("pageerror", lambda e: errors.append(str(e)[:200]))
    page.on("request", lambda r: external.add(urlparse(r.url).hostname)
            if urlparse(r.url).hostname not in ("localhost", "127.0.0.1") and r.url.startswith("http") else None)
    await page.goto(f"{BASE}/Performance_Lab?lang={lang}")
    await page.wait_for_timeout(7000)
    await choose_test(page, label)
    selected = await page.locator("div[class*='st-key-'][class*='lab_test']").first.inner_text()
    result = {"cas": f"{lang}/{test_id}", "type": kind, "epreuve_affichee": selected.split("\n")[-1].strip()}
    if kind == "illustration":
        details = page.locator("details").filter(has_text=EXPANDER[lang]).first
        result["volet_present"] = await details.count() == 1
        result["volet_replie_par_defaut"] = not await details.evaluate("d => d.open")
        await details.locator("summary").click()
        await page.wait_for_timeout(2500)
        img = details.locator("img").first
        await img.scroll_into_view_if_needed()
        result["image"] = await img.evaluate(
            "i => ({chargee: i.complete && i.naturalWidth > 0, naturelle: [i.naturalWidth, i.naturalHeight],"
            " affichee: [Math.round(i.getBoundingClientRect().width), Math.round(i.getBoundingClientRect().height)],"
            " fenetre: window.innerWidth, source_locale: i.src.startsWith(location.origin)})")
        captions = details.locator("[data-testid=stCaptionContainer]")
        result["legendes"] = [t.strip() for t in await captions.all_inner_texts()]
        result["sens_legende"] = await captions.first.evaluate("c => getComputedStyle(c).direction")
        target = details
    else:
        block = page.locator("[data-testid=stHorizontalBlock]").filter(has=page.locator("img")).first
        img = block.locator("img").first
        result["image"] = await img.evaluate(
            "i => ({chargee: i.complete && i.naturalWidth > 0, affichee: [Math.round(i.getBoundingClientRect().width),"
            " Math.round(i.getBoundingClientRect().height)], source_locale: i.src.startsWith(location.origin)})")
        result["legendes"] = [t.strip() for t in await block.locator("[data-testid=stCaptionContainer]").all_inner_texts()]
        target = block
    result["debordement_horizontal"] = await page.evaluate(
        "document.documentElement.scrollWidth > window.innerWidth + 1")
    result["exceptions_streamlit"] = await page.locator("[data-testid=stException]").count()
    result["erreurs_js"] = errors
    result["hotes_externes"] = sorted(h for h in external if h)
    await target.screenshot(path=str(OUT / f"{lang}_{test_id}.png"))
    await context.close()
    return result


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        results = []
        for case in CASES:
            results.append(await run_case(browser, p.devices, *case))
            print(json.dumps(results[-1], ensure_ascii=False))
        await browser.close()
    (OUT / "resultats.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


asyncio.run(main())
