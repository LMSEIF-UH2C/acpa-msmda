"""Cross-check actual Lab results against independently computed base R values."""
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda import lab_statistics as ls
a=np.array([[1,2,4],[2,4,5],[3,4,7],[4,6,8]],float)
b=np.array([[2,4,6],[3,7,8],[5,10,11],[6,10,13]],float)
x=np.arange(1.,9.)
m=np.array([1,4,2,5,3,8,6,7],float)
y=np.array([3,5,4,9,8,14,11,15],float)
p=ls.paired_test(a[:,0],a[:,1])
w=ls.independent_test(a[:,2],b[:,2])
r=ls.regression(y,np.column_stack([x,m]),moderation=True)
rm=ls.repeated_anova(a)
mx=ls.mixed_anova([a,b])
pc=ls.correlate(x,y)
sp=ls.correlate(x,y,"spearman")
fr=ls.friedman(a)
ow=ls.one_way([a[:,2],b[:,2]])
post=ls.paired_posthoc(a)
actual={"paired_t":p["t"],"paired_p":p["p"],"paired_ci_low":p["ci95"][0],"paired_ci_high":p["ci95"][1],"welch_t":w["t"],"welch_df":w["df"],"welch_p":w["p"],"pearson_r":pc["r"],"pearson_p":pc["p"],"spearman_r":sp["rho"],"spearman_p":sp["p"],"friedman_chi2":fr["chi2"],"friedman_p":fr["p"],"oneway_F":ow["F"],"oneway_p":ow["p"],"rm_F":rm["F"],"rm_p":rm["p"],"mixed_group_F":mx["group"]["F"],"mixed_time_F":mx["time"]["F"],"mixed_interaction_F":mx["group_time"]["F"],"mixed_interaction_p":mx["group_time"]["p"],"moderation_b":r["coefficients"][3]["b"],"moderation_se":r["coefficients"][3]["se"],"moderation_p":r["coefficients"][3]["p"],"moderation_r2":r["r2"],"moderation_F":r["model_F"]}
for i,c in enumerate(post): actual["holm_"+str(i)]=c["p_holm"]
out=subprocess.check_output(["Rscript",str(ROOT/"scripts/lab_reference.R")],text=True)
expected={}
for line in out.splitlines():
    key,value=line.split("\t")
    if key in expected: raise AssertionError("duplicate R key")
    expected[key]=float(value)
assert set(actual)==set(expected), (set(actual)-set(expected),set(expected)-set(actual))
report=[]
for key,value in actual.items():
    ref=expected[key]
    ok=bool(np.isclose(value,ref,rtol=1e-8,atol=1e-10))
    report.append({"metric":key,"acpa":value,"R":ref,"absolute_error":abs(value-ref),"pass":ok})
print(json.dumps(report,indent=2,allow_nan=False))
if not all(r["pass"] for r in report): sys.exit(1)
print(f"Independent R comparison: {len(report)}/{len(report)} passed")
