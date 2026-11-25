import asyncio, json, sys
from playwright.async_api import async_playwright
OUT="/home/claude/work/recette/"
L={"fr":("Sauvegarder ou restaurer le journal","Confirmer la restauration","Sauvegarder mes données","Journal (CSV)"),
   "ar":("حفظ أو استعادة السجل","تأكيد الاستعادة","حفظ بياناتي","السجل (CSV)")}
async def main(lang, device):
    exp,confirm,save,csvl=L[lang]
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(accept_downloads=True,**p.devices["iPhone 13"]) if device=="iphone" else await b.new_context(accept_downloads=True)
        pg=await ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        await pg.goto(f"http://localhost:8599/Cahier_Journalier?lang={lang}"); await pg.wait_for_timeout(6000)
        await pg.locator("summary").filter(has_text=exp).first.click(); await pg.wait_for_timeout(800)
        await pg.locator('input[type=file]').first.set_input_files(OUT+"journal_synthetique.json"); await pg.wait_for_timeout(4000)
        await pg.get_by_role("button",name=confirm).click(); await pg.wait_for_timeout(5000)
        frames=await pg.locator('[data-testid="stDataFrame"]').count()
        async with pg.expect_download() as d: await pg.get_by_role("button",name=save).click()
        dl=await d.value; await dl.save_as(OUT+f"dl_{device}_{lang}_journal.json")
        a=json.load(open(OUT+"journal_synthetique.json")); bb=json.load(open(OUT+f"dl_{device}_{lang}_journal.json"))
        same = {k:a[k]==bb.get(k) for k in a}
        async with pg.expect_download() as d: await pg.get_by_role("button",name=csvl).click()
        c=await d.value; await c.save_as(OUT+f"dl_{device}_{lang}_journal.csv")
        lines=open(OUT+f"dl_{device}_{lang}_journal.csv",encoding="utf-8-sig").read().splitlines()
        await pg.screenshot(path=OUT+f"shots/flow_{device}_{lang}_journal.png",full_page=True)
        print(device,lang,"tableaux affichés:",frames,"| aller-retour sauvegarde identique:",same,"| lignes CSV:",len(lines),lines[0][:80],"| erreurs JS:",errs[:2])
        await b.close()
for lang in sys.argv[2].split(","): asyncio.run(main(lang, sys.argv[1]))
