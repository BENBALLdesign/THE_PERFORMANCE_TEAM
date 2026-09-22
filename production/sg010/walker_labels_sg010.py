"""505 Walker Ave standalone PDFs: SG-009 labels -> SG-010 (Part B step 8).

The five standalone property PDFs on the shelf carry printed guide references from the S31 release. Three of
them name the guide edition in a way that is now stale:
  - FIELD CARDS 5x7 and LETTER PRINT: card footers "SG-009 / QC .. / N .."  -> "SG-010 / ..."
  - FINDINGS AND TIMELINE p.4:        "SG-009 through S31"                  -> "SG-010 through S39"
The IMAGE SEQUENCE p.7 sentence "...connected to the existing property cards and SG-009." is the Visual R2
historical statement of what R2 linked to at issue; it is retained (same rule as the combined packet). The
VECTOR OUTLINE has no edition text. Those two are carried byte-exact.

Same method as walker_sg010.swap: width-neutral digit swap at the same origin, font, size and colour; every
retained page is pixel-compared at 72 dpi outside the swapped boxes. Stage only: writes to the Seed Bank
work folder walker-sg010/output/standalone. Property Reviews is untouched until publish_sg010.py.
"""
from walker_sg010 import fitz, sha, save, PROP, WORK, swap
import json, re, datetime
import numpy as np

OUT = WORK/'output/standalone'
EDITS = {
    '505 WALKER - FIELD CARDS - 5x7.pdf': [('SG-009 /', 'SG-010 /')],
    '505 WALKER - FIELD CARDS - LETTER PRINT.pdf': [('SG-009 /', 'SG-010 /')],
    '505 WALKER - FINDINGS AND TIMELINE.pdf': [('SG-009 through S31', 'SG-010 through S39')],
}
CARRIED = ['505 WALKER - IMAGE SEQUENCE AND EVIDENCE.pdf', '505 WALKER - VECTOR OUTLINE.pdf']
HISTORICAL = 'existing property cards and SG-009'

def relabel(name, pairs):
    base = PROP/name; doc = fitz.open(base); ref = fitz.open(base); edits = []
    for i, pg in enumerate(doc):
        pending = []
        for old, new in pairs: pending += list(swap(pg, old, new))
        if not pending: continue
        pg.apply_redactions(images=0, graphics=1, text=0)
        for rr, t in pending:
            pg.insert_text(t['origin'], t['new'], fontname=t['font'], fontsize=t['size'],
                           color=tuple(((t['color'] >> k) & 255)/255 for k in (16, 8, 0)))
            edits.append(dict(page=i+1, old=t['old'], new=t['new'], rect=[round(v, 2) for v in rr]))
    left = [dict(page=k+1, text=m) for k, p in enumerate(doc) for m in re.findall(r'.{0,60}SG-009.{0,20}', p.get_text())]
    assert not left, left
    out = OUT/name; doc.save(out, garbage=4, deflate=True, no_new_id=True)
    new = fitz.open(out); checks = []
    for i in range(len(ref)):
        a = ref[i].get_pixmap(dpi=72); b = new[i].get_pixmap(dpi=72)
        A = np.frombuffer(a.samples, np.uint8).reshape(a.h, a.w, a.n); B = np.frombuffer(b.samples, np.uint8).reshape(b.h, b.w, b.n)
        mask = np.ones(A.shape[:2], bool)
        for e in edits:
            if e['page'] == i+1:
                x0, y0, x1, y1 = e['rect']; mask[max(0, int(y0)-3):int(y1)+4, max(0, int(x0)-3):int(x1)+4] = False
        diff = int((np.abs(A.astype(int)-B.astype(int)).max(axis=2)[mask] > 24).sum())
        checks.append(dict(page=i+1, body_pixels_changed_72dpi=diff))
    assert all(c['body_pixels_changed_72dpi'] == 0 for c in checks), checks
    assert len(new) == len(ref)
    return dict(file=name, pages=len(new), baseline_sha256=sha(base), sha256=sha(out), edits=edits, body_verification=checks)

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [relabel(n, pairs) for n, pairs in EDITS.items()]
    carried = []
    for n in CARRIED:
        src = PROP/n; txt = ''.join(p.get_text() for p in fitz.open(src))
        kept = re.findall(r'.{0,60}SG-009.{0,20}', txt)
        assert all(HISTORICAL in k for k in kept), kept
        carried.append(dict(file=n, sha256=sha(src), pages=len(fitz.open(src)), sg009_text_retained=[dict(text=k, reason='Visual R2 historical statement of its linkage at issue') for k in kept]))
    m = dict(schema='home-inspection-property-standalone-relabel/1', property='505 Walker Ave', status='STAGED - not published',
             built_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), output=str(OUT),
             method='Width-neutral in-place token swap (same font, size, colour, origin); 72 dpi body pixels asserted unchanged outside the swapped boxes',
             relabeled=rows, carried=carried, edits=sum(len(r['edits']) for r in rows))
    save(OUT/'standalone-manifest.json', m)
    print(json.dumps(dict(relabeled=[(r['file'], len(r['edits'])) for r in rows], carried=[c['file'] for c in carried])))

if __name__ == '__main__': build()
