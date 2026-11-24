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


    def test_mixed_two_occasions_interaction(self):
        from acpa_msmda.lab_statistics import mixed_anova, paired_posthoc
        from scipy import stats
        a=np.array([[1,2],[2,4],[4,5],[5,8]],float)
        b=np.array([[2,5],[3,7],[5,10],[6,10]],float)
        result=mixed_anova([a,b])
        t=stats.ttest_ind(a[:,1]-a[:,0],b[:,1]-b[:,0],equal_var=True)
        self.assertAlmostEqual(result["group_time"]["F"],t.statistic**2)
        self.assertAlmostEqual(result["group_time"]["p"],t.pvalue)
        with self.assertRaises(ValueError): mixed_anova([a,b[:3]])
        contrasts=paired_posthoc([[1,2,4],[2,4,5],[3,4,7],[4,6,8]])
        self.assertEqual(len(contrasts),3)
        self.assertTrue(all(r["p"]<=r["p_holm"]<=1 for r in contrasts))


    def test_orthogonal_moderation_reference(self):
        # Full 2x2 orthogonal design, two replicates per cell, residual +/- 1.
        x=np.repeat([-1.,-1.,1.,1.],2)
        m=np.repeat([-1.,1.,-1.,1.],2)
        y=10+2*x+3*m+4*x*m+np.tile([-1.,1.],4)
        r=regression(y,np.column_stack([x+10,m+20]),moderation=True)
        np.testing.assert_allclose([v["b"] for v in r["coefficients"]],[10,2,3,4])
        np.testing.assert_allclose([v["se"] for v in r["coefficients"]],[.5]*4)
        self.assertAlmostEqual(r["r2"],29/30)
        self.assertAlmostEqual(r["model_F"],116/3)
        self.assertEqual(r["predictor_centers"],[10.,20.])
        self.assertEqual(r["df"],4)

    def test_repeated_reference_exact(self):
        # Independent hand-calculation: SS time=24, SS residual=4, df=2,6.
        a=np.array([[2,3,6],[4,7,8],[6,7,10],[8,11,12]],float)
        r=repeated_anova(a)
        self.assertAlmostEqual(r["F"], 36.)
        self.assertAlmostEqual(r["partial_eta2"],12/13)
