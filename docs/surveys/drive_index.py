"""Metadata index of D:, F: and the heavy Dropbox roots, then redundancy candidates by (name, size).

Stat only; no hashing. Output: per-root folder totals (2 levels) and cross-root duplicate candidates grouped
by the folder pairs that share them, so the heavy overlaps show as a few lines instead of 300k rows.
"""
import collections
import json
import os
import sys
import time

ROOTS = {
    'D': r'D:\\',
    'F': r'F:\\',
    'DBX-ABSTRACTION': r'C:\Users\benja\Dropbox\ABSTRACTION nft',
    'DBX-BB_SEED': r'C:\Users\benja\Dropbox\BB_SEED',
    'DBX-TEAM': r'C:\Users\benja\Dropbox\THE PERFORMANCE TEAM',
}
SKIP = {'$RECYCLE.BIN', 'System Volume Information', '.venv', '__pycache__', 'node_modules', '.git', '_runtime'}
OUT = sys.argv[1]

index = {}          # (name, size) -> list of (root, relpath)
totals = {}
for label, root in ROOTS.items():
    t0 = time.time()
    lvl = collections.Counter(); n = collections.Counter(); files = 0; total = 0
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP]
        rel = os.path.relpath(dp, root)
        parts = [] if rel == '.' else rel.split(os.sep)
        for f in fn:
            try:
                s = os.stat(os.path.join(dp, f)).st_size
            except OSError:
                continue
            files += 1; total += s
            k = '/'.join(parts[:2]) if parts else '(root)'
            lvl[k] += s; n[k] += 1
            if s >= 65536:   # small files are too ambiguous for name+size matching
                index.setdefault((f, s), []).append((label, '/'.join(parts)))
    totals[label] = dict(root=root, bytes=total, files=files, seconds=round(time.time() - t0, 1),
                         level2=[dict(path=k, bytes=v, files=n[k]) for k, v in lvl.most_common(40)])
    print('INDEXED', label, files, total, totals[label]['seconds'], flush=True)

# Redundancy: same (name,size) present under two different (root, top-level folder) locations.
pairs = collections.Counter(); pair_files = collections.Counter(); samples = {}
for key, locs in index.items():
    if len(locs) < 2:
        continue
    tops = sorted({(lab, rel.split('/')[0] if rel else '(root)') for lab, rel in locs})
    if len(tops) < 2:
        continue
    for i in range(len(tops)):
        for j in range(i + 1, len(tops)):
            p = (tops[i], tops[j])
            pairs[p] += key[1]; pair_files[p] += 1
            samples.setdefault(p, []).append(dict(name=key[0], bytes=key[1], where=[f'{l}:{r}' for l, r in locs][:4]))
out = dict(roots=totals, redundancy=[dict(a=f'{a[0]}:{a[1]}', b=f'{b[0]}:{b[1]}', bytes=v, files=pair_files[(a, b)],
                                           samples=samples[(a, b)][:3]) for (a, b), v in pairs.most_common(60)])
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=1)
print('DONE', len(index), 'keys')
