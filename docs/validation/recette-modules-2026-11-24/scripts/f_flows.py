"""Parcours interactifs : continuité du contexte entre modules, recherche et exports, scénario, ateliers."""
import asyncio, sys
from playwright.async_api import async_playwright
OUT = "/home/claude/work/recette/"
LOG = []
def log(*a):
    LOG.append(" ".join(str(x) for x in a)); print(*a, flush=True)
async def settle(pg, ms=2500):
    await pg.wait_for_timeout(ms)
    for _ in range(20):
        if not await pg.locator('[data-testid="stStatusWidget"]').count(): break
        await pg.wait_for_timeout(500)
async def download(pg, name, fname):
    async with pg.expect_download() as d:
        await pg.get_by_role("button", name=name).first.click()
    dl = await d.value; path = OUT + "dl_" + fname; await dl.save_as(path)
    data = open(path, "rb").read(); log("  export", fname, len(data), "octets", data[:5])
    return data
async def run(lang, labels, device):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(accept_downloads=True, **(p.devices["iPhone 13"] if device == "iphone" else {"viewport": {"width": 1366, "height": 900}}))
        pg = await ctx.new_page(); errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        # 1. Contexte modifié dans Scénario, relu dans Ateliers après navigation par onglet
        await pg.goto(f"http://localhost:8599/Studio_Pedagogique?lang={lang}"); await settle(pg, 5000)
        await pg.locator('summary').filter(has_text=labels["lesson"]).first.click(); await settle(pg, 800)
        box = pg.get_by_label(labels["size"], exact=True); await box.fill("28"); await box.press("Enter"); await settle(pg)
        await pg.locator(".st-key-tabbar").get_by_text(labels["space_tab"], exact=True).click(); await settle(pg, 3500)
        await pg.locator("[data-testid=stMainBlockContainer]").get_by_text(labels["planner"], exact=True).first.click(); await settle(pg, 3500)
        summary = await pg.locator('summary').filter(has_text=labels["lesson"]).first.inner_text()
        log(device, lang, "contexte relu dans Ateliers :", summary.replace("\n", " "), "->", "OK" if "28" in summary else "ÉCHEC")
        await download(pg, labels["org_pdf"], f"{device}_{lang}_organisation.pdf")
        await download(pg, labels["csv"], f"{device}_{lang}_organisation.csv")
        # 2. Scénario : PDF et CSV
        await pg.goto(f"http://localhost:8599/Studio_Pedagogique?lang={lang}"); await settle(pg, 5000)
        await download(pg, labels["sc_pdf"], f"{device}_{lang}_scenario.pdf")
        await download(pg, labels["csv"], f"{device}_{lang}_scenario.csv")
        # 3. Technothèque : recherche, barre d'état, rapport PDF, nouvelle recherche
        await pg.goto(f"http://localhost:8599/Technologies_Reelles?lang={lang}"); await settle(pg, 5000)
        ta = pg.locator("textarea").first; await ta.fill(labels["query"]); await ta.press("Tab"); await settle(pg)
        await pg.get_by_role("button", name=labels["see"]).click(); await settle(pg, 5000)
        status = await pg.locator(".st-key-status_bar").inner_text()
        log(device, lang, "barre d'état :", status.strip())
        await download(pg, labels["pdf"], f"{device}_{lang}_rapport.pdf")
        await pg.get_by_role("button", name=labels["new"]).click(); await settle(pg)
        log(device, lang, "nouvelle recherche vide la demande :", (await pg.locator("textarea").first.input_value()) == "")
        await pg.screenshot(path=OUT + f"shots/flow_{device}_{lang}_search.png")
        log(device, lang, "erreurs JS :", errors[:3])
        await b.close()
L = {"fr": dict(lesson="Votre séance", size="Effectif", space_tab="Espace EPS", planner="Organiser les ateliers",
                org_pdf="Organisation (PDF)", sc_pdf="Scénario (PDF)", csv="Tableur (CSV)",
                query="basketball au lycée, 30 élèves, sans connexion", see="Voir les suggestions",
                pdf="Rapport PDF", new="Nouvelle recherche"),
     "ar": dict(lesson="حصتك", size="عدد التلاميذ", space_tab="فضاء التربية البدنية", planner="تنظيم الورشات",
                org_pdf="التنظيم (PDF)", sc_pdf="السيناريو (PDF)", csv="جدول بيانات (CSV)",
                query="كرة السلة في الثانوي لقسم من 30 تلميذا بدون اتصال", see="عرض الاقتراحات",
                pdf="تقرير PDF", new="بحث جديد"),
     "en": dict(lesson="Your lesson", size="Class size", space_tab="PE space", planner="Organise workshops",
                org_pdf="Organisation (PDF)", sc_pdf="Lesson plan (PDF)", csv="Spreadsheet (CSV)",
                query="basketball in high school, 30 pupils, no internet", see="See suggestions",
                pdf="PDF report", new="New search")}
for lang in sys.argv[2].split(","):
    asyncio.run(run(lang, L[lang], sys.argv[1]))
open(OUT + f"flows_{sys.argv[1]}.log", "w").write("\n".join(LOG))
