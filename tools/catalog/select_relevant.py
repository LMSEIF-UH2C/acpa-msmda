"""Sélection des applications pertinentes pour l'EPS à partir des données App Store."""
import json, re, unicodedata, collections, sys

def norm(t):
    t = unicodedata.normalize("NFKD", (t or "").casefold())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " " + re.sub(r"[^a-z0-9]+", " ", t) + " "

KW = {
 "Suivi et GPS": ["running", "run tracker", "jogging", "cycling", "ride", "hiking", "gps", "pedometer", "step counter", "steps", "walking", "marathon", "trail", "course a pied", "randonnee", "velo", "podometre"],
 "Course et chronométrage": ["stopwatch", "lap", "split", "race", "timing", "sprint", "athletics", "track and field", "chronometre", "chrono", "minuteur"],
 "Capteurs et tests": ["heart rate", "bpm", "vo2", "fitness test", "beep test", "jump", "reaction time", "balance", "accelerometer", "sensor", "frequence cardiaque", "test physique", "vertical", "power"],
 "Analyse vidéo et mouvement": ["slow motion", "video analysis", "replay", "frame by frame", "motion", "technique", "swing", "form", "coach", "ralenti", "analyse video"],
 "Activité physique et entraînement": ["workout", "exercise", "fitness", "training", "hiit", "yoga", "stretching", "strength", "gym", "pilates", "calisthenics", "dance", "jump rope", "tabata", "interval", "entrainement", "musculation", "exercices"],
 "Activité et bien-être": ["health", "fitness", "sleep", "meditation", "breathing", "wellness", "activity", "water", "hydration", "posture", "sante", "bien etre"],
 "Sports collectifs et tactique": ["football", "soccer", "basketball", "volleyball", "handball", "rugby", "tactic", "drill", "coach", "team", "score", "scoreboard", "badminton", "tennis", "table tennis", "futsal", "netball", "hockey", "baseball", "cricket"],
 "Natation et sports aquatiques": ["swim", "swimming", "pool", "lap", "natation", "water polo", "piscine"],
 "Gestion et planification": ["team", "coach", "club", "schedule", "roster", "attendance", "league", "tournament", "bracket", "practice", "season", "planning", "equipe"],
 "Questionnaires et évaluation": ["quiz", "assessment", "rubric", "poll", "survey", "test", "evaluation", "student", "class", "questionnaire"],
 "Évaluation et recherche pédagogique": ["teacher", "classroom", "student", "grade", "gradebook", "behavior", "observation", "portfolio", "enseignant", "eleves", "classe"],
 "Ressources et apprentissage": ["physical education", "pe teacher", "sport", "coach", "drill", "rules", "athlet", "gymnastic", "olympic", "learn", "education physique", "eps"],
 "Conception pédagogique et multimédia": ["lesson", "teacher", "mind map", "whiteboard", "presentation", "classroom", "interactive", "slides", "cours"],
 "Montage et supports": ["video editor", "edit video", "screen record", "stop motion", "collage", "qr code", "teleprompter", "montage", "video"],
 "Accessibilité et communication": ["sign language", "aac", "text to speech", "speech to text", "visual timer", "autism", "translate", "dyslexia", "accessibility", "deaf", "blind", "langue des signes"],
 "Cartographie et parcours": ["orienteering", "compass", "map", "offline maps", "geocach", "treasure hunt", "scavenger", "boussole", "carte", "course d orientation"],
}
BLOCK = ["dating", "vpn", "casino", "bet", "betting", "crypto", "bitcoin", "dna", "23andme", "loan", "shopping", "proxy", "tinder", "slots", "lottery", "rencontre", "pari", "stock trading", "forex"]
GENRES = {"Sports", "Health & Fitness", "Education", "Utilities", "Productivity", "Photo & Video", "Navigation", "Medical", "Graphics & Design"}
SOCIAL = {"YouTube", "Instagram", "Facebook", "TikTok", "Snapchat", "Google", "Safari", "WhatsApp Messenger", "Messenger"}

apps = json.load(open(sys.argv[1])); det = json.load(open(sys.argv[2]))
out = []
for a in apps:
    d = det.get(str(a["trackId"]))
    if not d or a["ratings"] < 100 or a["genre"] not in GENRES:
        continue
    if d.get("contentAdvisoryRating") == "17+":
        continue
    name = norm(a["name"]); text = name + norm(d["description"])
    if any(f" {b} " in text for b in BLOCK) or a["name"].replace("\xa0", " ").split(":")[0].strip() in SOCIAL:
        continue
    best = None
    for cat, hits in sorted(a["categories"].items(), key=lambda kv: -kv[1]):
        kws = KW[cat]
        in_name = sum(f" {norm(k).strip()} " in name for k in kws)
        in_text = sum(f" {norm(k).strip()} " in text for k in kws)
        if in_name >= 1 or in_text >= 3:
            best = (cat, in_name, in_text); break
    if best:
        a = dict(a, category=best[0], relevance=best[1] * 3 + best[2], description=d["description"][:300], sellerUrl=d.get("sellerUrl"))
        out.append(a)
json.dump(out, open(sys.argv[3], "w"), ensure_ascii=False)
c = collections.Counter(x["category"] for x in out)
print(len(out)); [print(v, k) for k, v in c.most_common()]
