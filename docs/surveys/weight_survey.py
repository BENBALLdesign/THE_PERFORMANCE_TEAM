"""Weight survey: bytes and file counts per top-level and second-level folder, by extension, plus git/vault markers."""
import collections
import json
import os
import sys
import time

ROOTS = [r'C:\Users\benja\Dropbox\ABSTRACTION nft', r'C:\Users\benja\Dropbox\BB_SEED', r'C:\Users\benja\Dropbox\DATABSTRACT']
OUT = sys.argv[1]
report = {}
for root in ROOTS:
    t0 = time.time()
    d1 = collections.Counter(); n1 = collections.Counter()
    d2 = collections.Counter(); n2 = collections.Counter()
    ext = collections.Counter(); next_ = collections.Counter()
    big = []
    total = 0; files = 0; markers = []
    for dp, dn, fn in os.walk(root):
        rel = os.path.relpath(dp, root)
        parts = [] if rel == '.' else rel.split(os.sep)
        for marker in ('.git', '.venv', 'node_modules', '_runtime', 'BB_BOOKS', 'BB_DESIGN'):
            if marker in dn:
                markers.append(os.path.join(rel, marker) if parts else marker)
        for f in fn:
            p = os.path.join(dp, f)
            try:
                s = os.stat(p).st_size
            except OSError:
                continue
            total += s; files += 1
            k1 = parts[0] if parts else '(root files)'
            k2 = '/'.join(parts[:2]) if len(parts) >= 2 else (parts[0] + '/(files)' if parts else '(root files)')
            d1[k1] += s; n1[k1] += 1; d2[k2] += s; n2[k2] += 1
            e = f.rsplit('.', 1)[-1].lower() if '.' in f else '(none)'
            ext[e] += s; next_[e] += 1
            if s > 50_000_000:
                big.append((s, os.path.relpath(p, root)))
    big.sort(reverse=True)
    report[root] = dict(bytes=total, files=files, seconds=round(time.time() - t0, 1), markers=markers[:40],
                        level1=[dict(path=k, bytes=v, files=n1[k]) for k, v in d1.most_common()],
                        level2=[dict(path=k, bytes=v, files=n2[k]) for k, v in d2.most_common(30)],
                        ext=[dict(ext=k, bytes=v, files=next_[k]) for k, v in ext.most_common(12)],
                        big=[dict(bytes=s, path=p) for s, p in big[:25]])
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=1)
    print('DONE', root, files, total, report[root]['seconds'], flush=True)
