"""Student t intervals for independent observations (or paired differences).
Critical values from the Student distribution, rounded to six decimals.
No interval for a degenerate or insufficient sample.
"""
from math import sqrt, isfinite
from statistics import mean, stdev

# Two-sided 95% critical values for df=1..30; for larger df use
# conservative lower degrees of freedom (explicitly reported).
CRITICAL = (12.706205,4.302653,3.182446,2.776445,2.570582,2.446912,2.364624,2.306004,2.262157,2.228139,2.200985,2.178813,2.160369,2.144787,2.131450,2.119905,2.109816,2.100922,2.093024,2.085963,2.079614,2.073873,2.068658,2.063899,2.059539,2.055529,2.051831,2.048407,2.045230,2.042272)
EXTRA = {40:2.021075,60:2.000298,80:1.990063,100:1.983972,120:1.979930}

def mean_interval(values):
    data=[v for v in values if v is not None]
    if any(not isfinite(v) for v in data):
        raise ValueError("Nonfinite sample")
    n=len(data)
    if n<2:
        return None
    sd=stdev(data)
    if sd==0:
        return None
    df=n-1
    used=min(df,30)
    if df>30:
        used=max([30]+[k for k in EXTRA if k<=df])
    critical=CRITICAL[used-1] if used<=30 else EXTRA[used]
    center=mean(data)
    margin=critical*sd/sqrt(n)
    return {"n":n,"df":df,"df_used":used,"mean":center,"lower":center-margin,"upper":center+margin}
