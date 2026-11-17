"""Presentation-only revision; unchanged frozen source counts and partitions."""
from common import *
FIG=Path(os.environ.get('RAC_FIGURE_OUTPUT',str(PROJECT/'reproduced/figures')))
FIG.mkdir(parents=True,exist_ok=True)
os.environ['MPLCONFIGDIR']=str(ROOT/'qa/.mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':7,'axes.labelsize':7,'axes.titlesize':8,'xtick.labelsize':6.5,'ytick.labelsize':6.5,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
s=pd.read_csv(ROOT/'source_data/F1_sources.csv').sort_values('records',ascending=False)
g=pd.read_csv(ROOT/'source_data/F1_components.csv')
p=pd.read_csv(ROOT/'source_data/F1_splits.csv')
assert len(s)==115 and len(g)==99 and s.records.sum()==1736
fig,axs=plt.subplots(2,2,figsize=(183/25.4,118/25.4),layout='constrained')
def title(a,label,t):
    a.set_title(t,loc='left',pad=11);a.text(-.12,1.06,label,transform=a.transAxes,fontweight='bold',fontsize=9)
a,b,c,d=axs.flat
title(a,'a','Units of analysis');a.axis('off')
for y,t in zip([.82,.49,.16],['1,736 mixture records','115 publication sources','99 association components']):
    a.text(.5,y,t,ha='center',va='center',transform=a.transAxes,fontsize=9,bbox=dict(boxstyle='round,pad=.6',fc='#EDF2F5',ec='#AAB4BD',lw=.7))
title(b,'b','Publication source sizes')
b.bar(np.arange(1,116),s.records,color='#4477AA',width=.9);b.set(xlabel='Rank by record count',ylabel='Mixture records',xlim=(0,116),ylim=(0,130),xticks=[1,30,60,90,115])
title(c,'c','Publication links within components')
counts=g.sources.value_counts().sort_index();c.bar(range(len(counts)),counts.values,color='#228833',width=.65)
c.set(xticks=range(len(counts)),xticklabels=counts.index,xlabel='Publication sources per component',ylabel='Association components',ylim=(0,105))
for x,v in enumerate(counts):c.text(x,v+2,str(v),ha='center')
title(d,'d','Group-isolated evaluation');d.axis('off')
for y,t,sub in [(.84,'2 repeats × 5 outer folds','Same rows recur across repeats'),(.49,'Fit → calibration → test','59–60 → 20 → 19–20 components'),(.14,'3,472 prediction events','1,736 unique mixture records')]:
    d.text(.02,y,t,transform=d.transAxes,fontsize=8,fontweight='bold');d.text(.02,y-.12,sub,transform=d.transAxes,fontsize=7)
for ext in ['svg','pdf','png','tiff']:
    kwargs={'dpi':600,'pil_kwargs':{'compression':'tiff_lzw'}} if ext=='tiff' else {'dpi':300} if ext=='png' else {}
    fig.savefig(FIG/f'Fig1_data_and_evidence.{ext}',**kwargs)
plt.close(fig)
(ROOT/'qa/Fig1_presentation_contract.json').write_text(json.dumps(dict(width_mm=183,height_mm=118,source_files=['F1_sources.csv','F1_components.csv','F1_splits.csv'],changes='Text density and layout only; counts and group isolation unchanged',formats=['editable SVG','PDF Type42','600dpi LZW TIFF','300dpi PNG']),indent=2),encoding='utf-8')
print('Fig. 1 presentation exported; frozen source counts unchanged')
