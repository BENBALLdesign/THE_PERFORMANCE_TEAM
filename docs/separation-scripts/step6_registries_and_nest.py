"""Step 6 of the separation: retire the installation's registry copies, then nest the installation under the checkout.

Ben rulings 2026-09-22: registries move to the checkout with an installation pointer; the installation
"THE PERFORMANCE TEAM" is part of "THE_PERFORMANCE_TEAM". Receipted, fail-closed, no bulk copy: the
installation is renamed in place (same volume), then every Seed Bank pointer's original_root is rewritten.
"""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CO = Path(r'C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM')
OLD = Path(r'C:\Users\benja\Dropbox\THE PERFORMANCE TEAM')
NEW = CO / 'THE PERFORMANCE TEAM'
REG = CO / 'registries'
REGISTRY_FILES = {
    'STUDY-GUIDE-EDITIONS.json': 'STUDY-GUIDE-EDITIONS.json',
    'APPENDIX-VERSIONS.json': 'APPENDIX-VERSIONS.json',
    'Sound Recordings/recordings-catalog.json': 'recordings-catalog.json',
    'Sound Recordings/recordings-catalog.csv': 'recordings-catalog.csv',
    'Sound Recordings/recording-aliases.csv': 'recording-aliases.csv',
    'Home Inspection Training/Library/CURRENT.json': 'Library/CURRENT.json',
}
POINTER = 'SEED BANK LOCATION.json'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def save(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


receipt = dict(schema='performance-team-separation-step6/1', at=now(), checkout=str(CO), old_installation=str(OLD), new_installation=str(NEW), steps=[])
assert OLD.is_dir() and not NEW.exists(), (OLD, NEW)
assert subprocess.run(['git', '-C', str(CO), 'status', '--short'], capture_output=True, text=True).stdout.strip() == '', 'checkout not clean'

# 1. Registries: every installation copy must equal the checkout copy, then it is retired.
# Rerun-safe: copies retired by an earlier run are already recorded in the installation's pointer; keep those records.
prior_pointer = OLD / 'REGISTRIES.json'
retired = list(read(prior_pointer)['files']) if prior_pointer.is_file() else []
prior_receipt = CO / 'docs/SEPARATION-STEP6-RECEIPT.json'
if prior_receipt.is_file():
    receipt['prior_attempt'] = read(prior_receipt)
for rel, reg in REGISTRY_FILES.items():
    src, dst = OLD / rel, REG / reg
    assert dst.is_file(), dst
    if src.exists():
        assert sha(src) == sha(dst), ('installation copy differs from the checkout registry', rel)
        src.unlink()
        retired.append(dict(installation_path=rel, registry=reg, sha256=sha(dst)))
pointer = dict(schema='performance-team-registries-location/1', at=now(),
               note='The registries moved to the THE_PERFORMANCE_TEAM checkout (Ben ruling 2026-09-22). Readers resolve them with tools/team_paths.registry(); the installation holds reading material only.',
               registries=str(REG), files=retired)
save(OLD / 'REGISTRIES.json', pointer)
receipt['steps'].append(dict(step='registries retired', files=retired, pointer=str(OLD / 'REGISTRIES.json')))
print('registries retired:', len(retired), flush=True)

# 2. Nest: rename in place.
moved_children = None
try:
    os.rename(OLD, NEW)
except PermissionError:
    # The old root is some process's working directory (this session's harness); move its children instead
    # and leave the empty shell with a pointer until the folder is released.
    NEW.mkdir()
    moved_children = []
    for child in sorted(OLD.iterdir()):
        for attempt in range(20):
            try:
                os.rename(child, NEW / child.name)
                break
            except PermissionError:
                if attempt == 19:
                    raise
                time.sleep(1.5)
        moved_children.append(child.name)
    (OLD / 'MOVED - SEE THE_PERFORMANCE_TEAM.md').write_text('# Moved\n\nThe installation now lives at\n\n' + str(NEW) + '\n\nThis empty folder can be deleted once nothing holds it open.\n', encoding='utf-8')
assert NEW.is_dir()
receipt['steps'].append(dict(step='installation renamed' if moved_children is None else 'installation children moved (old root held open; shell left with a pointer)',
                             from_=str(OLD), to=str(NEW), children=moved_children))
print('renamed', flush=True)

# 3. Pointers: rewrite original_root, keep the legacy value.
rewritten = []
for p in sorted(NEW.rglob(POINTER)):
    d = read(p)
    orig = Path(d['original_root'])
    assert orig.is_relative_to(OLD), (p, orig)
    d['legacy_original_root'] = str(orig)
    d['original_root'] = str(NEW / orig.relative_to(OLD))
    d['nested_at'] = now()
    assert Path(d['original_root']).resolve() == p.parent.resolve(), (p, d['original_root'])
    save(p, d)
    rewritten.append(str(p.relative_to(NEW)))
receipt['steps'].append(dict(step='pointers rewritten', count=len(rewritten), pointers=rewritten))
print('pointers rewritten:', len(rewritten), flush=True)

# 4. installation.json
inst = read(CO / 'installation.json')
inst['installation_root'] = str(NEW).replace('\\', '/')
inst.setdefault('legacy_installation_roots', []).append(str(OLD).replace('\\', '/'))
save(CO / 'installation.json', inst)
ex = read(CO / 'installation.example.json')
ex['legacy_installation_roots'] = []
ex['note'] += ' legacy_installation_roots lists earlier installation paths so records pinned before a move still verify.'
save(CO / 'installation.example.json', ex)

# 5. publish_sg010: plans pinned before the move name the old root.
pub = CO / 'production/sg010/publish_sg010.py'
s = open(pub, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
old_a = "def backup_rel(t):" + nl + "    t=Path(t);return Path(REGDIR)/t.relative_to(REG) if t.is_relative_to(REG) else t.relative_to(TEAM)" + nl
new_a = ("def rebase(t):" + nl +
         "    \"\"\"Map a path recorded before the installation moved (installation.json legacy_installation_roots) onto the current root.\"\"\"" + nl +
         "    t=Path(t)" + nl +
         "    for legacy in team_paths.settings().get('legacy_installation_roots',[]):" + nl +
         "        legacy=Path(legacy)" + nl +
         "        if t.is_relative_to(legacy):return TEAM/t.relative_to(legacy)" + nl +
         "    return t" + nl +
         "def backup_rel(t):" + nl +
         "    t=rebase(t);return Path(REGDIR)/t.relative_to(REG) if t.is_relative_to(REG) else t.relative_to(TEAM)" + nl)
assert s.count(old_a) == 1, 'backup_rel anchor'
s = s.replace(old_a, new_a)
old_b = "    t=Path(t)" + nl + "    if t.parent==TEAM and t.name in ROOT_REGISTRIES:return REG/t.name" + nl
new_b = "    t=rebase(t)" + nl + "    if t.parent==TEAM and t.name in ROOT_REGISTRIES:return REG/t.name" + nl
assert s.count(old_b) == 1, 'live_path anchor'
s = s.replace(old_b, new_b)
old_c = "    for r in plan['removals']:assert not Path(r['target']).exists(),r['target']" + nl
new_c = "    for r in plan['removals']:assert not rebase(r['target']).exists(),r['target']" + nl
assert s.count(old_c) == 1, 'removals anchor'
s = s.replace(old_c, new_c)
open(pub, 'w', encoding='utf-8', newline='').write(s)
receipt['steps'].append(dict(step='publish_sg010 rebase helper added', file=str(pub.relative_to(CO)), sha256=sha(pub)))

# 6. Verify.
sys.path.insert(0, str(CO / 'tools'))
import team_paths  # noqa: E402
assert team_paths.installation() == NEW
import home_inspection_storage as storage  # noqa: E402
for rel in rewritten:
    d = read(NEW / rel)
    assert storage.resolve(Path(d['original_root'])) == Path(d['bank_root']).resolve(), rel
import home_inspection_library as lib  # noqa: E402
cur = read(REG / 'Library/CURRENT.json')
status = lib.verify(NEW / 'Home Inspection Training/Library' / cur['package'], NEW)
assert status['status'] == 'current', status
receipt['steps'].append(dict(step='verified', pointers_resolve=len(rewritten), library=status['status']))
save(CO / 'docs/SEPARATION-STEP6-RECEIPT.json', receipt)
print(json.dumps(dict(status='step 6 complete', registries=len(retired), pointers=len(rewritten), library=status['status'], installation=str(NEW))), flush=True)
