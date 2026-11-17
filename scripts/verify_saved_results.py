"""Independent checks of frozen predictions. Never call producer mains or estimators."""
from pathlib import Path
import os,sys,csv,json,subprocess,time,importlib.util
sys.dont_write_bytecode=True
import numpy as np
import pandas as pd
import openpyxl
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reproduced';OUT.mkdir(exist_ok=True)
CHECKS=[]
def ck(name,condition,details):
    CHECKS.append(dict(check=name,status='PASS' if bool(condition) else 'FAIL',details=details));assert condition,(name,details)
def main():
    started=time.perf_counter()
    # Isolated process imports avoid the stages' original identically named common modules colliding.
    imported=[]
    for stage,module in [('', 'prepare'),('', 'experiment'),('phase2','prepare_phase2'),('phase2','run_experiments'),('phase2','analyze'),('phase3','prepare'),('phase3','supplement')]:
        script="import sys,importlib;sys.dont_write_bytecode=True;sys.path.insert(0,"+repr(str(ROOT/stage))+");importlib.import_module("+repr(module)+");print('imported')"
        r=subprocess.run([sys.executable,'-c',script],capture_output=True,text=True,cwd=ROOT)
        ck('Import '+stage+'/'+module,r.returncode==0,r.stderr[-500:] if r.returncode else 'No producer main executed');imported.append(stage+'/'+module)
    frozen=pd.read_csv(ROOT/'phase2/data/new_frozen.csv');p=pd.read_csv(ROOT/'phase2/results/predictions.csv');d=p[p.scenario=='main'].reset_index(drop=True)
    ck('Main cohort',len(frozen)==1736 and frozen.source_id.nunique()==115 and frozen.group.nunique()==99,'1736 rows / 115 publications / 99 components')
    ck('Two dependent prediction repeats',len(d)==3472 and d.groupby(['repeat','record_key']).size().eq(1).all() and d.groupby('repeat').size().eq(1736).all(),'No new independent observations inferred')
    for col in ['target','source_id','group']:
        mapped=frozen.set_index('record_id')[col];expected=d.record_id.map(mapped)
        ck('Prediction alignment '+col,np.allclose(expected,d[col],atol=1e-12) if col=='target' else expected.equals(d[col]),'Saved records join the frozen modelling matrix')
    book=openpyxl.load_workbook(ROOT/'data/raw/compressive_strength_database.xlsx',data_only=True);sheet=book.active
    raw=pd.DataFrame(list(sheet.values)[1:],columns=list(next(sheet.values)))
    for rng in sheet.merged_cells.ranges:
        assert rng.min_col==rng.max_col==2
        for row in range(rng.min_row,rng.max_row+1):raw.loc[row-2,'source_reference']=sheet.cell(rng.min_row,2).value
    rename={'ρ-RCA (kg/m3)':'density','CV-RCA (%)':'crushing','W-RCA (%)':'absorption','Cement (kg/m3)':'cement','FA (kg/m3)':'fly_ash','GGBS (kg/m3)':'slag','Water (kg/m3)':'water','Sand (kg/m3)':'sand','CA (kg/m3)':'coarse','RAR (%)':'rar','SP (kg/m3)':'sp','CS (MPa)':'target'}
    raw=raw.rename(columns=rename).set_index('record_id').loc[frozen.record_id]
    variables=list(rename.values())
    ck('Raw workbook numeric values',np.allclose(raw[variables].to_numpy(float),frozen[variables].to_numpy(float),atol=1e-12),'No label/geometry/unit conversion introduced')
    ck('Raw merged references',raw.source_reference.to_numpy().tolist()==frozen.source_reference.tolist(),'Only actual B-column merged source references restored')
    ck('Source-contained components',frozen.groupby('source_id').group.nunique().eq(1).all(),'Publication identity stays within one component')
    edges=pd.read_csv(ROOT/'phase2/results/verified_recipe_edges.csv');group=frozen.set_index('record_id').group
    ck('Known recipe edge isolation',len(edges)==556 and (edges.record_a.map(group)==edges.record_b.map(group)).all(),'All 556 saved target-free recipe edges contained')
    led=pd.read_csv(ROOT/'phase2/results/split_ledger.csv');runs=0
    for run,z in led.groupby('run'):
        parts={k:q for k,q in z.groupby('split')};assert set(parts)=={'fit','calibration','test'}
        for a,b in [('fit','calibration'),('fit','test'),('calibration','test')]:
            for col in ['group','source_id','record_key']:assert set(parts[a][col]).isdisjoint(parts[b][col]),(run,a,b,col)
        test=parts['test'];pred=p[p.run==run];assert set(test.record_key)==set(pred.record_key),run;runs+=1
    ck('All saved split roles isolated',runs==17,'17 runs, including metadata sensitivity and historical stress tests')
    oof=pd.read_csv(ROOT/'phase2/results/scale_training_oof.csv')
    ck('Scale OOF isolation',all(r.group not in set(r.fit_groups.split('|')) for r in oof.itertuples()),str(len(oof))+' saved OOF targets remain outside auxiliary fitting groups')
    sys.path.insert(0,str(ROOT/'phase3'));sys.modules.pop('common',None)
    import supplement as metrics
    thr=pd.read_csv(ROOT/'phase2/results/selection_thresholds.csv')
    trade=pd.read_csv(ROOT/'phase3/results/interval_score_tradeoff.csv');comparisons=[]
    radii=dict(metrics.INTERVALS,group_max='radius_group_max_90')
    for row in trade.itertuples():
        calc=metrics.summary(metrics.by_source(d,d[radii[row.interval]],np.ones(len(d),bool)))
        for field,value in calc.items():
            if field not in trade.columns:continue
            expected=getattr(row,field);assert np.isclose(value,expected,atol=1e-9,rtol=1e-9,equal_nan=True),(row.interval,field,value,expected)
            comparisons.append(dict(analysis='native_intervals',interval=row.interval,field=field,recomputed=value,frozen=expected))
    op=pd.read_csv(ROOT/'phase3/results/joint_retention_risk.csv',dtype={'repeat':str})
    for row in op.itertuples():
        z=d if row.repeat=='all' else d[d.repeat==int(row.repeat)].reset_index(drop=True)
        mask=metrics.mask_for(z,row.rule,row.target_retention,row.mode,thr)
        calc=metrics.summary(metrics.by_source(z,z[radii[row.interval]],mask))
        for field,value in calc.items():
            expected=getattr(row,field);assert np.isclose(value,expected,atol=1e-9,rtol=1e-9,equal_nan=True),(row.mode,row.rule,row.target_retention,row.interval,row.repeat,field,value,expected)
            comparisons.append(dict(analysis=f'{row.mode}_{row.rule}_{row.target_retention}_{row.repeat}',interval=row.interval,field=field,recomputed=value,frozen=expected))
    ck('Main interval and all selection metrics',len(op)==600,str(len(comparisons))+' stored values recalculated within 1e-9; all 600 operating points checked')
    # Existing score, coverage and confidence intervals are not statistically resampled.
    audit=pd.read_csv(ROOT/'reproducibility/frozen_audits/claim_value_audit.csv')
    ck('All paper result provenance retained',len(audit)==223 and all((ROOT/v).is_file() for v in audit.source.unique()),'223 audited values retain source CSVs, fields and row filters')
    for required in ['phase2/results/cluster_bootstrap_ci.csv','phase3/results/cluster_ci.csv','phase3/results/paired_cluster_changes.csv']:
        assert (ROOT/required).exists()
    ck('Frozen uncertainty outputs retained',True,'Input bytes checked by verify_integrity.py; no bootstrap rerun')
    pd.DataFrame(CHECKS).to_csv(OUT/'saved_result_checks.csv',index=False)
    pd.DataFrame(comparisons).to_csv(OUT/'metric_recalculation.csv',index=False,float_format='%.17g')
    report=dict(status='PASS',checks=len(CHECKS),recalculated_values=len(comparisons),operating_points=len(op),imported=imported,wall_seconds=time.perf_counter()-started,additional_fits=0,resampling=0,python=sys.version.split()[0],numpy=np.__version__,pandas=pd.__version__)
    (OUT/'saved_result_summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
