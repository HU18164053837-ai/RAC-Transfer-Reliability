from common import *
os.environ['MPLCONFIGDIR']=str(ROOT/'results/.mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':7,'axes.titlesize':8,'axes.labelsize':7,'xtick.labelsize':6,'ytick.labelsize':6,'legend.fontsize':6,'legend.frameon':False,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,'savefig.dpi':300})
COL={'pooled':'#315B7D','source_balanced':'#BB783B','adaptive':'#668D70','group_max':'#937DAB','adaptive_matched':'#C15B66'}
LAB={'pooled':'Pooled residual','source_balanced':'Source balanced','adaptive':'Adaptive (native)','group_max':'Group maximum','adaptive_matched':'Adaptive (budget)'}
RULECOL={'random':'#999999','tree_sd':'#937DAB','distance':'#BB783B','sigma':'#668D70','joint':'#315B7D'}
RULELAB={'random':'Random (100 repeats)','tree_sd':'Tree SD','distance':'Distance','sigma':'Adaptive width','joint':'Joint (pre-specified)'}
def export(fig,name):
    fig.savefig(FIG/f'{name}.svg',bbox_inches='tight')
    fig.savefig(FIG/f'{name}.pdf',bbox_inches='tight')
    fig.savefig(FIG/f'{name}.png',dpi=300,bbox_inches='tight')
    plt.close(fig)
def main():
    intervals=pd.read_csv(OUT/'interval_metrics.csv');src=pd.read_csv(OUT/'source_coverage.csv');sel=pd.read_csv(OUT/'selective_metrics.csv');rnd=pd.read_csv(OUT/'random_baseline_100.csv');diag=pd.read_csv(OUT/'source_diagnostics.csv')
    maini=intervals[(intervals.scenario=='main')&(intervals['repeat'].astype(str)=='all')]
    ss=src[src.scenario=='main'];order=ss[(ss.method=='pooled')&(ss.budget=='native')].sort_values('coverage').source_id.tolist()
    keys=[('pooled','native'),('source_balanced','native'),('adaptive','native'),('group_max','native'),('adaptive','matched')]
    labels=[LAB[m if b=='native' else 'adaptive_matched'] for m,b in keys]
    matrix=np.stack([ss[(ss.method==m)&(ss.budget==b)].set_index('source_id').loc[order].coverage.to_numpy() for m,b in keys])
    fig,axs=plt.subplots(2,1,figsize=(7.204724,120/25.4),gridspec_kw={'height_ratios':[1,1.4]},layout='constrained')
    im=axs[0].imshow(matrix,aspect='auto',vmin=0,vmax=1,cmap='cividis',interpolation='none')
    axs[0].set_yticks(range(len(labels)),labels);axs[0].set_xticks([0,24,49,74,99,114],[1,25,50,75,100,115]);axs[0].set_xlabel('All 115 publication sources, ordered by pooled coverage');axs[0].set_title('a  Source-level empirical coverage',loc='left',fontweight='bold')
    fig.colorbar(im,ax=axs[0],label='Coverage',pad=.015,fraction=.025)
    for j,(m,b) in enumerate(keys):
        values=np.sort(matrix[j]);key=m if b=='native' else 'adaptive_matched'
        axs[1].step(values,np.arange(1,len(values)+1)/len(values),where='post',color=COL[key],label=LAB[key],lw=1.2)
    axs[1].axvline(.9,color='#777777',ls='--',lw=.7);axs[1].set(xlabel='Within-source coverage (nominal 0.90)',ylabel='Fraction of sources',xlim=(-.02,1.02),ylim=(0,1.02));axs[1].legend(ncol=2,loc='upper left');axs[1].set_title('b  Distribution across sources (equal source weight)',loc='left',fontweight='bold')
    export(fig,'source_coverage_diagnostics')
    fig,axs=plt.subplots(1,2,figsize=(7.204724,83/25.4),layout='constrained')
    for method in METHODS:
        d=maini[(maini.method==method)&(maini.budget=='native')].sort_values('nominal')
        axs[0].plot(d.mean_width,d.source_macro_coverage,'-o',color=COL[method],label=LAB[method],ms=3,lw=1)
        offset={'pooled':(-7,-10),'source_balanced':(3,5),'adaptive':(3,-10),'group_max':(3,5)}[method]
        for r in d.itertuples():axs[0].annotate(str(int(round(r.nominal*100))),(r.mean_width,r.source_macro_coverage),xytext=((3,5) if method=='pooled' and r.nominal<.85 else offset),textcoords='offset points',fontsize=5,color=COL[method])
    b=maini[(maini.method=='adaptive')&(maini.budget=='matched')].iloc[0]
    axs[0].scatter([b.mean_width],[b.source_macro_coverage],marker='D',s=22,color=COL['adaptive_matched'],label=LAB['adaptive_matched'])
    axs[0].axhline(.9,color='#777777',ls='--',lw=.7);axs[0].set(xlabel='Mean full interval width (MPa)',ylabel='Equal-source coverage');axs[0].set_title('a  Reliability versus width',loc='left',fontweight='bold');axs[0].legend(loc='lower right',fontsize=5)
    for m,b in [('pooled','native'),('adaptive','native'),('adaptive','matched')]:
        d=ss[(ss.method==m)&(ss.budget==b)];key=m if b=='native' else 'adaptive_matched';x=np.sort(d.mean_width)
        axs[1].step(x,np.arange(1,len(x)+1)/len(x),where='post',label=LAB[key],color=COL[key])
    axs[1].set(xlabel='Source mean full width (MPa)',ylabel='Fraction of sources');axs[1].set_title('b  Distribution of width allocation',loc='left',fontweight='bold');axs[1].legend(loc='lower right')
    export(fig,'width_reliability')
    fig,axs=plt.subplots(2,2,figsize=(7.204724,133/25.4),layout='constrained')
    d=sel[(sel.scenario=='main')&(sel['mode']=='quota')&(sel.method=='adaptive')&(sel.budget=='matched')]
    rr=rnd[(rnd.method=='adaptive')&(rnd.budget=='matched')]
    for ax,metric,title,ylab in zip(axs.flat,['rmse','mae','source_macro_coverage','p10_source_coverage'],['a  Prediction error','b  Absolute error','c  Equal-source coverage','d  Low-coverage source tail'],['RMSE (MPa)','MAE (MPa)','Coverage','10th-percentile coverage']):
        agg=rr.groupby('target_retention')[metric].agg(['mean',lambda x:np.quantile(x,.025),lambda x:np.quantile(x,.975)]).sort_index()
        ax.fill_between(agg.index.to_numpy(float),agg.iloc[:,1].to_numpy(float),agg.iloc[:,2].to_numpy(float),color='#DDDDDD',alpha=.7,zorder=0)
        ax.plot(agg.index,agg['mean'],'--',color=RULECOL['random'],label=RULELAB['random'],lw=1)
        for rule in ['tree_sd','distance','sigma','joint']:
            z=d[d.selector==rule].sort_values('retention');ax.plot(z.retention,z[metric],'-o',color=RULECOL[rule],label=RULELAB[rule],ms=2.5,lw=1.4 if rule=='joint' else .8)
        if metric in ['source_macro_coverage','p10_source_coverage']:ax.axhline(.9,color='#777777',ls=':',lw=.6);ax.set_ylim(0,1.02)
        ax.set(xlabel='Actual sample retention',ylabel=ylab,xlim=(.48,1.02));ax.set_title(title,loc='left',fontweight='bold');ax.grid(axis='y',alpha=.15)
    axs[0,0].legend(fontsize=5,loc='upper left')
    export(fig,'selective_risk_retention')
    fig,axs=plt.subplots(1,3,figsize=(7.204724,78/25.4),layout='constrained')
    for ax,x,y,title,xlab,ylab in [(axs[0],'distance','mae','a  Input distance','Mean nearest-fit distance','Source MAE (MPa)'),(axs[1],'sigma','mae','b  Training-only error scale','Mean predicted scale (MPa)','Source MAE (MPa)'),(axs[2],'bias2_mse_ratio','pooled_coverage','c  Residual coherence','Squared source bias / MSE','Pooled source coverage')]:
        for risk,color,label in [(False,'#315B7D','Other sources'),(True,'#C15B66','Metadata-risk groups')]:
            z=diag[diag.metadata_risk==risk];ax.scatter(z[x],z[y],s=5+np.sqrt(z.n_records)*2,color=color,alpha=.65,edgecolors='none',label=label)
        ax.set(xlabel=xlab,ylabel=ylab);ax.set_title(title,loc='left',fontweight='bold')
        if x=='distance':ax.set_xscale('symlog',linthresh=1)
    axs[2].axhline(.9,color='#777777',ls='--',lw=.7);axs[0].legend(fontsize=5,loc='upper left')
    export(fig,'source_shift_residual_risk')
    fig,axs=plt.subplots(1,2,figsize=(7.204724,78/25.4),layout='constrained')
    d=sel[(sel.scenario=='main')&(sel['mode']=='calibration_threshold')&(sel.method=='adaptive')&(sel.budget=='matched')]
    for rule in ['random','tree_sd','distance','sigma','joint']:
        z=d[d.selector==rule].sort_values('target_retention');axs[0].plot(z.target_retention,z.retention,'-o',color=RULECOL[rule],label=('Random (fixed uniform)' if rule=='random' else RULELAB[rule]),ms=3);axs[1].plot(z.retention,z.source_retention,'-o',color=RULECOL[rule],ms=3)
    axs[0].plot([.5,1],[.5,1],':',color='gray',lw=.7);axs[0].set(xlabel='Target retention (calibration percentile)',ylabel='Actual test retention');axs[0].set_title('a  Fixed-threshold transfer',loc='left',fontweight='bold');axs[0].legend(fontsize=5)
    axs[1].set(xlabel='Actual test sample retention',ylabel='Fraction of sources retained',ylim=(0,1.03));axs[1].set_title('b  Publication retention',loc='left',fontweight='bold')
    export(fig,'threshold_and_source_retention')
    print('Exported 5 figures × SVG/PDF/PNG',flush=True)
if __name__=='__main__':main()
