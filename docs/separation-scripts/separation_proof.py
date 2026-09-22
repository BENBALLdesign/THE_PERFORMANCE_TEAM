"""Step 4 of the separation: from the new checkout, run shelf_sg010 -> library_sg010 -> qa_sg010 against the installation.

Writes only into the Seed Bank work folder (stage, library, qa-separation-proof). The Part B QA record
qa-final/visual-review.json is never touched: qa_sg010 is pointed at a separate proof folder.
"""
import datetime
import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

CO = Path(r'C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM')
PROD = CO / 'production/sg010'
sys.path.insert(0, str(PROD))
import prepare  # noqa: E402

REPORT = CO / 'docs/SEPARATION-PROOF.json'
out = dict(schema='performance-team-separation-proof/1', started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
           checkout=str(CO), installation=str(prepare.BASE), work=str(prepare.WORK), python=sys.version.split()[0], steps=[])


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def tree(root, skip=()):
    root = Path(root)
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name not in skip}


def step(name, fn):
    t0 = time.time()
    row = dict(step=name)
    try:
        row.update(result=fn(), status='ok')
    except Exception as e:  # noqa: BLE001
        row.update(status='failed', error=repr(e)[:800], trace=traceback.format_exc()[-2500:])
    row['seconds'] = round(time.time() - t0, 1)
    out['steps'].append(row)
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(name, row['status'], row['seconds'], 's', flush=True)
    return row['status'] == 'ok'


W = prepare.WORK
before_stage = tree(W / 'stage')
before_pkg = tree(W / 'library' / prepare.REV) if (W / 'library' / prepare.REV).exists() else {}


def run_shelf():
    import shelf_sg010
    r = shelf_sg010.main()
    after = tree(W / 'stage')
    return dict(returned=str(r)[:400], stage_files=len(after), unchanged=sum(after.get(k) == v for k, v in before_stage.items()),
                changed=[k for k, v in before_stage.items() if after.get(k) != v][:40], new=[k for k in after if k not in before_stage][:40])


def run_library():
    import library_sg010
    library_sg010.main()
    pkg = W / 'library' / prepare.REV
    after = tree(pkg)
    published = prepare.BASE / 'Home Inspection Training/Library' / prepare.REV
    pub = tree(published)
    same = sorted(k for k in after if pub.get(k) == after[k])
    differ = sorted(k for k in after if k in pub and pub[k] != after[k])
    only_staged = sorted(k for k in after if k not in pub)
    only_published = sorted(k for k in pub if k not in after)
    return dict(staged_package=str(pkg), published_package=str(published), staged_files=len(after), published_files=len(pub),
                identical_to_published=same, differ_from_published=differ, only_staged=only_staged, only_published=only_published,
                unchanged_since_before=sum(after.get(k) == v for k, v in before_pkg.items()) if before_pkg else None,
                report=json.loads((W / 'library/staged-build-report.json').read_text(encoding='utf-8')).get('verify'))


def run_qa():
    import qa_sg010
    qa_sg010.QA = W / 'qa-separation-proof'
    qa_sg010.main()
    idx = json.loads((qa_sg010.QA / 'index.json').read_text(encoding='utf-8'))
    prior = json.loads((W / 'qa-final/index.json').read_text(encoding='utf-8'))
    def key(e):
        return (e.get('file'), tuple(e.get('pages', [])), e.get('mode'))
    return dict(folder=str(qa_sg010.QA), sheets=len(idx), prior_sheets=len(prior), same_index_entries=len({key(e) for e in idx} & {key(e) for e in prior}),
                qa_final_untouched=(W / 'qa-final/visual-review.json').exists())


ok = step('shelf_sg010.main', run_shelf)
if ok:
    ok = step('library_sg010.main', run_library)
if ok:
    step('qa_sg010.main (QA -> qa-separation-proof)', run_qa)
out['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('PROOF', [(s['step'], s['status']) for s in out['steps']])
