"""Hash-verify two sample files for each of the top redundancy pairs from drive-index.json."""
import hashlib
import json
import os
import sys

d = json.load(open(sys.argv[1]))
ROOTS = {'D': 'D:/', 'F': 'F:/', 'DBX-ABSTRACTION': 'C:/Users/benja/Dropbox/ABSTRACTION nft',
         'DBX-BB_SEED': 'C:/Users/benja/Dropbox/BB_SEED', 'DBX-TEAM': 'C:/Users/benja/Dropbox/THE PERFORMANCE TEAM'}


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''):
            h.update(c)
    return h.hexdigest()


for pair in d['redundancy'][:14]:
    checks = []
    for s in pair['samples'][:2]:
        paths = []
        for w in s['where'][:3]:
            lab, rel = w.split(':', 1)
            p = os.path.join(ROOTS[lab], rel, s['name'])
            if os.path.exists(p):
                paths.append(p)
        if len(paths) >= 2:
            checks.append('IDENTICAL' if len({sha(p) for p in paths}) == 1 else 'DIFFER')
    print(f"{pair['bytes']/1e9:7.1f} GB {pair['files']:6d}  {pair['a']}  <->  {pair['b']}   samples: {checks}", flush=True)
