from pathlib import Path
import os,sys,hashlib,json
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;P1=ROOT.parent;P2=P1/'phase2';OLD=P1/'data/legacy_context'
if os.environ.get('RAC_ML_DEPS'):sys.path.insert(0,os.environ['RAC_ML_DEPS'])
import numpy as np
import pandas as pd
OUT=ROOT/'results';DATA=ROOT/'data';EVID=ROOT/'evidence';REPORT=ROOT/'reports'
for p in (OUT,DATA,EVID,REPORT):p.mkdir(exist_ok=True,parents=True)
REFS=[36,82,109,8,9,52,77]
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(d,name):pd.DataFrame(d).to_csv(OUT/name,index=False,encoding='utf-8-sig')
def snapshot():
    files=[]
    for base,dirs,fs in os.walk(P1):
        dirs[:]=[d for d in dirs if d not in ['phase3','__pycache__','.mplconfig']]
        for f in fs:files.append((Path(base)/f,P1,'prior_stages'))
    for sub in ['data','src','manuscript','results','reports','deliverables','submission_template_final']:
        for base,dirs,fs in os.walk(OLD/sub):
            for f in fs:files.append((Path(base)/f,OLD,'old_RAC956'))
    files.append((OLD/'PROJECT_STATUS.md',OLD,'old_RAC956'))
    return pd.DataFrame([dict(scope=scope,path=p.relative_to(root).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p,root,scope in sorted(files,key=lambda x:(x[2],str(x[0])))])

# Publication packaging: resolve shared immutable inputs once.
INPUT_PATHS = {'predictions.csv': 'phase2/results/predictions.csv', 'selection_thresholds.csv': 'phase2/results/selection_thresholds.csv', 'random_baseline_100.csv': 'phase2/results/random_baseline_100.csv', 'phase2_interval_metrics.csv': 'phase2/results/interval_metrics.csv', 'new_references.csv': 'data/derived/new_references.csv', 'new_frozen.csv': 'phase2/data/new_frozen.csv', 'old_input.csv': 'data/derived/old_modeling_copy.csv', 'old_all980_classification.csv': 'data/raw/legacy/classification_all_980.csv'}
def data_file(name):
    return P1 / INPUT_PATHS[name] if name in INPUT_PATHS else DATA/name
