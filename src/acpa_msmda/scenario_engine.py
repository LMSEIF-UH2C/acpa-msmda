"""Scénarisation et suggestions de supports par phase, sans notation inventée."""
from __future__ import annotations
import csv
import io
from .real_catalog import load_real_tools
from .i18n import t as _t

PHASES=(
 ("Diagnostic",("questionnaire","evaluation","quiz"),("Questionnaires et évaluation","Ressources et apprentissage")),
 ("Mise en activité",("video","demonstration","ressources"),("Analyse vidéo et mouvement","Ressources et apprentissage")),
 ("Apprentissage",("video","analyse","capteurs","mesure","ressources"),("Analyse vidéo et mouvement","Capteurs et tests","Ressources et apprentissage")),
 ("Régulation",("video","analyse","mesure","feedback"),("Analyse vidéo et mouvement","Capteurs et tests")),
 ("Évaluation",("evaluation","questionnaire","mesure","tests"),("Questionnaires et évaluation","Capteurs et tests")),
)
def recommend_phase_tools(phase,connectivity="Disponible",catalogue=None,limit=8):
    if phase not in {p[0] for p in PHASES}:raise ValueError("Phase inconnue")
    if connectivity not in ("Aucune","Limitée","Disponible"):raise ValueError("Connectivité inconnue")
    if limit<1:raise ValueError("Limite invalide")
    _,keywords,categories=next(p for p in PHASES if p[0]==phase)
    entries=catalogue if catalogue is not None else load_real_tools()
    found=[]
    for t in entries:
        if t.get("category") not in categories:continue
        if not t.get("source_url"):continue
        uses=set(t.get("uses",[]))
        overlap=sorted(uses.intersection(keywords))
        verified=t.get("evidence_status") in ("OFFICIAL_SOURCE_FEATURES_ONLY","FEATURES_VERIFIED_ON_OFFICIAL_SITE")
        if not overlap and not verified:continue
        if connectivity=="Aucune" and t.get("requirement")=="internet":continue
        notes=[]
        if connectivity!="Disponible" and t.get("requirement") in ("internet","à vérifier"):
            notes.append(_t("Connexion ou fonctionnement hors ligne à confirmer"))
        if not verified:notes.append(_t("Usages et compatibilité à confirmer"))
        found.append({"id":t["id"],"name":t["name"],"category":t["category"],"source_url":t["source_url"],"matched_uses":overlap,"notes":notes,"documented":verified})
    found.sort(key=lambda t:(-int(t["documented"]),-len(t["matched_uses"]),t["name"].casefold()))
    return found[:limit]
def validate_scenario(rows,total_minutes):
    if total_minutes<=0:raise ValueError("Durée totale invalide")
    if not rows:raise ValueError("Aucune phase")
    if any(not isinstance(r.get("Durée (min)"),int) or r["Durée (min)"]<0 for r in rows):
        raise ValueError("Durée de phase invalide")
    used=sum(r["Durée (min)"] for r in rows)
    return {"used_minutes":used,"available_minutes":total_minutes,"difference_minutes":used-total_minutes,"balanced":used==total_minutes}
def safe_cell(value):
    """Prevent spreadsheet formula execution when exported CSV is opened.

    Prefix text with an apostrophe if the first non-space/control character
    could be interpreted as a spreadsheet formula. Numeric cells stay numeric.
    """
    if not isinstance(value, str):
        return value
    candidate = value.lstrip().lstrip(chr(0xfeff) + chr(0x200b)).lstrip()
    if candidate.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value

COLUMNS=("Phase","Durée (min)","Activité / consignes","Supports","Évaluation / feedback")

def export_scenario_csv(metadata,rows):
    stream=io.StringIO()
    writer=csv.writer(stream)
    for key,value in metadata.items():writer.writerow([safe_cell(key),safe_cell(value)])
    writer.writerow([])
    columns=COLUMNS
    writer.writerow([_t(c) for c in columns])
    for row in rows:writer.writerow([safe_cell(_t(row.get(k,"")) if k=="Phase" else row.get(k,"")) for k in columns])
    return stream.getvalue().encode("utf-8-sig")
