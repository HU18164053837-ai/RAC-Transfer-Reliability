from pathlib import Path
import os,sys,hashlib,json
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;P1=ROOT.parent;OLD=P1/'data/legacy_context'
if os.environ.get('RAC_ML_DEPS'):sys.path.insert(0,os.environ['RAC_ML_DEPS'])
import numpy as np
import pandas as pd
OUT=ROOT/'results';DATA=ROOT/'data';FIG=ROOT/'figures'
for p in (OUT,DATA,FIG,ROOT/'reports'):p.mkdir(parents=True,exist_ok=True)
FULL=['density','crushing','absorption','cement','fly_ash','slag','water','sand','coarse','rar','sp']
CORE=['cement','fly_ash','slag','water','sand','coarse'];RECIPE=CORE+['rar','sp']
SEEDS=[2026110801,2026110802];RETENTIONS=[1.,.9,.8,.7,.5];ALPHAS=[.2,.1,.05]
METHODS=['pooled','source_balanced','adaptive','group_max']
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(d,name):pd.DataFrame(d).to_csv(OUT/name,index=False,encoding='utf-8-sig')
def stable_uniform(key):return int(hashlib.sha256(str(key).encode()).hexdigest()[:13],16)/16**13
def read_new():
    d=pd.read_csv(DATA/'new_input.csv');d['dataset']='new';d['record_key']='new:'+d.record_id.astype(str)
    return d

# Publication packaging: resolve shared immutable inputs once.
INPUT_PATHS = {'new_input.csv': 'data/derived/compressive_strength.csv', 'new_references.csv': 'data/derived/new_references.csv', 'old_input.csv': 'data/derived/old_modeling_copy.csv', 'phase1_groups.csv': 'results/new_groups.csv', 'phase1_split_ledger.csv': 'results/split_ledger.csv', 'transfer_groups.csv': 'results/transfer_groups.csv', 'database_README.md': 'data/raw/README.md'}
def data_file(name):
    return P1 / INPUT_PATHS[name] if name in INPUT_PATHS else DATA/name
