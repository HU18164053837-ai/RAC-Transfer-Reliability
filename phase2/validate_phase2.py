from common import *
import argparse,math
from prepare_phase2 import snapshot_old,snapshot_p1
CORE_FILES=['predictions.csv','calibration_predictions.csv','calibration_quantiles.csv','selection_thresholds.csv','split_ledger.csv','scale_training_oof.csv','split_checks.csv']
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');parser.add_argument('--protect',action='store_true');args=parser.parse_args()
    reference=OUT/'reproduction_reference.json';hashes={n:sha(OUT/n) for n in CORE_FILES}
    if args.record:
        assert not reference.exists(),'Never overwrite the original reproduction reference'
        reference.write_text(json.dumps(hashes,indent=2),encoding='utf-8');print('Recorded model-output SHA256 reference');return
    assert hashes==json.loads(reference.read_text()),'Model rerun differs from first run'
    lock=json.loads((OUT/'plan_lock_sha256.json').read_text());assert sha(ROOT/lock['path'])==lock['sha256']
    d=pd.read_csv(data_file('new_frozen.csv'));edges=pd.read_csv(OUT/'verified_recipe_edges.csv');parent=list(range(len(d)));ids={r:i for i,r in enumerate(d.record_id)}
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[max(a,b)]=min(a,b)
    for _,ix in d.groupby('source_id').indices.items():
        for j in ix[1:]:union(int(ix[0]),int(j))
    for r in edges.itertuples():union(ids[r.record_a],ids[r.record_b])
    roots=[find(i) for i in range(len(d))];assert len(set(roots))==99
    check=d[['group','source_id']].assign(recomputed=roots)
    assert check.groupby('group').recomputed.nunique().max()==1 and check.groupby('recomputed').group.nunique().max()==1
    assert d.groupby('source_id').group.nunique().max()==1
    led=pd.read_csv(OUT/'split_ledger.csv');audits=[]
    for run,g in led.groupby('run'):
        parts={k:z for k,z in g.groupby('split')}
        for a,b in [('fit','calibration'),('fit','test'),('calibration','test')]:
            for field in ['record_key','source_id','group']:
                overlap=len(set(parts[a][field])&set(parts[b][field]));assert overlap==0
                audits.append(dict(run=run,part_a=a,part_b=b,field=field,overlap=overlap))
    save(audits,'leakage_validation.csv')
    oof=pd.read_csv(OUT/'scale_training_oof.csv')
    assert not oof.duplicated(['run','record_key']).any()
    for r in oof.itertuples():assert r.group not in r.fit_groups.split('|')
    for run,g in oof.groupby('run'):
        fit=led[(led.run==run)&(led.split=='fit')]
        assert set(g.record_key)==set(fit.record_key)
        possible=set(fit.group)
        assert all(set(z.split('|')).issubset(possible) for z in g.fit_groups.unique())
    p=pd.read_csv(OUT/'predictions.csv');cal=pd.read_csv(OUT/'calibration_predictions.csv')
    primary=p[p.scenario=='main'];counts=primary.groupby(['repeat','record_key']).size();assert counts.eq(1).all() and len(counts)==3472
    for repeat,g in primary.groupby('repeat'):assert g.record_key.nunique()==1736 and g.source_id.nunique()==115 and g.group.nunique()==99
    assert np.allclose(p.radius_source_balanced_90_budget,p.radius_pooled_90,atol=1e-10,rtol=1e-10)
    for run,g in cal.groupby('run'):
        for method in METHODS:assert np.isclose(g[f'radius_{method}_90_budget'].mean(),g.radius_pooled_90.mean(),rtol=1e-12)
    for method in METHODS:
        assert np.all(p[f'radius_{method}_95']>=p[f'radius_{method}_90']-1e-10)
        assert np.all(p[f'radius_{method}_90']>=p[f'radius_{method}_80']-1e-10)
    from analyze import select_mask
    threshold=pd.read_csv(OUT/'selection_thresholds.csv');test=primary.reset_index(drop=True)
    shuffled=test.copy();shuffled['target']=test.target.sample(frac=1,random_state=19).to_numpy()
    for mode in ['quota','calibration_threshold']:
        for selector in ['random','tree_sd','distance','sigma','joint']:
            for r in RETENTIONS:
                a=select_mask(test,selector,r,mode,threshold);b=select_mask(shuffled,selector,r,mode,threshold);assert np.array_equal(a,b)
                if mode=='quota':
                    for _,ix in test.groupby('run').indices.items():assert a[ix].sum()==math.ceil(len(ix)*r)
    im=pd.read_csv(OUT/'interval_metrics.csv');v=im[(im.scenario=='main')&(im['repeat'].astype(str)=='all')&(im.method=='pooled')&(im.budget=='native')&(im.nominal==.9)].iloc[0]
    assert np.isclose(v.coverage,(np.abs(primary.target-primary.prediction)<=primary.radius_pooled_90+1e-12).mean())
    result=dict(byte_identical_full_model_rerun=True,model_output_files=CORE_FILES,plan_unchanged=True,source_group_reconstruction=True,source_groups=99,publications=115,split_source_recipe_overlap=0,training_only_group_OOF_pass=True,test_label_permutation_selection_invariance=True,source_balanced_equal_budget_equals_pooled=True,scale_budget_calibration_only=True,phase1_seen_data_disclosed=True,external_confirmation=False)
    if args.protect:
        for prefix,fn in [('old',snapshot_old),('phase1',snapshot_p1)]:
            before=pd.read_csv(OUT/(prefix+'_before.csv'));after=fn();after.to_csv(OUT/(prefix+'_after.csv'),index=False,encoding='utf-8-sig')
            z=before.merge(after,on='path',how='outer',suffixes=('_before','_after'),indicator=True)
            bad=z[(z['_merge']!='both')|(z.sha256_before!=z.sha256_after)|(z.bytes_before!=z.bytes_after)]
            save(bad,prefix+'_changes.csv');assert bad.empty,prefix+' protected products changed'
            result[prefix+'_protected_files']=len(before);result[prefix+'_changed_files']=len(bad)
        (OUT/'protection_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
