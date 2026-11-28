"""A5 browser acceptance: empty, invalid pin and positive synthetic dossier; no real admission."""
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

OUT=Path("internal-review-evidence")
OUT.mkdir(exist_ok=True)
LABELS={
    "fr":("Technothèque expérimentale","Configuration réelle — revue interne","Ce contexte correspond à la situation examinée","Évaluer la configuration interne","Abstention : aucune configuration complète admise.","Aucun candidat admissible","Configuration interne absente ou non vérifiable."),
    "ar":("المكتبة التقنية التجريبية","منظومة حقيقية — مراجعة داخلية","هذا السياق يطابق الحالة المدروسة","تقييم المنظومة الداخلية","امتناع: لا توجد منظومة كاملة مقبولة.","لا يوجد مرشح مقبول","التهيئة الداخلية غائبة أو غير قابلة للتحقق."),
    "en":("Experimental technology library","Real configuration — internal review","This context matches the situation under review","Evaluate internal configuration","Abstention: no complete admitted configuration.","No admissible candidate","Internal configuration missing or unverifiable."),
}
def main():
    results=[]
    try:
        with sync_playwright() as p:
            for engine in (p.chromium,p.webkit):
                browser=engine.launch()
                for lang,labels in LABELS.items():
                    for mode,port in (("empty",8504),("invalid_pin",8505),("positive",8506)):
                        page=browser.new_page(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
                        page.goto(f"http://127.0.0.1:{port}/?lang={lang}",wait_until="domcontentloaded")
                        button=page.get_by_role("button",name=labels[0],exact=True)
                        expect(button).to_be_visible(timeout=60000)
                        button.click()
                        panel=page.get_by_test_id("stExpander").filter(has=page.get_by_text(labels[1],exact=True))
                        expect(panel).to_be_visible(timeout=60000)
                        panel.locator("summary").scroll_into_view_if_needed()
                        panel.locator("summary").click()
                        if mode in ("empty","positive"):
                            action=panel.get_by_role("button",name=labels[3],exact=True)
                            expect(action).to_be_disabled()
                            panel.get_by_text(labels[2],exact=True).click()
                            expect(action).to_be_enabled()
                            action.click()
                            if mode=="empty":
                                expect(panel.get_by_text(labels[4],exact=True)).to_be_visible(timeout=60000)
                                expect(panel.get_by_text(labels[5],exact=True)).to_be_visible()
                            else:
                                warning,success,role,coverage={
                                    "fr":("Dossier synthétique de test — aucune admission réelle.","Configuration de test complète — résultat synthétique","Candidat de test 1","Couverture obligatoire : 1/1"),
                                    "ar":("ملف اختبار اصطناعي — لا قبول حقيقي.","منظومة اختبار كاملة — نتيجة اصطناعية","مرشح اختبار 1","التغطية الإلزامية : 1/1"),
                                    "en":("Synthetic test dossier — no real admission.","Complete test configuration — synthetic result","Test candidate 1","Required coverage : 1/1"),
                                }[lang]
                                expect(panel.get_by_text(warning,exact=True)).to_be_visible()
                                expect(panel.get_by_text(success,exact=True)).to_be_visible(timeout=60000)
                                expect(panel.get_by_text(role,exact=False)).to_be_visible()
                                expect(panel.get_by_text(coverage,exact=True)).to_be_visible()
                                expect(panel.get_by_text("LibreOffice Calc",exact=False)).to_have_count(0)
                        else:
                            expect(panel.get_by_text(labels[6],exact=True)).to_be_visible()
                            expect(panel.get_by_role("button",name=labels[3],exact=True)).to_have_count(0)
                        expect(page.get_by_test_id("stException")).to_have_count(0)
                        page.screenshot(path=str(OUT/f"{engine.name}-{lang}-{mode}.png"))
                        row={"engine":engine.name,"language":lang,"mode":mode,"status":"PASS"}
                        results.append(row)
                        print("A5_INTERNAL_PANEL_PASS "+json.dumps(row),flush=True)
                        page.close()
                browser.close()
    finally:
        (OUT/"results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    assert len(results)==18
if __name__=="__main__":
    main()
