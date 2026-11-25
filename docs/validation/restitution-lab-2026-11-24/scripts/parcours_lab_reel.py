import asyncio, sys
from playwright.async_api import async_playwright
OUT="/home/claude/work/recette/"
L={"fr":("Étude longitudinale (CSV)","t apparié","Calculer"),"ar":("دراسة طولية (CSV)","ت للعينات المترابطة",None),"en":("Longitudinal study (CSV)","Paired t",None)}
async def pick(pg, key, option):
    await pg.keyboard.press("Escape"); await pg.wait_for_timeout(300)
    await pg.locator(f".st-key-{key} [data-baseweb=select]").click(); await pg.wait_for_timeout(600)
    await pg.get_by_role("option", name=option, exact=True).first.click(); await pg.wait_for_timeout(1500)
async def main(lang):
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(**p.devices["iPhone 13"]); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)[:150]))
        await pg.goto(f"http://localhost:8599/Performance_Lab?lang={lang}"); await pg.wait_for_timeout(7000)
        await pg.locator("summary").filter(has_text=L[lang][0]).first.click(); await pg.wait_for_timeout(800)
        await pg.locator(".st-key-lab_study_enabled label").click(); await pg.wait_for_timeout(3000)
        await pg.locator('input[type=file]').first.set_input_files(OUT+"lab_synthetique_2880.csv"); await pg.wait_for_timeout(3000)
        await pg.locator(".st-key-lab_study_import button").click(); await pg.wait_for_timeout(6000)
        await pick(pg,"lab_study_group","TC1")
        for occ in ("T1","T2"): await pick(pg,"lab_study_occasions",occ)
        await pg.keyboard.press("Escape")
        await pick(pg,"lab_study_method",L[lang][1])
        await pg.locator(".st-key-lab_study_assumptions label").click(); await pg.wait_for_timeout(1500)
        await pg.locator(".st-key-lab_study_panel button").click(); await pg.wait_for_timeout(8000)
        card=pg.locator("[class*=_understand]").first
        print(lang, "carte Comprendre:", await card.count(), "| json visible:", await pg.locator("[data-testid=stJson]").first.is_visible(),
              "| exceptions:", await pg.locator("[data-testid=stException]").count(), "| JS:", errs[:1])
        await card.scroll_into_view_if_needed(); await pg.wait_for_timeout(800)
        await pg.screenshot(path=OUT+f"shots/lab_restitution_{lang}.png")
        print((await card.inner_text())[:600])
        await b.close()
asyncio.run(main(sys.argv[1]))
