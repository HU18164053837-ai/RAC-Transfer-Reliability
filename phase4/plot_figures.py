"""Formal figures from frozen numerical outputs; no fits or inferential resampling."""
from common import *
os.environ['MPLCONFIGDIR']=str(ROOT/'qa/.mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MaxNLocator
from PIL import Image
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':7,'axes.labelsize':7,'axes.titlesize':8,'xtick.labelsize':6.5,'ytick.labelsize':6.5,'legend.fontsize':6.5,'legend.frameon':False,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,'lines.linewidth':1.2,'savefig.facecolor':'white'})
W=183/25.4
def load(n):return pd.read_csv(SD/n)
def panel(ax,label,title):
    ax.set_title(title,loc='left',pad=9)
    ax.text(-.12,1.05,label,transform=ax.transAxes,fontweight='bold',fontsize=9,va='bottom')
def export(fig,name):
    fig.savefig(FIG/(name+'.svg'))
    fig.savefig(FIG/(name+'.pdf'))
    fig.savefig(FIG/(name+'.png'),dpi=300)
    fig.savefig(FIG/(name+'.tiff'),dpi=600,pil_kwargs={'compression':'tiff_lzw'})
    plt.close(fig)
def point_ci(ax,estimate,lo,hi,y,color,marker='o',label=None,scale=1):
    ax.errorbar(estimate*scale,y,xerr=np.array([[estimate-lo],[hi-estimate]])*scale,fmt=marker,color=color,markersize=4,capsize=2,lw=1,label=label)
def figures():
    # Figure 1: units and their observed sizes, not an invented material mechanism.
    sources=load('F1_sources.csv').sort_values('records',ascending=False);groups=load('F1_components.csv')
    fig=plt.figure(figsize=(W,135/25.4),layout='constrained');gs=fig.add_gridspec(2,2,height_ratios=[1,1.05],width_ratios=[1.2,1])
    a=fig.add_subplot(gs[0,0]);panel(a,'a','Rows, publications and association groups');a.set_axis_off()
    for y,title,sub in [(.82,'1,736 mixture records','All original outlier flags retained'),(.48,'115 publication sources','Bibliographic identity; not 115 laboratories'),(.14,'99 connected components','Publication identity and near-recipe links')]:
        box=FancyBboxPatch((.04,y-.09),.89,.2,boxstyle='round,pad=0.015',fc='#F1F4F6',ec='#AAB4BD',lw=.7,transform=a.transAxes);a.add_patch(box)
        a.text(.485,y+.035,title,ha='center',va='center',transform=a.transAxes,fontweight='bold',fontsize=8)
        a.text(.485,y-.035,sub,ha='center',va='center',transform=a.transAxes,fontsize=6.5)
    for y in [.69,.35]:a.annotate('',xy=(.485,y-.09),xytext=(.485,y+.025),xycoords='axes fraction',arrowprops=dict(arrowstyle='->',lw=.8,color='#596574'))
    b=fig.add_subplot(gs[0,1]);panel(b,'b','Records per publication source')
    b.bar(np.arange(1,116),sources.records,color=COLORS['pooled'],width=.9);b.set(xlabel='Publication rank by record count',ylabel='Mixture records',xlim=(0,116),ylim=(0,130));b.set_xticks([1,30,60,90,115])
    c=fig.add_subplot(gs[1,0]);panel(c,'c','Publications linked within components')
    cnt=groups.sources.value_counts().sort_index();c.bar(np.arange(len(cnt)),cnt.values,color=COLORS['source_balanced'],width=.65)
    c.set(xticks=np.arange(len(cnt)),xticklabels=cnt.index,xlabel='Publication sources per component',ylabel='Connected components',ylim=(0,105))
    for x,v in enumerate(cnt.values):c.text(x,v+2,str(v),ha='center',fontsize=7)
    d=fig.add_subplot(gs[1,1]);panel(d,'d','Frozen evaluation and evidence boundary');d.set_axis_off()
    lines=[('2 repeats × 5 outer folds','59–60 fit / 20 calibration / 19–20 test groups'),('3,472 prediction events','1,736 unique rows; repeats stay clustered'),('7 priority sources, 247 records','Original row-level confirmation: unknown'),('Independent confirmation','No qualifying new dataset admitted')]
    for y,(title,sub) in zip([.88,.62,.36,.10],lines):
        d.text(0,y,title,transform=d.transAxes,fontweight='bold',fontsize=7.5);d.text(0,y-.09,sub,transform=d.transAxes,fontsize=6.5)
    export(fig,'Fig1_data_and_evidence')
    # Figure 2: stored 99-component confidence intervals, native vs budget identified.
    t=pd.read_csv(ROOT/'tables/Table2_interval_reliability.csv').set_index('interval');effects=load('F2_F5_paired_changes.csv')
    fig,axs=plt.subplots(2,2,figsize=(W,145/25.4),layout='constrained')
    ax=axs[0,0];panel(ax,'a','Coverage at the 90% nominal level')
    for y,m in enumerate(METHODS):
        r=t.loc[m]
        for key,offset,mark in [('coverage_retained',-.10,'o'),('macro_coverage_survivors',.10,'s')]:point_ci(ax,r[key],r[key+'_ci_low'],r[key+'_ci_high'],y+offset,COLORS[m],mark,label=('Sample weighted' if mark=='o' else 'Source equal') if y==0 else None,scale=100)
    ax.set(yticks=range(5),yticklabels=[LABELS[m] for m in METHODS],xlim=(0,102),xlabel='Coverage (%)');ax.invert_yaxis();ax.axvline(90,color='#9EA5AA',ls='--',lw=.8);ax.legend(loc='lower left')
    ax=axs[0,1];panel(ax,'b','Width paid for coverage')
    for m in METHODS:
        r=t.loc[m];ax.scatter(r.mean_width,r.macro_coverage_survivors*100,c=COLORS[m],s=27,marker='s' if m=='adaptive_budget' else 'o',label=LABELS[m])
    ax.axhline(90,color='#9EA5AA',ls='--',lw=.8);ax.set(xlim=(0,60),ylim=(0,100),xlabel='Mean interval full width (MPa)',ylabel='Source-equal coverage (%)');ax.legend(loc='lower right',fontsize=6)
    for ax,metric,label in [(axs[1,0],'sample_interval_score','Sample-weighted score difference (MPa)'),(axs[1,1],'source_macro_interval_score','Source-equal score difference (MPa)')]:
        panel(ax,'c' if metric.startswith('sample') else 'd','Interval score relative to pooled')
        for y,m in enumerate(METHODS[1:]):
            q=effects[(effects.comparison==m+'_vs_pooled')&(effects.metric==metric)].iloc[0];point_ci(ax,q.delta,q.ci_low,q.ci_high,y,COLORS[m])
        ax.set(yticks=range(4),yticklabels=[LABELS[m] for m in METHODS[1:]],xlabel=label,xlim=(-6,20));ax.axvline(0,color='#9EA5AA',ls='--',lw=.8);ax.invert_yaxis()
    export(fig,'Fig2_coverage_interval_cost')
    # Figure 3: all 115 source columns, and all predictions in the three focus sources.
    sc=load('F3_all_source_coverage.csv');order=sc[sc.interval=='pooled'].sort_values(['conditional_coverage','source_id']).source_id.tolist()
    refs=load('F1_sources.csv').set_index('source_id').ref_no
    fig=plt.figure(figsize=(W,135/25.4),layout='constrained');gs=fig.add_gridspec(2,3,height_ratios=[.85,1.2])
    ax=fig.add_subplot(gs[0,:]);panel(ax,'a','Coverage across every publication source')
    matrix=np.stack([sc[sc.interval==m].set_index('source_id').loc[order].conditional_coverage.to_numpy()*100 for m in METHODS]);im=ax.imshow(matrix,aspect='auto',vmin=0,vmax=100,cmap='cividis',interpolation='none',extent=(.5,115.5,4.5,-.5))
    ax.set(yticks=range(5),yticklabels=[LABELS[m] for m in METHODS],xlabel='Publication rank by pooled coverage (all 115 sources)',xticks=[1,20,40,60,80,100,115]);fig.colorbar(im,ax=ax,label='Coverage (%)',fraction=.025,pad=.015)
    raw=load('F3_focus_predictions.csv');diag=load('F3_focus_diagnostics.csv');lo=np.floor(raw.residual.min()/5)*5;hi=5
    for k,no in enumerate([36,82,109]):
        ax=fig.add_subplot(gs[1,k]);n=raw[raw.ref_no==no].record_key.nunique();panel(ax,chr(98+k),f'Source DB{no} · {n} rows')
        z=raw[raw.ref_no==no]
        for rep,color,marker in [(0,COLORS['source_balanced'],'o'),(1,COLORS['adaptive_budget'],'^')]:
            q=z[z['repeat']==rep];ax.scatter(q.target,q.residual,s=15,color=color,marker=marker,alpha=.8,label=f'Repeat {rep+1}')
            bias=diag[(diag.ref_numbers==no)&(diag['repeat'].astype(str)==str(rep))].bias.iloc[0];ax.axhline(bias,color=color,lw=.8,ls='--')
        ax.axhline(0,color='#596574',lw=.7);ax.set(ylim=(lo,hi),xlabel='Database strength (MPa)',ylabel='Prediction − label (MPa)' if k==0 else '',xlim=(10,105));ax.set_xticks([20,60,100])
        if k==0:ax.legend(loc='lower left',fontsize=6)
    export(fig,'Fig3_source_coverage_residuals')
    # Figure 4: joint rule at all five pre-set quotas; no interpolated operating optimum.
    j=load('F4_F5_retention.csv');q=j[(j['mode']=='quota')&(j.rule=='joint')&(j.interval=='adaptive_budget')&(j['repeat'].astype(str)=='all')].sort_values('target_retention')
    fig,axs=plt.subplots(2,2,figsize=(W,145/25.4),layout='constrained');ci=load('F2_coverage_width_ci.csv')
    ax=axs[0,0];panel(ax,'a','Conditional prediction error')
    for metric,marker,color in [('rmse','o',COLORS['joint']),('mae','s',COLORS['pooled'])]:
        ax.plot(q.sample_retention*100,q[metric],marker=marker,color=color,label=metric.upper())
        for rate in [.8,.9]:
            r=q[np.isclose(q.target_retention,rate)].iloc[0];v=ci[(ci.analysis==f'quota_joint_{rate:.1f}')&(ci.metric==metric)].iloc[0]
            ax.errorbar(r.sample_retention*100,r[metric],yerr=[[r[metric]-v.ci_low],[v.ci_high-r[metric]]],fmt='none',color=color,capsize=2,lw=.8)
    ax.set(xlim=(48,102),ylim=(0,12),xlabel='Actual sample retention (%)',ylabel='Error on accepted events (MPa)');ax.legend()
    ax=axs[0,1];panel(ax,'b','Which coverage denominator?')
    for metric,label,color,marker in [('macro_coverage_survivors','Surviving sources',COLORS['source_balanced'],'o'),('macro_coverage_zero_absent','Zero if absent',COLORS['adaptive'],'s'),('macro_source_success_yield','Original-source successful service',COLORS['joint'],'^')]:ax.plot(q.sample_retention*100,q[metric]*100,color=color,marker=marker,label=label)
    ax.set(xlim=(48,102),ylim=(0,100),xlabel='Actual sample retention (%)',ylabel='Source-equal fraction (%)');ax.legend(loc='lower right',fontsize=6)
    ax=axs[1,0];panel(ax,'c','Retaining events versus retaining sources')
    for metric,label,color,marker in [('source_retention','Any service for a source',COLORS['source_balanced'],'o'),('macro_source_sample_retention','Mean within-source retention',COLORS['joint'],'s')]:ax.plot(q.sample_retention*100,q[metric]*100,color=color,marker=marker,label=label)
    ax.plot([50,100],[50,100],ls=':',color='#9EA5AA',label='Equal sample/source fraction');ax.set(xlim=(48,102),ylim=(0,100),xlabel='Actual sample retention (%)',ylabel='Source retention measure (%)');ax.legend(loc='lower right',fontsize=6)
    ax=axs[1,1];panel(ax,'d','Outcomes over the original source scope')
    x=np.arange(len(q));bottom=np.zeros(len(q))
    for field,label,color in [('macro_source_success_yield','Accepted and covered',COLORS['adaptive']),('macro_accepted_uncovered_share','Accepted and uncovered',COLORS['joint']),('macro_unserved_share','Rejected', '#B8BEC4')]:
        vals=q[field].to_numpy()*100;ax.bar(x,vals,bottom=bottom,color=color,width=.67,label=label);bottom+=vals
    ax.set(xticks=x,xticklabels=[f'{v*100:.0f}' for v in q.target_retention],ylim=(0,100),xlabel='Target sample retention (%)',ylabel='Mean original-source fraction (%)');ax.legend(loc='upper left',bbox_to_anchor=(0,-.23),fontsize=6)
    export(fig,'Fig4_retention_service_risk')
    # Figure 5: 100-random baseline means, full curves, and frozen paired contrasts.
    rnd=load('F5_random_100.csv');fig,axs=plt.subplots(2,2,figsize=(W,145/25.4),layout='constrained')
    for ax,metric,title,yl in [(axs[0,0],'rmse','Error reduction across simple scores','Accepted-event RMSE (MPa)'),(axs[0,1],'macro_source_success_yield','Service over the original source scope','Original-source successful service (%)')]:
        panel(ax,'a' if metric=='rmse' else 'b',title);factor=1 if metric=='rmse' else 100
        agg=rnd.groupby('target_retention').agg(x=('sample_retention','mean'),mean=(metric,'mean'),lo=(metric,lambda v:v.quantile(.025)),hi=(metric,lambda v:v.quantile(.975))).sort_index()
        ax.fill_between(agg.x*100,agg.lo*factor,agg.hi*factor,color=COLORS['random'],alpha=.18,linewidth=0);ax.plot(agg.x*100,agg['mean']*factor,color=COLORS['random'],ls='--',label='Random (100 permutations)')
        for rule in ['tree_sd','distance','sigma','joint']:
            z=j[(j['mode']=='quota')&(j.rule==rule)&(j.interval=='adaptive_budget')&(j['repeat'].astype(str)=='all')].sort_values('target_retention');ax.plot(z.sample_retention*100,z[metric]*factor,color=COLORS[rule],marker={'tree_sd':'o','distance':'s','sigma':'^','joint':'D'}[rule],markersize=3,label=LABELS[rule])
        ax.set(xlim=(48,102),ylim=(0,12) if metric=='rmse' else (0,100),xlabel='Actual sample retention (%)',ylabel=yl)
        if metric=='rmse':ax.legend(loc='lower right',fontsize=6)
    ax=axs[1,0];panel(ax,'c','Joint minus simple score at 80% quota')
    for y,rule in enumerate(['tree_sd','distance','sigma']):
        r=effects[(effects.comparison=='joint80_vs_'+rule)&(effects.metric=='rmse')].iloc[0];point_ci(ax,r.delta,r.ci_low,r.ci_high,y,COLORS[rule])
    ax.set(yticks=range(3),yticklabels=['Tree SD','Distance','Scale / width'],xlabel='Paired RMSE difference (MPa)',xlim=(-.55,.55));ax.axvline(0,color='#9EA5AA',lw=.8,ls='--');ax.invert_yaxis()
    ax=axs[1,1];panel(ax,'d','Sources wholly unserved at 80% quota')
    rules=['tree_sd','distance','sigma','joint'];centers=np.arange(4)
    for offset,repeat,label,color in [(-.22,'0','Repeat 1','#7D98AC'),(0,'1','Repeat 2','#B6C6D1'),(.22,'all','Both repeats','#BD7734')]:
        vals=[j[(j['mode']=='quota')&(j.rule==rule)&np.isclose(j.target_retention,.8)&(j.interval=='adaptive_budget')&(j['repeat'].astype(str)==repeat)].absent_sources.iloc[0] for rule in rules];ax.bar(centers+offset,vals,width=.21,color=color,label=label)
    ax.set(xticks=centers,xticklabels=['Tree SD','Distance','Scale /\nwidth','Joint'],ylim=(0,22),ylabel='Publication sources (of 115)');ax.yaxis.set_major_locator(MaxNLocator(integer=True));ax.legend(loc='upper left',fontsize=6)
    export(fig,'Fig5_baselines_source_exclusion')
    # Supplementary diagnostic panels reuse the complete frozen nominal-level results.
    allm=read(2,'interval_metrics.csv');v=allm[(allm.scenario=='main')&(allm['repeat'].astype(str)=='all')&(allm.budget=='native')]
    fig,axs=plt.subplots(1,2,figsize=(W,75/25.4),layout='constrained')
    for ax,metric,title in [(axs[0],'coverage','Sample-weighted calibration'),(axs[1],'source_macro_coverage','Source-equal calibration')]:
        panel(ax,'a' if metric=='coverage' else 'b',title)
        for m in ['pooled','source_balanced','adaptive','group_max']:
            z=v[v.method==m].sort_values('nominal');ax.plot(z.nominal*100,z[metric]*100,marker='o',color=COLORS[m],label=LABELS[m])
        ax.plot([0,100],[0,100],ls='--',color='#9EA5AA',lw=.8);ax.set(xlim=(0,100),ylim=(0,100),xlabel='Nominal coverage (%)',ylabel='Empirical coverage (%)')
    axs[1].legend(loc='lower right');export(fig,'FigS1_nominal_calibration')
    # All four tested representation/selection families and threshold mode stay in electronic SI.
    formats=[]
    for p in sorted(FIG.glob('*.tiff')):
        with Image.open(p) as im:formats.append(dict(file=p.name,pixels=list(im.size),dpi=[float(v) for v in im.info.get('dpi',())],compression=im.info.get('compression')))
    (ROOT/'qa/figure_exports.json').write_text(json.dumps(formats,indent=2),encoding='utf-8')
    print('Five main figures and one SI figure exported in SVG/PDF/TIFF/PNG')
if __name__=='__main__':figures()
