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


VERIFIED = ("OFFICIAL_SOURCE_FEATURES_ONLY", "FEATURES_VERIFIED_ON_OFFICIAL_SITE")


def recommend(context, votes=None, path=DEFAULT_PATH):
    """Recommandations parmi toutes les applications retenues dans le catalogue.

    Chaque fiche est comparée à la demande par les mots-clés EPS de son nom et de sa description
    officielle. Le classement favorise, dans l'ordre : le nombre de besoins couverts, leur présence
    dans le nom de l'application, les fonctions vérifiées, l'usage hors connexion annoncé quand il est
    demandé, puis les avis des enseignants. Chaque résultat indique si ses fonctions sont vérifiées.
    """
    from .keywords import keywords_in
    if not isinstance(context, str) or not context.strip(): raise ValueError("Contexte requis")
    analysis = analyze_context(ContextRequest(context, "fr"))
    offline = "connectivite_faible" in analysis.flags
    wanted = set(keywords_in(context))
    words = set(normalize_text(context).split())
    votes = votes or {}
    found = []
    for t in load_real_tools(path):
        if offline and t.get("requirement") == "internet": continue
        hits = wanted & set(t.get("keywords", []))
        documented = sorted({term for term in t.get("activities", []) + t.get("uses", []) if normalize_text(term) in words})
        if not hits and not documented: continue
        verified = t.get("evidence_status") in VERIFIED
        title_hits = wanted & set(t.get("title_keywords", []))
        score = (4 * len(hits | set(documented)) + 2 * len(title_hits) + (3 if verified else 0)
                 + (1 if offline and t.get("offline_hint") else 0) + max(-3, min(3, votes.get(t["id"], 0))))
        cautions = [t.get("caution", "")]
        if analysis.flags and "budget_serre" in analysis.flags and t.get("requirement") == "materiel":
            cautions.append("Coût du matériel à vérifier.")
        found.append({**t, "matched_terms": sorted(hits | set(documented)), "verified": verified,
                      "score": score, "cautions": cautions})
    found.sort(key=lambda t: (-t["score"], t["name"].casefold()))
    return {"context_flags": list(analysis.flags), "wanted": sorted(wanted), "matches": found,
            "method": "keyword_matching_full_catalogue", "ranking_validated": False}
