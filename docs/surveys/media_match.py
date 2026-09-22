"""Which installation media and evidence already sit in the Seed Bank (by hash), using the baseline record and the catalog."""
import collections
import json
from pathlib import Path

b = json.loads(Path(r'F:\SEED BANK\DATA_ARCHIVE\HOME_INSPECTION\_META\20260922-separation\baseline.json').read_text(encoding='utf-8'))
cat = json.loads(Path(r'C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM\registries\recordings-catalog.json').read_text(encoding='utf-8-sig'))
bank = {r['source_sha256']: r for r in cat['records']}
inbank = collections.Counter(); notbank = collections.Counter(); examples = []
for r in b['rows']:
    if r['path'].lower().endswith(('.wav', '.mp4', '.m4a', '.mp3', '.webm', '.mkv')):
        top = '/'.join(r['path'].split('/')[:3])
        if r['sha256'] in bank:
            inbank[top] += r['bytes']
        else:
            notbank[top] += r['bytes']
            if len(examples) < 6:
                examples.append((r['path'], r['bytes']))
print('media already in RECORDINGS bank (same hash):')
for k, v in inbank.most_common():
    print(f'  {v/1e6:8.1f} MB  {k}')
print('media NOT in bank:')
for k, v in notbank.most_common():
    print(f'  {v/1e6:8.1f} MB  {k}')
print('examples not in bank:', examples)
print('catalog records', len(cat['records']), 'status', cat.get('status'))
c = collections.Counter(); n = collections.Counter()
for r in b['rows']:
    p = r['path']
    if '/evidence' in p or '/Intake/' in p:
        e = p.rsplit('.', 1)[-1].lower(); c[e] += r['bytes']; n[e] += 1
print('evidence+intake by ext (MB, files):', {k: (round(v/1e6, 1), n[k]) for k, v in c.most_common(6)})
# older editions: which Study Guide Editions folders, sizes
c = collections.Counter(); n = collections.Counter()
for r in b['rows']:
    parts = r['path'].split('/')
    if len(parts) > 2 and parts[1] == 'Study Guide Editions':
        c[parts[2]] += r['bytes']; n[parts[2]] += 1
print('Study Guide Editions by folder (MB, files):')
for k, v in sorted(c.items()):
    print(f'  {v/1e6:8.1f} MB {n[k]:5d}  {k}')
