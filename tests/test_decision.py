"""Interface de décision : repères, affinage, rapport, barre d'état et nouvelle recherche."""
import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from acpa_msmda import decision, i18n  # noqa: E402
from acpa_msmda.context_engine import extract_flags  # noqa: E402
from acpa_msmda.real_catalog import recommend  # noqa: E402

PAGE = ROOT / "pages" / "4_Technologies_Reelles.py"


class Bars(unittest.TestCase):
    def test_three_bars_without_method_vocabulary(self):
        labels = [label for label, _ in decision.GROUPS]
        self.assertEqual(len(labels), 3)
        self.assertFalse(any("critère" in x.casefold() or "C1" in x for x in labels))
        codes = [c for _, group in decision.GROUPS for c in group]
        self.assertEqual(len(codes), len(set(codes)))

    def test_values(self):
        self.assertEqual(decision.bars({}), [(label, None) for label, _ in decision.GROUPS])
        full = decision.bars({f"C{i}": 10 for i in range(1, 19)})
        self.assertTrue(all(50 < v <= 100 for _, v in full))
        low = dict(decision.bars({"C14": 0, "C18": 0}))
        self.assertLess(low["Coût"], 50)


class Refine(unittest.TestCase):
    def test_refinements_understood_in_three_languages(self):
        for lang in ("fr", "ar", "en"):
            i18n.use(lang)
            query = decision.refine("basket", decision.REFINEMENTS)
            self.assertTrue({"connectivite_faible", "budget_serre", "grand_effectif", "inclusion"}
                            <= set(extract_flags(query)), lang)
        i18n.use("fr")

    def test_no_duplicate(self):
        i18n.use("fr")
        self.assertEqual(decision.refine("basket, gratuit", ["gratuit"]), "basket, gratuit")

    def test_free_and_arabic_requests_move_matching_apps_up(self):
        base = recommend("basketball score")["matches"][:10]
        asked = recommend("basketball score, application en arabe, gratuit")["matches"][:10]
        share = lambda ms: sum(bool((m.get("store") or {}).get("has_ar")) for m in ms)
        self.assertGreaterEqual(share(asked), share(base))


class Report(unittest.TestCase):
    def test_report_in_arabic_is_rtl_and_complete(self):
        i18n.use("ar")
        matches = recommend("كرة السلة")["matches"]
        page = decision.report_html("كرة السلة", ["النشاط: كرة السلة (مرجح)"], matches, 2466, 12.3).decode()
        i18n.use("fr")
        self.assertIn("dir='rtl'", page)
        self.assertIn("تقرير التوصيات", page)
        self.assertEqual(page.count("class='tool'"), 10)
        self.assertNotIn("critère", page.casefold())


class Page(unittest.TestCase):
    def test_status_bar_and_new_search(self):
        app = AppTest.from_file(str(PAGE), default_timeout=60)
        app.session_state["lang"] = "fr"
        app.run()
        app.text_area[0].set_value("natation au lycée, 30 élèves").run()
        self.assertTrue(any(c.value.startswith("Compris : Activité : natation") for c in app.caption))
        next(b for b in app.button if b.label == "Voir les suggestions").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any("applications examinées" in c.value for c in app.caption))
        next(b for b in app.button if b.label == "Nouvelle recherche").click().run()
        self.assertFalse(any("applications examinées" in c.value for c in app.caption))
        self.assertEqual(app.text_area[0].value, "")


if __name__ == "__main__":
    unittest.main()
