"""Two-occasion test-retest agreement, conditional on stable true performance."""
from math import sqrt, isfinite
from statistics import mean, stdev

def agreement(first, second):
    if len(first)!=len(second):
        raise ValueError("Unmatched series")
    pairs=[(a,b) for a,b in zip(first,second) if a is not None and b is not None]
    if any(not isfinite(x) for pair in pairs for x in pair):
        raise ValueError("Nonfinite measurement")
    n=len(pairs)
    if n<3:
        return None
    diffs=[b-a for a,b in pairs]
    bias=mean(diffs)
    sd=stdev(diffs)
    grand=mean([x for pair in pairs for x in pair])
    subjects=[mean(pair) for pair in pairs]
    occasions=[mean([pair[j] for pair in pairs]) for j in range(2)]
    ms_subject=2*sum((m-grand)**2 for m in subjects)/(n-1)
    ms_occasion=n*sum((m-grand)**2 for m in occasions)
    ms_error=sum((pair[j]-subjects[i]-occasions[j]+grand)**2 for i,pair in enumerate(pairs) for j in range(2))/(n-1)
    denominator=ms_subject+ms_error+2*(ms_occasion-ms_error)/n
    icc=(ms_subject-ms_error)/denominator if denominator>0 else None
    return {"n":n,"bias":bias,"sd":sd,"sem":sd/sqrt(2),"mdc95":1.96*sd,
            "lower":bias-1.96*sd,"upper":bias+1.96*sd,"icc":icc,
            "points":[{"mean":mean(pair),"difference":d} for pair,d in zip(pairs,diffs)]}
