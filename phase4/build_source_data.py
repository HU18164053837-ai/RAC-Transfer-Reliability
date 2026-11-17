"""Presentation-only extraction of frozen results. No estimator, fitting, or new inference."""
from common import *
import shutil
TRACE=[]
def extract(stage,name,filename,where=None,fields=None,note='Frozen values; no new inference'):
    z=read(stage,name)
    if where:z=z.query(where).copy()
    if fields:z=z[fields]
    save(z,SD/filename)
    TRACE.append(dict(output=filename,source=f'phase{stage}/results/{name}',filter=where or 'all rows',fields='|'.join(fields or list(z.columns)),calculation=note,producer=f'phase{stage}/'+('supplement.py' if stage==3 and name not in ['source_field_evidence.csv','source_verification_summary.csv'] else 'analyze.py' if stage==2 else 'curate_evidence.py')))
    return z
def main():
    f=pd.read_csv(P2/'data/new_frozen.csv');refs=pd.read_csv(P2/'data/new_references.csv')
    source=f.groupby(['source_id','group']).agg(records=('record_id','size'),ref_no=('ref_no',lambda x:','.join(map(str,sorted(set(x))))),metadata_risk=('metadata_risk_group','first')).reset_index()
    source['rank_size']=source.records.rank(method='first',ascending=False).astype(int)
    save(source,SD/'F1_sources.csv');save(f.groupby('group').agg(sources=('source_id','nunique'),records=('record_id','size')).reset_index(),SD/'F1_components.csv')
    TRACE.extend([dict(output=x,source='phase2/data/new_frozen.csv',filter='all 1,736 rows',fields='source_id|group|record_id|ref_no|metadata_risk_group',calculation='Descriptive counts only; 115 sources and 99 components',producer='phase4/build_source_data.py') for x in ['F1_sources.csv','F1_components.csv']])
    extract(2,'split_checks.csv','F1_splits.csv',"scenario=='main'")
    trade=extract(3,'interval_score_tradeoff.csv','F2_interval_metrics.csv')
    extract(2,'cluster_bootstrap_ci.csv','F2_coverage_width_ci.csv')
    extract(3,'paired_cluster_changes.csv','F2_F5_paired_changes.csv')
    extract(3,'cluster_ci.csv','F2_F4_cluster_ci.csv')
    ss=extract(3,'interval_score_by_source.csv','F3_all_source_coverage.csv')
    diag=extract(3,'focus_residual_diagnostics.csv','F3_focus_diagnostics.csv')
    p=read(2,'predictions.csv');d=p[p.scenario=='main'].copy()
    ds=d[d.ref_no.isin([36,82,109])][['record_key','ref_no','source_id','group','repeat','fold','target','prediction']].copy();ds['residual']=ds.prediction-ds.target
    save(ds,SD/'F3_focus_predictions.csv')
    TRACE.append(dict(output='F3_focus_predictions.csv',source='phase2/results/predictions.csv',filter="scenario=main; ref_no in [36,82,109]; all records and both repeats",fields='record_key|ref_no|source_id|group|repeat|fold|target|prediction',calculation='residual=prediction-target; no averaging or subsampling',producer='phase2/run_experiments.py; phase4/build_source_data.py'))
    j=extract(3,'joint_retention_risk.csv','F4_F5_retention.csv')
    extract(3,'source_retention_ledger.csv','F4_F5_source_ledger.csv')
    extract(3,'random_joint_metrics_100.csv','F5_random_100.csv')
    extract(3,'disappeared_sources.csv','F5_disappeared_sources.csv')
    # Table 1: each factual row has an explicit primary frozen evidence location.
    t1=[('Main cohort','1,736 mixture records; all original flags retained','phase2/data/new_frozen.csv; phase2/data/database_README.md'),('Inputs and target','11 numeric inputs; 28-day MPa label; 150 mm cube equivalence is a compiler claim','phase2/common.py FULL; phase2/data/database_README.md'),('Publication identity','115 canonical publication sources; database references [2] and [75] share one DOI','phase2/data/new_references.csv'),('Association unit','99 connected components; source identity plus eight-field near-recipe links','phase2/results/verified_recipe_edges.csv; phase2/data/new_frozen.csv'),('Repeated evaluation','2 × 5 outer component folds; 3,472 prediction events; 1,736 unique records','phase2/results/predictions.csv; phase2/results/split_ledger.csv'),('Unresolved metadata','7 priority sources, 247 records; original row-level confirmation incomplete for all seven','phase3/results/source_verification_summary.csv'),('Risk sensitivity','4 flagged components, 254 records removed in an existing one-repeat analysis','phase2/results/label_summary.csv; phase2/results/interval_metrics.csv'),('Independent confirmation','6 candidates screened; 0 admitted records in the bounded search','phase3/results/independent_candidates.csv'),('Historical corpus','980 raw candidates; 722 frozen records; 586 in six-input stress cohort','phase3/data/old_all980_classification.csv; phase2/data/old_input.csv core_eligible; phase2/data/legacy_count_evidence.md')]
    save([dict(item=a,scope_or_evidence=b,trace=c) for a,b,c in t1],ROOT/'tables/Table1_evidence_scope.csv')
    # Table 2 uses stored confidence intervals (different fixed seeds documented in captions).
    c2=read(2,'cluster_bootstrap_ci.csv');c3=read(3,'cluster_ci.csv')
    rows=[]
    for m in METHODS:
        r=trade[trade.interval==m].iloc[0];row=dict(interval=m)
        for metric in ['coverage_retained','macro_coverage_survivors','mean_width','sample_interval_score','source_macro_interval_score']:row[metric]=r[metric]
        analysis={'pooled':'pooled_native','source_balanced':'source_balanced_native','adaptive':'adaptive_native','adaptive_budget':'adaptive_matched','group_max':'group_max_native'}[m]
        for key,dest in [('coverage','coverage_retained'),('source_macro_coverage','macro_coverage_survivors'),('mean_width','mean_width')]:
            q=c2[(c2.analysis==analysis)&(c2.metric==key)].iloc[0]
            assert np.isclose(q.estimate,r[dest]);row[dest+'_ci_low']=q.ci_low;row[dest+'_ci_high']=q.ci_high
        if m!='pooled':
            for key in ['sample_interval_score','source_macro_interval_score']:
                q=c3[(c3.analysis==m+'_vs_pooled')&(c3.metric==key)].iloc[0];assert np.isclose(q.estimate,r[key]);row[key+'_ci_low']=q.ci_low;row[key+'_ci_high']=q.ci_high
        else:
            # Pooled score CI is not in the frozen tables; leave genuinely unavailable bounds empty.
            for key in ['sample_interval_score','source_macro_interval_score']:row[key+'_ci_low']=np.nan;row[key+'_ci_high']=np.nan
        rows.append(row)
    save(rows,ROOT/'tables/Table2_interval_reliability.csv')
    rnd=read(3,'random_joint_metrics_100.csv');t3=[]
    for rate in [1.,.9,.8]:
        for rule in (['joint'] if rate==1 else ['random','tree_sd','distance','sigma','joint']):
            if rule=='random':
                z=rnd[np.isclose(rnd.target_retention,rate)];r=z.select_dtypes('number').mean().to_dict();r['aggregation']='100 frozen random permutations; mean';r['rmse_random_sd']=z.rmse.std(ddof=1)
            else:r=j[(j['repeat'].astype(str)=='all')&(j['mode']=='quota')&(j.rule==rule)&(j.interval=='adaptive_budget')&np.isclose(j.target_retention,rate)].iloc[0].to_dict();r['aggregation']='Frozen score ordering; both repeats pooled'
            r.update(rule='none' if rate==1 else rule,target_retention=rate);t3.append(r)
    cols=['rule','target_retention','aggregation','sample_retention','source_retention','absent_sources','macro_source_sample_retention','rmse','mae','coverage_retained','macro_coverage_survivors','macro_coverage_zero_absent','macro_source_success_yield','sample_success_yield','mean_width','rmse_random_sd']
    save(pd.DataFrame(t3).reindex(columns=cols),ROOT/'tables/Table3_selection_service.csv')
    TRACE.extend([dict(output='tables/Table2_interval_reliability.csv',source='phase3/results/interval_score_tradeoff.csv; phase2/results/cluster_bootstrap_ci.csv; phase3/results/cluster_ci.csv',filter='main, both repeats; 90% nominal; native and adaptive budget',fields='coverage_retained|macro_coverage_survivors|mean_width|sample_interval_score|source_macro_interval_score|ci_low|ci_high',calculation='Join stored estimates and confidence bounds only; pooled score bounds unavailable',producer='phase2/analyze.py; phase3/supplement.py'),dict(output='tables/Table3_selection_service.csv',source='phase3/results/joint_retention_risk.csv; random_joint_metrics_100.csv',filter='quota; adaptive_budget; repeat=all; targets 1,.9,.8',fields='all reported risk/retention/service fields',calculation='Frozen values; random baseline 100-permutation means and descriptive SD, not a bootstrap CI',producer='phase3/supplement.py')])
    # Electronic SI: full files, not selected favourable results.
    archive=[(P2,'results',x) for x in ['interval_metrics.csv','source_coverage.csv','source_associations.csv','source_diagnostics.csv','residual_decomposition.csv','sensitivity_subsets.csv','selective_metrics.csv','selection_thresholds.csv','random_baseline_100.csv','cluster_bootstrap_ci.csv','paired_changes.csv','split_checks.csv','split_ledger.csv','verified_recipe_edges.csv','label_summary.csv','key_issue_ledger.csv','calibration_quantiles.csv','predictions.csv','calibration_predictions.csv','scale_training_oof.csv']]
    archive +=[(P3,'results',x) for x in ['source_verification_summary.csv','source_field_evidence.csv','source_access_log.csv','independent_candidates.csv','bounded_search_log.csv','novelty_matrix.csv','source_retention_ledger.csv','disappeared_sources.csv','joint_retention_risk.csv','random_joint_metrics_100.csv','paired_cluster_changes.csv','cluster_ci.csv','focus_residual_diagnostics.csv']]
    archive +=[(P2,'data',x) for x in ['new_references.csv','new_label_source_ledger.csv','new_frozen.csv','old_label_ledger.csv']]
    idx=[]
    for stage,sub,name in archive:
        src=stage/sub/name;dest=SI/'electronic'/stage.name/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);assert sha(src)==sha(dest)
        idx.append(dict(file=dest.relative_to(ROOT).as_posix(),original=src.relative_to(PROJECT).as_posix(),rows=len(pd.read_csv(src)),sha256=sha(dest)))
    save(idx,SI/'electronic_file_index.csv')
    # Master source ledger retains all 115 original denominators, including unserved sources.
    base=ss[ss.interval=='adaptive_budget'][['source_id','n','accepted','covered','conditional_coverage']].rename(columns={'n':'original_events','conditional_coverage':'unselected_adaptive_budget_coverage'})
    ledger=source.merge(base,on='source_id',validate='one_to_one')
    save(ledger,SI/'S1_all_115_sources.csv')
    save(TRACE,OUT/'result_source_mapping.csv')
    print('Source data and 3 main tables extracted; electronic SI files',len(idx))
if __name__=='__main__':main()
