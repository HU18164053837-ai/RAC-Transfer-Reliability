from common import *
import math
RATES=[1.,.9,.8,.7,.5];RULES=['random','tree_sd','distance','sigma','joint']
INTERVALS={'pooled':'radius_pooled_90','source_balanced':'radius_source_balanced_90','adaptive':'radius_adaptive_90','adaptive_budget':'radius_adaptive_90_budget'}
def mask_for(d,rule,rate,mode,thresholds):
    # Only score and run/key columns are used, never observed strength.
    keep=np.zeros(len(d),bool)
    for run,ix in d.groupby('run').indices.items():
        ix=np.asarray(ix)
        if rate==1:keep[ix]=True;continue
        if mode=='quota':
            order=np.lexsort((d.iloc[ix].random.to_numpy(),d.iloc[ix][rule].to_numpy()))
            keep[ix[order[:math.ceil(len(ix)*rate)]]]=True
        else:
            row=thresholds[(thresholds.run==run)&(thresholds.selector==rule)&np.isclose(thresholds.retention,rate)].iloc[0]
            keep[ix]=d.iloc[ix][rule].to_numpy()<=row.threshold
    return keep
def by_source(d,radius,mask):
    y=d.target.to_numpy();mu=d.prediction.to_numpy();ae=np.abs(y-mu);r=np.asarray(radius,float);mask=np.asarray(mask,bool)
    z=pd.DataFrame(dict(source_id=d.source_id,group=d.group,n=np.ones(len(d)),accepted=mask.astype(int),covered=(mask&(ae<=r+1e-12)).astype(int),sae=mask*ae,sse=mask*(y-mu)**2,width=mask*2*r,score=mask*(2*r+20*np.maximum(ae-r,0))))
    g=z.groupby(['source_id','group'],sort=True).sum().reset_index()
    g['retention']=g.accepted/g.n;g['conditional_coverage']=np.divide(g.covered,g.accepted,out=np.full(len(g),np.nan),where=g.accepted>0)
    g['coverage_zero_if_absent']=g.conditional_coverage.fillna(0);g['success_yield']=g.covered/g.n
    g['unserved_share']=1-g.retention;g['accepted_uncovered_share']=(g.accepted-g.covered)/g.n
    assert np.allclose(g.success_yield+g.unserved_share+g.accepted_uncovered_share,1)
    return g
def summary(g):
    n=g.n.sum();a=g.accepted.sum();present=g.accepted>0
    return dict(sample_retention=a/n,source_retention=present.mean(),absent_sources=int((~present).sum()),macro_source_sample_retention=g.retention.mean(),coverage_retained=g.covered.sum()/a if a else np.nan,macro_coverage_survivors=g.loc[present,'conditional_coverage'].mean(),macro_coverage_zero_absent=g.coverage_zero_if_absent.mean(),sample_success_yield=g.covered.sum()/n,macro_source_success_yield=g.success_yield.mean(),macro_unserved_share=g.unserved_share.mean(),macro_accepted_uncovered_share=g.accepted_uncovered_share.mean(),macro_unserved_or_uncovered=1-g.success_yield.mean(),rmse=np.sqrt(g.sse.sum()/a) if a else np.nan,mae=g.sae.sum()/a if a else np.nan,mean_width=g.width.sum()/a if a else np.nan,sample_interval_score=g.score.sum()/a if a else np.nan,source_macro_interval_score=(g.loc[present,'score']/g.loc[present,'accepted']).mean(),min_source_retention=g.retention.min(),p10_source_retention=g.retention.quantile(.1),p10_zero_absent_coverage=g.coverage_zero_if_absent.quantile(.1))
def boot(g,draws,group_index):
    mult=draws[:,[group_index[v] for v in g.group]];n=mult@g.n.to_numpy();a=mult@g.accepted.to_numpy();s=mult.sum(axis=1);present=(g.accepted>0).to_numpy()
    return dict(sample_retention=a/n,source_retention=(mult@present.astype(float))/s,macro_source_sample_retention=(mult@g.retention.to_numpy())/s,macro_coverage_survivors=(mult@g.coverage_zero_if_absent.to_numpy())/(mult@present.astype(float)),macro_coverage_zero_absent=(mult@g.coverage_zero_if_absent.to_numpy())/s,sample_success_yield=(mult@g.covered.to_numpy())/n,macro_source_success_yield=(mult@g.success_yield.to_numpy())/s,macro_unserved_or_uncovered=1-(mult@g.success_yield.to_numpy())/s,rmse=np.sqrt((mult@g.sse.to_numpy())/a),mae=(mult@g.sae.to_numpy())/a,mean_width=(mult@g.width.to_numpy())/a,sample_interval_score=(mult@g.score.to_numpy())/a,source_macro_interval_score=(mult@(g.score/g.accepted).fillna(0).to_numpy())/(mult@present.astype(float)))
def main():
    p=pd.read_csv(data_file('predictions.csv'));d=p[p.scenario=='main'].reset_index(drop=True);thr=pd.read_csv(data_file('selection_thresholds.csv'));refs=pd.read_csv(data_file('new_references.csv'));frozen=pd.read_csv(data_file('new_frozen.csv'))
    mapping=refs.groupby('source_id').ref_no.apply(lambda x:','.join(map(str,x))).to_dict()
    rows=[];source_ledger=[];absent=[];store={}
    for mode in ['quota','calibration_threshold']:
        for rule in RULES:
            for rate in RATES:
                mask=mask_for(d,rule,rate,mode,thr)
                for interval,col in INTERVALS.items():
                    for repeat,sub_ix in [('all',np.arange(len(d)))]+[(str(rep),ix) for rep,ix in d.groupby('repeat').indices.items()]:
                        sub=d.iloc[sub_ix].reset_index(drop=True);g=by_source(sub,sub[col],mask[sub_ix]);g['ref_numbers']=g.source_id.map(mapping)
                        rows.append(dict(mode=mode,rule=rule,target_retention=rate,interval=interval,repeat=repeat,**summary(g)))
                        if repeat=='all':store[(mode,rule,rate,interval)]=g
                        if interval=='adaptive_budget':
                            z=g.copy();z['mode']=mode;z['rule']=rule;z['target_retention']=rate;z['repeat']=repeat;source_ledger.append(z)
                            for r in g[g.accepted==0].itertuples():absent.append(dict(mode=mode,rule=rule,target_retention=rate,repeat=repeat,source_id=r.source_id,ref_numbers=r.ref_numbers,group=r.group,original_events=int(r.n)))
    save(rows,'joint_retention_risk.csv');save(pd.concat(source_ledger,ignore_index=True),'source_retention_ledger.csv');save(absent,'disappeared_sources.csv')
    # Full-coverage interval-score comparison, row weighted and equal publication weighted.
    scores=[];score_sources=[];full={}
    for interval,col in list(INTERVALS.items())+[('group_max','radius_group_max_90')]:
        g=by_source(d,d[col],np.ones(len(d),bool));full[interval]=g
        scores.append(dict(interval=interval,**summary(g)))
        z=g.copy();z['interval']=interval;z['ref_numbers']=z.source_id.map(mapping);score_sources.append(z)
    save(scores,'interval_score_tradeoff.csv');save(pd.concat(score_sources,ignore_index=True),'interval_score_by_source.csv')
    # Reproduce the actual Phase 2 random baseline procedure; no relabelling or extra fits.
    random_rows=[]
    for rep in range(100):
        permutations={}
        for run,ix in d.groupby('run').indices.items():
            seed=2026110890+rep+sum(ord(c) for c in run)*1000
            permutations[run]=(np.asarray(ix),np.random.default_rng(seed).permutation(len(ix)))
        for rate in RATES:
            m=np.zeros(len(d),bool)
            for ix,order in permutations.values():m[ix[order[:math.ceil(len(ix)*rate)]]]=True
            g=by_source(d,d.radius_adaptive_90_budget,m);random_rows.append(dict(random_rep=rep,target_retention=rate,**summary(g)))
    random_rows=pd.DataFrame(random_rows);save(random_rows,'random_joint_metrics_100.csv')
    oldrand=pd.read_csv(data_file('random_baseline_100.csv'));base=oldrand[(oldrand.method=='adaptive')&(oldrand.budget=='matched')]
    joined=random_rows.merge(base,left_on=['random_rep','target_retention'],right_on=['rep','target_retention'],suffixes=('_new','_p2'),validate='one_to_one')
    assert np.allclose(joined.rmse_new,joined.rmse_p2,atol=1e-10)
    # 99-component bootstrap, conditional on Phase 2 fitted predictions; both rounds stay clustered.
    group_order=sorted(d.group.unique());group_index={g:i for i,g in enumerate(group_order)}
    draws=np.random.default_rng(2026110833).multinomial(len(group_order),np.full(len(group_order),1/len(group_order)),size=2000)
    contrasts=[];cis=[]
    def compare(label,a,b):
        aa,bb=boot(a,draws,group_index),boot(b,draws,group_index);sa,sb=summary(a),summary(b)
        for key in aa:
            lo,hi=np.quantile(aa[key]-bb[key],[.025,.975]);contrasts.append(dict(comparison=label,metric=key,delta=sa[key]-sb[key],ci_low=lo,ci_high=hi))
            lo,hi=np.quantile(aa[key],[.025,.975]);cis.append(dict(analysis=label,metric=key,estimate=sa[key],ci_low=lo,ci_high=hi))
    for interval in ['source_balanced','adaptive','adaptive_budget','group_max']:compare(interval+'_vs_pooled',full[interval],full['pooled'])
    joint=store[('quota','joint',.8,'adaptive_budget')]
    compare('joint80_vs_no_rejection',joint,full['adaptive_budget'])
    for rule in ['distance','tree_sd','sigma']:compare('joint80_vs_'+rule,joint,store[('quota',rule,.8,'adaptive_budget')])
    save(contrasts,'paired_cluster_changes.csv');save(cis,'cluster_ci.csv')
    # Source-specific residual shifts are descriptive; do not use them to judge data authenticity.
    diagnostics=[]
    focus_ids=set(refs[refs.ref_no.isin(REFS)].source_id)
    for repeat,dd in [('all',d)]+[(str(rep),z) for rep,z in d.groupby('repeat')]:
        for source,z in dd[dd.source_id.isin(focus_ids)].groupby('source_id'):
            err=z.prediction-z.target;ae=np.abs(err)
            diagnostics.append(dict(repeat=repeat,source_id=source,ref_numbers=mapping[source],unique_records=z.record_key.nunique(),prediction_events=len(z),target_mean=z.target.mean(),prediction_mean=z.prediction.mean(),bias=err.mean(),mae=ae.mean(),rmse=np.sqrt(np.mean(err**2)),bias2_mse_ratio=err.mean()**2/np.mean(err**2),negative_residual_fraction=(err<0).mean(),positive_residual_fraction=(err>0).mean(),pooled_coverage=(ae<=z.radius_pooled_90+1e-12).mean(),balanced_coverage=(ae<=z.radius_source_balanced_90+1e-12).mean(),adaptive_budget_coverage=(ae<=z.radius_adaptive_90_budget+1e-12).mean()))
    save(diagnostics,'focus_residual_diagnostics.csv')
    # Record known source identifiers of all databases for independent-candidate screening.
    old=pd.read_csv(data_file('old_input.csv'));allold=pd.read_csv(data_file('old_all980_classification.csv'));known=sorted(set(refs.source_id)|set(old.source_id)|set(allold.source_id));save([dict(source_id=s) for s in known],'known_sources.csv')
    print('Supplement complete; no model fits. Main predictions',len(d),'sources',d.source_id.nunique(),'joint80',json.dumps(summary(joint),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
