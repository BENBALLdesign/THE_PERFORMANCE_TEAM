"""SG-010 staged shelf: a CURRENT EDITION-shaped tree with its manifest, assembled in the Seed Bank.

Part A groundwork (navigation and the library both need the shelf rows and hashes); Part B adds the Start Here
PDF, the final manifest and publication. Stage only: never writes CURRENT EDITION, Study Guide Editions or Library.

Run order: navigation_sg010.py -> shelf_sg010.py -> library_sg010.py
"""
from prepare import *
import datetime
from pypdf import PdfReader
from references_sg010 import shelf_rows,RECEIPT
STAGE=WORK/'stage';TRAIN=STAGE/'Home Inspection Training';SHELF=TRAIN/'CURRENT EDITION';EDS=TRAIN/'Study Guide Editions'
NAV=WORK/'navigation';LAYER=OUT/'layered';CARDS=WORK/'field-cards-64-sg010';WALKER=WORK/'walker-sg010/output';STANDALONE=WALKER/'standalone'
LIVE=BASE/'Home Inspection Training/CURRENT EDITION';LIVE_EDITION=BASE/'Home Inspection Training/Study Guide Editions/SG-010'
IDS=['SG-010','SG-010-L1','SG-010-W1'];PARENT='SG-010-2026-09-21';ISSUE=REV   # P1 builds on the first SG-010 issue
for forbidden in ('CURRENT EDITION','Study Guide Editions','Dropbox'):assert forbidden not in str(WORK),WORK
def plan():
    """Shelf rows (manifest shape, no hashes yet): staged SG-010 material plus byte-exact carries from the live shelf."""
    apps=read(OUT/'study-guide-L1.json')['appendices'];rows=[]
    rows.append(dict(source=NAV/'STUDY GUIDE - SG-010.pdf',file='STUDY GUIDE - SG-010.pdf',kind='guide',title='SG-010',edition='SG-010',revision=REV))
    rows.append(dict(source=LAYER/'STUDY GUIDE - SG-010-W1.pdf',file='STUDY GUIDE - SG-010-W1.pdf',kind='guide',title='SG-010-W1',edition='SG-010-W1',revision=REV))
    rows.append(dict(source=NAV/'STUDY GUIDE - SG-010-L1.pdf',file='STUDY GUIDE - SG-010-L1.pdf',kind='guide',title='SG-010-L1',edition='SG-010-L1',revision=REV))
    for a in apps:
        fn=f"{a['id']}-v{a['version']}"
        rows.append(dict(source=LAYER/f'Appendices/Compact/{fn}-C1.pdf',file=f'Compact Appendices/{fn}-C1.pdf',kind='compact',title=a['title'],id=a['id'],version=a['version']+'-C1',revision=REV))
    for a in apps:
        fn=f"{a['id']}-v{a['version']}";src=(NAV if a['id']=='APP-D' else LAYER/'Appendices')/f'{fn}.pdf'  # APP-D carries the glossary bookmarks
        rows.append(dict(source=src,file=f'Long Appendices/{fn}.pdf',kind='long',title=a['title'],id=a['id'],version=a['version'],revision=REV))
    for fn in ['QUICK CHARTS - 64 CARDS - 5x7.pdf','QUICK CHARTS - 64 CARDS - LETTER PRINT.pdf']:
        rows.append(dict(source=CARDS/'painted'/fn,file='Field Cards/'+fn,kind='cards',title=fn,revision=REV))
    live=read(LIVE/'_Maintenance/manifest.json')
    relabeled={r['file']:r for r in read(STANDALONE/'standalone-manifest.json')['relabeled']} if (STANDALONE/'standalone-manifest.json').exists() else {}
    combined='Property Review/505 WALKER - COMBINED PROPERTY REVIEW.pdf';walker_sha=sha(WALKER/Path(combined).name)
    for r in live['files']:
        if r['kind'] in ('source','property','diagram'):
            name=Path(r['file']).name
            if name in relabeled and r['sha256']==relabeled[name]['baseline_sha256']:
                # Part B step 8 (first publication only): SG-009 -> SG-010 labels swapped in place; body pixels asserted unchanged.
                s=relabeled[name];rows.append(dict(r,source=STANDALONE/name,revision=REV,relabeled_from=live['issue_id'],receipt_sha256=s['sha256']))
            elif r['file']==combined:
                assert r['sha256']==walker_sha,'live Walker packet differs from the staged build';rows.append(dict(r,source=WALKER/name,carried_from=live['issue_id'],carried_sha256=r['sha256']))
            else:
                # Carried byte-exact from the live shelf; the copy step re-verifies the recorded hash.
                rows.append(dict(r,source=LIVE/r['file'],carried_from=live['issue_id'],carried_sha256=r['sha256']))
    have={r['file'] for r in rows}
    rows+=[r for r in shelf_rows() if r['file'] not in have]   # new reference PDFs not yet on the live shelf
    if combined not in have:rows.append(dict(source=WALKER/Path(combined).name,file=combined,kind='property',title='Combined property review / 20 pages / SG-010 routes and prompts',revision=REV))
    assert len({r['file'] for r in rows})==len(rows)
    return rows
def copy_rows(rows):
    out=[]
    for r in rows:
        src=Path(r['source']);dst=SHELF/r['file'];assert src.exists(),src
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        row={k:v for k,v in r.items() if k not in ('source','carried_sha256','receipt_sha256')}
        row.update(source=str(src),sha256=sha(dst),bytes=dst.stat().st_size,pages=len(PdfReader(dst).pages))
        expected=r.get('carried_sha256') or r.get('receipt_sha256')
        if expected:assert row['sha256']==expected,('carried file changed',r['file'])
        if 'pages' in r:assert row['pages']==r['pages'],('page count',r['file'])
        out.append(row)
    return out
def visual_language(files):
    base=read(LIVE_EDITION/'visual-language.json');layers=read(LAYER/'layers-report.json')
    import palette_sg010
    base.update(revision=REV,parent=PARENT,name='Field Card Concordance / Visual Language C1 / P1 grayscale retune (SG-010)',
        status='Local study-guide language carried from SG-009 C1; P1 re-tunes the eight area band tones in lightness (hue kept) so every band separates in grayscale; card header ink colours unchanged; no global palette token or vocabulary admission',
        area_palette=palette_sg010.palette_record(),grayscale_rule=dict(luma_ladder=palette_sg010.TARGET,min_step=palette_sg010.MIN_STEP,label_ink_switch=palette_sg010.INK_SWITCH),
        input_source_pins={r['file']:r['sha256'] for r in files if r['kind'] in ('guide','compact','long','cards')},
        scope=dict(guides=3,appendix_cuts=16,card_print_formats=2,directory=1,pages_added='see manifest; SG-010 is a cumulative edition, not a paint-only revision'),
        layers=dict(report=str(LAYER/'layers-report.json'),meaning=layers['meaning'],policy=layers.get('policy'),
                    marks={d['file']:dict(safety=d['safety_marks'],maryland=d['md_marks']) for d in layers['documents']}),
        limits_by_card_note='Card text is unchanged from SG-009; the per-card limit list is carried as-is.')
    return base
def main():
    for p in [NAV/'STUDY GUIDE - SG-010.pdf',NAV/'STUDY GUIDE - SG-010-L1.pdf',NAV/'APP-D-v1.3.pdf',NAV/'navigation.json',NAV/'FIND A SUBJECT.html']:
        assert p.exists(),('run navigation_sg010.py first',p)
    if STAGE.exists():shutil.rmtree(STAGE)
    files=copy_rows(plan())
    live=read(LIVE/'_Maintenance/manifest.json')
    # Non-manifest companions carried with the diagram (as on the live shelf).
    for fn in ['Source Diagrams/CC-S32-01 - 3-Way and 4-Way Switches.png','Source Diagrams/CC-S32-01.json']:shutil.copy2(LIVE/fn,SHELF/fn)
    shutil.copy2(NAV/'FIND A SUBJECT.html',SHELF/'FIND A SUBJECT.html')
    # Part B step 8: the Start Here directory, built from the copied rows and link-checked against the staged tree.
    import directory_sg010
    start=directory_sg010.build(files,SHELF/'00 - START HERE.pdf',WORK/'directory-raw.pdf');links=directory_sg010.validate(SHELF,files,start)
    for r in files:assert sha(SHELF/r['file'])==r['sha256'] and len(PdfReader(SHELF/r['file']).pages)==r['pages'],r['file']
    assert {p.relative_to(SHELF).as_posix() for p in SHELF.rglob('*.pdf')}=={r['file'] for r in files}|{'00 - START HERE.pdf'}
    m=dict(schema=1,assembled_on='22 September 2026',registry='pending publication (Part B step 10)',current_editions=IDS,presentation_revision=REV,
        card_branding_revision=live['card_branding_revision'],inspection_revision=live['inspection_revision'],branding_source_sha256=live['branding_source_sha256'],
        files=files,unavailable_sources=live['unavailable_sources'],
        scope='Complete SG-010 through S39: three guides, both appendix cuts, 64 cards, the 20-page Walker combined packet plus its five standalone PDFs, 21 original reference PDFs and one flagged source diagram.',
        copy_policy='Byte-exact copies of staged guides/cards and verified original source PDFs; carried SG-009 sources re-verified against their recorded hashes; three Walker standalone PDFs relabeled SG-009 -> SG-010 in place with bodies pixel-verified; no source rewriting.',
        directory=dict(file=start.name,pages=links['pages'],sha256=sha(start)),
        validation=dict(status='STAGED: PDF membership, hashes, page counts and all directory links verified; full visual verification and publication pending (Part B steps 9-10)',pdfs=len(files)+1,linked_pdfs=links['linked_pdfs'],links=links['links'],
                        source_pdfs=sum(r['kind']=='source' for r in files),source_diagrams=sum(r['kind']=='diagram' for r in files),unavailable_source_ids=[u['id'] for u in live['unavailable_sources']]),
        assembled_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),issue_id=ISSUE,parent_issue_id=PARENT,issue_path='pending publication (Part B step 10)',
        incorporation='SG-010 cumulative incorporation of S33-S39 across all guide cuts, both appendix cuts, the general cards and the Walker packet; contiguous L1 sections; colour/pattern/safety/MD layers reapplied.',
        visual_language_revision=REV,stage=str(SHELF),published=False)
    save(SHELF/'_Maintenance/manifest.json',m)
    save(SHELF/'_Maintenance/issue.json',dict(current_issue=ISSUE,parent_issue=PARENT,path=str(SHELF),source_coverage='S01-S39',complete_pdf_count=len(files)+1,start_here=start.name,published=False))
    shutil.copy2(NAV/'navigation.json',SHELF/'_Maintenance/navigation.json');shutil.copy2(RECEIPT,SHELF/'_Maintenance/reference-downloads.json')
    for fn in ['PROPERTY REVIEW PROCESS.md','LIBRARY BUILD NOTES.md']:shutil.copy2(LIVE/'_Maintenance'/fn,SHELF/'_Maintenance'/fn)
    shutil.copy2(WORK/'walker-sg010/output/change-manifest.json',SHELF/'_Maintenance/property-packet-change.json');shutil.copy2(STANDALONE/'standalone-manifest.json',SHELF/'_Maintenance/property-standalone-relabel.json')
    (SHELF/'_Maintenance/README.txt').write_text('Open 00 - START HERE.pdf. This is the complete SG-010 reading issue through S39, built on SG-009 / S32-C1-2026-09-21. Three guides (compact, long cut, walking cut), both appendix cuts A-H, 64 general cards, the 20-page 505 Walker combined packet with its five standalone PDFs, 21 original reference PDFs and the separately printable CC-S32-01 switching chart are included. Prior issues, editions and raw recordings are preserved. H14 remains unavailable. No physical print test has been performed.\n',encoding='utf-8')
    # Edition data folders: the structured owners the library indexes (staged shape of Study Guide Editions/SG-010*).
    e=EDS/'SG-010';(e/'Appendices/Quick Charts - 64 Cards').mkdir(parents=True)
    shutil.copy2(NAV/'navigation.json',e/'navigation.json');shutil.copy2(NAV/'navigation.html',e/'navigation.html');shutil.copy2(NAV/'navigation-review.json',e/'navigation-review.json')
    shutil.copy2(OUT/'study-guide.json',e/'study-guide.json');shutil.copy2(LAYER/'contents-locations-SG-010.json',e/'contents-locations.json')
    for a in read(OUT/'study-guide-L1.json')['appendices']:shutil.copy2(OUT/a['path'].replace('.html','.json'),e/'Appendices'/Path(a['path']).name.replace('.html','.json'))
    for fn in ['cards.json','concordance.json','sg010-card-update.json','field-card-fact-aliases-SG009-to-SG010.json']:shutil.copy2(CARDS/fn,e/'Appendices/Quick Charts - 64 Cards'/fn)
    save(e/'visual-language.json',visual_language(files))
    (EDS/'SG-010-L1').mkdir();shutil.copy2(OUT/'study-guide-L1.json',EDS/'SG-010-L1/study-guide.json');shutil.copy2(OUT/'page-index-L1.json',EDS/'SG-010-L1/page-index.json')
    (EDS/'SG-010-W1').mkdir();shutil.copy2(OUT/'walking-cut.json',EDS/'SG-010-W1/study-guide.json')
    save(WORK/'stage-report.json',dict(stage=str(STAGE),issue=ISSUE,files=len(files),pages=sum(r['pages'] for r in files),bytes=sum(r['bytes'] for r in files),
        by_kind={k:sum(r['kind']==k for r in files) for k in ['guide','compact','long','cards','source','property','diagram']},
        carried=sum('carried_from' in r for r in files),relabeled=sum('relabeled_from' in r for r in files),manifest_sha256=sha(SHELF/'_Maintenance/manifest.json'),start_here=dict(file=start.name,**links,sha256=m['directory']['sha256'])))
    print(json.dumps(read(WORK/'stage-report.json'),indent=1))
if __name__=='__main__':main()
