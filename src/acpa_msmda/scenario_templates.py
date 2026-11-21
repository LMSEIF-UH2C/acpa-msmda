"""Modèles de scénarios EPS modifiables et contrôle de cohérence."""
from __future__ import annotations
import json
from pathlib import Path
DEFAULT_TEMPLATES=Path(__file__).resolve().parents[2]/"data"/"scenario_templates.json"
EXPECTED=("Diagnostic","Mise en activité","Apprentissage","Régulation","Évaluation")
def load_templates(path=DEFAULT_TEMPLATES):
    raw=json.loads(Path(path).read_text(encoding="utf-8"))
    entries=raw["templates"]
    if len({t["id"] for t in entries})!=len(entries):raise ValueError("Identifiants de modèles dupliqués")
    for t in entries:
        if [p["phase"] for p in t["phases"]]!=list(EXPECTED):raise ValueError("Phases du modèle invalides")
        if sum(p["minutes"] for p in t["phases"])!=t["duration"]:raise ValueError("Durée du modèle incohérente")
    return entries
def apply_template(template,session):
    session["activity"]=template["activity"]
    session["level"]=template["level"]
    session["duration"]=template["duration"]
    session["objectives"]=template["objectives"]
    session["prerequisites"]=template["prerequisites"]
    session["constraints"]=template["constraints"]
    for i,phase in enumerate(template["phases"]):
        session[f"action_{i}"]=phase["activity"]
        session[f"minutes_{i}"]=phase["minutes"]
        session[f"evaluation_{i}"]=phase["success"]
        session[f"supports_{i}"]=[v for v in phase["media"] if v!="Aucun"]
def scenario_checks(rows,objectives):
    issues=[]
    if not objectives.strip():issues.append("Précisez les objectifs de la séance.")
    for r in rows:
        if r["Durée (min)"]>0 and not r["Activité / consignes"].strip():issues.append(f"{r['Phase']} : activité à préciser.")
        if r["Durée (min)"]>0 and not r["Évaluation / feedback"].strip():issues.append(f"{r['Phase']} : critère de réussite à préciser.")
    return issues
