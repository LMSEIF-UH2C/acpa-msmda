import asyncio, sys
from playwright.async_api import async_playwright
OUT="/home/claude/work/recette/"
async def main(device):
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(**(p.devices["iPhone 13"] if device=="iphone" else {"viewport":{"width":1366,"height":900}}))
        pg=await ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
        await pg.goto("http://localhost:8599/Performance_Lab?lang=fr"); await pg.wait_for_timeout(7000)
        await pg.locator("summary").filter(has_text="Étude longitudinale (CSV)").first.click(); await pg.wait_for_timeout(800)
        await pg.locator(".st-key-lab_study_enabled label").click(); await pg.wait_for_timeout(3000)
        await pg.locator('input[type=file]').first.set_input_files(OUT+"lab_synthetique_2880.csv"); await pg.wait_for_timeout(4000)
        await pg.locator(".st-key-lab_study_import button").click(); await pg.wait_for_timeout(12000)
        info=await pg.evaluate("""()=>({exc:[...document.querySelectorAll('[data-testid=stException]')].map(e=>e.innerText.slice(0,200)),
           err:[...document.querySelectorAll('[data-testid=stAlertContentError]')].map(e=>e.innerText.slice(0,200)),
           charts:document.querySelectorAll('[data-testid=stVegaLiteChart], .vega-embed').length,
           tables:document.querySelectorAll('[data-testid=stDataFrame],[data-testid=stTable]').length})""")
        await pg.screenshot(path=OUT+f"shots/flow_{device}_lab_import.png",full_page=False)
        print(device, info, "erreurs JS:", errs[:2])
        await b.close()
asyncio.run(main(sys.argv[1]))
