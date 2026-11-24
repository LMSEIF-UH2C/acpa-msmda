"""Explicit complete-case inference for independent participants; no causal claims."""
from __future__ import annotations
import numpy as np
from scipy import stats

def vector(values):
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 3 or not np.isfinite(x).all():
        raise ValueError("At least three finite observations required")
    return x

def correlate(a, b, method="pearson"):
    x,y=vector(a),vector(b)
    if len(x)!=len(y) or np.ptp(x)==0 or np.ptp(y)==0:
        raise ValueError("Equal paired lengths and nonconstant variables required")
    if method=="pearson":
        r=stats.pearsonr(x,y)
        ci=r.confidence_interval()
        return {"n":len(x),"r":float(r.statistic),"p":float(r.pvalue),"ci95":[float(ci.low),float(ci.high)]}
    if method=="spearman":
        r=stats.spearmanr(x,y)
        return {"n":len(x),"rho":float(r.statistic),"p":float(r.pvalue)}
    raise ValueError("Unknown correlation")

def paired_test(before, after, method="t"):
    x,y=vector(before),vector(after)
    if len(x)!=len(y):
        raise ValueError("Paired lengths differ")
    d=y-x
    if method=="t":
        sd=float(np.std(d,ddof=1))
        if sd==0:
            raise ValueError("Constant paired differences")
        r=stats.ttest_rel(y,x)
        ci=r.confidence_interval()
        return {"n":len(d),"t":float(r.statistic),"df":len(d)-1,"p":float(r.pvalue),"mean_difference":float(np.mean(d)),"dz":float(np.mean(d)/sd),"ci95":[float(ci.low),float(ci.high)]}
    if method=="wilcoxon":
        if not np.any(d):
            raise ValueError("All paired differences are zero")
        r=stats.wilcoxon(d,alternative="two-sided")
        return {"n":len(d),"W":float(r.statistic),"p":float(r.pvalue)}
    raise ValueError("Unknown paired test")

def independent_test(a,b,method="welch"):
    x,y=vector(a),vector(b)
    if method=="welch":
        if np.var(x,ddof=1)==0 and np.var(y,ddof=1)==0:
            raise ValueError("Both groups constant")
        r=stats.ttest_ind(x,y,equal_var=False)
        ci=r.confidence_interval()
        return {"n1":len(x),"n2":len(y),"t":float(r.statistic),"df":float(r.df),"p":float(r.pvalue),"mean_difference":float(np.mean(x)-np.mean(y)),"ci95":[float(ci.low),float(ci.high)]}
    if method=="mann_whitney":
        r=stats.mannwhitneyu(x,y,alternative="two-sided")
        return {"n1":len(x),"n2":len(y),"U":float(r.statistic),"p":float(r.pvalue),"rank_biserial":float(2*r.statistic/(len(x)*len(y))-1)}
    raise ValueError("Unknown independent test")

def repeated_anova(values):
    """One within-subject factor, balanced complete cases. Uncorrected sphericity assumption."""
    a=np.asarray(values,dtype=float)
    if a.ndim!=2 or min(a.shape)<3 or not np.isfinite(a).all():
        raise ValueError("At least three complete subjects and occasions required")
    n,k=a.shape
    grand=a.mean()
    ss_time=n*np.sum((a.mean(axis=0)-grand)**2)
    ss_error=np.sum((a-a.mean(axis=0)-a.mean(axis=1)[:,None]+grand)**2)
    df1=k-1;df2=(n-1)*df1
    if ss_error<=np.finfo(float).eps:
        raise ValueError("Zero residual variance")
    f=(ss_time/df1)/(ss_error/df2)
    cov=np.cov(a,rowvar=False)
    center=np.eye(k)-np.ones((k,k))/k
    cov=center@cov@center
    den=(k-1)*np.trace(cov@cov)
    epsilon=float(np.clip(np.trace(cov)**2/den,1/(k-1),1)) if den>0 else None
    return {"n":n,"k":k,"F":float(f),"df1":df1,"df2":df2,"p":float(stats.f.sf(f,df1,df2)),"partial_eta2":float(ss_time/(ss_time+ss_error)),"gg_epsilon":epsilon,"p_gg":float(stats.f.sf(f,epsilon*df1,epsilon*df2)) if epsilon else None}

def friedman(values):
    a=np.asarray(values,dtype=float)
    if a.ndim!=2 or min(a.shape)<3 or not np.isfinite(a).all() or np.all(np.ptp(a,axis=1)==0):
        raise ValueError("Nondegenerate complete panel required")
    n,k=a.shape
    r=stats.friedmanchisquare(*a.T)
    return {"n":n,"k":k,"chi2":float(r.statistic),"p":float(r.pvalue),"kendall_W":float(r.statistic/(n*(k-1)))}

def regression(y,predictors,moderation=False):
    """OLS with classical errors. Moderation uses centered X and M and their product."""
    y=vector(y); x=np.asarray(predictors,dtype=float)
    if x.ndim!=2 or x.shape[0]!=len(y) or not np.isfinite(x).all() or x.shape[1]<1:
        raise ValueError("Invalid predictor matrix")
    centers = None
    if moderation:
        if x.shape[1]!=2:
            raise ValueError("Moderation requires X and M")
        centers=x.mean(axis=0)
        x=x-centers
        x=np.column_stack((x,x[:,0]*x[:,1]))
    X=np.column_stack((np.ones(len(y)),x))
    df=len(y)-X.shape[1]
    if df<2 or np.linalg.matrix_rank(X)!=X.shape[1]:
        raise ValueError("Insufficient degrees of freedom or collinearity")
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    residual=y-X@beta
    sse=float(residual@residual); sst=float(np.sum((y-y.mean())**2))
    if sse<=np.finfo(float).eps or sst==0:
        raise ValueError("Degenerate residual or outcome variance")
    condition=float(np.linalg.cond(X))
    if not np.isfinite(condition) or condition>1e8:
        raise ValueError("Ill-conditioned model; rescale or remove collinear predictors")
    # SVD-based covariance avoids explicitly inverting the normal equations.
    _, singular, vt=np.linalg.svd(X,full_matrices=False)
    covariance=(vt.T*(1/singular**2))@vt*sse/df
    se=np.sqrt(np.diag(covariance))
    t=beta/se; crit=stats.t.ppf(.975,df)
    r2=1-sse/sst
    p=X.shape[1]-1
    model_f=max(0., ((sst-sse)/p)/(sse/df))
    standardized=residual/np.sqrt(sse/df)
    return {"n":len(y),"df":df,"r2":r2,"adjusted_r2":1-(1-r2)*(len(y)-1)/df,"model_F":model_f,"model_df1":p,"model_p":float(stats.f.sf(model_f,p,df)),"residual_sd":float(np.sqrt(sse/df)),"max_abs_scaled_residual":float(np.max(np.abs(standardized))),"predictor_centers":None if centers is None else centers.tolist(),"coefficients":[{"b":float(b),"se":float(s),"t":float(v),"p":float(2*stats.t.sf(abs(v),df)),"ci95":[float(b-crit*s),float(b+crit*s)]} for b,s,v in zip(beta,se,t)],"condition_number":condition}

def one_way(groups):
    arrays=[vector(g) for g in groups]
    if len(arrays)<2:
        raise ValueError("At least two groups required")
    all_values=np.concatenate(arrays)
    ssb=sum(len(g)*(g.mean()-all_values.mean())**2 for g in arrays)
    ssw=sum(np.sum((g-g.mean())**2) for g in arrays)
    if ssw<=0:
        raise ValueError("Zero within-group variance")
    r=stats.f_oneway(*arrays)
    return {"n":len(all_values),"F":float(r.statistic),"df1":len(arrays)-1,"df2":len(all_values)-len(arrays),"p":float(r.pvalue),"eta2":float(ssb/(ssb+ssw))}


def mixed_anova(groups):
    """Balanced group sizes, complete panels, independent subjects, common covariance.
    Equal n is required to avoid ambiguous sums-of-squares conventions.
    """
    arrays=[np.asarray(g,dtype=float) for g in groups]
    if len(arrays)<2 or any(a.ndim!=2 or min(a.shape)<2 or not np.isfinite(a).all() for a in arrays):
        raise ValueError("At least two valid complete groups required")
    if len({a.shape for a in arrays})!=1:
        raise ValueError("Equal group sizes and common occasions required")
    a=np.stack(arrays)
    g,n,k=a.shape
    if n<3:
        raise ValueError("At least three subjects per group required")
    grand=a.mean()
    gm=a.mean(axis=(1,2))
    tm=a.mean(axis=(0,1))
    cell=a.mean(axis=1)
    sm=a.mean(axis=2)
    ss_group=n*k*np.sum((gm-grand)**2)
    ss_subject=k*np.sum((sm-gm[:,None])**2)
    ss_time=g*n*np.sum((tm-grand)**2)
    ss_interaction=n*np.sum((cell-gm[:,None]-tm[None,:]+grand)**2)
    ss_error=np.sum((a-cell[:,None,:]-sm[:,:,None]+gm[:,None,None])**2)
    df_subject=g*(n-1)
    df_error=df_subject*(k-1)
    if min(ss_subject,ss_error)<=np.finfo(float).eps:
        raise ValueError("Degenerate error variance")
    residual=np.concatenate([x-x.mean(axis=0) for x in arrays])
    c=np.eye(k)-np.ones((k,k))/k
    cov=c@np.cov(residual,rowvar=False)@c
    den=(k-1)*np.trace(cov@cov)
    eps=float(np.clip(np.trace(cov)**2/den,1/(k-1),1)) if den>0 else 1.0
    def effect(ss,df,error,edf,correction=1.0):
        f=(ss/df)/(error/edf)
        return {"F":float(f),"df1":df,"df2":edf,"p":float(stats.f.sf(f,df,edf)),
                "partial_eta2":float(ss/(ss+error)), "gg_epsilon":correction,
                "p_gg":float(stats.f.sf(f,df*correction,edf*correction))}
    return {"groups":g,"n_per_group":n,"occasions":k,
            "group":effect(ss_group,g-1,ss_subject,df_subject),
            "time":effect(ss_time,k-1,ss_error,df_error,eps),
            "group_time":effect(ss_interaction,(g-1)*(k-1),ss_error,df_error,eps)}

def paired_posthoc(values):
    """Pairwise paired t tests with Holm familywise correction."""
    from itertools import combinations
    a=np.asarray(values,dtype=float)
    if a.ndim!=2 or min(a.shape)<3 or not np.isfinite(a).all():
        raise ValueError("Complete panel required")
    results=[]
    for i,j in combinations(range(a.shape[1]),2):
        r=paired_test(a[:,i],a[:,j])
        results.append({"first":i,"second":j,**r})
    order=sorted(range(len(results)),key=lambda i:results[i]["p"])
    running=0.
    for rank,i in enumerate(order):
        running=max(running,min(1.,(len(order)-rank)*results[i]["p"]))
        results[i]["p_holm"]=running
    return results
