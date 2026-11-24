import unittest
import numpy as np
from acpa_msmda.lab_statistics import correlate, paired_test, independent_test, repeated_anova, friedman, regression, one_way

class LabStatisticsTests(unittest.TestCase):
    def test_correlation(self):
        self.assertAlmostEqual(correlate([1,2,3,4],[4,3,2,1])["r"], -1)
        self.assertAlmostEqual(correlate([1,2,3,4],[4,3,2,1],"spearman")["rho"], -1)
        with self.assertRaises(ValueError): correlate([1,1,1],[1,2,3])
    def test_paired(self):
        result=paired_test([1,2,3,4],[2,4,6,8])
        self.assertAlmostEqual(result["t"], 3.872983346207417)
        self.assertAlmostEqual(result["mean_difference"], 2.5)
        self.assertAlmostEqual(result["dz"], 1.9364916731037085)
        self.assertEqual(paired_test([1,2,3,4],[2,4,6,8],"wilcoxon")["W"],0)
    def test_independent(self):
        self.assertAlmostEqual(independent_test([1,2,3],[4,5,6])["t"], -3.6742346141747673)
        self.assertEqual(independent_test([1,2,3],[4,5,6],"mann_whitney")["U"],0)
        self.assertAlmostEqual(one_way([[1,2,3],[4,5,6]])["F"],13.5)
    def test_repeated(self):
        a=[[1,2,4],[2,4,5],[3,4,7],[4,6,8]]
        r=repeated_anova(a)
        self.assertEqual((r["df1"],r["df2"]),(2,6))
        self.assertGreater(r["F"],0)
        self.assertTrue(.5<=r["gg_epsilon"]<=1)
        self.assertAlmostEqual(friedman(a)["chi2"],8)
    def test_regression(self):
        x=np.arange(6,dtype=float)
        y=[1,3,6,6,9,11]
        r=regression(y,x[:,None])
        self.assertAlmostEqual(r["coefficients"][1]["b"], np.cov(x,y)[0,1]/np.var(x,ddof=1))
        with self.assertRaises(ValueError): regression(y,np.column_stack([x,x]))
