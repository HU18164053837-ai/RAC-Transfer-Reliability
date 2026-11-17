from pathlib import Path
import sys
sys.dont_write_bytecode=True
import csv,hashlib,json,re,unicodedata,zipfile,difflib
import pandas as pd
import numpy as np
import openpyxl
ROOT=Path(__file__).resolve().parent; OLD=ROOT/'_historical_project_not_distributed'
RAW=ROOT/'data/raw'; DER=ROOT/'data/derived'; OUT=ROOT/'results'
LEG=RAW/'legacy'
for p in (RAW,DER,OUT,ROOT/'reports'):p.mkdir(parents=True,exist_ok=True)
def save(d,name):d.to_csv(DER/name,index=False,encoding='utf-8-sig')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def protected():
    files=[OLD/'PROJECT_STATUS.md']
    for folder in ['data','src','manuscript','results','reports','deliverables','submission_template_final']:
        for base,ds,fs in __import__('os').walk(OLD/folder):
            for f in fs:files.append(Path(base)/f)
    return sorted(set(files))
def manifest():
    return pd.DataFrame([dict(path=str(p.relative_to(OLD)),bytes=p.stat().st_size,sha256=sha(p)) for p in protected()])
def doi(s):
    m=re.search(r'10\.\d{4,9}/[^\s<>]+',str(s),re.I)
    return m.group(0).lower().rstrip('.,;') if m else ''
def normalize(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKC',s).lower()).strip()
def main():
    before=ROOT/'results/old_protected_before.csv'
    if not before.exists() and OLD.exists():manifest().to_csv(before,index=False,encoding='utf-8-sig')
    text=(RAW/'README.md').read_text(encoding='utf-8').replace('\\','')
    refs=[]
    for line in text.splitlines():
        m=re.match(r'^\[(\d+)\]\s+(.*)',line)
        if m:
            ref=m.group(2); identifier=doi(ref)
            refs.append(dict(ref_no=int(m.group(1)),citation=ref,doi=identifier,source_id=identifier or 'new:'+normalize(ref)))
    refs=pd.DataFrame(refs); assert len(refs)==119
    save(refs,'new_references.csv'); lookup=refs.set_index('ref_no')
    profiles=[]; merge_log=[]
    for stem,target in [('compressive_strength','CS (MPa)'),('slump','SL (mm)')]:
        p=RAW/(stem+'_database.xlsx'); w=openpyxl.load_workbook(p,data_only=True); s=w.active
        d=pd.DataFrame(list(s.values)[1:],columns=list(next(s.values)))
        for r in s.merged_cells.ranges:
            assert r.min_col==r.max_col==2
            v=s.cell(r.min_row,2).value
            for row in range(r.min_row,r.max_row+1):
                d.loc[row-2,'source_reference']=v
                merge_log.append(dict(database=stem,record_id=d.loc[row-2,'record_id'],excel_row=row,merged_range=str(r),source_reference=v))
        assert d.source_reference.notna().all()
        d['ref_no']=d.source_reference.str.extract(r'(\d+)').astype(int)
        d['source_id']=d.ref_no.map(lookup.source_id)
        assert d.source_id.notna().all() and d.record_id.is_unique
        rename={'ρ-RCA (kg/m3)':'density','CV-RCA (%)':'crushing','W-RCA (%)':'absorption','Cement (kg/m3)':'cement','FA (kg/m3)':'fly_ash','GGBS (kg/m3)':'slag','Water (kg/m3)':'water','Sand (kg/m3)':'sand','CA (kg/m3)':'coarse','RAR (%)':'rar','SP (kg/m3)':'sp',target:'target'}
        d=d.rename(columns=rename); features=list(rename.values())[:-1]
        assert np.isfinite(d[features+['target']].to_numpy(float)).all()
        d['dataset']=stem
        save(d,stem+'.csv')
        prof=dict(dataset=stem,rows=len(d),columns_original=15,reference_numbers=d.ref_no.nunique(),canonical_sources=d.source_id.nunique(),numeric_missing=int(d[features+['target']].isna().sum().sum()),outlier_flagged=int(d.outlier_flag.sum()),zero_target=int((d.target==0).sum()),exact_input_duplicate_excess=int(d.duplicated(features).sum()),exact_input_target_duplicate_excess=int(d.duplicated(features+['target']).sum()))
        profiles.append(prof)
        save(d.groupby(['ref_no','source_id']).agg(rows=('record_id','size'),target_min=('target','min'),target_max=('target','max')).reset_index(),stem+'_sources.csv')
        save(d[features+['target']].describe().T.reset_index(names='variable'),stem+'_profile.csv')
    save(pd.DataFrame(profiles),'database_summary.csv'); save(pd.DataFrame(merge_log),'source_merge_recovery.csv')
    old=pd.read_csv(LEG/'modeling.csv'); allold=pd.read_csv(LEG/'classification_all_980.csv')
    inv=pd.read_csv(LEG/'source_inventory.csv'); corrections=pd.read_csv(LEG/'source_identifier_corrections.csv')
    olds=set(allold.source_id.dropna().map(doi))|set(inv.doi.dropna().map(doi))|set(corrections.verified_identifier.dropna().map(doi))
    matches=refs.copy(); matches['doi_overlap_old_all']=matches.doi.map(lambda x: bool(x) and x in olds)
    matches['doi_overlap_old_model']=matches.doi.isin(set(old.source_id)) & matches.doi.ne('')
    save(matches,'source_overlap.csv')
    # Bounded candidate review: title/surname matching is only a candidate, never established identity.
    candidates=[]
    for r in refs.itertuples():
        first=normalize(r.citation.split('.')[0]); surname=normalize(r.citation.split(',')[0]).split()[-1]
        years=re.findall(r'\b(?:19|20)\d{2}\b',r.citation)
        for o in inv.itertuples():
            if surname and re.search(r'\b'+re.escape(surname)+r'\b',normalize(str(o.reference))) and any(y in str(o.reference) for y in years):
                candidates.append(dict(new_ref=r.ref_no,new_citation=r.citation,old_reference=o.reference,old_doi=doi(o.doi),status='surname_year_candidate_only'))
    save(pd.DataFrame(candidates,columns=['new_ref','new_citation','old_reference','old_doi','status']),'source_identity_candidates.csv')
    old['sand']=old.natural_fine+old.recycled_fine; old['coarse']=old.natural_coarse+old.recycled_coarse
    old['rar']=100*old.recycled_coarse/old.coarse; old['target']=old.cs_mpa;old['dataset']='old'
    old['core_eligible']=(old[['silica_fume','metakaolin','recycled_fine']]==0).all(axis=1)
    save(old,'old_modeling_copy.csv')
    # Raw-workbook overlap includes all 980 candidates, not only cleaned 722.
    x=pd.read_excel(LEG/'RACdatadriven.xlsx',sheet_name='RACdata',header=None)
    raw=x.iloc[3:,:19].copy();raw.columns=list(x.iloc[0,:3])+list(x.iloc[1,3:19])
    save(raw,'old_raw_980_copy.csv')
    core=['cement','fly_ash','slag','water','sand','coarse']
    new=pd.read_csv(DER/'compressive_strength.csv')
    # Exact and near collisions use only inputs. Near: every dose within 1 kg/m3; RAR within 1 percentage point when used.
    def pairs(a,b,cols,tol):
        aa=a[cols].to_numpy(float);bb=b[cols].to_numpy(float)
        records=[]
        for i in range(len(aa)):
            dist=np.abs(bb-aa[i]); hit=np.flatnonzero((dist<=np.array(tol)+1e-8).all(axis=1))
            for j in hit: records.append(dict(old_id=a.iloc[i].record_id,new_id=b.iloc[j].record_id,max_abs_difference=float(dist[j].max()),old_source=a.iloc[i].source_id,new_source=b.iloc[j].source_id,exact=bool((dist[j]<1e-8).all())))
        return pd.DataFrame(records,columns=['old_id','new_id','max_abs_difference','old_source','new_source','exact'])
    save(pairs(old,new,core,[1]*6),'cross_core_recipe_collisions.csv')
    save(pairs(old,new,core+['rar'],[1]*7),'cross_core_rar_recipe_collisions.csv')
    # Original candidate doses: explicit legacy structural-zero assumptions; not admission for modeling.
    rr=pd.DataFrame({'record_id':pd.to_numeric(raw['No.']),'source_id':raw['doi'].map(doi)})
    for dest,col in [('cement','OPC'),('fly_ash','FA'),('slag','GGBS'),('water','Water')]:rr[dest]=pd.to_numeric(raw[col],errors='coerce')
    rr[['fly_ash','slag']]=rr[['fly_ash','slag']].fillna(0)
    rr['sand']=raw[['NFA','RFA']].apply(pd.to_numeric,errors='coerce').sum(axis=1,min_count=1)
    rr['coarse']=raw[['NCA','RCA']].apply(pd.to_numeric,errors='coerce').sum(axis=1,min_count=1)
    save(pairs(rr,new,core,[1]*6),'cross_raw980_core_recipe_collisions.csv')
    dictionary=[]
    for name in core:
        dictionary.append(dict(variable=name,unit='kg/m3',compatibility='conditional',note={'cement':'水泥产品并非保证纯OPC','fly_ash':'新旧均为单独报告剂量','slag':'新旧均为单独报告剂量','water':'报告拌合水，有效/总水及预湿口径可能不同','sand':'旧NFA+RFA；迁移主试验限制旧RFA=0；新库仅报告砂','coarse':'旧NCA+RCA；新CA为粗骨料总量'}[name]))
    for name,note in [('rar','旧为质量剂量比；新替代率质量/体积口径未细化，不用于迁移主试验'),('density/crushing/absorption/sp','新库有，旧冻结输入没有；不可伪造补齐'),('silica_fume/metakaolin/recycled_fine','旧有，新库无；迁移主试验限制旧此三者=0，不假设所有新记录无隐藏掺料'),('target','均28天；新为150mm立方体等效CS，旧报告值试件不统一；仅操作性迁移，不作物理等价结论')]:dictionary.append(dict(variable=name,unit='varies',compatibility='limited',note=note))
    save(pd.DataFrame(dictionary),'variable_compatibility.csv')
    inputs=sorted(p for p in RAW.rglob('*') if p.is_file())
    pd.DataFrame([dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in inputs]).to_csv(OUT/'input_sha256.csv',index=False,encoding='utf-8-sig')
    print(json.dumps({'summary':profiles,'source_doi_matches':int(matches.doi_overlap_old_all.sum()),'candidate_matches':candidates,'old_core_eligible':int(old.core_eligible.sum()),'cross_core_collisions':len(pd.read_csv(DER/'cross_core_recipe_collisions.csv'))},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
