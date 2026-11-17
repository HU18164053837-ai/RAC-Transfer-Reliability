"""Check published bytes without network, models or statistical resampling."""
from pathlib import Path
import csv,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    with (ROOT/'checksums/files_sha256.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    for r in rows:
        p=ROOT/r['path'];assert p.is_file(),r['path'];assert sha(p)==r['sha256'],r['path']
    out=ROOT/'reproduced';out.mkdir(exist_ok=True)
    (out/'integrity.json').write_text(json.dumps(dict(status='PASS',verified_files=len(rows),additional_fits=0,resampling=0),indent=2),encoding='utf-8')
    print('PASS SHA-256:',len(rows),'files')
if __name__=='__main__':main()
