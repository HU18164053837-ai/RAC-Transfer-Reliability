"""Bounded reproducible feasibility experiments; no hyperparameter search."""
from pathlib import Path
import sys,os,json,platform,hashlib,math
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
# Read-only reuse for missing scientific capabilities. Never install into the old project.
if os.environ.get('RAC_ML_DEPS'):sys.path.insert(0,os.environ['RAC_ML_DEPS'])
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GroupShuffleSplit,train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from scipy.stats import spearmanr
DER=ROOT/'data/derived';OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
SEEDS=[20261107,20261108,20261109]
FULL=['density','crushing','absorption','cement','fly_ash','slag','water','sand','coarse','rar','sp']
CORE=['cement','fly_ash','slag','water','sand','coarse']
RECIPE=CORE+['rar','sp']
CONFIG=dict(model='ExtraTreesRegressor',n_estimators=200,min_samples_leaf=3,max_features=1.0,n_jobs=1,seeds=SEEDS,alpha=.1,threshold_mpa=30,near_tolerance_kg=1,near_tolerance_rar_percentage_point=1,near_tolerance_sp_kg=.1)
def save(d,name):pd.DataFrame(d).to_csv(OUT/name,index=False,encoding='utf-8-sig')
class Union:
    def __init__(self,n):self.p=list(range(n))
    def find(self,x):
        while self.p[x]!=x:self.p[x]=self.p[self.p[x]];x=self.p[x]
        return x
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b:self.p[max(a,b)]=min(a,b)
def groups(d,cols,tol,label):
    d=d.reset_index(drop=True).copy();u=Union(len(d));edges=[]
    for _,idx in d.groupby('source_id').groups.items():
        idx=list(idx)
        for i in idx[1:]:u.union(idx[0],i)
    x=d[cols].to_numpy(float)
    for i in range(len(x)):
        diff=np.abs(x[i+1:]-x[i]); js=np.flatnonzero((diff<=np.array(tol)+1e-8).all(axis=1))+i+1
        for j in js:
            u.union(i,int(j))
            edges.append(dict(record_a=d.iloc[i].record_id,record_b=d.iloc[j].record_id,source_a=d.iloc[i].source_id,source_b=d.iloc[j].source_id,exact=bool((np.abs(x[i]-x[j])<1e-8).all()),max_abs_diff=float(np.abs(x[i]-x[j]).max())))
    d['group']=[f'{label}_G{u.find(i):04d}' for i in range(len(d))]
    save(edges,label+'_recipe_edges.csv');save(d[['record_id','source_id','group']],label+'_groups.csv')
    return d
def split(d,seed,grouped=True):
    ids=np.arange(len(d))
    if grouped:
        dev,te=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=seed).split(ids,groups=d.group))
        tr0,ca0=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=seed+100).split(dev,groups=d.iloc[dev].group))
        tr,ca=dev[tr0],dev[ca0]
        gs=[set(d.iloc[idx].group) for idx in [tr,ca,te]]
        assert not(gs[0]&gs[1] or gs[0]&gs[2] or gs[1]&gs[2])
        ss=[set(d.iloc[idx].source_id) for idx in [tr,ca,te]]
        assert not(ss[0]&ss[1] or ss[0]&ss[2] or ss[1]&ss[2])
    else:
        dev,te=train_test_split(ids,test_size=.2,random_state=seed)
        tr,ca=train_test_split(dev,test_size=.25,random_state=seed+100)
    return tr,ca,te
def quantile(scores):
    a=np.sort(np.asarray(scores,float));k=math.ceil((len(a)+1)*.9)
    return float(a[k-1]) if k<=len(a) else float('inf')
predictions=[];splits=[];metrics=[];checks=[]
def summarize(p,scenario,seed,method,subset='all'):
    if not len(p):return
    y=p.target.to_numpy();pred=p.pred.to_numpy();q=p['q_'+method].to_numpy()
    err=np.abs(y-pred);cover=err<=q
    z=p[['source_id','group']].copy();z['ae']=err;z['sqe']=(y-pred)**2;z['cover']=cover
    source=z.groupby('source_id').agg(mae=('ae','mean'),mse=('sqe','mean'),coverage=('cover','mean'))
    group=z.groupby('group').cover.all()
    accepted=(pred-q>=30); n=int(accepted.sum())
    metrics.append(dict(scenario=scenario,seed=seed,method=method,subset=subset,n=len(p),sources=p.source_id.nunique(),groups=p.group.nunique(),rmse=float(np.sqrt(mean_squared_error(y,pred))),mae=float(mean_absolute_error(y,pred)),r2=float(r2_score(y,pred)) if len(p)>1 else np.nan,source_macro_mae=source.mae.mean(),source_macro_rmse=np.sqrt(source.mse).mean(),source_macro_coverage=source.coverage.mean(),coverage=float(cover.mean()),width=float((2*q).mean()),complete_group_coverage=float(group.mean()),min_source_coverage=float(source.coverage.min()),median_source_coverage=float(source.coverage.median()),accepted_30mpa=n,false_accepts_30mpa=int((accepted&(y<30)).sum()),false_accept_rate_30mpa=float((y[accepted]<30).mean()) if n else np.nan,rejected_ad_fraction=float((~p.in_domain).mean()),distance_abs_error_spearman=float(spearmanr(p.distance,err).statistic) if len(p)>2 else np.nan))
def run(train,cal,test,cols,scenario,seed,dummy=False):
    assert set(train.record_key).isdisjoint(set(cal.record_key)) and set(train.record_key).isdisjoint(set(test.record_key)) and set(cal.record_key).isdisjoint(set(test.record_key))
    for label,d in [('fit',train),('calibration',cal),('test',test)]:
        for r in d[['record_key','source_id','group']].itertuples(index=False):splits.append(dict(scenario=scenario,seed=seed,split=label,record_key=r.record_key,source_id=r.source_id,group=r.group))
    if dummy:
        cp=np.full(len(cal),train.target.mean());tp=np.full(len(test),train.target.mean())
    else:
        model=ExtraTreesRegressor(n_estimators=200,min_samples_leaf=3,max_features=1.0,n_jobs=1,random_state=seed)
        model.fit(train[cols],train.target);cp=model.predict(cal[cols]);tp=model.predict(test[cols])
    residual=np.abs(cal.target.to_numpy()-cp)
    rowq=quantile(residual)
    scores=pd.DataFrame({'group':cal.group.to_numpy(),'score':residual}).groupby('group').score.max()
    groupq=quantile(scores)
    scaler=RobustScaler().fit(train[cols]);nn=NearestNeighbors(n_neighbors=1).fit(scaler.transform(train[cols]))
    cd=nn.kneighbors(scaler.transform(cal[cols]),return_distance=True)[0][:,0]
    td=nn.kneighbors(scaler.transform(test[cols]),return_distance=True)[0][:,0]
    threshold=float(np.quantile(cd,.9))
    p=test[['record_key','record_id','dataset','source_id','group','target']].copy()
    p['pred']=tp;p['q_row']=rowq;p['q_group']=groupq;p['distance']=td;p['ad_threshold']=threshold;p['in_domain']=td<=threshold
    p['scenario']=scenario;p['seed']=seed
    predictions.append(p)
    for method in ['row','group']:
        summarize(p,scenario,seed,method)
        summarize(p[p.in_domain],scenario,seed,method,'in_domain')
        summarize(p[~p.in_domain],scenario,seed,method,'out_domain')
    checks.append(dict(scenario=scenario,seed=seed,train_rows=len(train),cal_rows=len(cal),test_rows=len(test),train_groups=train.group.nunique(),cal_groups=cal.group.nunique(),test_groups=test.group.nunique(),train_sources=train.source_id.nunique(),cal_sources=cal.source_id.nunique(),test_sources=test.source_id.nunique(),train_test_source_overlap=len(set(train.source_id)&set(test.source_id)),train_cal_source_overlap=len(set(train.source_id)&set(cal.source_id)),train_test_group_overlap=len(set(train.group)&set(test.group)),row_radius=rowq,group_radius=groupq,ad_threshold=threshold,features='|'.join(cols)))
    print(scenario,seed,'n',len(train),len(cal),len(test),'q',round(rowq,3),round(groupq,3),'RMSE',round(np.sqrt(np.mean((tp-test.target)**2)),3),flush=True)
def main():
    new=pd.read_csv(DER/'compressive_strength.csv');old=pd.read_csv(DER/'old_modeling_copy.csv')
    new['record_key']='new:'+new.record_id;old['record_key']='old:'+old.record_id.astype(str)
    old['record_id']=old.record_id.astype(str);new['dataset']='new';old['dataset']='old'
    new=groups(new,RECIPE,[1]*7+[.1],'new')
    old=old[old.core_eligible].copy().reset_index(drop=True)
    combined=groups(pd.concat([old,new],ignore_index=True),CORE,[1]*6,'transfer')
    # Exclude whole connected target groups if they contain any training-domain source/recipe.
    crossgroups=set(combined[combined.dataset=='old'].group)&set(combined[combined.dataset=='new'].group)
    combined['cross_domain_connected']=combined.group.isin(crossgroups)
    save(combined[['record_key','source_id','group','cross_domain_connected']],'transfer_exclusion_ledger.csv')
    oldt=combined[combined.dataset=='old'].reset_index(drop=True);newt=combined[combined.dataset=='new'].reset_index(drop=True)
    for seed in SEEDS:
        for grouped,name in [(False,'new_random_diagnostic'),(True,'new_grouped')]:
            tr,ca,te=split(new,seed,grouped)
            run(new.iloc[tr],new.iloc[ca],new.iloc[te],FULL,name,seed)
            if grouped:run(new.iloc[tr],new.iloc[ca],new.iloc[te],FULL,'new_grouped_dummy',seed,True)
        for source,target,name in [(oldt,newt,'old_to_new'),(newt,oldt,'new_to_old')]:
            tr,ca=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=seed).split(source,groups=source.group))
            target=target[~target.cross_domain_connected].copy()
            assert set(source.group).isdisjoint(set(target.group))
            assert set(source.source_id).isdisjoint(set(target.source_id))
            run(source.iloc[tr],source.iloc[ca],target,CORE,name,seed)
    allp=pd.concat(predictions,ignore_index=True);save(allp,'predictions.csv');save(splits,'split_ledger.csv');save(metrics,'metrics.csv');save(checks,'split_checks.csv')
    source_rows=[]
    for (scenario,seed),d in allp.groupby(['scenario','seed']):
        for source,g in d.groupby('source_id'):
            err=np.abs(g.target-g.pred)
            source_rows.append(dict(scenario=scenario,seed=seed,source_id=source,n=len(g),mae=err.mean(),bias=(g.pred-g.target).mean(),rmse=np.sqrt(np.mean(err**2)),coverage_row=(err<=g.q_row).mean(),coverage_group=(err<=g.q_group).mean(),mean_distance=g.distance.mean(),in_domain_fraction=g.in_domain.mean()))
    save(source_rows,'per_source_metrics.csv')
    env=dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__,config=CONFIG,group_counts=dict(new_sources=int(new.source_id.nunique()),new_groups=int(new.group.nunique()),old_core_rows=len(old),old_core_sources=int(old.source_id.nunique()),old_transfer_groups=int(oldt.group.nunique()),new_transfer_groups=int(newt.group.nunique()),cross_domain_components=len(crossgroups)))
    (OUT/'environment_config.json').write_text(json.dumps(env,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(env['group_counts'],ensure_ascii=False),flush=True)
if __name__=='__main__':main()
