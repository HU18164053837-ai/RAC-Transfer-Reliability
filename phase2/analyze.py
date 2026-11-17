from common import *
import math
from scipy.stats import spearmanr
SELECTORS=['random','tree_sd','distance','sigma','joint']
def select_mask(d,selector,retention,mode,thresholds=None):
    # This function receives ONLY unlabelled scores/keys/run. No response is accessed.
    result=np.zeros(len(d),bool)
    for run,ix in d.groupby('run',sort=True).indices.items():
        ix=np.asarray(ix);score=d.iloc[ix][selector].to_numpy(float)
        if retention==1:result[ix]=True;continue
        if mode=='quota':
            tie=d.iloc[ix]['random'].to_numpy(float)
            order=np.lexsort((tie,score));keep=order[:math.ceil(len(ix)*retention)]
            result[ix[keep]]=True
        else:
            q=thresholds[(thresholds.run==run)&(thresholds.selector==selector)&np.isclose(thresholds.retention,retention)].threshold.iloc[0]
            result[ix]=score<=q
    return result
def metrics(d,radius,mask=None,alpha=.1):
    if mask is None:mask=np.ones(len(d),bool)
    n_total=len(d);orig_sources=d.source_id.nunique();s=d.loc[mask].copy();r=np.asarray(radius)[mask]
    if not len(s):return dict(n=0,retention=0.,sources=0,source_retention=0.)
    err=s.target.to_numpy()-s.prediction.to_numpy();ae=np.abs(err);cov=ae<=r+1e-12
    w=2*r;s['ae']=ae;s['sqe']=err**2;s['covered']=cov;s['width']=w
    g=s.groupby('source_id').agg(n=('covered','size'),mae=('ae','mean'),mse=('sqe','mean'),coverage=('covered','mean'),width=('width','mean'),unique_records=('record_key','nunique'))
    good=g[g.unique_records>=5]
    score=w+2/alpha*np.maximum(ae-r,0)
    complete=s.groupby(['repeat','group']).covered.all().mean()
    return dict(n=len(s),unique_records=s.record_key.nunique(),retention=len(s)/n_total,sources=len(g),source_retention=len(g)/orig_sources,fully_rejected_sources=orig_sources-len(g),rmse=np.sqrt(np.mean(err**2)),mae=ae.mean(),coverage=cov.mean(),source_macro_coverage=g.coverage.mean(),min_source_coverage=g.coverage.min(),p10_source_coverage=g.coverage.quantile(.1),worst_source_coverage_n5=good.coverage.min() if len(good) else np.nan,worst_source_mae_n5=good.mae.max() if len(good) else np.nan,eligible_sources_n5=len(good),source_fraction_below80=(g.coverage<.8).mean(),mean_width=w.mean(),median_width=np.median(w),p90_width=np.quantile(w,.9,method='inverted_cdf'),source_macro_mae=g.mae.mean(),interval_score=score.mean(),complete_group_coverage=complete)
def bootstrap_arrays(d,radius,mask,draws,source_order,source_groups):
    s_index=pd.Categorical(d.source_id,categories=source_order).codes
    err=(d.target-d.prediction).to_numpy();r=np.asarray(radius);m=np.asarray(mask,float)
    n=np.bincount(s_index,weights=m,minlength=len(source_order))
    sae=np.bincount(s_index,weights=m*np.abs(err),minlength=len(source_order));sse=np.bincount(s_index,weights=m*err**2,minlength=len(source_order))
    covered=np.bincount(s_index,weights=m*(np.abs(err)<=r+1e-12),minlength=len(source_order));width=np.bincount(s_index,weights=m*2*r,minlength=len(source_order))
    source_cov=np.divide(covered,n,out=np.zeros_like(n),where=n>0);valid=n>0
    mult=draws[:,source_groups];den=mult@n
    macro_den=mult@valid.astype(float)
    res={'rmse':np.sqrt((mult@sse)/den),'mae':(mult@sae)/den,'coverage':(mult@covered)/den,'mean_width':(mult@width)/den,'source_macro_coverage':(mult@(source_cov*valid))/macro_den}
    order=np.argsort(source_cov);weights=mult[:,order]*valid[order];cdf=np.cumsum(weights,axis=1)/macro_den[:,None]
    res['p10_source_coverage']=source_cov[order[np.argmax(cdf>=.1,axis=1)]]
    return res
def weighted_spearman_bootstrap(x,y,weights):
    # Exact midranks of the replicated-source sample, without materializing duplicates.
    ranks=[]
    for values in [x,y]:
        unique,inv=np.unique(values,return_inverse=True);mass=np.zeros((len(weights),len(unique)))
        for j in range(len(values)):mass[:,inv[j]]+=weights[:,j]
        midpoint=np.cumsum(mass,axis=1)-mass/2
        ranks.append(midpoint[:,inv])
    total=weights.sum(axis=1);rx,ry=ranks
    rx=rx-(weights*rx).sum(axis=1)[:,None]/total[:,None]
    ry=ry-(weights*ry).sum(axis=1)[:,None]/total[:,None]
    return (weights*rx*ry).sum(axis=1)/np.sqrt((weights*rx**2).sum(axis=1)*(weights*ry**2).sum(axis=1))
def main():
    p=pd.read_csv(OUT/'predictions.csv');threshold=pd.read_csv(OUT/'selection_thresholds.csv');results=[];per_source=[];strata=[]
    for scenario,d0 in p.groupby('scenario'):
        for repeat_label,d in [('all',d0)]+[(str(rep),z) for rep,z in d0.groupby('repeat')]:
            d=d.reset_index(drop=True)
            for level in [80,90,95]:
                for method in METHODS:
                    for budget in (['native','matched'] if level==90 else ['native']):
                        col=f'radius_{method}_{level}'+('_budget' if budget=='matched' else '')
                        rec=dict(scenario=scenario,repeat=repeat_label,method=method,nominal=level/100,budget=budget,**metrics(d,d[col],alpha=1-level/100))
                        results.append(rec)
                        if level==90 and repeat_label=='all':
                            for source,s in d.groupby('source_id'):
                                mm=metrics(s,s[col]);per_source.append(dict(scenario=scenario,method=method,budget=budget,source_id=source,group=s.group.iloc[0],source_n_records=s.record_key.nunique(),**mm))
                            if scenario=='main':
                                for name,mask in [('RAC',d.rar>0),('natural_control',d.rar==0),('unique_input_target',d.unique_xy_first.astype(bool)),('metadata_risk',d.metadata_risk_group.astype(bool)),('metadata_not_flagged',~d.metadata_risk_group.astype(bool))]:
                                    dd=d[mask];strata.append(dict(stratum=name,method=method,budget=budget,**metrics(dd,dd[col])))
    save(results,'interval_metrics.csv');save(per_source,'source_coverage.csv');save(strata,'sensitivity_subsets.csv')
    selections=[];ledger=[]
    # Use four representations. Fixed-radius source balancing cannot alter its own width ranking.
    evals=[('pooled','native'),('source_balanced','native'),('adaptive','native'),('adaptive','matched')]
    for scenario,d0 in p.groupby('scenario'):
        d=d0.reset_index(drop=True);unlabelled=d[['run','record_key','random','tree_sd','distance','sigma','joint']]
        for mode in ['quota','calibration_threshold']:
            for selector in SELECTORS:
                for retain in RETENTIONS:
                    mask=select_mask(unlabelled,selector,retain,mode,threshold)
                    for method,budget in evals:
                        col=f'radius_{method}_90'+('_budget' if budget=='matched' else '')
                        selections.append(dict(scenario=scenario,mode=mode,selector=selector,target_retention=retain,method=method,budget=budget,**metrics(d,d[col],mask)))
                    if scenario=='main':
                        z=d.loc[mask,['run','record_key']].copy();z['mode']=mode;z['selector']=selector;z['target_retention']=retain;ledger.append(z)
    save(selections,'selective_metrics.csv');save(pd.concat(ledger,ignore_index=True),'selection_ledger.csv')
    mainp=p[p.scenario=='main'].reset_index(drop=True)
    random=[]
    for rep in range(100):
        permutations={}
        for run,ix in mainp.groupby('run').indices.items():
            seed=2026110890+rep+sum(ord(c) for c in run)*1000
            permutations[run]=(np.asarray(ix),np.random.default_rng(seed).permutation(len(ix)))
        for retain in RETENTIONS:
            mask=np.zeros(len(mainp),bool)
            for ix,order in permutations.values():mask[ix[order[:math.ceil(len(ix)*retain)]]]=True
            for method,budget in [('pooled','native'),('adaptive','native'),('adaptive','matched')]:
                col=f'radius_{method}_90'+('_budget' if budget=='matched' else '')
                random.append(dict(rep=rep,target_retention=retain,method=method,budget=budget,**metrics(mainp,mainp[col],mask)))
    save(random,'random_baseline_100.csv')
    # Connected-component paired bootstrap. Preserve both test rounds for a row as one cluster.
    src=mainp.groupby('source_id').group.first();source_order=src.index.to_numpy();group_order=np.array(sorted(mainp.group.unique()))
    gmap={g:i for i,g in enumerate(group_order)};source_groups=np.array([gmap[g] for g in src])
    draws=np.random.default_rng(2026110899).multinomial(len(group_order),np.full(len(group_order),1/len(group_order)),size=2000)
    ci=[];paired=[]
    def boot(label,radius,mask,reference=None):
        arr=bootstrap_arrays(mainp,radius,mask,draws,source_order,source_groups)
        point=metrics(mainp,radius,mask)
        for metric,values in arr.items():
            lo,hi=np.quantile(values,[.025,.975]);ci.append(dict(analysis=label,metric=metric,estimate=point[metric],ci_low=lo,ci_high=hi,clusters=len(group_order),bootstrap=2000))
        if reference is not None:
            refarr,refpoint=reference
            for metric,values in arr.items():
                diff=values-refarr[metric];lo,hi=np.quantile(diff,[.025,.975]);paired.append(dict(analysis=label,metric=metric,delta=point[metric]-refpoint[metric],ci_low=lo,ci_high=hi))
            reduction=1-arr['rmse']/refarr['rmse'];lo,hi=np.quantile(reduction,[.025,.975]);paired.append(dict(analysis=label,metric='relative_rmse_reduction',delta=1-point['rmse']/refpoint['rmse'],ci_low=lo,ci_high=hi))
        return arr,point
    ones=np.ones(len(mainp),bool);pooled=boot('pooled_native',mainp.radius_pooled_90,ones)
    for method in ['source_balanced','adaptive','group_max']:
        for budget in ['native','matched']:
            col=f'radius_{method}_90'+('_budget' if budget=='matched' else '')
            boot(method+'_'+budget,mainp[col],ones,pooled)
    adapt_ref=boot('adaptive_matched_random_expectation',mainp.radius_adaptive_90_budget,ones)
    unl=mainp[['run','record_key','random','tree_sd','distance','sigma','joint']]
    for mode in ['quota','calibration_threshold']:
        for retain in [.9,.8]:
            for selector in ['tree_sd','distance','sigma','joint']:
                mask=select_mask(unl,selector,retain,mode,threshold)
                boot(f'{mode}_{selector}_{retain:.1f}',mainp.radius_adaptive_90_budget,mask,adapt_ref)
    jointmask=select_mask(unl,'joint',.8,'quota',threshold)
    for rule in ['tree_sd','distance','sigma']:
        baseline_mask=select_mask(unl,rule,.8,'quota',threshold)
        ref=bootstrap_arrays(mainp,mainp.radius_adaptive_90_budget,baseline_mask,draws,source_order,source_groups),metrics(mainp,mainp.radius_adaptive_90_budget,baseline_mask)
        boot('quota_joint_0.8_vs_'+rule,mainp.radius_adaptive_90_budget,jointmask,ref)
    save(ci,'cluster_bootstrap_ci.csv');save(paired,'paired_changes.csv')
    # Source-level association diagnostics. Outcomes used only after selection rules are fixed.
    diag=[]
    for source,d in mainp.groupby('source_id'):
        ae=np.abs(d.target-d.prediction);biases=[]
        for rep,z in d.groupby('repeat'):biases.append(float(np.mean(z.prediction-z.target)**2/np.mean((z.prediction-z.target)**2)))
        diag.append(dict(source_id=source,group=d.group.iloc[0],refs=','.join(map(str,sorted(d.ref_no.dropna().astype(int).unique()))),n_records=d.record_key.nunique(),mae=ae.mean(),bias=(d.prediction-d.target).mean(),bias2_mse_ratio=np.mean(biases),mean_target=d.target.mean(),distance=d.distance.mean(),tree_sd=d.tree_sd.mean(),sigma=d.sigma.mean(),feature_shift=d.source_feature_shift.mean(),water_binder=d.wb.mean(),absorption=d.absorption.mean(),rar=d.rar.mean(),pooled_coverage=(ae<=d.radius_pooled_90).mean(),adaptive_budget_coverage=(ae<=d.radius_adaptive_90_budget).mean(),metadata_risk=bool(d.metadata_risk_group.iloc[0])))
    diag=pd.DataFrame(diag);save(diag,'source_diagnostics.csv')
    corr=[];rng=np.random.default_rng(2026110898)
    for feature in ['distance','tree_sd','sigma','feature_shift','water_binder','absorption','rar']:
        for outcome in ['mae','pooled_coverage','adaptive_budget_coverage','bias2_mse_ratio']:
            r=spearmanr(diag[feature],diag[outcome]).statistic
            # Same component resampling as materializing repeated source rows; vectorized exact weighted ranks.
            chosen=rng.choice(len(group_order),(2000,len(group_order)),replace=True)
            mass=np.zeros((2000,len(group_order)),int)
            np.add.at(mass,(np.repeat(np.arange(2000),len(group_order)),chosen.ravel()),1)
            weights=mass[:,[gmap[g] for g in diag.group]]
            vals=weighted_spearman_bootstrap(diag[feature].to_numpy(),diag[outcome].to_numpy(),weights)
            # Verify implementation against direct replicated-source Spearman on fixed resamples.
            for b in range(3):
                idx=np.repeat(np.arange(len(diag)),weights[b])
                direct=spearmanr(diag.iloc[idx][feature],diag.iloc[idx][outcome]).statistic
                assert abs(direct-vals[b])<1e-10
            lo,hi=np.quantile(vals,[.025,.975]);corr.append(dict(feature=feature,outcome=outcome,spearman=r,ci_low=lo,ci_high=hi,bootstrap=2000,interpretation='exploratory_association_no_causal_claim'))
    save(corr,'source_associations.csv')
    # Descriptive within-source residual coherence, with two rounds kept separate.
    decomp=[]
    for repeat,d in mainp.groupby('repeat'):
        z=d.assign(err=d.prediction-d.target);gg=z.groupby('source_id').err.agg(['mean','size'])
        decomp.append(dict(repeat=repeat,bias_energy_fraction=float(np.sum(gg['size']*gg['mean']**2)/np.sum(z.err**2)),sources=len(gg),mae=float(np.mean(np.abs(z.err)))))
    save(decomp,'residual_decomposition.csv')
    print('Analysis complete; primary intervals',len(results),'selection rows',len(selections),'bootstrap contrasts',len(paired),flush=True)
if __name__=='__main__':main()
