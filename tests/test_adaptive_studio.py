import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda.adaptive_studio import redistribute_minutes, balanced_groups, adaptation_notes

class AdaptiveStudioTests(unittest.TestCase):
    def test_exact_total_and_zero_phases(self):
        for duration in range(15, 241):
            result = redistribute_minutes([5, 10, 30, 0, 5], duration)
            self.assertEqual(sum(result), duration)
            self.assertEqual(result[3], 0)
            self.assertTrue(all(x >= 0 for x in result))
    def test_defaults_and_identity(self):
        self.assertEqual(redistribute_minutes([0]*5, 60), [5,10,30,10,5])
        self.assertEqual(redistribute_minutes([5,10,30,10,5], 60), [5,10,30,10,5])
        with self.assertRaises(ValueError):
            redistribute_minutes([5]*5, 0)
    def test_balanced_groups(self):
        for count in range(1,151):
            for target in (1, 3, 6, 12, 150):
                sizes = balanced_groups(count, target)
                self.assertEqual(sum(sizes), count)
                self.assertLessEqual(max(sizes), target)
                self.assertGreater(min(sizes), 0)
                self.assertLessEqual(max(sizes)-min(sizes), 1)

    def test_contextual_advice(self):
        from acpa_msmda import i18n
        try:
            i18n.use("fr")
            base = adaptation_notes("Découverte", False, False, "Disponible", "Téléphone enseignant")
            constrained = adaptation_notes("Découverte", True, True, "Aucune", "Aucun")
            self.assertEqual(len(base), 1)
            self.assertEqual(len(constrained), 5)
            self.assertEqual(constrained[0], base[0])
            self.assertNotEqual(base[0], adaptation_notes("Approfondissement", False, False, "Disponible", "Téléphone enseignant")[0])
            for lang in ("ar", "en"):
                i18n.use(lang)
                translated = adaptation_notes("Découverte", True, True, "Aucune", "Aucun")
                self.assertEqual(len(translated), 5)
                self.assertTrue(all(a != b for a, b in zip(translated, constrained)))
        finally:
            i18n.use("fr")
