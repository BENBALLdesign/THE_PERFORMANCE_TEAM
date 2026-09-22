"""Step 1 of the THE PERFORMANCE TEAM separation: hash every file under the installation before any move."""
import hashlib, json, os, sys, time, datetime

ROOT = r'C:\Users\benja\Dropbox\THE PERFORMANCE TEAM'


def main(out):
    rows = []
    t0 = time.time()
    total = 0
    for dp, dn, fn in os.walk(ROOT):
        dn.sort()
        fn.sort()
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT).replace(os.sep, '/')
            h = hashlib.sha256()
            try:
                with open(p, 'rb') as fh:
                    for chunk in iter(lambda: fh.read(1 << 22), b''):
                        h.update(chunk)
                st = os.stat(p)
                rows.append(dict(path=rel, bytes=st.st_size, sha256=h.hexdigest(),
                                 mtime=datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat(timespec='seconds')))
                total += st.st_size
            except Exception as e:  # noqa: BLE001
                rows.append(dict(path=rel, error=repr(e)))
    doc = dict(schema='performance-team-separation-baseline/1', root=ROOT,
               recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
               purpose='Step 1 of the THE PERFORMANCE TEAM repository separation (handoff 4, 2026-09-22): '
                       'SHA-256 of every file before any move, so the split can be verified lossless.',
               files=len(rows), bytes=total, errors=sum('error' in r for r in rows),
               seconds=round(time.time() - t0, 1), rows=rows)
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print('DONE', len(rows), total, doc['errors'], doc['seconds'])


if __name__ == '__main__':
    main(sys.argv[1])
