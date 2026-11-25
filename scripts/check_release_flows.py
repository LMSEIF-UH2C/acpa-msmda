"""Recette des modules par AppTest (exécution réelle des pages, sans navigateur)."""
import argparse, json, sys, traceback
from datetime import date, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from streamlit.testing.v1 import AppTest
LOG = []
def log(step, ok, detail=""):
    LOG.append({"étape": step, "résultat": "réussi" if ok else "échec", "détail": detail}); print("OK " if ok else "KO ", step, "|", detail, flush=True)
def page(name, lang="fr", state=None):
    app = AppTest.from_file(str(ROOT / "pages" / name), default_timeout=90)
    app.session_state["lang"] = lang
    for k, v in (state or {}).items(): app.session_state[k] = v
    return app.run()
def btn(app, label): return next(b for b in app.button if b.label == label)
def run(step, fn):
    try: fn()
    except Exception as e: log(step, False, f"{type(e).__name__}: {e}"[:300]); traceback.print_exc(limit=1)

# 1. Évaluer votre contexte
def tech_eval():
    for lang, text, label, expect in (("fr", "endurance, 35 élèves, sans connexion", "Analyser mon contexte", "Vos besoins et priorités"),
                                      ("ar", "التحمل، 35 تلميذا، بدون اتصال", "تحليل سياقي", None),
                                      ("en", "endurance, 35 pupils, no internet", "Analyse my context", None)):
        app = page("9_Evaluation_Technologie.py", lang)
        app.text_area[0].set_value(text).run()
        b = [x for x in app.button if x.key == "analyze_context"][0]; b.click().run()
        subs = [s.value for s in app.subheader]; writes = [m.value for m in app.markdown]
        log(f"Évaluer · analyse ({lang})", not app.exception and len(subs) >= 1 and any("35" in w for w in writes),
            f"sous-titres={subs[:2]} ; lignes={[w for w in writes if '35' in w][:1]}")
run("Évaluer", tech_eval)

# 2. Évaluation formative : grille, critère, observation, export
def formative():
    app = page("7_Evaluation_Formative.py")
    app.text_input[0].set_value("G1").run()
    btn(app, "Créer une nouvelle grille").click().run()
    log("Formative · nouvelle grille", not app.exception, f"exceptions={len(app.exception)}")
    adders = [b for b in app.button if b.label in ("Ajouter le critère proposé",)]
    if adders: adders[0].click().run()
    dl = [d.proto.label for d in app.get("download_button")]
    log("Formative · exports proposés", not app.exception and {"Sauvegarder mes évaluations (Excel)", "Exporter les observations (Excel)"}.issubset(dl) and not any("JSON" in x or "CSV" in x for x in dl), str(dl))
run("Formative", formative)

# 3. Cahier journalier : cycle, créneau, génération, export
def journal():
    app = page("8_Cahier_Journalier.py")
    d0 = date(2026, 9, 7)
    app.number_input(key=None) if False else None
    form_inputs = app.date_input
    app.date_input[0].set_value(d0); app.date_input[1].set_value(d0 + timedelta(days=40))
    [b for b in app.button if b.label == "Enregistrer le cycle"][0].click().run()
    log("Journal · cycle enregistré", not app.exception and len(app.dataframe) >= 1, f"tableaux={len(app.dataframe)} erreurs={[e.value for e in app.error]}")
    ti = [x for x in app.text_input if x.label == "Code du groupe (non nominatif)"][0]; ti.set_value("TC1")
    [b for b in app.button if b.label == "Enregistrer le créneau"][0].click().run()
    log("Journal · créneau enregistré", not app.exception and len(app.dataframe) >= 2, f"tableaux={len(app.dataframe)} erreurs={[e.value for e in app.error]}")
    gen = btn(app, "Générer les séances annuelles"); gen.click().run()
    dl = [d.proto.label for d in app.get("download_button")]
    entries = app.session_state["acpa_store"]["journal_entries"]
    log("Journal · génération des séances", not app.exception and bool(entries) and {"Sauvegarder mes données", "Journal (Excel)", "Sauvegarder les projets de cycle"}.issubset(dl), f"séances={len(entries)} exports={dl}")
run("Journal", journal)

# 4. Mode terrain : chaque outil s'affiche
def field():
    for tool in ("Chronomètre", "Compteurs", "Scores", "Rotations", "Équipes", "Consignes"):
        app = page("6_Mode_Terrain.py")
        app.radio[0].set_value(tool).run()
        log(f"Terrain · {tool}", not app.exception, f"exceptions={len(app.exception)}")
run("Terrain", field)

# 5. Espace EPS : un bouton par module
def space():
    for lang in ("fr", "ar", "en"):
        app = page("10_Espace_EPS.py", lang)
        log(f"Espace EPS · liens ({lang})", not app.exception and len(app.button) >= 5, str([b.label for b in app.button][:6]))
run("Espace", space)
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, default=Path("recette-apptest.json"))
args = parser.parse_args()
args.output.write_text(json.dumps(LOG, ensure_ascii=False, indent=2), encoding="utf-8")
passed = sum(row["résultat"] == "réussi" for row in LOG)
print(f"Recette AppTest : {passed}/{len(LOG)}", flush=True)
sys.exit(0 if passed == len(LOG) == 17 else 1)
