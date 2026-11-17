from common import *
import argparse,ast
FILES=['joint_retention_risk.csv','source_retention_ledger.csv','disappeared_sources.csv','interval_score_tradeoff.csv','random_joint_metrics_100.csv','paired_cluster_changes.csv','focus_residual_diagnostics.csv']
def main():
    p=__import__('argparse').ArgumentParser();p.add_argument('--record',action='store_true');p.add_argument('--protect',action='store_true');a=p.parse_args();reference=OUT/'reproduction_reference.json'
    current={name:sha(OUT/name) for name in FILES}
    if a.record:
        assert not reference.exists();reference.write_text(json.dumps(current,indent=2),encoding='utf-8');print('Recorded first supplement hashes');return
    assert current==json.loads(reference.read_text()),'Supplement reproduction mismatch'
    lock=json.loads((OUT/'plan_sha256.json').read_text());assert sha(ROOT/lock['file'])==lock['sha256']
    for name in ['predictions.csv','selection_thresholds.csv','random_baseline_100.csv']:assert sha(DATA/name)==sha(P2/'results'/name)
    data=pd.read_csv(data_file('predictions.csv'));d=data[data.scenario=='main'].reset_index(drop=True);thr=pd.read_csv(data_file('selection_thresholds.csv'))
    assert len(d)==3472 and d.record_key.nunique()==1736 and d.source_id.nunique()==115 and d.group.nunique()==99
    from supplement import mask_for,RULES,RATES
    unl=d[['run','record_key','random','tree_sd','distance','sigma','joint']].copy();shuffled=d.copy();shuffled.target=shuffled.target.sample(frac=1,random_state=63).to_numpy()
    for mode in ['quota','calibration_threshold']:
        for rule in RULES:
            last=np.ones(len(d),bool)
            for rate in RATES:
                x=mask_for(unl,rule,rate,mode,thr);y=mask_for(shuffled,rule,rate,mode,thr)
                assert np.array_equal(x,y) and np.all(~x|last);last=x
    led=pd.read_csv(OUT/'source_retention_ledger.csv');assert np.allclose(led.success_yield+led.unserved_share+led.accepted_uncovered_share,1)
    result=pd.read_csv(OUT/'joint_retention_risk.csv');full=result[(result['repeat'].astype(str)=='all')&(result.target_retention==1)]
    assert np.allclose(full.macro_source_success_yield,full.macro_coverage_survivors)
    assert np.allclose(full.macro_coverage_zero_absent,full.macro_coverage_survivors)
    baseline=pd.read_csv(P2/'results/selective_metrics.csv')
    here=result[(result['repeat'].astype(str)=='all')&(result.interval=='adaptive_budget')]
    prior=baseline[(baseline.scenario=='main')&(baseline.method=='adaptive')&(baseline.budget=='matched')]
    z=here.merge(prior,left_on=['mode','rule','target_retention'],right_on=['mode','selector','target_retention'],suffixes=('_p3','_p2'),validate='one_to_one')
    assert np.allclose(z.rmse_p3,z.rmse_p2) and np.allclose(z.macro_coverage_survivors,z.source_macro_coverage) and np.allclose(z.source_retention_p3,z.source_retention_p2)
    e=pd.read_csv(OUT/'source_field_evidence.csv');assert set(e.status)<=set(['已证实','存在冲突','无法核实'])
    summary=json.loads((OUT/'evidence_summary.json').read_text());assert summary['independent_candidates']==6 and summary['rows_admitted']==0 and summary['search_closed']
    # Source scores must reproduce the Phase 2 interval-score definition.
    scores=pd.read_csv(OUT/'interval_score_tradeoff.csv');old=pd.read_csv(data_file('phase2_interval_metrics.csv'))
    for name in ['pooled','source_balanced','adaptive','group_max']:
        ref=old[(old.scenario=='main')&(old['repeat'].astype(str)=='all')&(old.method==name)&(old.nominal==.9)&(old.budget=='native')].iloc[0]
        obs=scores[scores.interval==name].iloc[0];assert np.isclose(ref.interval_score,obs.sample_interval_score)
    fits=0
    for f in ROOT.glob('*.py'):
        tree=ast.parse(f.read_text(encoding='utf-8'))
        fits+=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='fit' for n in ast.walk(tree))
    assert fits==0
    out=dict(full_supplement_byte_reproduction=True,predictions_exactly_reused=True,additional_model_fits=0,phase2_metrics_reproduced=True,selection_label_invariance=True,joint_partition_identity=True,source_denominator=115,cluster_count=99,rows=1736,prediction_events=3472,query_budget_respected=True,external_confirmation=False,search_closed=True)
    if a.protect:
        before=pd.read_csv(OUT/'protected_before.csv');after=snapshot();after.to_csv(OUT/'protected_after.csv',index=False,encoding='utf-8-sig')
        merged=before.merge(after,on=['scope','path'],how='outer',suffixes=('_before','_after'),indicator=True)
        bad=merged[(merged['_merge']!='both')|(merged.bytes_before!=merged.bytes_after)|(merged.sha256_before!=merged.sha256_after)]
        save(bad,'protected_changes.csv');assert bad.empty,'Protected prior products changed'
        out['old_files']=int((before.scope=='old_RAC956').sum());out['prior_stage_files']=int((before.scope=='prior_stages').sum());out['changed_files']=0
        (OUT/'protection_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    elif (OUT/'protection_validation.json').exists():out.update({k:v for k,v in json.loads((OUT/'protection_validation.json').read_text()).items() if k in ['old_files','prior_stage_files','changed_files']})
    (OUT/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
