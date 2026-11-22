"""Collecte d'applications réelles via l'API publique de recherche de l'App Store.

Chaque résultat est une fiche publiée par Apple (nom, éditeur, page officielle, genre, prix,
nombre d'avis). Les fonctions pédagogiques ne sont PAS déduites : elles restent à vérifier.
"""
import json
import time
import urllib.parse
import urllib.request

QUERIES = {
 "Suivi et GPS": ["running tracker", "gps running app", "cycling tracker", "hiking gps", "step counter", "walking tracker", "run coach"],
 "Course et chronométrage": ["stopwatch", "lap timer", "race timing", "sprint timer", "track and field", "split timer"],
 "Capteurs et tests": ["beep test", "fitness test", "vertical jump", "reaction time test", "heart rate monitor", "vo2 max", "sprint speed test", "balance test"],
 "Analyse vidéo et mouvement": ["video analysis sport", "slow motion video coach", "motion analysis", "video delay", "swing analysis", "form check workout", "sports video replay"],
 "Activité physique et entraînement": ["home workout", "hiit timer", "interval timer", "strength training log", "calisthenics", "stretching", "yoga", "kids exercise", "dance workout", "jump rope", "pilates", "tabata", "bodyweight workout", "gym log"],
 "Activité et bien-être": ["fitness tracker health", "sleep tracker", "meditation kids", "water reminder", "posture", "breathing exercise"],
 "Sports collectifs et tactique": ["football tactics board", "soccer coach", "basketball coach", "volleyball coach", "handball", "rugby coach", "tactic board", "scoreboard", "basketball stats", "volleyball stats", "soccer drills", "badminton", "table tennis", "tennis coach", "futsal", "netball"],
 "Natation et sports aquatiques": ["swim tracker", "swimming workouts", "swim coach", "swim lap counter", "water polo"],
 "Gestion et planification": ["team management sports", "coach planner", "practice planner", "sports club management", "attendance tracker", "team randomizer", "tournament bracket", "league manager"],
 "Questionnaires et évaluation": ["rubric assessment", "student assessment", "quiz maker", "classroom polling", "survey maker"],
 "Évaluation et recherche pédagogique": ["classroom observation", "gradebook teacher", "teacher planner", "behavior tracker classroom", "student portfolio"],
 "Ressources et apprentissage": ["physical education", "pe teacher", "sport education", "gymnastics skills", "athletics training", "sport rules", "coaching drills", "olympic sports"],
 "Conception pédagogique et multimédia": ["lesson planner", "mind map", "whiteboard teacher", "presentation maker", "interactive lesson"],
 "Montage et supports": ["video editor", "screen recorder", "stop motion", "photo collage", "qr code generator", "teleprompter"],
 "Accessibilité et communication": ["sign language", "aac communication", "text to speech", "speech to text", "visual timer", "translator app"],
 "Cartographie et parcours": ["orienteering", "compass", "offline maps", "geocaching", "treasure hunt", "qr code scavenger hunt"],
}
COUNTRIES = ["us", "fr", "gb"]
GENRES = {"Sports", "Health & Fitness", "Education", "Utilities", "Productivity", "Photo & Video", "Navigation",
          "Medical", "Lifestyle", "Reference", "Graphics & Design",
          "Sport", "Forme et santé", "Éducation", "Utilitaires", "Productivité", "Photo et vidéo", "Médecine",
          "Style de vie", "Référence", "Graphisme et design", "Health and Fitness"}


def fetch(term, country):
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(
        {"term": term, "entity": "software", "country": country, "limit": 200})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)["results"]
        except Exception:
            time.sleep(10 * (attempt + 1))
    return []


def main(out):
    apps = {}
    for category, terms in QUERIES.items():
        for term in terms:
            for country in COUNTRIES:
                for r in fetch(term, country):
                    if r.get("primaryGenreName") not in GENRES:
                        continue
                    key = r["trackId"]
                    entry = apps.setdefault(key, {"trackId": key, "name": r["trackName"], "seller": r.get("sellerName"),
                                                  "url": r["trackViewUrl"].split("?")[0].replace("/" + country + "/", "/us/"),
                                                  "genre": r.get("primaryGenreName"), "price": r.get("price"),
                                                  "ratings": 0, "categories": {}, "terms": set(), "countries": set()})
                    entry["ratings"] = max(entry["ratings"], r.get("userRatingCount") or 0)
                    entry["categories"][category] = entry["categories"].get(category, 0) + 1
                    entry["terms"].add(term)
                    entry["countries"].add(country)
                time.sleep(3.2)
        print(category, len(apps), flush=True)
    for e in apps.values():
        e["terms"] = sorted(e["terms"]); e["countries"] = sorted(e["countries"])
    json.dump(list(apps.values()), open(out, "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
