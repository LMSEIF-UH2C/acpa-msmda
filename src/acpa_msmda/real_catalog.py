"""Matching transparent des références documentées du catalogue réel."""
from __future__ import annotations
import json
import re
from pathlib import Path
from .context_engine import normalize_text,analyze_context,detect_language
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
    analysis=analyze_context(ContextRequest(context,detect_language(context)))
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
    analysis=analyze_context(ContextRequest(context,detect_language(context)))
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


# Besoins voisins : une demande de cross ou de course sur route retrouve aussi les outils de course.
# Applications réelles du catalogue sans rapport avec l'EPS malgré un mot commun (boussole...).
NOT_EPS = re.compile(r"qibla|kaaba|mushroom|prayer", re.IGNORECASE)
# Marques dont les applications servent surtout avec leur montre ou leur capteur.
DEVICE_BRANDS = re.compile(r"\b(garmin|polar|coros|suunto|wahoo|fitbit|whoop|zepp|amazfit|chronojump)\b", re.IGNORECASE)

RELATED = {"cross": ("course", "endurance"), "course sur route": ("course",),
           "beach": ("volleyball", "football", "handball")}


def recommend(context, votes=None, path=DEFAULT_PATH):
    """Recommandations parmi toutes les applications retenues dans le catalogue.

    Pertinence : chaque besoin de la demande trouvé dans la fiche compte, davantage s'il s'agit d'une
    activité physique (natation, basket...) que d'une fonction (chronomètre, score...), et davantage
    s'il figure dans le nom de l'application que dans sa seule description. Un besoin voisin
    (RELATED) compte pour moitié. Quand la demande nomme une activité et que des fiches y répondent,
    les fiches qui ne couvrent aucune activité (plateformes généralistes) sont écartées.

    Adéquation affichée (sur 100) = moitié pertinence, moitié qualité sur les 18 critères pondérés
    selon les contraintes (50 pour une fiche non encore évaluée), avec de petits ajustements :
    fonctions vérifiées, usage hors connexion annoncé quand il est demandé, interface en arabe pour
    une demande en arabe, avis des enseignants. Les fiches sont classées par cette adéquation, si bien
    que l'ordre affiché suit toujours le score affiché. Une fiche évaluée hors programme d'EPS n'est
    pas recommandée.
    """
    from .scoring import relevant, score as criteria_score
    from .keywords import ACTIVITIES, keywords_in
    from .store_info import cautions as store_cautions, works_offline
    if not isinstance(context, str) or not context.strip(): raise ValueError("Contexte requis")
    language = detect_language(context)
    analysis = analyze_context(ContextRequest(context, language))
    offline = "connectivite_faible" in analysis.flags
    wanted = set(keywords_in(context))
    related = {r for k in wanted for r in RELATED.get(k, ())} - wanted
    activities = (wanted | related) & ACTIVITIES
    best = sum((3 if k in ACTIVITIES else 1) * 3 for k in wanted) or 1
    votes = votes or {}
    found = []
    weights = analysis.weights.values
    for t in load_real_tools(path):
        # Seules les applications retrouvées sur une source officielle sont suggérées.
        if not t.get("source_url") or (t.get("store") or {}).get("available") is False: continue
        if offline and t.get("requirement") == "internet": continue
        if NOT_EPS.search(t["name"]): continue
        rated = t.get("criteria_scores")
        if rated and (not relevant(rated) or (offline and rated.get("C6") == 1.0)): continue
        keys = set(t.get("keywords", []))
        # Activités et usages documentés à la main sur la fiche : comparés par mot-clé, quelle que
        # soit la langue de la demande.
        documented = {k for term in t.get("activities", []) + t.get("uses", []) for k in keywords_in(term)} & wanted
        hits = (wanted & keys) | documented
        near = (related & keys) - hits
        if not hits and not near and not documented: continue
        strong = set(t.get("title_keywords", [])) | documented
        relevance = (sum((3 if k in ACTIVITIES else 1) * (3 if k in strong else 1) for k in hits)
                     + sum(1.5 if k in ACTIVITIES else .5 for k in near))
        verified = t.get("evidence_status") in VERIFIED
        quality = criteria_score(rated, weights) if rated else None
        bonus = ((3 if verified else 0) + (4 if offline and works_offline(t) else 0)
                 + (4 if language == "ar" and (t.get("store") or {}).get("has_ar") else 0)
                 + 2 * max(-3, min(3, votes.get(t["id"], 0))))
        fit = max(0.0, min(100.0, 50 * min(1.0, relevance / best) + .5 * (quality if quality is not None else 50.0) + bonus))
        cautions = [t.get("caution", "")] + store_cautions(t)
        device = t.get("requirement") == "materiel" or bool(DEVICE_BRANDS.search(t["name"]))
        if device:
            cautions.append("Matériel requis : montre ou capteur compatible.")
            if "budget_serre" in analysis.flags:
                cautions.append("Coût du matériel à vérifier.")
        found.append({**t, "matched_terms": sorted(hits | documented | near), "device": device, "verified": verified,
                      "activity_hit": bool((hits | near | documented) & ACTIVITIES),
                      "offline_hint": works_offline(t), "relevance": relevance,
                      "score": relevance + bonus, "fit": round(fit, 1), "cautions": cautions,
                      "criteria_total": quality})
    # Demande qui nomme une activité : les outils sans aucune activité commune sont écartés,
    # sauf si aucune fiche ne couvre l'activité (on garde alors les outils de fonction).
    if activities and any(t["activity_hit"] for t in found):
        found = [t for t in found if t["activity_hit"]]
    found.sort(key=lambda t: (-t["fit"], -t["relevance"], not t["verified"], t["name"].casefold()))
    return {"context_flags": list(analysis.flags), "wanted": sorted(wanted), "related": sorted(related),
            "language": language, "matches": found,
            "method": "keyword_matching_full_catalogue", "ranking_validated": False}
