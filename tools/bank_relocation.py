"""Explicit, hash-verified relocation of bulk installation folders into the Seed Bank.

Ported from the 2026-09-21 backup-routing migration (BB_CODE/.scratch/home-inspection-bank-correction/migrate.py)
so the process lives with the Team and is repeatable from a spec instead of hand-edited constants.

    python tools/bank_relocation.py <spec.json> plan     # inventory + hash every planned file; pin the plan in the bank
    python tools/bank_relocation.py <spec.json> copy     # copy to the bank, verify every byte, journal progress (resumable)
    python tools/bank_relocation.py <spec.json> retire   # recheck both sides, unlink retired sources, leave pointers
    python tools/bank_relocation.py <spec.json> finish   # resolve every pointer, verify the library, record the routes
    python tools/bank_relocation.py <spec.json> status

The spec names groups: a source folder (relative to the installation), a target folder (relative to the bank's
home-inspection domain), a kind, and optional `keep` globs for files that are copied to the bank but stay in
Dropbox too (small issue records that readers expect beside the pointer). The plan is immutable once written.
Copy all bytes and verify before retiring any source. Retirement only unlinks exact planned files after
rechecking both hashes. Nothing here writes bulk into Dropbox, and nothing runs without the registered bank.
"""
from pathlib import Path
import datetime
import fnmatch
import hashlib
import json
import os
import shutil
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import team_paths  # noqa: E402
import home_inspection_storage as storage  # noqa: E402

MARKERS = {storage.POINTER, 'README - SEED BANK.md', 'Open in Seed Bank.lnk'}
LOCKS = {'.export.lock', '.intake.lock'}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_name(p.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    os.replace(temp, p)


def bounded(path, root):
    p = Path(path).resolve()
    r = Path(root).resolve()
    assert p.is_relative_to(r) and p != r, (p, r)
    return p


def files(root):
    for folder, dirs, names in os.walk(root):
        for d in dirs:
            p = Path(folder) / d
            assert not p.is_symlink() and not p.is_junction(), ('Unexpected directory redirect', p)
        for name in names:
            p = Path(folder) / name
            assert not p.is_symlink(), ('Unexpected file link', p)
            yield p


def kept(rel, patterns):
    return any(fnmatch.fnmatch(rel, pat) for pat in patterns)


class Migration:
    def __init__(self, spec_path):
        self.spec_path = Path(spec_path).resolve()
        self.spec = read(self.spec_path)
        assert self.spec['schema'] == 'performance-team-bank-relocation-spec/1', self.spec.get('schema')
        self.id = self.spec['migration']
        self.installation = team_paths.installation()
        self.domain = storage.domain_root()          # fails closed without the registered bank
        self.meta = self.domain / '_META' / self.id
        self.plan_path = self.meta / 'relocation-plan.json'
        self.docs = team_paths.CHECKOUT / 'docs/relocations'

    # ---------------------------------------------------------------- plan
    def plan(self):
        assert not self.plan_path.exists(), 'Preserve the existing plan: ' + str(self.plan_path)
        groups = []
        for g in self.spec['groups']:
            source = bounded(self.installation / g['source'], self.installation)
            target = bounded(self.domain / g['target'], self.domain)
            assert source.is_dir(), ('Missing source', source)
            assert not target.exists(), ('Destination already exists; review before merging', target)
            keep = g.get('keep', [])
            entries = []
            for p in sorted(files(source)):
                assert p.name not in LOCKS, ('Active or unresolved lock', p)
                assert p.name not in MARKERS, ('Source already carries a bank pointer', p)
                rel = p.relative_to(source).as_posix()
                stat = p.stat()
                h = sha(p)
                end = p.stat()
                assert (stat.st_size, stat.st_mtime_ns) == (end.st_size, end.st_mtime_ns), ('Changed while hashing', p)
                entries.append(dict(file=rel, bytes=stat.st_size, mtime_ns=stat.st_mtime_ns, sha256=h, keep=kept(rel, keep)))
            groups.append(dict(source=str(source), target=str(target), kind=g['kind'], keep=keep, files=entries))
            print('Inventoried', g['source'], len(entries), 'files', f"{sum(e['bytes'] for e in entries)/1e6:.1f} MB", flush=True)
        plan = dict(schema='home-inspection-bank-relocation/1', migration=self.id, created_at=now(), vault_id=storage.VAULT_ID,
                    spec=str(self.spec_path), spec_sha256=sha(self.spec_path), installation=str(self.installation),
                    purpose=self.spec.get('purpose'), preserved=self.spec.get('preserved'), groups=groups,
                    file_count=sum(len(g['files']) for g in groups),
                    bytes=sum(f['bytes'] for g in groups for f in g['files']),
                    kept_count=sum(f['keep'] for g in groups for f in g['files']))
        save(self.plan_path, plan)
        summary = {k: v for k, v in plan.items() if k != 'groups'}
        summary['groups'] = [dict(source=g['source'], target=g['target'], kind=g['kind'], files=len(g['files']),
                                  bytes=sum(f['bytes'] for f in g['files'])) for g in groups]
        save(self.meta / 'plan-summary.json', summary)
        save(self.docs / (self.id + '-plan-summary.json'), summary)
        print(json.dumps({k: summary[k] for k in ['migration', 'file_count', 'bytes', 'kept_count']}), flush=True)

    # ---------------------------------------------------------------- copy
    def copy(self):
        plan = read(self.plan_path)
        journal = self.meta / 'copy-journal.jsonl'
        done_groups = set()
        if journal.exists():
            for line in journal.read_text(encoding='utf8').splitlines():
                done_groups.add(json.loads(line)['source'])
        copied = 0
        for index, group in enumerate(plan['groups']):
            src = Path(group['source'])
            dst = bounded(group['target'], self.domain)
            if str(src) in done_groups:
                copied += len(group['files'])
                continue
            current = {p.relative_to(src).as_posix() for p in files(src)} - MARKERS
            assert current == {r['file'] for r in group['files']}, ('Source membership changed', src, sorted(current ^ {r['file'] for r in group['files']})[:5])
            dst.mkdir(parents=True, exist_ok=True)
            for row in group['files']:
                p = bounded(src / row['file'], src)
                q = bounded(dst / row['file'], dst)
                assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], ('Source changed since plan', p)
                if q.exists():
                    assert sha(q) == row['sha256'], ('Unrecognized destination', q)
                else:
                    q.parent.mkdir(parents=True, exist_ok=True)
                    tmp = q.with_name(q.name + '.seed-copy.tmp')
                    assert not tmp.exists(), tmp
                    shutil.copy2(p, tmp)
                    assert sha(tmp) == row['sha256'], tmp
                    os.replace(tmp, q)
                copied += 1
            with journal.open('a', encoding='utf8') as f:
                f.write(json.dumps(dict(at=now(), group=index, source=str(src), target=str(dst), verified_files=len(group['files']))) + '\n')
            save(self.meta / 'progress.json', dict(phase='copy verified', groups_copied=index + 1, groups_total=len(plan['groups']),
                                                   files_copied=copied, files_total=plan['file_count'], at=now()))
            print('Verified bank copy', src.name, copied, '/', plan['file_count'], flush=True)
        save(self.meta / 'copy-verification.json', dict(status='all bank copies verified', files=copied, bytes=plan['bytes'],
                                                        plan_sha256=sha(self.plan_path), at=now()))
        print('COPY VERIFIED', copied, 'files', flush=True)

    # ---------------------------------------------------------------- retire
    def retire(self):
        plan = read(self.plan_path)
        verification = read(self.meta / 'copy-verification.json')
        assert sha(self.plan_path) == verification['plan_sha256']
        assert verification['files'] == plan['file_count']
        journal = self.meta / 'retirement-journal.jsonl'
        intents = set()
        if journal.exists():
            for line in journal.read_text(encoding='utf8').splitlines():
                row = json.loads(line)
                assert row['plan_sha256'] == verification['plan_sha256']
                intents.add((row['group'], row['file']))
        # Recheck every source and destination before the first unlink.
        for index, group in enumerate(plan['groups']):
            src = Path(group['source'])
            dst = Path(group['target'])
            existing = {p.relative_to(src).as_posix() for p in files(src)}
            if existing & MARKERS:
                pointer = read(src / storage.POINTER)
                assert pointer['migration'] == self.id and Path(pointer['bank_root']) == dst
            actual = existing - MARKERS
            expected = {r['file'] for r in group['files']}
            retired = {r['file'] for r in group['files'] if not r['keep']}
            assert not actual - expected, ('New unplanned files', src, sorted(actual - expected)[:5])
            assert all((index, p) in intents for p in (retired - actual)), ('Missing unretired file', src)
            for row in group['files']:
                assert sha(dst / row['file']) == row['sha256'], ('Bank copy changed', dst / row['file'])
                if row['file'] in actual:
                    assert sha(src / row['file']) == row['sha256'], ('Source changed', src / row['file'])
        done = 0
        for index, group in enumerate(plan['groups']):
            src = bounded(group['source'], self.installation)
            dst = bounded(group['target'], self.domain)
            for row in group['files']:
                p = bounded(src / row['file'], src)
                q = bounded(dst / row['file'], dst)
                assert sha(q) == row['sha256']
                if row['keep']:
                    assert p.exists() and sha(p) == row['sha256'], ('Kept file missing or changed', p)
                    continue
                if p.exists():
                    assert sha(p) == row['sha256']
                    with journal.open('a', encoding='utf8') as f:   # durable intent: safe resume between unlink and receipt
                        f.write(json.dumps(dict(plan_sha256=verification['plan_sha256'], group=index, file=row['file'])) + '\n')
                        f.flush()
                        os.fsync(f.fileno())
                    for attempt in range(12):
                        try:
                            p.unlink()
                            break
                        except PermissionError:
                            if attempt == 11:
                                raise
                            time.sleep(.25 * (attempt + 1))
                else:
                    assert (index, row['file']) in intents
                done += 1
            # Empty folders only; the source root stays as a small landing point (kept files stay in place).
            for folder, dirs, names in os.walk(src, topdown=False):
                p = Path(folder)
                if p != src and not any(p.iterdir()):
                    bounded(p, src)
                    p.rmdir()
            pointer = dict(schema='seed-bank-location/1', vault_id=storage.VAULT_ID, original_root=str(src), bank_root=str(dst),
                           migration=self.id, kind=group['kind'], files=len(group['files']),
                           bytes=sum(f['bytes'] for f in group['files']),
                           kept_in_place=[f['file'] for f in group['files'] if f['keep']] if group['keep'] else [],
                           plan=str(self.plan_path), status='bank copy hash-verified; Dropbox payload retired', relocated_at=now())
            save(src / storage.POINTER, pointer)
            (src / 'README - SEED BANK.md').write_text(
                '# Stored in the Seed Bank\n\nThe verified files now live at:\n\n' + str(dst) + '\n\n'
                'Use the JSON location record (SEED BANK LOCATION.json) or tools/home_inspection_storage.py resolve(<old path>) '
                'in the THE_PERFORMANCE_TEAM checkout. Keep bulk writes at the bank location. This folder holds pointers'
                + (' and the small records listed under kept_in_place' if group['keep'] else '') + '; no folder junction is used.\n',
                encoding='utf8')
            print('Retired verified Dropbox payload', src.name, flush=True)
        save(self.meta / 'retirement-receipt.json', dict(status='payloads relocated; landing pointers present', files=done,
                                                         bytes=plan['bytes'], groups=len(plan['groups']), at=now()))
        print('RETIRED', done, 'files', flush=True)

    # ---------------------------------------------------------------- finish
    def finish(self):
        plan = read(self.plan_path)
        receipt = read(self.meta / 'retirement-receipt.json')
        assert receipt['files'] == plan['file_count'] and receipt['bytes'] == plan['bytes']
        assert not (self.meta / 'storage-completion.json').exists(), 'Already completed; review before replay'
        routes = []
        for group in plan['groups']:
            old, target = Path(group['source']), Path(group['target'])
            pointer = read(old / storage.POINTER)
            assert pointer['migration'] == self.id and Path(pointer['bank_root']) == target
            remaining = {p.relative_to(old).as_posix() for p in files(old)}
            kept_files = {f['file'] for f in group['files'] if f['keep']}
            assert remaining <= MARKERS | kept_files, ('Unexpected files left beside the pointer', old, sorted(remaining - MARKERS - kept_files)[:5])
            assert storage.resolve(old) == target.resolve()
            for row in group['files']:
                if not row['keep']:
                    assert storage.resolve(old / row['file']) == (target / row['file']).resolve()
            assert {p.relative_to(target).as_posix() for p in files(target)} == {r['file'] for r in group['files']}
            routes.append(dict(original_root=str(old), bank_root=str(target), kind=group['kind'], files=len(group['files']),
                               bytes=sum(f['bytes'] for f in group['files']), kept_in_place=sorted(kept_files)))
        import home_inspection_library as library
        current = read(team_paths.registry('Library/CURRENT.json'))
        package = self.installation / 'Home Inspection Training/Library' / current['package']
        status = library.verify(package, self.installation)
        assert status['status'] == 'current', status
        locations_path = self.installation / 'Home Inspection Training/Library/STORAGE LOCATIONS.json'
        locations = read(locations_path) if locations_path.exists() else dict(schema='home-inspection-storage-locations/1', roots=[])
        locations.setdefault('migrations', []).append(dict(migration=self.id, at=now(), manifest=str(self.plan_path), purpose=plan.get('purpose')))
        locations.setdefault('roots', []).extend(routes)
        locations.update(resolver=str(HERE / 'home_inspection_storage.py'), bank_domain=str(self.domain), updated_at=now())
        save(locations_path, locations)
        result = dict(status='complete', migration=self.id, at=now(), relocated_files=receipt['files'], relocated_bytes=receipt['bytes'],
                      landing_roots=len(routes), current_library=status['status'], bank_domain=str(self.domain),
                      dropbox_sync_health='not established; Dropbox was not restarted')
        save(self.meta / 'storage-completion.json', result)
        save(self.docs / (self.id + '-receipt.json'), dict(result, routes=routes))
        print(json.dumps(result), flush=True)

    def status(self):
        out = dict(migration=self.id, meta=str(self.meta))
        for name in ['relocation-plan.json', 'copy-verification.json', 'retirement-receipt.json', 'storage-completion.json', 'progress.json']:
            p = self.meta / name
            out[name] = (read(p) if name != 'relocation-plan.json' else 'present') if p.exists() else None
        print(json.dumps(out, indent=1))


if __name__ == '__main__':
    m = Migration(sys.argv[1])
    getattr(m, sys.argv[2])()
