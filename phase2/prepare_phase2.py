from common import *
import shutil,re,os
def snapshot_old():
    paths=[OLD/'PROJECT_STATUS.md']
    for sub in ['data','src','manuscript','results','reports','deliverables','submission_template_final']:
        for base,ds,fs in os.walk(OLD/sub):
            for f in fs:paths.append(Path(base)/f)
    return pd.DataFrame([dict(path=str(p.relative_to(OLD)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(paths))])
def snapshot_p1():
    files=[]
    for base,ds,fs in os.walk(P1):
        ds[:]=[d for d in ds if d not in ['phase2','__pycache__','.mplconfig']]
        for f in fs:files.append(Path(base)/f)
    return pd.DataFrame([dict(path=str(p.relative_to(P1)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)])
def main():
    for name,fn in [('old_before.csv',snapshot_old),('phase1_before.csv',snapshot_p1)]:
        if not (OUT/name).exists():fn().to_csv(OUT/name,index=False,encoding='utf-8-sig')
    copies=[(P1/'data/derived/compressive_strength.csv',data_file('new_input.csv')),(P1/'data/derived/new_references.csv',data_file('new_references.csv')),(P1/'results/new_groups.csv',data_file('phase1_groups.csv')),(P1/'data/derived/old_modeling_copy.csv',data_file('old_input.csv')),(P1/'results/split_ledger.csv',data_file('phase1_split_ledger.csv')),(P1/'data/raw/README.md',data_file('database_README.md')),(OLD/'data/frozen/cs_v1/provenance/row_verification_ledger.csv',data_file('old_row_evidence.csv')),(OLD/'results/audit/source_age_status.csv',data_file('old_source_age_evidence.csv')),(OLD/'reports/data_audit_preliminary.md',data_file('legacy_count_evidence.md')),(OLD/'results/audit/Kou_thesis_specimen_curing_context.csv',data_file('old_specimen_context.csv'))]
    for a,b in copies:
        if not b.exists():shutil.copyfile(a,b)
        assert sha(a)==sha(b)
    for a,b in [(P1/'results/transfer_groups.csv',data_file('transfer_groups.csv')),(P1/'requirements.txt',ROOT/'requirements.txt')]:
        if not b.exists():shutil.copyfile(a,b)
        assert sha(a)==sha(b)
    d=pd.read_csv(data_file('new_input.csv'));g=pd.read_csv(data_file('phase1_groups.csv'));d=d.merge(g[['record_id','group']],on='record_id',validate='one_to_one')
    assert len(d)==1736 and d.source_id.nunique()==115 and d.group.nunique()==99
    assert d.groupby('source_id').group.nunique().max()==1
    x=d[RECIPE].to_numpy(float);tol=np.array([1]*7+[.1]);edges=[]
    for i in range(len(d)):
        hits=np.flatnonzero((np.abs(x[i+1:]-x[i])<=tol+1e-8).all(axis=1))+i+1
        for j in hits:
            assert d.iloc[i].group==d.iloc[j].group
            edges.append(dict(record_a=d.iloc[i].record_id,record_b=d.iloc[j].record_id,group=d.iloc[i].group,source_a=d.iloc[i].source_id,source_b=d.iloc[j].source_id,exact=bool((np.abs(x[i]-x[j])<1e-8).all())))
    save(edges,'verified_recipe_edges.csv')
    risks=set(d.loc[d.ref_no.isin([8,9,52,77]),'group']);d['metadata_risk_group']=d.group.isin(risks)
    d['unique_xy_first']=~d.duplicated(FULL+['target']);d.to_csv(data_file('new_frozen.csv'),index=False,encoding='utf-8-sig')
    source=d.groupby(['source_id','group']).agg(n=('record_id','size'),refs=('ref_no',lambda z:','.join(map(str,sorted(set(z))))),metadata_risk_group=('metadata_risk_group','first')).reset_index()
    source['age_days']=28;source['age_evidence']='curator_README_only';source['unit']='MPa';source['label_geometry']='150mm_cube_equivalent_curator_claim';source['original_geometry']='unknown';source['test_standard']='unknown';source['conversion_factor']='unknown';source['independent_experiment_status']='not_fully_established'
    source.to_csv(data_file('new_label_source_ledger.csv'),index=False,encoding='utf-8-sig')
    old=pd.read_csv(data_file('old_input.csv'));ev=pd.read_csv(data_file('old_row_evidence.csv'))
    old=old.merge(ev[['No.','age_status','candidate_age_days','evidence_url','note']],left_on='record_id',right_on='No.',how='left',validate='one_to_one')
    assert (old.age_days==28).all() and (old.candidate_age_days==28).all()
    old['unit']='MPa';old['original_geometry']='unknown';old['test_standard']='unknown';old['geometry_evidence']='unknown'
    mapping={'10.1061/(asce)mt.1943-5533.0001748':('150mm_cube','existing_primary_source_audit; Elchalakani2017 methods'), '10.1016/j.conbuildmat.2012.06.060':('100mm_cube','existing_primary_source_audit; Kou2012 methods')}
    for s,(geo,basis) in mapping.items():
        mask=old.source_id.str.lower()==s;old.loc[mask,'original_geometry']=geo;old.loc[mask,'geometry_evidence']=basis
    old[['record_id','source_id','age_days','age_status','candidate_age_days','unit','original_geometry','test_standard','geometry_evidence','evidence_url','note']].to_csv(data_file('old_label_ledger.csv'),index=False,encoding='utf-8-sig')
    save([dict(dataset='new',rows=len(d),sources=d.source_id.nunique(),groups=d.group.nunique(),known_age_rows=1736,independently_original_geometry_rows=0,test_standard_known_rows=0,risk_rows=int(d.metadata_risk_group.sum()),risk_groups=len(risks)),dict(dataset='old_frozen',rows=len(old),sources=old.source_id.nunique(),groups=old.validation_group.nunique(),known_age_rows=int(old.candidate_age_days.eq(28).sum()),independently_original_geometry_rows=int(old.original_geometry.ne('unknown').sum()),test_standard_known_rows=0,risk_rows=0,risk_groups=0)],'label_summary.csv')
    facts=[dict(issue='RAC956_vs_980',finding='Original workbook IDs1-980; page Dataset4 says956; IDs957-980 Limbachiya2012; no evidence they are version2 additions',evidence='legacy_count_evidence.md + https://data.mendeley.com/datasets/wc898ff5pj/2',status='count_resolved_description_discrepancy_not_author_erratum'),dict(issue='refs2_75',finding='sameDOI; samegroup asserted',evidence='new_references.csv',status='resolved'),dict(issue='ref52',finding='Publisher identifies rubber-aggregate concrete confined by steel tubes; row-level mapping to RAC remains unresolved',evidence='https://sylx.ustc.edu.cn/sylx/article/issue/2021_36_6',status='material_or_source_mismatch_risk_not_adjudicated'),dict(issue='ref109',finding='Publisher title and authors corroborated; original size/standard/fulltext not established',evidence='https://www.gncl.cn/CN/Y2013/V44/I17/31',status='metadata_only'),dict(issue='ref101',finding='No primary fulltext recovered in bounded search',evidence='database_README.md reference101',status='unknown'),dict(issue='refs8_9',finding='prediction-model titles indicate possible recompiled data; direct experimental provenance unresolved',evidence='new_references.csv',status='sensitivity_only'),dict(issue='ref77',finding='title includes silica fume absent from modeling columns; extracted subgroup unidentified',evidence='new_references.csv',status='sensitivity_only')]
    save(facts,'key_issue_ledger.csv')
    save([dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(DATA.glob('*')) if p.is_file()],'input_sha256.csv')
    lock=ROOT/'ANALYSIS_PLAN_LOCKED.md';(OUT/'plan_lock_sha256.json').write_text(json.dumps(dict(path=lock.name,sha256=sha(lock)),indent=2),encoding='utf-8')
    print('Prepared: rows',len(d),'groups',d.group.nunique(),'risk groups',len(risks),'risk rows',d.metadata_risk_group.sum(),'near edges',len(edges),flush=True)
if __name__=='__main__':main()
