"""SG-010 new reference PDFs: verify the receipt against the bytes and add the Weil-McLain manual (handoff 2, Part A step 7).

The seven PDFs live in the Seed Bank work folder `references`. This module is also the single place that names
their shelf files (Source PDFs/<APP-E id> - <title>.pdf) for shelf_sg010 / navigation_sg010.
"""
from prepare import *
import datetime
from pypdf import PdfReader
REFS=WORK/'references'
RECEIPT=REFS/'reference-receipt.json'
BOILER_URL='https://www.weil-mclain.com/wp-content/uploads/EG-Series-7-Boiler-Manual-0425.pdf'
# receipt file -> (APP-E external_references id, shelf title)
SHELF={
 'NHIE - Policies Procedures and Content Outline.pdf':('S36-NHIE','NHIE Policies, Procedures and Content Outline'),
 'CPSC - Range Stability.pdf':('S33-TIP','CPSC - Range Stability'),
 'CPSC - Dryer Fire Prevention.pdf':('S33-DRYER','CPSC - Dryer Fire Prevention'),
 'DOE - Durable Attics.pdf':('S34-ATTIC','DOE - Durable Attics'),
 'DOE - Air Sealing.pdf':('S34-AIR','DOE - Air Sealing'),
 'Maryland - Smoke Alarm Statute 9-104.pdf':('S33-MD-ALARM','Maryland Public Safety 9-104 - Smoke Alarms'),
 'Weil-McLain - EG Series 7 Boiler Manual.pdf':('S38-BOILER','Weil-McLain EG Series 7 Boiler Manual'),
}
def shelf_rows():
    """Manifest-style rows (without hashes) for the seven SG-010 source PDFs."""
    receipt={r['file']:r for r in read(RECEIPT)}
    rows=[]
    for fn,(rid,title) in SHELF.items():
        r=receipt[fn]
        rows.append(dict(source=str(REFS/fn),file=f'Source PDFs/{rid} - {title}.pdf',kind='source',id=rid,title=title,pages=r['pages'],cited_url=r['url'],retrieved_url=r['url'],retrieved_at=r['retrieved_at'],receipt_sha256=r['sha256']))
    return rows
def main():
    receipt=read(RECEIPT)
    import content_s38
    assert content_s38.BOILER==BOILER_URL,content_s38.BOILER
    wm=REFS/'Weil-McLain - EG Series 7 Boiler Manual.pdf'
    if not any(r['file']==wm.name for r in receipt):
        st=wm.stat()
        receipt.append(dict(file=wm.name,url=BOILER_URL,sha256=sha(wm),pages=len(PdfReader(wm).pages),bytes=st.st_size,
            retrieved_at=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(),
            retrieved_at_basis='file modification time of the downloaded copy; hash recorded 2026-09-21',
            cited_by='content_s38.py BOILER (S38-BOILER); steam_systems refs; APP-E external_references',
            note='Manufacturer-specific example (15-psi steam safety valve vs 30-psi water relief for this product); not a generic specification.'))
    # Every receipt row must match the bytes on disk before anything cites the local copy.
    for r in receipt:
        p=REFS/r['file'];assert p.exists(),p
        assert sha(p)==r['sha256'],('hash mismatch',r['file'])
        assert len(PdfReader(p).pages)==r['pages'],('page mismatch',r['file'])
        assert r['file'] in SHELF,('no shelf name',r['file'])
    save(RECEIPT,receipt)
    print(json.dumps(dict(receipt=str(RECEIPT),entries=len(receipt),verified='sha256 + page count of every entry',shelf_files=[r['file'] for r in shelf_rows()]),indent=1))
if __name__=='__main__':main()
