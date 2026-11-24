import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from streamlit.testing.v1 import AppTest  # noqa: E402

from acpa_msmda import feedback  # noqa: E402


class FeedbackStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["ACPA_FEEDBACK_PATH"] = str(Path(self.tmp.name) / "votes.jsonl")

    def tearDown(self):
        os.environ.pop("ACPA_FEEDBACK_PATH", None)
        self.tmp.cleanup()

    def test_votes_are_counted_and_changed_votes_replace_the_old_one(self):
        feedback.record("a", True)
        feedback.record("a", True)
        feedback.record("b", False)
        feedback.record("b", True, previous=False)  # changement d'avis
        t = feedback.tallies()
        self.assertEqual((t["a"]["useful"], t["a"]["not_useful"]), (2, 0))
        self.assertEqual((t["b"]["useful"], t["b"]["not_useful"]), (1, 0))
        self.assertEqual(feedback.score(t["a"]), 2)
        self.assertEqual(feedback.score(None), 0)

    def test_damaged_lines_are_ignored(self):
        feedback.record("a", True)
        with feedback.store_path().open("a", encoding="utf-8") as f:
            f.write("{pas du json\n")
        self.assertEqual(feedback.tallies()["a"]["useful"], 1)

    def test_only_anonymous_fields_are_stored(self):
        feedback.record("a", False)
        line = feedback.store_path().read_text(encoding="utf-8").strip()
        self.assertEqual(set(__import__("json").loads(line)), {"tool", "useful", "delta", "day"})

    def test_labels(self):
        self.assertEqual(feedback.label(None), "Pas encore d'avis d'enseignant.")
        feedback.record("a", True)
        self.assertIn("1 utile en séance", feedback.label(feedback.tallies()["a"]))

    def test_one_vote_per_session_and_vote_can_change(self):
        votes = {}
        self.assertTrue(feedback.apply_vote(votes, "a", True))
        self.assertFalse(feedback.apply_vote(votes, "a", True))  # double clic ignoré
        self.assertTrue(feedback.apply_vote(votes, "a", False))  # changement d'avis
        t = feedback.tallies()["a"]
        self.assertEqual((t["useful"], t["not_useful"]), (0, 1))

    def test_catalogue_page_records_votes_and_ranks_useful_tools_first(self):
        at = AppTest.from_file(str(ROOT / "pages" / "4_Technologies_Reelles.py"), default_timeout=60).run()
        self.assertFalse(at.exception)
        self.assertTrue(any("sans identifiant d’utilisateur" in c.value and "leur conservation dépend de l’hébergement" in c.value for c in at.caption))
        self.assertTrue(any("Le navigateur peut transmettre l’audio" in c.value for c in at.caption))
        at.toggle[0].set_value(True).run()
        no_buttons = [b for b in at.button if str(b.key).startswith("no_")]
        last = no_buttons[-1].key[len("no_"):]
        at.button(key=f"yes_{last}").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(feedback.tallies()[last]["useful"], 1)
        at.button(key=f"yes_{last}").click().run()  # deuxième clic : pas de double vote
        self.assertEqual(feedback.tallies()[last]["useful"], 1)
        before = [b.key for b in at.button if str(b.key).startswith("yes_")]
        self.assertEqual(before[-1], f"yes_{last}")  # pas de saut de la fiche pendant la visite
        fresh = AppTest.from_file(str(ROOT / "pages" / "4_Technologies_Reelles.py"), default_timeout=60).run()
        fresh.toggle[0].set_value(True).run()
        first_card = next(b for b in fresh.button if str(b.key).startswith("yes_"))
        self.assertEqual(first_card.key, f"yes_{last}")  # à la visite suivante, la fiche jugée utile est en tête
        self.assertTrue(any("1 utile en séance" in c.value for c in at.caption))


if __name__ == "__main__":
    unittest.main()
