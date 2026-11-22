"""Estimation automatique des critères pour les fiches non notées à la main.

Les règles suivent les ancres de la grille de notation (version 3) et lisent la description de
l'éditeur (1 500 premiers caractères, comme les évaluateurs). Elles ont été calibrées sur les 100
fiches doublement notées, puis contrôlées hors échantillon sur 70 fiches tirées au hasard et notées
à la main. Seuls les critères dont l'accord hors échantillon atteint κ ≥ .60 sont conservés :

    C1 capteurs (κ = .86), C3 fiabilité (.88), C4 protection des données (1.00),
    C13 lien avec les programmes (κ = .70, κ pondéré = .65 ; décision de pertinence juste à 87 %,
    toutes les erreurs observées étant des inclusions, aucune exclusion à tort),
    C14 coût (.69 ; κ pondéré .81), C15 usage avec une classe (.69 ; .84), C17 liaison (.65).

Les autres critères restent « NR » ; C9 et C10 valent « SO » quand C13 vaut « SO ».
Les descriptions ne sont jamais écrites dans le catalogue.

Usage : python tools/catalog/project_criteria.py <dossier de travail>
(le dossier contient catalog/details.json, aptoide/aptoide_meta.json et fdroid/index-v2.json)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data" / "real_tools_catalog.json"
CODES = [f"C{i}" for i in range(1, 19)]
KEPT = ("C1", "C3", "C4", "C13", "C14", "C15", "C17")


def _loc(v):
    return (v.get("fr") or v.get("en-US") or next(iter(v.values()), "")) if isinstance(v, dict) else (v or "")


def load_desc(work: Path):
    ios = json.loads((work / "catalog/details.json").read_text(encoding="utf-8"))
    apt = json.loads((work / "aptoide/aptoide_meta.json").read_text(encoding="utf-8"))
    fdr = json.loads((work / "fdroid/index-v2.json").read_text(encoding="utf-8"))["packages"]

    def desc(i):
        k, _, r = i.partition("-")
        if k == "ios":
            d = ios.get(r) or {}
            return d.get("description", ""), d.get("contentAdvisoryRating", "")
        if k == "apt":
            m = apt.get(r) or {}
            return (m.get("summary") or "") + " " + (m.get("description") or ""), m.get("pegi", "")
        if k == "fd" and r in fdr:
            m = fdr[r]["metadata"]
            return _loc(m.get("summary")) + " " + _loc(m.get("description")), "FDROID"
        return "", ""
    return desc


def has(text, *patterns):
    return any(re.search(p, text) for p in patterns)


ACT8 = [r"\bathlet", r"athlétisme", r"track (and|&) field", r"\bsprint", r"\brunn(er|ing)\b", r"\brun tracker", r"\bjogg",
        r"\bcourse à pied", r"\bendurance\b", r"\bgymnast", r"\bfootball\b", r"\bsoccer\b", r"\bfutsal", r"\bhandball",
        r"\bbasket", r"\bvolley", r"\bswim", r"\bnatation", r"\bjudo\b", r"\bstopwatch", r"\bchronom", r"\bscoreboard",
        r"\bscore ?keep", r"\bscorekeeper", r"\btimer\b", r"\bstats? (app|tracker)", r"\blap timer", r"\bsplit times?\b", r"\brelay\b", r"\bhigh jump|long jump|shot put|javelin|discus"]
ACT5 = [r"\bworkout", r"\bfitness", r"\bexercise", r"\bstrength", r"\bcardio", r"\bhiit\b", r"\btabata", r"\bstretch",
        r"\bmobility", r"\bflexib", r"\byoga\b", r"\bpilates", r"\bwalk", r"\bsteps?\b", r"\bpedometer", r"\bheart rate",
        r"\binterval", r"\bentraînement", r"\bmusculation", r"\bsport", r"\btraining", r"\bhiking|\btrail|orienteering|mountain bik|\bmtb\b",
        r"\bboxing|karate|taekwondo|martial art|kung fu|wrestling|jiu.?jitsu", r"\bdance|danse"]
ACT2 = [r"\bgolf", r"\bformula 1|\bf1\b|motorsport|racing car|nascar", r"\bski(ing)?\b", r"\bcycling\b|bike computer|bicycle computer|indoor bike|smart trainer",
        r"\bface yoga|skin care|\bbeauty\b",
        r"\bcable machine|\bgym machine", r"\bsoftball|baseball|cricket|pickleball|padel|bowling|darts|poker|chess",
        r"\bmeditat|mindful"]
NONPA = [r"\btranslat", r"\bvideo editor|photo editor|edit(ing)? (your )?(photos|videos)", r"\bpresentation", r"\bmind ?map",
         r"\bquiz\b", r"\bnews\b", r"\btickets?\b", r"\bartwork|\bart gallery", r"\bspreadsheet|\bdocument editor|word processor",
         r"\bsexual|erection|ejaculation", r"\bwhiteboard\b", r"\bshift calendar|work schedule", r"\bcompass\b.*\bdriving|driving directions",
         r"\blive scores?\b.*\b(news|fixtures|highlights|fans?)\b|\b(news|fixtures|highlights)\b.*\blive scores?\b", r"\bfantasy (football|league|team)",
         r"\btv (guide|schedules?)|broadcast(s|ers)?\b", r"\bfootball league\b.*\bcompanion|official app of", r"office 365|microsoft 365|project management|to-?do list|organi[sz]e teamwork"]
NONPA_CAT = {"Montage et supports", "Conception pédagogique et multimédia", "Organisation et bureautique",
             "Assistants IA et recherche", "Communication et visioconférence", "Données et automatisation"}


def c13(t, d):
    name = t["name"].lower()
    full = name + " " + d
    pa8 = has(full, *ACT8)
    pa5 = has(full, *ACT5)
    pa2 = has(name, *ACT2) or (t["category"] not in {"Activité physique et entraînement", "Gestion et planification"}
                               and has(d[:200], *[a for a in ACT2 if 'beauty' not in a and 'meditat' not in a]) and not has(d[:200], *ACT8))
    if pa2 and not has(name, *ACT8):
        return 2.0
    if not pa8 and not pa5:
        if t["category"] in NONPA_CAT or has(full, *NONPA) or not d.strip():
            return "SO" if d.strip() else "NR"
        return "SO" if has(full, *NONPA) else "NR"
    if has(name + " " + d[:400], *NONPA) and not has(d, r"\bcoach(es|ing)?\b.*\b(drills?|training|practice)|\btrain(ing)? (your|session)|\bworkouts?\b"):
        return "SO"
    if pa2 and not has(name, *ACT8):
        return 2.0
    if pa8 and (has(name, *ACT8) or t["category"] in {"Course et chronométrage", "Sports collectifs et tactique",
                                                       "Analyse vidéo et mouvement", "Natation et sports aquatiques"}):
        return 8.0
    if pa8 and not pa5:
        return 8.0
    return 5.0


def rate(t, desc):
    d0, age = desc(t["id"])
    # Même entrée que les évaluateurs du pilote : description nettoyée, 1 500 premiers caractères.
    d = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", d0)).strip()[:1500].lower()
    name = t["name"].lower()
    full = name + " " + d
    s = {c: "NR" for c in CODES}
    if not d.strip():
        s["C13"] = c13(t, "")
        if s["C13"] == "SO":
            s["C9"] = s["C10"] = "SO"
        s["risque"] = 0.0
        return s
    s["C13"] = c13(t, d)
    nonpa = s["C13"] == "SO"
    # C1 capteurs
    if has(full, r"\bgps\b", r"heart rate|fréquence cardiaque|bpm\b", r"accelerometer|gyroscope|barometer", r"\bsensor|capteur",
           r"pedometer|step count|track(s)? (your )?steps", r"apple watch|garmin|fitbit|polar|wahoo|bluetooth"):
        s["C1"] = 7.0 if has(d, r"accura\w* (to|within) \d|±\s?\d|validated|clinically") else 4.0
    else:
        s["C1"] = "SO"
    # C2 retour en temps réel (données de pratique)
    if nonpa:
        s["C2"] = "SO"
    elif has(d, r"real[- ]?time", r"\blive (stats|tracking|feedback|score|activit)", r"\binstant(ly)? (feedback|results?|check|track)"):
        s["C2"] = 8.0
    # C3 fiabilité
    if has(d, r"in the background", r"(screen is )?locked", r"lock screen", r"auto(matic)?[- ]?(save|backup)", r"backup"):
        s["C3"] = 6.0
    # C4 données
    if has(d, r"no (account|sign[- ]?up|registration|login)", r"without (an )?account", r"data (is |are )?stored locally|stored on your device|local[- ]first",
           r"no tracking|stays? on (your|the) device"):
        s["C4"] = 9.0
    # C5 export
    if has(d, r"\bcsv\b", r"excel|spreadsheet", r"\bgpx\b|\bkml\b|\bfit file|\btcx\b", r"\bexport"):
        s["C5"] = 8.0
    elif has(d, r"\bshare\b|\bsharing\b|\bpdf\b|send (it|them|results)"):
        s["C5"] = 5.0
    # C6 hors connexion
    if has(d, r"fully offline|completely offline|works? (entirely |completely )?offline|works without (an )?internet|no internet (connection )?(required|needed)|without internet connection|no wi-?fi needed|sans connexion|hors ligne|sans internet"):
        s["C6"] = 10.0
    elif has(d, r"offline (maps?|mode|use|access|support)|download\w* (\w+ ){0,4}offline|use (them )?offline|available offline|even offline"):
        s["C6"] = 6.0
    elif t.get("requirement") == "internet":
        s["C6"] = 1.0
    # C7 batterie
    if has(d, r"battery[- ]?(saving|friendly|efficient)|save(s)? (your )?battery|économise la batterie|low battery (usage|consumption)"):
        s["C7"] = 7.0
    # C8 type d'outil
    cat = t["category"]
    if nonpa:
        s["C8"] = "SO"
    elif has(full, r"stopwatch|chronom|interval timer|tabata timer|hiit timer|workout timer|lap timer|\btimer\b") or \
            (has(full, r"\bgps\b") and has(full, r"\brun|\bjog|\bwalk|marche|course")):
        s["C8"] = 8.0
    elif has(full, r"video analysis|slow[- ]?motion analysis|frame[- ]by[- ]frame|side[- ]by[- ]side|analy[sz]e (your )?(technique|swing|form|movement)|telestrat|drawing tools"):
        s["C8"] = 7.0
    elif has(full, r"scoreboard|score ?keep|scorekeeper|lineup|roster|tactic|playbook|formation|schedul|planner|calendar|attendance|club management|team management"):
        s["C8"] = "SO"
    elif has(full, r"gamif|badges?|leaderboard|earn (points|coins|rewards)|level up"):
        s["C8"] = 4.0
    elif has(full, r"apple watch|garmin|fitbit|polar|wearable|heart rate monitor|smart trainer|sensor"):
        s["C8"] = 3.0
    # C9 engagement
    if nonpa:
        s["C9"] = "SO"
    elif has(full, r"\bmatch(es)?\b|tournament|compet(e|ition)|challenge (your )?friends|leaderboards?|with friends|\bleagues?\b|pickup games|play(ing)? with"):
        s["C9"] = 8.0
    elif has(d, r"progress|statistic|\bstats\b|charts?|graphs?|history|personal (best|record)|audio feedback|voice (coach|feedback|summary)|records? your"):
        s["C9"] = 6.0
    elif has(d, r"for coaches|coaches can|referee|umpire") and not has(d, r"athletes (can|see)"):
        s["C9"] = 3.0
    # C10 motivation
    if nonpa:
        s["C10"] = "SO"
    else:
        auto = has(d, r"(create|build|design|customi[sz]e|make) (your )?own (workouts?|routines?|sessions?|plans?|programs?|exercises?|training)",
                   r"set (your )?(own )?(goals?|targets?)", r"choose (your )?(workouts?|exercises?|goals?|distance)", r"custom (workouts?|routines?)")
        comp = has(d, r"track (your )?progress|progress (charts?|tracking|graphs?)|see (your )?(improvement|progress)|personal (best|record)|monitor (your )?progress|skill tests?")
        rel = has(d, r"communit|friends|social|share (your )?(progress|results|achievements)|coach(es)? (can )?message|message (your )?coach")
        n = auto + comp + rel
        if n:
            s["C10"] = {1: 4.0, 2: 6.0, 3: 8.0}[n]
        elif has(d, r"badges?|rewards?|points|medals|gift cards"):
            s["C10"] = 5.0
    # C11 facilité
    if has(d, r"easy to use|easy-to-use|simple|intuitive|user[- ]friendly|one tap|1-tap|in seconds|facile|quick(ly)? (and easily|setup|start)"):
        s["C11"] = 8.0
    elif has(d, r"professional[- ]grade|advanced users|steep learning"):
        s["C11"] = 3.0
    # C12 accessibilité
    if has(d, r"voiceover|screen reader|accessib|large (text|font)|big fonts?|text[- ]to[- ]speech|spoken|high contrast|daltoni|colou?r[- ]?blind"):
        s["C12"] = 6.0
    # C14 coût
    free = has(d, r"\bfree\b|gratuit")
    noads = has(d, r"no ads|ad[- ]free|sans pub")
    nopay = has(d, r"no in[- ]app purchases|no subscription|subscription[- ]free|no payments?")
    if t["id"].startswith("fd-") or has(d, r"open[- ]source|source code"):
        s["C14"] = 10.0
    elif free and noads and nopay:
        s["C14"] = 10.0
    elif has(d, r"subscri|premium|free trial|membership|unlock (all|everything|full)|pro version|per (month|year|week)|/month|/year|\$\d+(\.\d+)? ?(/|per|a) ?(month|year|week)"):
        s["C14"] = 7.0 if has(d, r"always free|free version|free features|optional subscription|free download|free to download|our free app|free app\b|is free\b|optional (subscription|premium)") else 4.0
    elif free and has(d, r"\bads\b|advertis"):
        s["C14"] = 7.0
    elif free:
        s["C14"] = 8.0
    # C15 classe
    if has(d, r"roster|lineups?|manage (your )?(\w+ )?(teams?|players|athletes|students|squads?|league|classes)|organi[sz](e|ing) (\w+ )?(athletes|players|teams|tournaments?|matches|league)|entire group|multiple (runners|athletes|user profiles|classes)|student roster|unlimited students|by player|player (and team )?stat|team names|teams and players|squads?\b|pair[- ]up players"):
        s["C15"] = 8.0
    elif has(d, r"collaborat|share (with|it|your|the)|invite|communit|social network|with friends"):
        s["C15"] = 5.0
    elif has(d, r"only for one|single user|just you\b"):
        s["C15"] = 2.0
    # C16 support
    if has(d, r"support@|contact (us|me)|questions\?|feedback\?|tutorials?|manuals?|help cent(er|re)|@\w+\.\w+"):
        s["C16"] = 6.0
    # C17 intégration
    if has(d, r"apple health|healthkit|health app|google fit|health connect|strava|garmin|fitbit|withings|polar|icloud|google drive|dropbox|sync"):
        s["C17"] = 7.0
    if nonpa:
        s["C9"] = s["C10"] = "SO"
    # risque
    r = 0.0
    if has(d, r"turn[- ]by[- ]turn|navigat|follow (the |a )?route") and not nonpa:
        r = 0.5
    if age in ("17+", "18+", "PEGI-18"):
        r = 0.5
    s["risque"] = r
    return s




def estimate(t, desc) -> dict:
    """Critères retenus seulement ; les autres valent « NR »."""
    full = rate(t, desc)
    out = {c: (full[c] if c in KEPT else "NR") for c in CODES}
    if out["C13"] == "SO":
        out["C9"] = out["C10"] = "SO"
    out["risque"] = full["risque"]
    return out


def main(work: Path) -> None:
    desc = load_desc(work)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    stats = Counter()
    for tool in catalog["tools"]:
        if tool.get("criteria_scores") and tool.get("criteria_method") != "estimation":
            stats["notées à la main"] += 1
            tool.setdefault("criteria_method", "double_notation")
            continue
        tool["criteria_scores"] = estimate(tool, desc)
        tool["criteria_method"] = "estimation"
        stats["estimées"] += 1
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(dict(stats))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
