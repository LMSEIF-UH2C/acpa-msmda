import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from playwright.async_api import async_playwright
import recette_banque_visuelle as R
async def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); R.OUT = out
    async with async_playwright() as p:
        b = await p.chromium.launch(); res = []
        for case in [("fr", "sprint30", "Sprint 30 m", "illustration"), ("ar", "sprint30", "عدو 30 م", "illustration"), ("en", "sprint30", "30 m sprint", "illustration")]:
            res.append(await R.run_case(b, p.devices, *case)); print(json.dumps(res[-1], ensure_ascii=False)[:600])
        await b.close()
    (out / "resultats_sprint.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
asyncio.run(main())
