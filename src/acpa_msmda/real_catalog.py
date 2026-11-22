"""Matching transparent des références documentées du catalogue réel."""
from __future__ import annotations
import json
from pathlib import Path
from .context_engine import normalize_text,analyze_context
from .contracts import ContextRequest
DEFAULT_PATH=Path(__file__).resolve().parents[2]/"data"/"real_tools_catalog.json"
def load_real_tools(path=DEFAULT_PATH):
    raw=json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("dataset_type")!="REAL_TOOLS_UNSCORED":raise ValueError("Catalogue incompatible")
    items=raw.get("tools",[])
    if not isinstance(items,list) or len({t["id"] for t in items})!=len(items):raise ValueError("Identifiants invalides")
    return items
def match_real_tools(context,path=DEFAULT_PATH):
    if not isinstance(context,str) or not context.strip():raise ValueError("Contexte requis")
    analysis=analyze_context(ContextRequest(context,"fr"))
    words=set(normalize_text(context).split())
    matches=[]
    for t in load_real_tools(path):
        if t.get("evidence_status") not in ("OFFICIAL_SOURCE_FEATURES_ONLY","FEATURES_VERIFIED_ON_OFFICIAL_SITE"):continue
        matched=[term for term in t.get("activities",[])+t.get("uses",[]) if normalize_text(term) in words]
        if not matched:continue
        # Sans connexion : un outil qui exige internet n'est jamais proposé.
        if "connectivite_faible" in analysis.flags and t.get("requirement")=="internet":continue
        cautions=[t.get("caution","")]
        if "budget_serre" in analysis.flags and t.get("requirement")=="materiel":cautions.append("Coût du matériel à vérifier.")
        matches.append({**t,"matched_terms":sorted(set(matched)),"cautions":cautions})
    matches.sort(key=lambda t:(-len(t["matched_terms"]),t["name"].casefold()))
    return {"context_flags":list(analysis.flags),"matches":matches,"method":"descriptive_keyword_matching","ranking_validated":False,"scores":None}


# Pistes parmi les fiches en cours de documentation : les noms des applications sont souvent en
# anglais, d'où cette correspondance entre les mots des enseignants et les termes des magasins.
FR_EN={
 "course":("run","running","runner","jog","marathon"),"endurance":("run","running","cardio","endurance","walk"),
 "marche":("walk","walking","step","pedometer"),"vitesse":("sprint","speed","timer"),"sprint":("sprint","speed"),
 "chronometrage":("stopwatch","timer","lap"),"chrono":("stopwatch","timer","lap"),"chronometre":("stopwatch","timer"),
 "natation":("swim","swimming","pool"),"football":("football","soccer"),"basket":("basketball","hoops"),
 "basketball":("basketball","hoops"),"volley":("volleyball",),"volleyball":("volleyball",),"handball":("handball",),
 "rugby":("rugby",),"tennis":("tennis",),"badminton":("badminton",),"gymnastique":("gymnastics","gym","flexibility"),
 "acrosport":("gymnastics","acro"),"yoga":("yoga",),"musculation":("strength","gym","workout","dumbbell"),
 "renforcement":("strength","workout","bodyweight","core"),"etirement":("stretch","stretching","flexibility"),
 "souplesse":("stretch","stretching","flexibility","splits"),"orientation":("compass","orienteering","map","maps","gps"),
 "video":("video","slow","motion","replay"),"analyse":("video","analysis","slow","motion"),"saut":("jump","vertical"),
 "corde":("jump rope","rope"),"echauffement":("warm","warm up","stretch"),"cardio":("cardio","hiit","heart"),
 "frequence":("heart","pulse","bpm"),"evaluation":("gradebook","assessment","quiz","rubric"),"notes":("gradebook",),
 "groupes":("team","group","groups"),"equipes":("team","teams","group"),"tactique":("tactic","tactics","playbook","board"),
 "score":("score","scoreboard"),"tournoi":("tournament","bracket"),"danse":("dance",),"boxe":("boxing",),
 "judo":("judo",),"karate":("karate",),"velo":("bike","cycling"),"randonnee":("hike","hiking","trail"),
 "intervalle":("interval","tabata","hiit"),"hiit":("hiit","interval","tabata"),"tabata":("tabata","interval"),
}


def match_pending_tools(context,votes=None,limit=8,path=DEFAULT_PATH):
    """Pistes parmi les fiches non encore documentées, signalées comme telles à l'enseignant."""
    if not isinstance(context,str) or not context.strip():raise ValueError("Contexte requis")
    analysis=analyze_context(ContextRequest(context,"fr"))
    words=set(normalize_text(context).split())
    terms=set(words)
    for w in words:terms.update(FR_EN.get(w,()))
    terms={t for t in terms if len(t)>2}
    found=[]
    for t in load_real_tools(path):
        if t.get("evidence_status") in ("OFFICIAL_SOURCE_FEATURES_ONLY","FEATURES_VERIFIED_ON_OFFICIAL_SITE"):continue
        if "connectivite_faible" in analysis.flags and t.get("requirement")=="internet":continue
        text=" "+normalize_text(" ".join([t["name"],t.get("category",""),t.get("screening_use","")]))+" "
        hits=sorted({term for term in terms if f" {normalize_text(term)} " in text})
        if hits:found.append({**t,"matched_terms":hits})
    votes=votes or {}
    found.sort(key=lambda t:(-votes.get(t["id"],0),-len(t["matched_terms"]),t["name"].casefold()))
    return found[:limit]
