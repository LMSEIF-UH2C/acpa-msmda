"""Modèles de scénarios EPS modifiables et contrôle de cohérence."""
from __future__ import annotations
import json
from pathlib import Path
from .i18n import t
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
    """Charge un modèle dans le contexte partagé et dans le scénario de la session."""
    from .session_context import store
    data=store(session)
    data["activity"]=template["activity"]
    data.pop("activity_specialty",None)
    data.pop("scenario_phase_tools",None)
    data["level"]=template["level"]
    data["duration"]=template["duration"]
    data["objectives"]=t(template["objectives"])
    data["prerequisites"]=t(template["prerequisites"])
    data["equipment"]=t(template["constraints"])
    for i,phase in enumerate(template["phases"]):
        data[f"action_{i}"]=t(phase["activity"])
        data[f"minutes_{i}"]=phase["minutes"]
        data[f"evaluation_{i}"]=t(phase["success"])
        data[f"supports_{i}"]=[v for v in phase["media"] if v!="Aucun"]
def scenario_checks(rows,objectives):
    issues=[]
    if not objectives.strip():issues.append(t("Précisez les objectifs de la séance."))
    for r in rows:
        if r["Durée (min)"]>0 and not r["Activité / consignes"].strip():issues.append(t("{phase} : activité à préciser.",phase=t(r["Phase"])))
        if r["Durée (min)"]>0 and not r["Évaluation / feedback"].strip():issues.append(t("{phase} : critère de réussite à préciser.",phase=t(r["Phase"])))
    return issues
