import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.intervals import mean_interval

class IntervalTests(unittest.TestCase):
    def test_known_student_interval(self):
        result=mean_interval([1,2,3,None])
        self.assertEqual(result["n"],3)
        self.assertAlmostEqual(result["mean"],2)
        self.assertAlmostEqual(result["lower"],-0.4841377,places=5)
        self.assertAlmostEqual(result["upper"],4.4841377,places=5)
    def test_conservative_df(self):
        result=mean_interval(list(range(150)))
        self.assertEqual(result["df"],149)
        self.assertEqual(result["df_used"],120)
    def test_insufficient_or_degenerate(self):
        for values in ([],[1],[2,2,2]):
            self.assertIsNone(mean_interval(values))
        with self.assertRaises(ValueError):
            mean_interval([1,float("inf")])
