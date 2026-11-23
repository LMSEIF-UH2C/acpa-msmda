"""Pertinence des suggestions : requêtes de référence, faux amis, outils généralistes, confiance."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from acpa_msmda.keywords import keywords_in  # noqa: E402
from acpa_msmda.real_catalog import recommend  # noqa: E402
from acpa_msmda.understanding import understand  # noqa: E402

# Requête de référence -> mots-clés dont au moins un doit figurer dans chacun des 5 premiers résultats.
REFERENCE = {
    "natation au lycée, 30 élèves": {"natation"},
    "basketball : tactique et score": {"basketball"},
    "course d'orientation en forêt avec boussole": {"orientation"},
    "endurance sans connexion, classe de 35": {"endurance", "course"},
    "évaluation en handball": {"handball"},
    "volley score": {"volleyball"},
    "tennis de table": {"tennis de table"},
    "cross-country scolaire": {"cross", "course", "endurance"},
    "العدو الريفي": {"cross", "course", "endurance"},
    "السباحة في الثانوي": {"natation"},
    "basketball team stats for 30 pupils": {"basketball"},
}


class ReferenceQueries(unittest.TestCase):
    def test_no_off_topic_result_in_top_five(self):
        for query, expected in REFERENCE.items():
            top = recommend(query)["matches"][:5]
            self.assertEqual(len(top), 5, query)
            for tool in top:
                self.assertTrue(expected & set(tool["matched_terms"]), f"{query} -> {tool['name']}")

    def test_generalist_platforms_left_out_of_sport_queries(self):
        names = {t["name"] for t in recommend("évaluation en handball")["matches"]}
        self.assertFalse(names & {"H5P", "Google Forms", "Moodle", "Genially"})
        self.assertIn("Google Forms", {t["name"] for t in recommend("évaluation questionnaire")["matches"]})

    def test_order_follows_displayed_score(self):
        for query in REFERENCE:
            fits = [t["fit"] for t in recommend(query)["matches"]]
            self.assertEqual(fits, sorted(fits, reverse=True), query)
            self.assertTrue(all(0 <= f <= 100 for f in fits))

    def test_no_compass_for_prayer(self):
        names = " ".join(t["name"] for t in recommend("course d'orientation boussole")["matches"])
        self.assertNotIn("Qibla", names)

    def test_device_bound_apps_flagged(self):
        garmin = next(t for t in recommend("course endurance")["matches"] if t["name"] == "Garmin Connect")
        self.assertIn("Matériel requis : montre ou capteur compatible.", garmin["cautions"])


class FalseFriends(unittest.TestCase):
    def test_orientation_race_is_not_running(self):
        self.assertEqual(keywords_in("course d'orientation"), ["orientation"])
        self.assertEqual(keywords_in("سباق التوجيه"), ["orientation"])

    def test_catalogue_side_ignores_ambiguous_english(self):
        self.assertEqual(keywords_in("Of course, rotate the screen orientation", catalog=True), [])
        self.assertEqual(keywords_in("golf course GPS", catalog=True), ["golf"])

    def test_school_sport_programme_activities(self):
        for text, key in (("pétanque", "petanque"), ("الكرة الحديدية", "petanque"), ("échecs", "echecs"),
                          ("الشطرنج", "echecs"), ("tir à l'arc", "tir a l arc"), ("الرماية بالنبال", "tir a l arc"),
                          ("jeux traditionnels", "jeux traditionnels"), ("العدو الريفي", "cross")):
            self.assertIn(key, keywords_in(text), text)


class Understanding(unittest.TestCase):
    def values(self, text):
        return {(i.parameter, i.value): i.confidence for i in understand(text)}

    def test_french(self):
        v = self.values("natation au lycée, 30 élèves, sans connexion")
        self.assertEqual(v[("Activité", "natation")], .9)
        self.assertEqual(v[("Niveau", "Lycée")], .9)
        self.assertEqual(v[("Effectif", "30")], .9)
        self.assertIn(("Contrainte", "Sans connexion"), v)

    def test_arabic(self):
        v = self.values("جري المداومة لقسم من 35 تلميذا بدون انترنت في الإعدادي")
        self.assertIn(("Activité", "endurance"), v)
        self.assertEqual(v[("Niveau", "Collège")], .7)
        self.assertEqual(v[("Effectif", "35")], .9)
        self.assertIn(("Contrainte", "Sans connexion"), v)

    def test_weak_clue(self):
        self.assertEqual(self.values("handball 24")[("Effectif", "24")], .5)
        self.assertNotIn(("Effectif", "30"), self.values("sprint 30 m"))


if __name__ == "__main__":
    unittest.main()
