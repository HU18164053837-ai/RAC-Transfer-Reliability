"""Re-render frozen plotting data into a separate directory, without fits or new inference."""
from pathlib import Path
import subprocess,sys,os,json,time,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
    start=time.perf_counter();output=ROOT/'reproduced/figures';output.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(ROOT/'reproduced/.mplconfig'),RAC_FIGURE_OUTPUT=str(output))
    for name in ['plot_figures.py','plot_fig1_v02.py']:
        subprocess.run([sys.executable,str(ROOT/'phase4'/name)],env=env,cwd=ROOT,check=True)
    checked=[]
    for ref in sorted((ROOT/'figures').glob('*.png')):
        p=output/ref.name;a=np.asarray(Image.open(ref));b=np.asarray(Image.open(p));same=a.shape==b.shape and np.array_equal(a,b)
        checked.append(dict(figure=ref.name,dimensions=list(b.shape),pixel_identical=bool(same)))
        for ext in ['svg','pdf','tiff']:assert (output/(ref.stem+'.'+ext)).is_file()
    assert len(checked)==6
    result=dict(status='PASS' if all(x['pixel_identical'] for x in checked) else 'RENDERED_PLATFORM_VARIATION',figure_count=6,figures=checked,wall_seconds=time.perf_counter()-start,additional_fits=0,resampling=0,note='PDF/SVG timestamps may differ; frozen originals are never overwritten. Cross-platform fonts can change pixels.')
    (ROOT/'reproduced/figure_reproduction.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
