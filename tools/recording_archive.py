"""Apply a hash-pinned recordings archive plan with a restartable receipt.

Only individual files enumerated in the plan may be moved or removed. New bank
copies are read back and verified. Same-volume renames preserve the already
hashed file's identity, length and timestamp; they do not rewrite media bytes.
The full original-path alias list lives in the catalog, including duplicates.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,time
from home_inspection_storage import bank_root,VAULT_ID

import sys;sys.path.insert(0,str(Path(__file__).resolve().parent))
import team_paths
_installation=team_paths.installation(strict=False)
MEDIA=(_installation/'Sound Recordings') if _installation else None   # None until installation.json names the installation
CATALOG='recordings-catalog.json'
MIRROR=team_paths.registry(CATALOG)   # the small tracked catalog copy; the bank copy stays authoritative for media

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp')
    with tmp.open('w',encoding='utf8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    # Dropbox/indexers briefly hold synced files open; retry the atomic replace.
    for attempt in range(40):
        try:tmp.replace(p);return
        except PermissionError:
            if attempt==39:raise
            time.sleep(0.25*(1+attempt%8))
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def confined(path,roots):
    raw=Path(path).absolute();resolved=raw.resolve()
    if not any(resolved.is_relative_to(root.resolve()) and resolved!=root.resolve() for root in roots):raise ValueError('Path outside authorized roots: '+str(path))
    if resolved!=raw:raise ValueError('Symlink/junction path not allowed: '+str(path))
    return resolved
def fingerprint(p,record):
    a=p.stat()
    if a.st_size!=record['size'] or digest(p)!=record['source_sha256']:raise ValueError('Hash/size mismatch: '+str(p))
    b=p.stat()
    if (a.st_size,a.st_mtime_ns)!=(b.st_size,b.st_mtime_ns):raise ValueError('File changed while verifying: '+str(p))
    return (b.st_size,b.st_mtime_ns)
def verified_inventory_stamp(p,record):
    """Reuse the completed full hash only while its exact path metadata agrees."""
    st=p.stat()
    observed=next((a for a in record.get('aliases',[]) if a.get('kind')=='observed original path' and Path(a['path'])==p),None)
    if observed and (st.st_size,st.st_mtime_ns)==(observed.get('size'),observed.get('mtime_ns')):
        return (st.st_size,st.st_mtime_ns)
    return fingerprint(p,record)
def validate(plan):
    bank=bank_root()/'RECORDINGS'
    if plan['vault_id']!=VAULT_ID or Path(plan['bank_root']).resolve()!=bank.resolve():raise ValueError('Wrong catalog bank')
    destinations=set();ids=set();sources=set()
    for r in plan['records']:
        if r['recording_id'] in ids:raise ValueError('Duplicate recording ID')
        ids.add(r['recording_id'])
        if len(r['source_sha256'])!=64 or r['recording_id']!='R'+r['source_sha256'][:12]:raise ValueError('Invalid content identity')
        target=confined(r['canonical_path'],[bank])
        if target!=confined(bank/r['bank_relative_path'],[bank]):raise ValueError('Destination disagreement')
        if str(target).casefold() in destinations:raise ValueError('Duplicate destination')
        destinations.add(str(target).casefold())
        for src in r['observed_paths']:
            p=confined(src,[r for r in (MEDIA,bank) if r])
            if str(p).casefold() in sources:raise ValueError('Source listed twice')
            sources.add(str(p).casefold())
    if sources & destinations:raise ValueError('Source/destination overlap')
    return bank
def apply(plan_path,busy_lock=None,jobs_dir=None):
    plan=read(plan_path);bank=validate(plan)
    if busy_lock and Path(busy_lock).exists():raise RuntimeError('Extraction queue is still using original paths; wait for it to finish')
    if jobs_dir:
        original_paths={str(Path(p)).casefold() for r in plan['records'] for p in r['observed_paths']}
        for job_file in Path(jobs_dir).glob('*-job.json'):
            job=read(job_file)
            if job.get('state')=='running' and any(str(Path(a)).casefold() in original_paths for a in job.get('command',[])):
                raise RuntimeError('An active extraction still uses an original path: '+str(job_file))
    transaction=bank/'_catalog/migrations/2026-09-21'
    transaction.mkdir(parents=True,exist_ok=True)
    archived_plan=transaction/'plan.json'
    if archived_plan.exists():
        if read(archived_plan)!=plan:raise RuntimeError('This transaction already has a different immutable plan')
    else:save(archived_plan,plan)
    eventfile=transaction/'events.jsonl'
    def event(action,**fields):
        with eventfile.open('a',encoding='utf8') as f:
            f.write(json.dumps(dict(at=now(),action=action,**fields),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    catalog=dict(plan);catalog['status']='migration in progress'
    def publish():
        catalog['updated_at']=now();save(bank/CATALOG,catalog);save(MIRROR,catalog)
    publish()
    lock=transaction/'migration.lock'
    with lock.open('x',encoding='utf8') as f:json.dump(dict(pid=os.getpid(),started_at=now()),f)
    try:
        for i,r in enumerate(catalog['records']):
            dst=confined(r['canonical_path'],[bank]);dst.parent.mkdir(parents=True,exist_ok=True)
            originals=[confined(p,[r for r in (MEDIA,bank) if r]) for p in r['observed_paths']]
            renamed_identity=None;verified_copy=False
            if not dst.exists():
                candidates=sorted([p for p in originals if p.exists()],key=lambda p:(not p.is_relative_to(bank),str(p)))
                if not candidates:raise FileNotFoundError('No source or canonical file: '+r['recording_id'])
                src=candidates[0];stamp=verified_inventory_stamp(src,r)
                if src.is_relative_to(bank):
                    event('rename_intent',recording_id=r['recording_id'],source=str(src),destination=str(dst),sha256=r['source_sha256'])
                    if (src.stat().st_size,src.stat().st_mtime_ns)!=stamp:raise ValueError('Source changed before rename')
                    renamed_identity=src.stat().st_ino
                    src.rename(dst)
                    after=dst.stat()
                    if (after.st_size,after.st_mtime_ns)!=stamp or after.st_ino!=renamed_identity:raise ValueError('File identity changed during atomic bank rename')
                else:
                    partial=dst.with_suffix(dst.suffix+'.partial')
                    if partial.exists():
                        fingerprint(partial,r)
                    else:
                        event('copy_intent',recording_id=r['recording_id'],source=str(src),destination=str(dst),sha256=r['source_sha256'])
                        with src.open('rb') as fi,partial.open('xb') as fo:
                            shutil.copyfileobj(fi,fo,16*1024*1024);fo.flush();os.fsync(fo.fileno())
                        if (src.stat().st_size,src.stat().st_mtime_ns)!=stamp:raise ValueError('Source changed while copying')
                        fingerprint(partial,r);shutil.copystat(src,partial)
                    partial_identity=partial.stat().st_ino
                    partial.rename(dst)
                    if dst.stat().st_ino!=partial_identity or dst.stat().st_size!=r['size']:raise ValueError('Verified bank copy changed during promotion')
                    verified_copy=True
            if renamed_identity is None and not verified_copy:fingerprint(dst,r)
            method='inventory SHA-256 plus unchanged file identity, size and timestamp across atomic same-volume rename' if renamed_identity is not None else 'full SHA-256 readback of bank copy and unchanged file identity at promotion' if verified_copy else 'full SHA-256 readback of canonical file'
            event('canonical_verified',recording_id=r['recording_id'],destination=str(dst),sha256=r['source_sha256'],size=r['size'],method=method)
            r.update(archive_status='canonical verified; retiring old paths',canonical_verified_at=now())
            r['archive_verification_method']=method
            publish()
            for src in originals:
                if not src.exists():continue
                stamp=verified_inventory_stamp(src,r)
                if dst.stat().st_size!=r['size']:raise ValueError('Canonical changed before retirement')
                event('retire_verified_alias',recording_id=r['recording_id'],source=str(src),destination=str(dst),sha256=r['source_sha256'])
                if (src.stat().st_size,src.stat().st_mtime_ns)!=stamp:raise ValueError('Source changed before retirement')
                src.unlink()
            r['archive_status']='archived and verified';publish()
            print(f'{i+1}/{len(catalog["records"])} {r["recording_id"]} {r["title"]}',flush=True)
        catalog['status']='complete';catalog['completed_at']=now();publish()
        save(transaction/'receipt.json',dict(status='complete',completed_at=now(),catalog_sha256=digest(bank/CATALOG),records=len(catalog['records']),originals=sum(r['role']=='original' for r in catalog['records']),observed_files=sum(len(r['observed_paths']) for r in catalog['records']),summary=plan['summary']))
    finally:lock.unlink(missing_ok=True)
    return catalog
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('plan');ap.add_argument('--apply',action='store_true');ap.add_argument('--busy-lock');ap.add_argument('--jobs-dir');a=ap.parse_args()
    if a.apply:apply(a.plan,a.busy_lock,a.jobs_dir)
    else:
        p=read(a.plan);validate(p);print(json.dumps(p['summary'],indent=2))
if __name__=='__main__':main()
