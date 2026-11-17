from common import *
import shutil
def main():
    before=OUT/'protected_before.csv'
    if not before.exists():snapshot().to_csv(before,index=False,encoding='utf-8-sig')
    pairs=[(P2/'results/predictions.csv','predictions.csv'),(P2/'results/selection_thresholds.csv','selection_thresholds.csv'),(P2/'results/random_baseline_100.csv','random_baseline_100.csv'),(P2/'results/interval_metrics.csv','phase2_interval_metrics.csv'),(P1/'data/derived/new_references.csv','new_references.csv'),(P2/'data/new_frozen.csv','new_frozen.csv'),(P2/'data/old_input.csv','old_input.csv'),(P1/'data/raw/legacy/classification_all_980.csv','old_all980_classification.csv')]
    for src,name in pairs:
        dest=data_file(name)
        if not dest.exists():shutil.copyfile(src,dest)
        assert sha(src)==sha(dest)
    refs=pd.read_csv(data_file('new_references.csv'));d=pd.read_csv(data_file('new_frozen.csv'))
    focus=d[d.ref_no.isin(REFS)].merge(refs[['ref_no','citation','doi']],on='ref_no',how='left',validate='many_to_one')
    focus.to_csv(data_file('focus_records.csv'),index=False,encoding='utf-8-sig')
    save([dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(DATA.glob('*.csv'))],'input_sha256.csv')
    (OUT/'plan_sha256.json').write_text(json.dumps(dict(file='PLAN_LOCKED.md',sha256=sha(ROOT/'PLAN_LOCKED.md')),indent=2),encoding='utf-8')
    print('Frozen focus rows',len(focus),'sources',focus.source_id.nunique(),flush=True)
if __name__=='__main__':main()
