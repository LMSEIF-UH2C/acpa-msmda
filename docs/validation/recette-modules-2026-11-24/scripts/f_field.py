import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(**p.devices["iPhone 13"])
        for lang in ("ar","en"):
            await pg.goto(f"http://localhost:8599/Mode_Terrain?lang={lang}"); await pg.wait_for_timeout(5000)
            start={"ar":"بدء","en":"Start"}[lang]
            await pg.get_by_role("button",name=start,exact=True).first.click(); await pg.wait_for_timeout(4000)
            txt=await pg.locator('[data-testid="stMetric"]').first.inner_text()
            labels=[await x.inner_text() for x in await pg.locator('[data-testid="stMainBlockContainer"] button').all()]
            print(lang, repr(txt), [l for l in labels if l][:8])
            await pg.screenshot(path=f"/home/claude/work/recette/shots/flow_field_{lang}.png")
        await b.close()
asyncio.run(main())
