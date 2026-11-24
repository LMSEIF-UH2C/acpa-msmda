"""Learning library: multilingual content, diagrams and context preservation."""
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda import i18n, session_context as ctx
from acpa_msmda.learning_library import load_situations, details, diagram_svg, diagram_drawing, apply_situation, selected_situation
from acpa_msmda.pdf import situation_pdf

class LearningLibraryTests(unittest.TestCase):
    def tearDown(self):
        i18n.use("fr")

    def test_registry_and_diagrams(self):
        items = load_situations()
        self.assertGreaterEqual(len(items), 5)
        self.assertEqual(len({s["id"] for s in items}), len(items))
        for s in items:
            self.assertIn(s["activity"], ctx.APS)
            self.assertIn(s["level"], ctx.LEVELS)
            self.assertEqual(s["status"], "proposed")
            ElementTree.fromstring(diagram_svg(s["diagram"]))
            self.assertGreater(len(diagram_drawing(s["diagram"]).contents), 2)
            for lang in ("fr", "ar", "en"):
                i18n.use(lang)
                self.assertEqual(set(details(s)), {"objective", "organisation", "success", "easier", "harder", "safety"})
                self.assertTrue(all(details(s).values()))
                self.assertTrue(situation_pdf(s).startswith(b"%PDF"))

    def test_apply_preserves_context(self):
        s = load_situations()[0]
        session = {}
        for key, value in (("activity", s["activity"]), ("level", s["level"]), ("class_size", 42), ("duration", 90), ("minutes_2", 40)):
            ctx.put(session, key, value)
        apply_situation(s, session)
        self.assertEqual(ctx.get(session, "class_size"), 42)
        self.assertEqual(ctx.get(session, "duration"), 90)
        self.assertEqual(ctx.get(session, "minutes_2"), 40)
        self.assertEqual(selected_situation(session)["id"], s["id"])
        self.assertEqual(ctx.get(session, "evaluation_2"), s["fr"]["success"])
        ctx.put(session, "activity", "Autre")
        self.assertIsNone(selected_situation(session))
