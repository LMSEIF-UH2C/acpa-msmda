"""Informations des magasins : affichage, vigilances et règles de suggestion."""
import datetime as dt
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from acpa_msmda import store_info  # noqa: E402
from acpa_msmda.real_catalog import load_real_tools, recommend  # noqa: E402
from feature_vocabulary import FEATURES, announced_features  # noqa: E402

TOOL = {"store": {"name": "App Store", "available": True, "checked_at": "2026-11-23",
                  "price": "Téléchargement gratuit", "languages": ["EN", "AR", "FR", "DE", "ES"],
                  "platforms": ["iPhone", "iPad"], "age_rating": "4+", "last_update": "2019-05-02",
                  "publisher": "Éditeur"},
        "features_announced": ["Chronomètre", "Suivi GPS"]}


class StoreInfoTests(unittest.TestCase):
    def test_languages_put_french_and_arabic_first(self):
        self.assertEqual(store_info.languages_label(["EN", "AR", "FR", "DE", "ES"]),
                         "français, arabe, anglais, 2 autres")

    def test_details_in_teacher_order(self):
        labels = [label for label, _ in store_info.details(TOOL)]
        self.assertEqual(labels, ["Prix", "Langues", "Plateformes", "Âge", "Mise à jour", "Éditeur"])

    def test_stale_app_is_flagged(self):
        notes = store_info.cautions(TOOL, today=dt.date(2026, 11, 23))
        self.assertIn("Peu mise à jour : dernière version en 2019.", notes)

    def test_adult_rating_is_flagged(self):
        tool = {"store": {"available": True, "age_rating": "17+"}}
        self.assertTrue(any("déconseillée" in n for n in store_info.cautions(tool)))

    def test_no_network_permission_means_offline(self):
        self.assertTrue(store_info.works_offline({"store": {"available": True, "uses_internet": False}}))
        self.assertFalse(store_info.works_offline({"store": {"available": True, "uses_internet": True}}))

    def test_unavailable_store_shows_nothing(self):
        self.assertEqual(store_info.details({"store": {"available": False}}), [])


class FeatureVocabularyTests(unittest.TestCase):
    def test_whole_expressions_only(self):
        self.assertEqual(announced_features("A simple stopwatch with lap times."), ["Chronomètre"])
        self.assertEqual(announced_features("Golf course maps and screen orientation lock."), [])

    def test_french_descriptions(self):
        self.assertIn("Fonctionne hors connexion", announced_features("Séances accessibles hors ligne."))


class CatalogueStoreDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tools = load_real_tools()

    def test_announced_features_come_from_the_vocabulary(self):
        allowed = set(FEATURES)
        for t in self.tools:
            self.assertTrue(set(t.get("features_announced", [])) <= allowed, t["id"])

    def test_no_description_text_is_stored(self):
        for t in self.tools:
            store = t.get("store", {})
            self.assertNotIn("description", store, t["id"])
            for value in store.values():
                if isinstance(value, str):
                    self.assertLess(len(value), 120, t["id"])

    def test_store_data_present_for_store_links(self):
        linked = [t for t in self.tools if "apps.apple.com" in (t.get("source_url") or "")]
        self.assertTrue(linked)
        self.assertTrue(all(t.get("store") for t in linked))

    def test_unlinked_entries_are_never_suggested(self):
        unlinked = {t["id"] for t in self.tools if not t.get("source_url")}
        self.assertTrue(unlinked)
        for query in ("course d'endurance", "basket", "évaluation", "analyse vidéo", "chronométrage"):
            ids = {t["id"] for t in recommend(query)["matches"]}
            self.assertFalse(ids & unlinked, query)


if __name__ == "__main__":
    unittest.main()
