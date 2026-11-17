from pathlib import Path
import os,sys,json
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
if os.environ.get('RAC_ML_DEPS'):sys.path.insert(0,os.environ['RAC_ML_DEPS'])
os.environ['MPLCONFIGDIR']=str(ROOT/'results/.mplconfig')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=ROOT/'results';DER=ROOT/'data/derived'
def main():
    m=pd.read_csv(OUT/'metrics.csv');p=pd.read_csv(OUT/'predictions.csv');new=pd.read_csv(DER/'compressive_strength.csv')
    meta=new[['record_id','ref_no','rar','outlier_flag','water','cement','fly_ash','slag','absorption','crushing']].copy()
    meta['wb']=meta.water/(meta.cement+meta.fly_ash+meta.slag)
    q=p[p.scenario=='new_grouped'].merge(meta,on='record_id',how='left',validate='many_to_one')
    q['abs_error']=np.abs(q.target-q.pred);q['coverage_row']=q.abs_error<=q.q_row
    q['coverage_group']=q.abs_error<=q.q_group
    rows=[]
    for seed,d in q.groupby('seed'):
        subsets={'RAC':d.rar>0,'natural_control':d.rar==0,'original_outlier_flag_0':d.outlier_flag==0,'original_outlier_flag_1':d.outlier_flag==1,'water_binder_le_045':d.wb<=.45,'water_binder_045_060':(d.wb>.45)&(d.wb<=.60),'water_binder_gt_060':d.wb>.60,'absorption_gt_6':d.absorption>6,'absorption_le_6':d.absorption<=6}
        for name,mask in subsets.items():
            s=d[mask]
            if len(s):rows.append(dict(seed=seed,stratum=name,n=len(s),sources=s.source_id.nunique(),mae=s.abs_error.mean(),bias=(s.pred-s.target).mean(),coverage_row=s.coverage_row.mean(),coverage_group=s.coverage_group.mean(),in_domain=s.in_domain.mean()))
    pd.DataFrame(rows).to_csv(OUT/'exploratory_strata.csv',index=False,encoding='utf-8-sig')
    # Seed summaries are descriptive across repeated overlapping partitions, not independent replications.
    selected=m[m.subset=='all']
    summary=selected.groupby(['scenario','method']).agg(seeds=('seed','size'),rmse_mean=('rmse','mean'),rmse_min=('rmse','min'),rmse_max=('rmse','max'),mae_mean=('mae','mean'),r2_mean=('r2','mean'),coverage_mean=('coverage','mean'),coverage_min=('coverage','min'),coverage_max=('coverage','max'),width_mean=('width','mean'),source_macro_coverage_mean=('source_macro_coverage','mean'),complete_group_coverage_mean=('complete_group_coverage','mean'),reject_fraction_mean=('rejected_ad_fraction','mean')).reset_index()
    summary.to_csv(OUT/'key_metrics.csv',index=False,encoding='utf-8-sig')
    refs=pd.read_csv(DER/'new_references.csv');rmap=refs.groupby('source_id').ref_no.apply(lambda x:','.join(map(str,x)))
    src=pd.read_csv(OUT/'per_source_metrics.csv');src['ref_no']=src.source_id.map(rmap)
    src.to_csv(OUT/'per_source_metrics_with_refs.csv',index=False,encoding='utf-8-sig')
    sizes=pd.read_csv(OUT/'new_groups.csv').groupby('group').agg(n=('record_id','size'),sources=('source_id','nunique')).sort_values('n',ascending=False)
    sizes.to_csv(OUT/'new_group_sizes.csv',encoding='utf-8-sig')
    joined=new.merge(pd.read_csv(OUT/'new_groups.csv')[['record_id','group']],on='record_id',validate='one_to_one')
    multis=joined.groupby('group').agg(n=('record_id','size'),sources=('source_id','nunique'),refs=('ref_no',lambda z:','.join(map(str,sorted(set(z)))))).reset_index()
    multis[multis.sources>1].to_csv(OUT/'multisource_recipe_components.csv',index=False,encoding='utf-8-sig')
    # Exact same 11 inputs with inconsistent responses: count clusters, not just excess rows.
    features=['density','crushing','absorption','cement','fly_ash','slag','water','sand','coarse','rar','sp']
    dup=new.groupby(features,dropna=False).agg(n=('target','size'),targets=('target','nunique'),target_min=('target','min'),target_max=('target','max'),refs=('ref_no',lambda x:','.join(map(str,sorted(set(x)))))).reset_index()
    dup[dup.n>1].to_csv(OUT/'new_exact_input_duplicate_clusters.csv',index=False,encoding='utf-8-sig')
    desc=dict(exact_duplicate_clusters=int((dup.n>1).sum()),conflicting_target_clusters=int((dup.targets>1).sum()),conflicting_target_rows=int(dup.loc[dup.targets>1,'n'].sum()),largest_group_rows=int(sizes.n.max()),multisource_groups=int((sizes.sources>1).sum()),new_rac_rows=int((new.rar>0).sum()),new_control_rows=int((new.rar==0).sum()),doi_present_references=int(refs.doi.notna().sum()))
    (OUT/'diagnostic_counts.json').write_text(json.dumps(desc,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200})
    names=['new_random_diagnostic','new_grouped','old_to_new','new_to_old'];labels=['Random rows\n(diagnostic)','New sources\n(grouped)','Old → New\n(6 features)','New → Old\n(6 features)']
    fig,axs=plt.subplots(1,3,figsize=(12.6,3.7),layout='constrained')
    for i,name in enumerate(names):
        d=selected[(selected.scenario==name)&(selected.method=='row')]
        axs[0].scatter(np.full(len(d),i),d.rmse,color='#236B8E',s=30)
        axs[0].plot([i-.18,i+.18],[d.rmse.mean()]*2,color='#163F59',lw=2)
        axs[1].scatter(np.full(len(d),i)-.07,d.coverage*100,color='#236B8E',s=26)
        dg=selected[(selected.scenario==name)&(selected.method=='group')]
        axs[1].scatter(np.full(len(dg),i)+.07,dg.coverage*100,color='#BB6528',marker='s',s=25)
        axs[2].scatter(np.full(len(d),i)-.07,d.width,color='#236B8E',s=26)
        axs[2].scatter(np.full(len(dg),i)+.07,dg.width,color='#BB6528',marker='s',s=25)
    axs[1].axhline(90,color='gray',ls='--',lw=1)
    for ax,title,y in zip(axs,['A  Point error','B  Empirical row coverage','C  Interval width'],['RMSE (MPa)','Coverage (%)','Full width (MPa)']):
        ax.set_title(title,loc='left',fontweight='bold');ax.set_ylabel(y);ax.set_xticks(range(4),labels,fontsize=8);ax.grid(axis='y',alpha=.18)
    axs[1].set_ylim(70,102)
    axs[2].scatter([],[],label='Row-residual calibration',color='#236B8E');axs[2].scatter([],[],label='Group-max calibration',color='#BB6528',marker='s');axs[2].legend(fontsize=7,frameon=False,loc='upper left')
    fig.savefig(OUT/'feasibility_metrics.png');fig.savefig(OUT/'feasibility_metrics.pdf');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(9.2,3.5),layout='constrained')
    colors=['#236B8E','#BB6528','#558B5B']
    for i,seed in enumerate(sorted(q.seed.unique())):
        d=m[(m.scenario=='new_grouped')&(m.method=='row')&(m.seed==seed)]
        a=d[d.subset=='in_domain'].iloc[0];b=d[d.subset=='out_domain'].iloc[0]
        axs[0].plot([0,1],[a.mae,b.mae],'-o',color=colors[i],label=str(seed))
        axs[1].plot([0,1],[a.coverage*100,b.coverage*100],'-o',color=colors[i])
    for ax in axs:ax.set_xticks([0,1],['Inside AD','Outside AD']);ax.grid(axis='y',alpha=.18)
    axs[0].set_ylabel('MAE (MPa)');axs[1].set_ylabel('Row interval coverage (%)');axs[1].axhline(90,color='gray',ls='--');axs[0].legend(frameon=False,fontsize=8)
    axs[0].set_title('A  Error after distance screening',loc='left',fontweight='bold');axs[1].set_title('B  Screening leaves residual risk',loc='left',fontweight='bold')
    fig.savefig(OUT/'applicability_domain.png');fig.savefig(OUT/'applicability_domain.pdf');plt.close(fig)
    print(json.dumps(desc,indent=2));print(summary.to_string(index=False))
if __name__=='__main__':main()
