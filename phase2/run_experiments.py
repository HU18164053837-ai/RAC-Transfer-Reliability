from common import *
import math,platform
import sklearn,scipy
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GroupKFold,GroupShuffleSplit,KFold
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import NearestNeighbors
def base(seed,leaf=3):return ExtraTreesRegressor(n_estimators=200,min_samples_leaf=leaf,max_features=1.,n_jobs=1,random_state=seed)
def ordinary_q(scores,alpha):
    z=np.sort(np.asarray(scores));k=math.ceil((len(z)+1)*(1-alpha)-1e-12)
    return float(z[k-1]) if k<=len(z) else float('inf')
def balanced_q(scores,sources,alpha):
    s=np.asarray(sources);_,inv,cnt=np.unique(s,return_inverse=True,return_counts=True)
    level=(1-alpha)*(len(cnt)+1)/len(cnt)
    if level>1+1e-12:return float('inf')
    ix=np.argsort(scores,kind='stable');weights=1/(len(cnt)*cnt[inv]);cdf=np.cumsum(weights[ix])
    k=min(int(np.searchsorted(cdf,level-1e-12)),len(ix)-1)
    return float(np.asarray(scores)[ix[k]])
def tree_sd(model,x):return np.std(np.stack([t.predict(x.to_numpy()) for t in model.estimators_]),axis=0)
def ecdf(reference,values):return np.searchsorted(np.sort(reference),values,side='right')/len(reference)
PRED=[];CAL=[];SPLITS=[];OOF=[];CHECK=[];THRESH=[];QTABLE=[]
def model_run(train,cal,test,cols,scenario,repeat,fold,seed):
    train=train.reset_index(drop=True);cal=cal.reset_index(drop=True);test=test.reset_index(drop=True)
    key=f'{scenario}_R{repeat}_F{fold}'
    for a,b in [(train,cal),(train,test),(cal,test)]:
        assert set(a.record_key).isdisjoint(set(b.record_key))
        assert set(a.group).isdisjoint(set(b.group))
        assert set(a.source_id).isdisjoint(set(b.source_id))
    for part,d in [('fit',train),('calibration',cal),('test',test)]:
        for r in d[['record_key','source_id','group']].itertuples(index=False):SPLITS.append(dict(run=key,scenario=scenario,repeat=repeat,fold=fold,split=part,record_key=r.record_key,source_id=r.source_id,group=r.group))
    model=base(seed).fit(train[cols],train.target)
    pc=model.predict(cal[cols]);pt=model.predict(test[cols])
    oof=np.full(len(train),np.nan)
    for inner,(tr,va) in enumerate(GroupKFold(n_splits=3).split(train,groups=train.group)):
        assert set(train.iloc[tr].group).isdisjoint(set(train.iloc[va].group))
        aux=base(seed+inner+11).fit(train.iloc[tr][cols],train.iloc[tr].target)
        oof[va]=aux.predict(train.iloc[va][cols])
        for j in va:OOF.append(dict(run=key,record_key=train.iloc[j].record_key,group=train.iloc[j].group,inner_fold=inner,observed=float(train.iloc[j].target),prediction=float(oof[j]),fit_groups='|'.join(sorted(set(train.iloc[tr].group)))))
    assert np.isfinite(oof).all()
    scale=base(seed+51,10).fit(train[cols],np.log1p(np.abs(train.target.to_numpy()-oof)))
    sc=np.maximum(1,np.expm1(scale.predict(cal[cols])));st=np.maximum(1,np.expm1(scale.predict(test[cols])))
    scaler=RobustScaler().fit(train[cols]);zx=scaler.transform(train[cols]);zc=scaler.transform(cal[cols]);zt=scaler.transform(test[cols])
    nn=NearestNeighbors(n_neighbors=1).fit(zx)
    dc=nn.kneighbors(zc)[0][:,0];dt=nn.kneighbors(zt)[0][:,0]
    sdc=tree_sd(model,cal[cols]);sdt=tree_sd(model,test[cols])
    jc=np.maximum(ecdf(dc,dc),ecdf(sc,sc));jt=np.maximum(ecdf(dc,dt),ecdf(sc,st))
    c=cal[['record_key','record_id','source_id','group','dataset','target']].copy();p=test[['record_key','record_id','source_id','group','dataset','target']].copy()
    for d,pred,sigma,dist,sd,joint in [(c,pc,sc,dc,sdc,jc),(p,pt,st,dt,sdt,jt)]:
        d['prediction']=pred;d['sigma']=sigma;d['distance']=dist;d['tree_sd']=sd;d['joint']=joint
        d['random']=[stable_uniform(f'{key}:{rid}') for rid in d.record_key]
        d['run']=key;d['scenario']=scenario;d['repeat']=repeat;d['fold']=fold
    for v in ['rar','absorption','crushing','cement','fly_ash','slag','water','metadata_risk_group','unique_xy_first','ref_no']:
        if v in test:p[v]=test[v].to_numpy()
    p['wb']=test.water.to_numpy()/(test.cement+test.fly_ash+test.slag).to_numpy()
    shift=pd.DataFrame(zt,columns=cols).groupby(test.source_id).mean().abs().mean(axis=1)
    p['source_feature_shift']=test.source_id.map(shift).to_numpy()
    residual=np.abs(cal.target.to_numpy()-pc)
    gmax=pd.DataFrame({'group':cal.group,'r':residual}).groupby('group').r.max().to_numpy()
    for alpha in ALPHAS:
        level=int(round(100*(1-alpha)))
        qs={'pooled':ordinary_q(residual,alpha),'source_balanced':balanced_q(residual,cal.source_id,alpha),'adaptive':balanced_q(residual/sc,cal.source_id,alpha),'group_max':ordinary_q(gmax,alpha)}
        for method,q in qs.items():
            sigmat=st if method=='adaptive' else np.ones(len(test));sigmac=sc if method=='adaptive' else np.ones(len(cal))
            p[f'radius_{method}_{level}']=q*sigmat;c[f'radius_{method}_{level}']=q*sigmac
            factor=1.
            if level==90:
                factor=float(qs['pooled']/np.mean(q*sigmac)) if np.isfinite(q) else 0.
                assert factor>0 and np.isfinite(factor)
                p[f'radius_{method}_90_budget']=q*sigmat*factor;c[f'radius_{method}_90_budget']=q*sigmac*factor
            QTABLE.append(dict(run=key,scenario=scenario,repeat=repeat,fold=fold,method=method,nominal=1-alpha,q=q,cal_mean_width=float(np.mean(2*q*sigmac)),budget_multiplier=factor,cal_sources=cal.source_id.nunique(),cal_groups=cal.group.nunique()))
    for selector in ['random','tree_sd','distance','sigma','joint']:
        for retain in RETENTIONS:
            threshold=float('inf') if retain==1 else float(retain if selector=='random' else np.quantile(c[selector],retain))
            THRESH.append(dict(run=key,selector=selector,retention=retain,threshold=threshold))
    CHECK.append(dict(run=key,scenario=scenario,repeat=repeat,fold=fold,seed=seed,fit_n=len(train),cal_n=len(cal),test_n=len(test),fit_groups=train.group.nunique(),cal_groups=cal.group.nunique(),test_groups=test.group.nunique(),source_overlap=0,group_overlap=0,features='|'.join(cols),zero_iqr_features='|'.join(np.array(cols)[np.subtract(*np.percentile(train[cols],[75,25],axis=0))==0])))
    PRED.append(p);CAL.append(c)
    print(key,'rows',len(train),len(cal),len(test),'RMSE',round(np.sqrt(np.mean((pt-test.target)**2)),3),'radii',round(float(p.radius_pooled_90.mean()),3),round(float(p.radius_adaptive_90.mean()),3),flush=True)
def outer(d,scenario,seeds):
    unique=np.array(sorted(d.group.unique()))
    for repeat,seed in enumerate(seeds):
        for fold,(devg,testg) in enumerate(KFold(5,shuffle=True,random_state=seed).split(unique)):
            dev=d[d.group.isin(unique[devg])];test=d[d.group.isin(unique[testg])]
            tr,ca=next(GroupShuffleSplit(1,test_size=.25,random_state=seed+fold+200).split(dev,groups=dev.group))
            model_run(dev.iloc[tr],dev.iloc[ca],test,FULL,scenario,repeat,fold,seed+fold*100)
def main():
    lock=json.loads((OUT/'plan_lock_sha256.json').read_text());assert sha(ROOT/lock['path'])==lock['sha256']
    d=pd.read_csv(data_file('new_frozen.csv'));d['dataset']='new';d['record_key']='new:'+d.record_id.astype(str)
    outer(d,'main',SEEDS)
    outer(d[~d.metadata_risk_group].copy(),'metadata_sensitivity',SEEDS[:1])
    # Reuse the exact Phase 1 six-feature split and component map for historical cross-corpus stress.
    old=pd.read_csv(data_file('old_input.csv'));old=old[old.core_eligible].copy();old['record_id']=old.record_id.astype(str);old['record_key']='old:'+old.record_id;old['dataset']='old'
    trans=pd.read_csv(data_file('transfer_groups.csv'))
    # transfer_groups contains old/new ID collisions only if textual IDs collide; CS_ prefix avoids collision.
    allx=pd.concat([old,d],ignore_index=True).drop(columns='group',errors='ignore').merge(trans[['record_id','group']].assign(record_id=lambda x:x.record_id.astype(str)),on='record_id',how='left',validate='one_to_one')
    assert allx.group.notna().all()
    led=pd.read_csv(data_file('phase1_split_ledger.csv'))
    for name in ['old_to_new','new_to_old']:
        sub=led[(led.scenario==name)&(led.seed==20261107)]
        parts={k:allx[allx.record_key.isin(z.record_key)] for k,z in sub.groupby('split')}
        model_run(parts['fit'],parts['calibration'],parts['test'],CORE,name,0,0,20261107)
    save(pd.concat(PRED,ignore_index=True),'predictions.csv');save(pd.concat(CAL,ignore_index=True),'calibration_predictions.csv');save(SPLITS,'split_ledger.csv');save(OOF,'scale_training_oof.csv');save(CHECK,'split_checks.csv');save(THRESH,'selection_thresholds.csv');save(QTABLE,'calibration_quantiles.csv')
    env=dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__,scipy=scipy.__version__,seeds=SEEDS,base=dict(n_estimators=200,min_samples_leaf=3,max_features=1.,n_jobs=1),scale=dict(n_estimators=200,min_samples_leaf=10,target='log1p(group_OOF_abs_error)',floor_mpa=1),plan_sha256=lock['sha256'],proper_model_fits=len(CHECK),auxiliary_and_scale_fits=4*len(CHECK))
    (OUT/'environment.json').write_text(json.dumps(env,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
