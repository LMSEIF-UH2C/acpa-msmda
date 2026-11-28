"""Browser acceptance of the isolated experimental entry.

Run against three local Streamlit instances: disabled, enabled, missing DB.
No remote service, external source navigation or student data.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

LABELS={
    "fr":("Technothèque expérimentale","Pistes documentaires","Registre expérimental indisponible."),
    "ar":("المكتبة التقنية التجريبية","موارد موثقة أولياً","السجل التجريبي غير متاح."),
    "en":("Experimental technology library","Documentary leads","Experimental register unavailable."),
}
BASE={"disabled":8501,"enabled":8502,"missing":8503}
OUT=Path("dual-entry-evidence")
OUT.mkdir(exist_ok=True)
def home(page):
    expect(page.locator(".st-key-core_find")).to_be_visible(timeout=60000)
    expect(page.locator(".st-key-core_evaluate")).to_be_visible()
    expect(page.locator(".st-key-core_prepare")).to_be_visible()
    expect(page.locator(".st-key-tabbar a[data-testid='stPageLink-NavLink']")).to_have_count(5)
def no_exception(page):
    expect(page.get_by_test_id("stException")).to_have_count(0)
def centered_click(locator):
    locator.evaluate("(el) => el.scrollIntoView({block: 'center', inline: 'nearest'})")
    locator.click()

def run(browser,engine,lang,mode):
    page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,
                          is_mobile=True,has_touch=True)
    base=f"http://127.0.0.1:{BASE[mode]}"
    label,metric,missing=LABELS[lang]
    page.goto(f"{base}/?lang={lang}",wait_until="domcontentloaded")
    home(page)
    button=page.get_by_role("button",name=label,exact=True)
    if mode=="disabled":
        expect(button).to_have_count(0)
        # A direct request must not expose the experimental route either.
        page.goto(f"{base}/experimental-ecosystem?lang={lang}",wait_until="domcontentloaded")
        home(page)
        expect(button).to_have_count(0)
        expect(page.get_by_text("MagicSchool",exact=True)).to_have_count(0)
        expect(page.get_by_role("heading",name=label,exact=True)).to_have_count(0)
        # Streamlit may display its own missing-page dialog over the fallback home.
        # Preserve evidence; explicitly open the valid root URL before testing stable navigation.
        page.screenshot(path=str(OUT/f"{engine}-{lang}-disabled-direct.png"))
        page.goto(f"{base}/?lang={lang}",wait_until="domcontentloaded")
        home(page)
        expect(button).to_have_count(0)
    else:
        expect(button).to_be_visible()
        centered_click(button)
        expect(page.get_by_role("heading",name=label,exact=True)).to_be_visible(timeout=60000)
        if mode=="enabled":
            expect(page.get_by_text(metric,exact=True)).to_be_visible()
            expect(page.get_by_test_id("stMetricValue").first).to_have_text("34")
            expect(page.get_by_test_id("stMetricValue").nth(1)).to_have_text("2500")
            expect(page.get_by_text("MagicSchool",exact=True)).to_be_visible()
            expect(page.get_by_text("jamovi",exact=True)).to_be_visible()
            proposal=json.loads((Path(__file__).resolve().parents[1]/"data/experimental_qualification_proposals.json").read_text(encoding="utf-8"))["records"][3]
            assert proposal["record_id"]=="doc_web:WD04"
            panel=page.get_by_test_id("stExpander").filter(has=page.get_by_text("jamovi",exact=True))
            centered_click(panel.locator("summary"))
            for field in ("documented_function","variant","scenario","documented_limits"):
                expect(panel.get_by_text(proposal[field],exact=True)).to_be_visible()
            warning={"fr":"Toutes les contraintes contextuelles restent à vérifier. Aucun score attribué.","ar":"جميع القيود السياقية تحتاج إلى تحقق. لم يتم إسناد أي درجة.","en":"All contextual constraints require verification. No score assigned."}[lang]
            expect(panel.get_by_text(warning,exact=True)).to_be_visible()
            role={"fr":"Usage complémentaire envisagé","ar":"استخدام تكميلي مقترح","en":"Proposed complementary use"}[lang]
            expect(panel.get_by_text(role,exact=True)).to_be_visible()
            panel.get_by_text(proposal["scenario"],exact=True).scroll_into_view_if_needed()
            page.screenshot(path=str(OUT/f"{engine}-{lang}-qualification.png"))
            print("A3_PANEL_PASS "+json.dumps({"engine":engine,"language":lang,"record":"doc_web:WD04"}),flush=True)
            labels={
                "fr":("Diagnostic documentaire réel","Analyser les preuves","Aucune recommandation opérationnelle","Simulation fictive — relais","Lancer la simulation","Configuration fictive complète"),
                "ar":("التشخيص الوثائقي الحقيقي","تحليل الأدلة","لا توجد توصية تشغيلية","محاكاة افتراضية — التتابع","تشغيل المحاكاة","منظومة افتراضية كاملة"),
                "en":("Real documentary diagnosis","Analyze evidence","No operational recommendation","Fictional simulation — relay","Run simulation","Complete fictional configuration"),
            }[lang]
            real=page.get_by_test_id("stExpander").filter(has=page.get_by_text(labels[0],exact=True))
            centered_click(real.locator("summary"))
            centered_click(real.get_by_role("button",name=labels[1],exact=True))
            expect(real.get_by_text(labels[2],exact=True)).to_be_visible(timeout=60000)
            page.screenshot(path=str(OUT/f"{engine}-{lang}-a5-real.png"))
            demo=page.get_by_test_id("stExpander").filter(has=page.get_by_text(labels[3],exact=True))
            centered_click(demo.locator("summary"))
            centered_click(demo.get_by_role("button",name=labels[4],exact=True))
            expect(demo.get_by_text(labels[5],exact=True)).to_be_visible(timeout=60000)
            page.screenshot(path=str(OUT/f"{engine}-{lang}-a5-demo.png"))
            print("A5_DECISION_PASS "+json.dumps({"engine":engine,"language":lang}),flush=True)
        else:
            expect(page.get_by_text(missing,exact=False)).to_be_visible()
            expect(page.get_by_test_id("stMetric")).to_have_count(0)
        no_exception(page)
        page.screenshot(path=str(OUT/f"{engine}-{lang}-{mode}.png"))
        page.locator(".st-key-tabbar a[data-testid='stPageLink-NavLink']").first.click()
        home(page)
        expect(button).to_be_visible()
    no_exception(page)
    # A stable route must remain usable in every mode.
    centered_click(page.locator(".st-key-core_find button"))
    expect(page.locator(".st-key-core_find")).to_have_count(0,timeout=60000)
    expect(page.get_by_test_id("stTextArea").first).to_be_visible(timeout=60000)
    expect(page.locator(".st-key-tabbar a[data-testid='stPageLink-NavLink']")).to_have_count(5)
    no_exception(page)
    page.screenshot(path=str(OUT/f"{engine}-{lang}-{mode}-stable.png"))
    page.close()
    return {"engine":engine,"language":lang,"mode":mode,"stable_route":"PASS","result":"PASS"}

def main():
    results=[]
    try:
        with sync_playwright() as p:
            for engine in (p.chromium,p.webkit):
                browser=engine.launch()
                for lang in LABELS:
                    for mode in BASE:
                        row=run(browser,engine.name,lang,mode)
                        results.append(row)
                        print("A2_BROWSER_PASS "+json.dumps(row),flush=True)
                browser.close()
    finally:
        (OUT/"results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    assert len(results)==18
if __name__=="__main__":
    main()
