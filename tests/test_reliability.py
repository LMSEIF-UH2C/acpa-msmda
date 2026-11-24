"""Analytical fixtures for two-occasion absolute agreement."""
import sys
import unittest
from math import sqrt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.reliability import agreement

class ReliabilityTests(unittest.TestCase):
    def test_perfect_agreement(self):
        r=agreement([1,2,3,4],[1,2,3,4])
        self.assertAlmostEqual(r["icc"],1)
        for key in ("bias","sd","sem","mdc95","lower","upper"):
            self.assertAlmostEqual(r[key],0)

    def test_constant_bias_penalizes_absolute_agreement(self):
        r=agreement([1,2,3],[2,3,4])
        self.assertAlmostEqual(r["icc"],2/3)
        self.assertAlmostEqual(r["bias"],1)
        self.assertAlmostEqual(r["lower"],1)
        self.assertAlmostEqual(r["upper"],1)
        self.assertAlmostEqual(r["sem"],0)

    def test_variable_differences_and_missing(self):
        r=agreement([1,2,3,None,5],[1,3,5,4,None])
        self.assertEqual(r["n"],3)
        self.assertAlmostEqual(r["bias"],1)
        self.assertAlmostEqual(r["sd"],1)
        self.assertAlmostEqual(r["sem"],1/sqrt(2))
        self.assertAlmostEqual(r["mdc95"],1.96)
        self.assertAlmostEqual(r["lower"],-.96)
        self.assertAlmostEqual(r["upper"],2.96)
        self.assertAlmostEqual(r["icc"],12/17)
        self.assertEqual(r["points"],[{"mean":1,"difference":0},{"mean":2.5,"difference":1},{"mean":4,"difference":2}])

    def test_degenerate_and_invalid(self):
        self.assertIsNone(agreement([1,1,1],[1,1,1])["icc"])
        self.assertIsNone(agreement([1,2,None],[1,2,3]))
        with self.assertRaises(ValueError):
            agreement([1],[1,2])
        with self.assertRaises(ValueError):
            agreement([1,2,float("nan")],[1,2,3])
