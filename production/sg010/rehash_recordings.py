"""Independent re-hash of every canonical recording in the bank against recordings-catalog.json (handoff 2, Part A step 4).
Reads only. Writes one small receipt to the Seed Bank work folder; never touches the catalog or the media."""
from prepare import *
import datetime,time
CATALOG=REG/'recordings-catalog.json'
def main():
 cat=read(CATALOG);rows=[];t0=time.time();total=0
 for r in cat['records']:
  p=Path(r['canonical_path']);row=dict(recording_id=r['recording_id'],canonical_path=str(p))
  if not p.exists():row.update(status='MISSING')
  else:
   size=p.stat().st_size;h=hashlib.sha256()
   with p.open('rb') as f:
    for chunk in iter(lambda:f.read(1<<24),b''):h.update(chunk)
   digest=h.hexdigest();total+=size
   row.update(size=size,catalog_size=r['size'],sha256=digest,catalog_sha256=r['source_sha256'],
              status='OK' if digest==r['source_sha256'] and size==r['size'] else 'MISMATCH')
  rows.append(row);print(row['status'],r['recording_id'],p.name,flush=True)
 counts={s:sum(1 for x in rows if x['status']==s) for s in ['OK','MISMATCH','MISSING']}
 receipt=dict(catalog=str(CATALOG),catalog_sha256=sha(CATALOG),records=len(rows),bytes_read=total,seconds=round(time.time()-t0,1),
              verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='independent full SHA-256 read of every canonical file; compared to catalog source_sha256 and size',counts=counts,rows=rows)
 save(WORK/'recordings-rehash-receipt.json',receipt)
 print('RESULT',counts,f'{total/1e9:.3f} GB in {receipt["seconds"]}s')
 sys.exit(0 if counts['OK']==len(rows) else 1)
if __name__=='__main__':main()
