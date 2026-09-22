"""SG-010 archive and publish (Part B step 10).

Modes (run in this order, from this folder):
  stage    assemble the publish tree in the Seed Bank work folder `publish` (TEAM-relative paths): the staged shelf
           with its final manifest, the three edition folders, the frozen-issue pointer folder, root registries,
           root shelf PDFs, Property Reviews updates and the Library pointers. Requires qa-final/visual-review.json
           (Part B step 9) with status "pass".
  plan     hash every write and removal against the live tree; pin publication-plan.json.
  publish  back up every replaced or removed file into the established Seed Bank history
           (Backups/Current Set History/before-<issue>), apply the plan, rebuild the library against the published
           tree, move Library/CURRENT.json, assemble the frozen issue in the Seed Bank, verify, write receipts.
  verify   re-run the verification alone.
Never writes into Dropbox from any path outside the pinned plan; never backs up into Dropbox.
"""
from prepare import *
import datetime,os,time,html
from pypdf import PdfReader
import shelf_sg010,references_sg010
sys.path.insert(0,str(REPO/'tools'))
import home_inspection_library as lib
TEAM=BASE;TRAINING=TEAM/'Home Inspection Training';CURRENT=TRAINING/'CURRENT EDITION';PROPERTY=TEAM/'Property Reviews/505 Walker Ave';LIBRARY=TRAINING/'Library'
IDS=shelf_sg010.IDS;PARENT=shelf_sg010.PARENT;SHELF=shelf_sg010.SHELF;EDS=shelf_sg010.EDS;WALKER=shelf_sg010.WALKER;STANDALONE=shelf_sg010.STANDALONE;CARDS=shelf_sg010.CARDS;LAYER=shelf_sg010.LAYER;NAV=shelf_sg010.NAV
PUB=WORK/'publish';PLAN=PUB/'publication-plan.json';RECEIPT=PUB/'publication-receipt.json'
ISSUE_PTR=LIB/'SG-010 Issues'/REV                      # small Dropbox pointer folder (issue.json + Data)
BANK_ISSUE=storage.domain_root()/'Issues'/REV           # frozen standalone reading set (bulk) in the Seed Bank
BACKUP=storage.backup_root()/('before-'+REV)
NOW=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
CHANGE='Presentation revision P1 of the cumulative SG-010 edition (through S39): area band tones re-tuned so all eight house areas separate in grayscale (hue kept, card header ink unchanged); appendix pagination control (no orphan rows or empty source lines); continuation-page area tabs; gutter-first Maryland crabs in appendices; larger near-square compact figure. Content, page maps and card bindings unchanged.'
STATE='Published cumulative edition through S39 / presentation revision P1'
FIRST_ISSUE='SG-010-2026-09-21'
COVERAGE='S01-S39; 39 source recordings (S37 is a 74-second assessment-result clip; S39 is the repaired recording, ending at fireplace screen 13 of 15)'
LIMITS=['Internal study and field preparation; not a property inspection or compliance certification','Physical flashlight/crayon print test not performed','H14 historical source PDF remains unavailable; source gap retained','S39 fireplace screens 14-15 and the Unit 6 exam are not on the recording; stated in N14, APP-G and D1-T12','No field card covers hydronic, steam or electric heat, or fireplace operation directly','NHIE outline gaps listed in APP-B: EVSE, indoor-air management (partial), countertops/cabinets, smart home, sprinklers, smart-tech limits, service-life table']
def cp(src,dst):dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
REGDIR='_registries'   # staging folder for files whose live home is the checkout's registries/, not the installation
ROOT_REGISTRIES={'STUDY-GUIDE-EDITIONS.json','APPENDIX-VERSIONS.json'}
def staged(p):
    p=Path(p)
    q=PUB/REGDIR/p.relative_to(REG) if p.is_relative_to(REG) else PUB/p.relative_to(TEAM)
    q.parent.mkdir(parents=True,exist_ok=True);return q
def target_of(p):
    """Live path of a staged file: registries live in the checkout, everything else in the installation."""
    rel=Path(p).relative_to(PUB)
    return REG.joinpath(*rel.parts[1:]) if rel.parts[0]==REGDIR else TEAM/rel
def confine(t):
    t=Path(t);return inside(t,REG) if t.resolve().is_relative_to(REG.resolve()) else inside(t,TEAM)
def backup_rel(t):
    t=Path(t);return Path(REGDIR)/t.relative_to(REG) if t.is_relative_to(REG) else t.relative_to(TEAM)
def live_path(t):
    """Plans pinned before the separation name the registries at the installation root; they now live in the checkout."""
    t=Path(t)
    if t.parent==TEAM and t.name in ROOT_REGISTRIES:return REG/t.name
    if t==LIBRARY/'CURRENT.json':return LIBRARY_CURRENT
    return t
def stage_json(p,d):save(staged(p),d)
def doc(title,body):return '<!doctype html><meta charset="utf-8"><title>'+html.escape(title)+'</title><style>body{font:17px system-ui;max-width:960px;margin:35px auto;color:#1a1a5e}p,li{line-height:1.5}img{max-width:95%}</style><h1>'+html.escape(title)+'</h1>'+body
def inside(p,root):
    p=Path(p).resolve();root=Path(root).resolve();assert p.is_relative_to(root) and p!=root,p;return p
def apprec(a,ed,cut,pdf):
    """Registry/publication appendix row (SG-009 shape), hashed from the staged shelf copy."""
    r=dict(id=a['id'],version=a['version'],title=a['title'],pages=a['pages'],path=a['path'],pdf=a['pdf'],pdf_sha256=sha(pdf),presentation_revision=REV)
    if cut=='compact':r['based_on_version']=a['based_on_version']
    if ed=='SG-010-L1':r['path']='../SG-010/'+a['path'];r['pdf']='../SG-010/'+a['pdf']
    return r
def stage():
    qa=read(WORK/'qa-final/visual-review.json');assert qa['status']=='pass',qa
    m=read(SHELF/'_Maintenance/manifest.json');assert m['published'] is False and m['directory']
    if PUB.exists():shutil.rmtree(PUB)
    PUB.mkdir(parents=True)
    # --- CURRENT EDITION: the staged shelf, with the final manifest fields.
    for p in SHELF.rglob('*'):
        if p.is_file():cp(p,staged(CURRENT/p.relative_to(SHELF)))
    # --- Edition folders.
    compact=read(OUT/'study-guide.json');l1=read(OUT/'study-guide-L1.json');w1=read(OUT/'walking-cut.json')
    e=EDS/'SG-010'
    for p in e.rglob('*'):
        if p.is_file():cp(p,staged(LIB/'SG-010'/p.relative_to(e)))
    for ed in ['SG-010-L1','SG-010-W1']:
        for p in (EDS/ed).rglob('*'):
            if p.is_file():cp(p,staged(LIB/ed/p.relative_to(EDS/ed)))
    apps={}
    for cut,data in [('compact',compact),('long',l1)]:
        rows=[]
        for a in data['appendices']:
            shelfpdf=SHELF/('Compact Appendices' if cut=='compact' else 'Long Appendices')/Path(a['pdf']).name
            cp(shelfpdf,staged(LIB/'SG-010'/a['pdf']))
            for ext in ['.html','.json']:
                src=OUT/Path(a['path']).with_suffix(ext)
                if src.exists():cp(src,staged(LIB/'SG-010'/Path(a['path']).with_suffix(ext)))
            rows.append(apprec(a,'SG-010' if cut=='compact' else 'SG-010-L1',cut,shelfpdf))
        apps[cut]=rows
    save(staged(LIB/'SG-010/compact-appendices.json'),apps['compact'])
    for p in CARDS.rglob('*'):
        if p.is_file() and 'qa' not in p.relative_to(CARDS).parts and not (p.parent==CARDS and p.suffix=='.pdf'):cp(p,staged(LIB/'SG-010/Appendices/Quick Charts - 64 Cards'/p.relative_to(CARDS)))
    for fn in ['QUICK CHARTS - 64 CARDS - 5x7.pdf','QUICK CHARTS - 64 CARDS - LETTER PRINT.pdf']:cp(SHELF/'Field Cards'/fn,staged(LIB/'SG-010/Appendices/Quick Charts - 64 Cards'/fn))
    cp(SHELF/'STUDY GUIDE - SG-010.pdf',staged(LIB/'SG-010/STUDY GUIDE - SG-010.pdf'));cp(OUT/'STUDY GUIDE.html',staged(LIB/'SG-010/STUDY GUIDE.html'))
    cp(SHELF/'STUDY GUIDE - SG-010-L1.pdf',staged(LIB/'SG-010-L1/STUDY GUIDE - SG-010-L1.pdf'))
    cp(SHELF/'STUDY GUIDE - SG-010-W1.pdf',staged(LIB/'SG-010-W1/STUDY GUIDE - SG-010-W1.pdf'));cp(OUT/'STUDY GUIDE - SG-010-W1.html',staged(LIB/'SG-010-W1/STUDY GUIDE.html'))
    for fn in ['page-index.json','scope-coverage.json','assessment-review.json','housing-data.json','housing-data.csv','external-references.json','intake-sources.json']:
        if (OUT/fn).exists():cp(OUT/fn,staged(LIB/'SG-010'/fn))
    shutil.copytree(OUT/'Source Diagrams',staged(LIB/'SG-010/Source Diagrams'),dirs_exist_ok=True)
    for fn in ['editorial-review.json','field-card-review-lock.json','field-card-fact-aliases-SG009-to-SG010.json']:cp(HERE/fn,staged(LIB/'SG-010'/fn))
    # Presentation Source: the production scripts and the small build reports (reproducibility record, not bulk).
    src=staged(LIB/'SG-010/Presentation Source'/REV)
    for p in HERE.glob('*'):
        if p.suffix in ('.py','.md','.json'):cp(p,src/p.name)
    for rel in ['stage-report.json','recordings-rehash-receipt.json','baseline.json','output/layered/layers-report.json','output/layered/contents-layout.json','navigation/navigation-review.json','library/staged-build-report.json','walker-sg010/output/change-manifest.json','walker-sg010/output/standalone/standalone-manifest.json','references/reference-receipt.json','qa-final/index.json','qa-final/visual-review.json','field-cards-64-sg010/sg010-card-update.json']:
        cp(WORK/rel,src/'reports'/Path(rel).name)
    (src/'README.md').write_text(f'# SG-010 presentation source / {REV}\n\nProduction scripts from THE PERFORMANCE TEAM/Home Inspection Training/SG-010 Production and the small build reports. Pipeline: prepare_content -> render_sg010 (appendices terms l1 compact_appendices compact walking) -> contents_sg010 -> paint_sg010 -> cards_sg010 -> walker_sg010 -> references_sg010 -> walker_labels_sg010 -> navigation_sg010 -> shelf_sg010 -> library_sg010 -> qa_sg010 -> publish_sg010 (stage / plan / publish). Bulk outputs, QA proofs and the frozen issue live in the Seed Bank (F:\\SEED BANK\\DATA_ARCHIVE\\HOME_INSPECTION). Content modules content_s33/s34/scope/assessment/s38/s39 hold the S33-S39 source reviews; editorial-review.json lists the reviewed corrections.\n',encoding='utf-8')
    # Publication records per edition.
    pubs={}
    for ed,data,cut,topics in [('SG-010',compact,'compact',len(compact['pages'])),('SG-010-L1',l1,'long',len(l1['pages'])),('SG-010-W1',w1,None,len(w1['pages']))]:
        pdf=staged(LIB/ed/f'STUDY GUIDE - {ed}.pdf');pages=len(PdfReader(pdf).pages);aa=apps.get(cut,[]) if cut else []
        pub=dict(edition=ed,status='published cumulative edition / presentation revision P1',date='2026-09-21',presentation_date='2026-09-22',published_at=NOW(),pdf_pages=pages,topic_sections=topics,sessions=39,new_sessions=[],first_issue=FIRST_ISSUE,
            source_coverage=COVERAGE,pending_recordings='No further recording identified; the announced practice exam remains unmatched (Library/Intake/practice-exam-pending.json)',pdf_sha256=sha(pdf),appendices=aa,appendix_pages=sum(a['pages'] for a in aa),
            appendix_cut=cut or 'route companion',presentation_revision=REV,companion_editions=[x for x in IDS if x!=ed],published_directory=str(LIB/ed),validation='validation.json',visual_review='visual-review.json',limits=LIMITS,
            change=CHANGE,current_issue=REV,parent_issue=PARENT,issue_path=str(ISSUE_PTR),issue_bank_path=str(BANK_ISSUE),incorporation=CHANGE,navigation_revision=REV,edition_family='SG-010',parent_edition_family='SG-009')
        stage_json(LIB/ed/'publication.json',pub);pubs[ed]=pub
        stage_json(LIB/ed/'validation.json',dict(status='pass',issue=REV,parent=PARENT,pdf_sha256=pub['pdf_sha256'],pages=pages,review='SG-010/Presentation Source/'+REV+'/reports/visual-review.json',links='directory links, contents-layer links, finder/index links and glossary bookmarks verified (navigation-review.json, shelf manifest validation)'))
        stage_json(LIB/ed/'visual-review.json',dict(status='Pass',issue=REV,pdf_sha256=pub['pdf_sha256'],method=qa['method'],defects_fixed=qa.get('defects_fixed',[]),physical_print_test=False))
        staged(LIB/ed/'index.html').write_text(doc(ed,'<p><a href="STUDY GUIDE - '+ed+'.pdf">Open the PDF</a>'+(' / <a href="STUDY GUIDE.html">Browse topic links</a>' if staged(LIB/ed/'STUDY GUIDE.html').exists() else '')+' / <a href="../../CURRENT EDITION/00 - START HERE.pdf">Current PDF directory</a></p><p>Cumulative SG-010 edition through S39. Prior SG-009 issues are retained unchanged.</p>'),encoding='utf-8')
    readme=('# SG-010 / cumulative edition through S39\n\nComplete issue '+REV+' builds on SG-009 / '+PARENT+'. Open ../../CURRENT EDITION/00 - START HERE.pdf. The 32-page compact guide (28 charts), 127-page long cut (139 topics in 14 contiguous sections), eight-page walking cut, both appendix cuts (A1.8 B1.7 C1.9 D1.3 E1.4 F1.3 G1.3 H1.2; 18 + 86 pages), 64 cards (22 rebound, IDs and wording unchanged), the 20-page Walker packet and 21 original reference PDFs form one complete reading issue.\n\n'
        'S33-S39 add kitchen and bath appliances, alarms and life safety, insulation and ventilation, professional scope and reporting (NHIE outline coverage in APP-B), the S37 assessment result (36/50, staged with its limits), hydronic, steam and electric heat, cooling water and air, and interior floors, glazing, egress, doors, stairs and fireplaces. Open items are stated, not hidden: S39 fireplace screens 14-15 and the Unit 6 exam are missing (N14, APP-G, D1-T12); no card covers hydronic/steam/electric heat or fireplace operation; H14 remains unavailable; the NHIE gaps are listed in APP-B.\n\n'
        'navigation.json (368 entries, 62 subject aliases as retrieval routes only) and contents-locations.json are derived retrieval data, not admitted vocabulary. APP-D v1.3 owns the 107 definitions and 14 numbered notes. The Field Card Concordance and field-card-fact-aliases-SG009-to-SG010.json resolve every SG-009 card fact to SG-010 (0 stranded). Raw recordings are archived in the Seed Bank (Sound Recordings/RECORDING ARCHIVE - LEDGER.pdf). Physical print testing is not performed. Local reproducible build inputs are in Presentation Source/'+REV+'.\n')
    acc=read(HERE/'field-card-acceptance.json');readme+='\n## Presentation revision P1 / '+REV+'\n\n'+CHANGE+' Grayscale rule: '+json.dumps(read(EDS/'SG-010/visual-language.json')['grayscale_rule'])+'. Ben acceptance ('+acc['date']+'): '+acc['accepted']+' See field-card-acceptance.json.\n'
    staged(LIB/'SG-010/README.md').write_text(readme,encoding='utf-8');cp(HERE/'field-card-acceptance.json',staged(LIB/'SG-010/field-card-acceptance.json'))
    # --- Root registries.
    reg=read(REG/'STUDY-GUIDE-EDITIONS.json');reg.update(current_edition='SG-010',current_long_cut='SG-010-L1',current_walking_cut='SG-010-W1',working_edition=None,updated_at=NOW(),pending_source_note='S33-S39 incorporated; no further available recording identified; announced practice exam unmatched (Library/Intake/practice-exam-pending.json)')
    for ed,pub in pubs.items():
        row=dict(id=ed,date='2026-09-21',sessions=39,edition_family='SG-010',change=CHANGE,presentation_revision=REV,state=STATE,path=f'Home Inspection Training/Study Guide Editions/{ed}/STUDY GUIDE - {ed}.pdf',pages=pub['pdf_pages'],duplex_sheets=(pub['pdf_pages']+1)//2,pdf_sha256=pub['pdf_sha256'],updated_at=NOW(),appendices=pub['appendices'],current_issue=REV,parent_issue=PARENT,issue_path=str(ISSUE_PTR))
        old=next((x for x in reg['editions'] if x['id']==ed),None)
        if old:old.update(row)   # presentation revision: same edition row, new issue
        else:reg['editions'].append(row)
    stage_json(REG/'STUDY-GUIDE-EDITIONS.json',reg);stage_json(LIB/'SG-010/STUDY-GUIDE-EDITIONS.json',reg)
    ar=read(REG/'APPENDIX-VERSIONS.json');ar.update(updated_at=NOW(),current={a['id']:a['version'] for a in apps['compact']},current_long_cut={a['id']:a['version'] for a in apps['long']},long_cut_current={a['id']:a['version'] for a in apps['long']})
    live=read(CURRENT/'_Maintenance/manifest.json');prev={(r['id'],r['kind']):r for r in live['files'] if r['kind'] in ('compact','long')}
    for cut in apps:
        for a in apps[cut]:
            if any(x['id']==a['id'] and x['version']==a['version'] for x in ar['history']):
                for x in ar['history']:
                    if x['id']==a['id'] and x['version']==a['version']:x.update(pdf_sha256=a['pdf_sha256'],presentation_revision=REV)
                continue   # content version already registered; only the presentation revision changes
            entry={k:a[k] for k in ['id','version','title','pages','pdf_sha256','presentation_revision']};entry.update(date='2026-09-21',issued_with=['SG-010' if cut=='compact' else 'SG-010-L1'],path='Home Inspection Training/Study Guide Editions/SG-010/'+(a['path'].removeprefix('../SG-010/')),pdf='Home Inspection Training/Study Guide Editions/SG-010/'+(a['pdf'].removeprefix('../SG-010/')),change='SG-010 cumulative update for S33-S39; earlier versions retained')
            if cut=='compact':entry['based_on_version']=a['based_on_version']
            ar['history'].append(entry)
    ar['presentation_revisions'].append(dict(issue=REV,parent_issue=PARENT,scope=CHANGE,files=[dict(appendix=a['id'],cut=cut,version=a['version'],pdf_sha256=a['pdf_sha256'],previous_version=prev[(a['id'],cut)]['version'],previous_pdf_sha256=prev[(a['id'],cut)]['sha256'],previous_copy=str(storage.domain_root()/'Issues'/PARENT/prev[(a['id'],cut)]['file'])) for cut in apps for a in apps[cut]]))
    stage_json(REG/'APPENDIX-VERSIONS.json',ar);stage_json(LIB/'SG-010/APPENDIX-VERSIONS.json',ar)
    document_map(reg)
    # --- Training root shelf files (established aliases of the current compact set).
    cp(SHELF/'STUDY GUIDE - SG-010.pdf',staged(TRAINING/'STUDY GUIDE.pdf'));cp(SHELF/'STUDY GUIDE - SG-010-W1.pdf',staged(TRAINING/'WALKING CUT - W1.pdf'))
    for p in TRAINING.glob('APP-*.pdf'):
        aid=p.name.split(' - ')[0];row=next(r for r in m['files'] if r['kind']=='compact' and r['id']==aid);cp(SHELF/row['file'],staged(p))
    landing=doc('Home Inspection / through S39','<p><a href="CURRENT EDITION/00 - START HERE.pdf">Open the current PDF directory</a></p><p>Complete SG-010 cumulative edition: compact, long and walking guides, both appendix cuts, 64 general cards, the 505 Walker packet and 21 reference PDFs. The flagged switching chart also prints separately. Prior SG-009 issues are retained.</p>')
    for fn in ['index.html','STUDY GUIDE.html']:staged(TRAINING/fn).write_text(landing,encoding='utf-8')
    pending=read(TRAINING/'PENDING RECORDINGS.json');pending.update(state='Published through S39 (SG-010); announced practice exam unmatched; no pending recording',completed_sessions=[f'S{i:02}' for i in range(1,40)],completed_edition='SG-010',companion_edition='SG-010-L1',completed_at=NOW(),updated_at=NOW(),progress=str(LIB/'SG-010/README.md'),published_issue=REV)
    for f in pending['files']:
        if f['id']=='S33':f.update(status='incorporated in SG-010 (content_s33.py); recording archived in the Seed Bank',published=True,edition='SG-010')
    stage_json(TRAINING/'PENDING RECORDINGS.json',pending)
    # --- Property Reviews.
    change=read(WALKER/'change-manifest.json');stand=read(STANDALONE/'standalone-manifest.json')
    cp(WALKER/'505 WALKER - COMBINED PROPERTY REVIEW.pdf',staged(PROPERTY/'505 WALKER - COMBINED PROPERTY REVIEW.pdf'));cp(WALKER/'concordance-SG010-crosswalk.json',staged(PROPERTY/'concordance-SG010-crosswalk.json'))
    for r in stand['relabeled']:cp(STANDALONE/r['file'],staged(PROPERTY/r['file']))
    stage_json(PROPERTY/('property-packet-change-'+REV+'.json'),dict(change,status='published with '+REV,standalone_relabel=stand))
    packet=read(PROPERTY/'combined-packet.json');cpdf=staged(PROPERTY/'505 WALKER - COMBINED PROPERTY REVIEW.pdf');packet_changed=sha(cpdf)!=packet['pdf_sha256']
    parts=[dict(title='Findings and timeline',file='505 WALKER - FINDINGS AND TIMELINE.pdf',start_page=1,end_page=4,pages=4,sha256=next(r['sha256'] for r in stand['relabeled'] if 'FINDINGS' in r['file'])),
           dict(title='SG-010 routes and review prompts',file=None,start_page=5,end_page=6,pages=2,note='New in SG-010: card routes to current charts and conditional prompts from S33/S34/S38/S39; 0 observed conditions added'),
           dict(title='Dated images and evidence',file='505 WALKER - IMAGE SEQUENCE AND EVIDENCE.pdf',start_page=7,end_page=13,pages=7,sha256=next(c['sha256'] for c in stand['carried'] if 'IMAGE' in c['file'])),
           dict(title='Property outline',file='505 WALKER - VECTOR OUTLINE.pdf',start_page=14,end_page=14,pages=1,sha256=next(c['sha256'] for c in stand['carried'] if 'OUTLINE' in c['file'])),
           dict(title='Field cards - Letter sheets',file='505 WALKER - FIELD CARDS - LETTER PRINT.pdf',start_page=15,end_page=20,pages=6,sha256=next(r['sha256'] for r in stand['relabeled'] if 'LETTER' in r['file']))]
    packet.update(compiled_at=change['built_at'],guide_reference_issue=REV,pages=20,pdf_sha256=sha(cpdf),previous_pdf_sha256=packet['pdf_sha256'],parts=parts,scope='Reviewed S31/Visual R2 property content with SG-010 routes and conditional course prompts; no new property evidence or conclusions',pending='none; SG-010 published',published_at=NOW(),bank_build=str(WALKER/'505 WALKER - COMBINED PROPERTY REVIEW.pdf'),change_manifest='property-packet-change-'+REV+'.json',crosswalk='concordance-SG010-crosswalk.json',backup=str(BACKUP))
    packet['validation'].update(visual_review=qa['method'],physical_print_test=False,body_pixels_unchanged_at_72dpi_outside_edits=True)
    if packet_changed:stage_json(PROPERTY/'combined-packet.json',packet)
    else:packet=read(PROPERTY/'combined-packet.json')   # P1 leaves the packet bytes alone; keep its record as published
    pm=read(PROPERTY/'manifest.json')
    for row in pm['pdfs']:
        r=next((x for x in stand['relabeled'] if x['file']==row['name']),None)
        if r:row.update(sha256=r['sha256'],bytes=(STANDALONE/r['file']).stat().st_size,previous_sha256=r['baseline_sha256'],relabeled='SG-009 -> SG-010 in place; body pixels unchanged')
    pm.update(reference_issue=REV,issue_path=str(ISSUE_PTR),guide_basis='SG-010 through S39',current_guide_pdf_sha256=sha(SHELF/'STUDY GUIDE - SG-010.pdf'),sg010_crosswalk='concordance-SG010-crosswalk.json',combined_packet='combined-packet.json',
        incorporation_review='SG-010 reference update: all 12 card routes resolve to SG-010 charts and L1 pages (concordance-SG010-crosswalk.json); 222 fact aliases, 10 conditional prompts, 0 new observed conditions. Card and findings footers relabeled SG-010 in place; imagery and outline byte-exact; findings F01-F07 unchanged.')
    stage_json(PROPERTY/'manifest.json',pm)
    if '## SG-010 reference update / ' not in (PROPERTY/'README.md').read_text(encoding='utf8'):staged(PROPERTY/'README.md').write_text((PROPERTY/'README.md').read_text(encoding='utf8')+'\n## SG-010 reference update / '+REV+'\n\nThe combined packet is now 20 pages: two SG-010 pages (routes for the 12 cards; conditional prompts from S33/S34/S38/S39) follow the findings. They cite only the retained findings and add no observed condition. Card footers and the findings basis line now read SG-010; imagery, outline, findings and Visual R2 are unchanged. Routes: concordance-SG010-crosswalk.json; change record: property-packet-change-'+REV+'.json.\n',encoding='utf8')
    # --- Library pointers (the package itself is built after publish, against the published tree).
    libreadme=library_readme();staged(LIBRARY/'README.md').write_text(libreadme,encoding='utf8');staged(CURRENT/'_Maintenance/LIBRARY LOOKUP.md').write_text(libreadme,encoding='utf8')
    if packet_changed:stage_json(LIBRARY/'Packets/505-Walker-combined.json',dict(read(LIBRARY/'Packets/505-Walker-combined.json'),pdf_sha256=sha(cpdf),manifest_sha256=sha(staged(PROPERTY/'combined-packet.json')),pages=20,guide_reference_issue=REV,scope=packet['scope'],pending='none',sections=[dict(title=p['title'],start_page=p['start_page'],end_page=p['end_page']) for p in parts]))
    stage_json(LIBRARY/'SG-010 CONTINUATION.json',dict(read(LIBRARY/'SG-010 CONTINUATION.json'),updated_at=NOW(),status='SG-010 published as '+REV+'; see Study Guide Editions/SG-010/README.md',published_issue=REV))
    cs=read(LIBRARY/'COURSE STATUS.json');cs.update(updated_at=NOW(),published_issue=REV,published_source_coverage='S01-S39',all_recordings_incorporated=True,recordings_status='All 39 identified recordings reviewed and incorporated in SG-010; recordings archived in F:\\SEED BANK\\RECORDINGS (89 catalog records re-hashed OK); the announced practice exam remains unmatched',pending_sources=[],gate='SG-010 published; the next edition waits for a new recording or a Ben review of the unreviewed card bindings / QC-047 safety flag')
    cs['practice_exam'].update(status='unmatched; S37 (74-second result clip, 36/50 Initial Assessment) is staged in APP-G and assessment-review.json and is not asserted to be the announced practice exam',source_identified=False)
    stage_json(LIBRARY/'COURSE STATUS.json',cs)
    fr=read(LIBRARY/'FINAL READINESS.json');fr.update(checked_at=NOW(),status='SG-010 published through S39; physical print test and Ben review of new card bindings still open',published_issue=REV,reviewed_source_coverage='S01-S39',current_pdf_count=50,current_library_verification='rebuilt against the published tree at publish; verify current',available_unincorporated=[],remaining=['Physical print test','Ben review of the 22 rebound cards and the QC-047 safety flag','Practice-exam source match (unresolved)','Next: separate THE PERFORMANCE TEAM into its own repository (BB_SEED)'],property_packet='505 Walker combined packet 20 pages with SG-010 routes and prompts; 0 new observed conditions')
    stage_json(LIBRARY/'FINAL READINESS.json',fr)
    pe=read(LIBRARY/'Intake/practice-exam-pending.json');pe.update(status='unmatched at SG-010 publication; S37 result clip (36/50 Initial Assessment) staged separately in APP-G / assessment-review.json, not asserted to be this exam',checked_at=NOW());stage_json(LIBRARY/'Intake/practice-exam-pending.json',pe)
    # --- Frozen-issue pointer folder (Dropbox, small) and CURRENT manifest final fields.
    save(staged(ISSUE_PTR/'SEED BANK LOCATION.json'),dict(schema='seed-bank-location/1',vault_id=storage.VAULT_ID,original_root=str(ISSUE_PTR),bank_root=str(BANK_ISSUE),status='frozen standalone reading set assembled in the Seed Bank at publish; this folder holds the issue record and small data only'))
    registry=staged(REG/'STUDY-GUIDE-EDITIONS.json')
    m.update(registry=str(REG/'STUDY-GUIDE-EDITIONS.json'),registry_sha256=sha(registry),issue_path=str(ISSUE_PTR),issue_bank_path=str(BANK_ISSUE),published=True,published_at=NOW(),stage=str(SHELF),
        validation=dict(m['validation'],status='PDF membership, hashes, page counts, all directory links and rendered layout verified',visual_review=qa['method'],physical_print_test=False))
    stage_json(CURRENT/'_Maintenance/manifest.json',m)
    stage_json(CURRENT/'_Maintenance/issue.json',dict(current_issue=REV,parent_issue=PARENT,path=str(ISSUE_PTR),bank_path=str(BANK_ISSUE),source_coverage='S01-S39',complete_pdf_count=m['validation']['pdfs'],start_here=m['directory']['file'],published=True))
    for p in staged(CURRENT).rglob('*'):
        if p.is_file() and p.suffix=='.pdf':assert p.relative_to(staged(CURRENT)).as_posix() in {r['file'] for r in m['files']}|{m['directory']['file']}
    print(json.dumps(dict(staged=str(PUB),files=sum(1 for p in PUB.rglob('*') if p.is_file()))))
def document_map(reg):
    rows=[e for e in reg['editions']];md=TEAM/'TRAINING-DOCUMENT-MAP.md';hp=TEAM/'TRAINING-DOCUMENT-MAP.html'
    def link(e):return e['path'].replace(' ','%20')
    table='## Edition register\n\nCurrent field edition: **SG-010**. Long cut: **SG-010-L1**. Walking cut: **SG-010-W1**. Earlier editions retained.\n\n| Edition | Date | Sessions | Pages | Open |\n|---|---|---:|---:|---|\n'+''.join(f"| {e['id']} | {e['date']} | {e['sessions']} | {e.get('pages','')} | [Open]({link(e)}) |\n" for e in rows)
    s=md.read_text(encoding='utf8');a=s.index('<!-- EDITIONS START -->');b=s.index('<!-- EDITIONS END -->');s=s[:a]+'<!-- EDITIONS START -->\n'+table+'<!-- EDITIONS END -->'+s[b+len('<!-- EDITIONS END -->'):]
    if 'register updated' not in s:s=s.replace('Working arrangement · 19 September 2026','Working arrangement · 19 September 2026 · register updated 22 September 2026',1)
    s=s.replace('register updated 21 September 2026','register updated 22 September 2026')
    staged(md).write_text(s,encoding='utf8')
    h=hp.read_text(encoding='utf8');a=h.index('<!-- EDITIONS START -->');b=h.index('<!-- EDITIONS END -->')
    body='<!-- EDITIONS START --><section><h2>Edition register</h2><p>Current field edition: SG-010 (32 pages / 16 sheets duplex). Long cut: SG-010-L1 (127 pages). Walking cut: SG-010-W1 (8 pages). Eight appendices print separately in two depths.</p><table><tr><th>Edition</th><th>Date</th><th>Sessions</th><th>Pages</th><th>Change</th></tr>'+''.join(f"<tr><td><a href=\"{link(e)}\">{e['id']}</a></td><td>{e['date']}</td><td>{e['sessions']}</td><td>{e.get('pages','')}</td><td>{html.escape(e['change'])}</td></tr>" for e in rows)+'</table><p><a href="Home%20Inspection%20Training/CURRENT%20EDITION/00%20-%20START%20HERE.pdf">Open the current PDF directory</a></p></section><!-- EDITIONS END -->'
    staged(hp).write_text(h[:a]+body+h[b+len('<!-- EDITIONS END -->'):],encoding='utf8')
def library_readme():
    base=(LIBRARY/'README.md').read_text(encoding='utf8')
    if '## Current package / '+REV in base:return base  # already this issue's text (publish applied)
    cut=base.find('## Current package / ')
    if cut<0:cut=base.index('## Next incorporation')
    return base[:cut]+('## Current package / '+REV+'\n\nCURRENT.json now names **Library/'+REV+'** (SG-010 through S39: 1145 records, 5550 relations, 50 PDFs incl. the Start Here directory, 107 definitions, 14 numbered notes). It was built against the published tree after publication, verified `current`, and its manifest hash is pinned in CURRENT.json. The frozen S32-C1-2026-09-21 package is untouched. Facts keep the edition in their own ID prefix: SG-009-prefixed property facts still verify against the frozen SG-009 guide; SG-010 facts verify against Study Guide Editions/SG-010/study-guide.json.\n\n'
        'Course status: all 39 identified recordings are incorporated; the announced practice exam remains unmatched (Intake/practice-exam-pending.json); S37 is the staged 36/50 Initial Assessment result clip. Open content gaps are listed in Study Guide Editions/SG-010/README.md. Physical print testing is not performed.\n\n'
        '## Combined property packet\n\nThe 20-page **505 WALKER - COMBINED PROPERTY REVIEW.pdf** (Property Reviews/505 Walker Ave) adds SG-010 routes and conditional prompts (pp. 5-6) to the P1 packet; 0 observed conditions added. **Packets/505-Walker-combined.json** carries its path, checksum and section ranges. Recording lookup: RECORDINGS - LOOKUP.md.\n\n'
        '## Seed Bank locations\n\nBackups, build payloads, QA proofs, the frozen issue copies and the recording archive live in **F:/SEED BANK/DATA_ARCHIVE/HOME_INSPECTION** and **F:/SEED BANK/RECORDINGS**. The published reading shelf stays in Dropbox. Study Guide Editions/SG-010 Issues/'+REV+' holds the issue record and points to the bank copy. Bank-only material requires the bank volume; bulk jobs stop if it is unavailable.\n')
def plan():
    assert PUB.exists() and not PLAN.exists(),'stage first / plan already pinned'
    live=read(CURRENT/'_Maintenance/manifest.json')
    for r in live['files']:assert sha(CURRENT/r['file'])==r['sha256'],('live shelf changed',r['file'])
    assert sha(CURRENT/live['directory']['file'])==live['directory']['sha256'] and sha(REG/'STUDY-GUIDE-EDITIONS.json')==live['registry_sha256']
    assert not BACKUP.exists() and not BANK_ISSUE.exists() and not ISSUE_PTR.exists() and not (LIBRARY/REV).exists()
    writes=[]
    for p in sorted(PUB.rglob('*')):
        if not p.is_file():continue
        t=target_of(p);confine(t);before=sha(t) if t.exists() else None
        if before!=sha(p):writes.append(dict(source=str(p),target=str(t),before_sha256=before,sha256=sha(p),bytes=p.stat().st_size))
    keep={str(target_of(p)) for p in PUB.rglob('*') if p.is_file()}
    removals=[dict(target=str(p),before_sha256=sha(p)) for p in sorted(CURRENT.rglob('*')) if p.is_file() and str(p) not in keep]
    order=lambda r:(Path(r['target']).name in {'manifest.json','publication.json','issue.json','STUDY-GUIDE-EDITIONS.json','APPENDIX-VERSIONS.json','PENDING RECORDINGS.json','CURRENT.json'},r['target'])
    writes.sort(key=order)
    plan=dict(issue=REV,parent=PARENT,backup=str(BACKUP),bank_issue=str(BANK_ISSUE),writes=writes,removals=removals,parent_receipt_sha256=sha(CURRENT/'_Maintenance/publication-receipt.json'),
              summary=dict(writes=len(writes),replacements=sum(r['before_sha256'] is not None for r in writes),new_files=sum(r['before_sha256'] is None for r in writes),removals=len(removals),bytes=sum(r['bytes'] for r in writes),current_pdfs=50,source_coverage='S01-S39'))
    save(PLAN,plan);print(json.dumps(plan['summary']))
def publish():
    plan=read(PLAN);assert not RECEIPT.exists();backup=inside(plan['backup'],storage.backup_root());assert not backup.exists()
    for r in plan['writes']:
        s=inside(r['source'],PUB);t=confine(r['target']);assert sha(s)==r['sha256'];assert (sha(t) if t.exists() else None)==r['before_sha256'],t
    for r in plan['removals']:t=inside(r['target'],CURRENT);assert sha(t)==r['before_sha256'],t
    # 1. Archive every replaced or removed file into the established Seed Bank history (never Dropbox).
    for r in plan['writes']+plan['removals']:
        if r['before_sha256'] is None:continue
        p=Path(r['target']);b=backup/backup_rel(p);cp(p,b);assert sha(b)==r['before_sha256']
    cp(PLAN,backup/'publication-plan.json');cp(CURRENT/'_Maintenance/publication-receipt.json',backup/'parent-publication-receipt.json')
    save(backup/'ARCHIVE.json',dict(issue=REV,parent=PARENT,archived_at=NOW(),what='The SG-009 CURRENT EDITION set (all 42 PDFs + maintenance records), root shelf PDFs, registries, Library pointers and Property Reviews files replaced or removed by the SG-010 publication; byte-exact, hash-verified',files=sum(1 for p in backup.rglob('*') if p.is_file())))
    print('Previous files archived and hash-verified:',backup,flush=True)
    # 2. Apply the plan (removals first so the shelf never holds two editions; writes replace atomically).
    for r in plan['removals']:
        p=inside(r['target'],CURRENT);assert sha(p)==r['before_sha256'];p.unlink()
    for d in sorted({p for p in CURRENT.rglob('*') if p.is_dir()},reverse=True):
        if not any(d.iterdir()):d.rmdir()
    for r in plan['writes']:
        p=confine(r['target']);assert (sha(p) if p.exists() else None)==r['before_sha256'];p.parent.mkdir(parents=True,exist_ok=True)
        temp=p.with_name(p.name+'.sg010-publish.tmp');assert not temp.exists();cp(r['source'],temp);assert sha(temp)==r['sha256']
        for i in range(8):
            try:os.replace(temp,p);break
            except PermissionError:
                if i==7:raise
                time.sleep(.5)
    print('Plan applied.',flush=True)
    finish(backup)
def finish(backup=BACKUP):
    """Steps 3-5 after the plan is applied; re-runnable while Library/CURRENT.json still names the parent package."""
    plan=read(PLAN);assert read(LIBRARY_CURRENT)['issue']==PARENT,'CURRENT.json already moved'
    if (LIBRARY/REV).exists():shutil.rmtree(LIBRARY/REV)
    if BANK_ISSUE.exists():shutil.rmtree(BANK_ISSUE)
    if ISSUE_PTR.exists():
        for q in ISSUE_PTR.iterdir():
            if q.name!='SEED BANK LOCATION.json':(shutil.rmtree(q) if q.is_dir() else q.unlink())
    # 3. Library: rebuild against the published tree (no overlay), then and only then move CURRENT.json.
    package=LIBRARY/REV;result=lib.build(TEAM,package,overlay=None,edition='SG-010',glossary='APP-D-v1.3.json')
    cp(REPO/'tools/home_inspection_library.py',package/'home_inspection_library.py');(package/'README.md').write_text(library_readme(),encoding='utf8')
    contract=read(package/'manifest.json')
    for name in ['home_inspection_library.py','README.md']:contract['files'][name]=sha(package/name)
    contract.update(course_progress=dict(percent=100,basis='user reported course pass; all 39 identified recordings incorporated',source_completeness_verified=False,full_course_review='SG-010 incorporates S01-S39; announced practice exam unmatched'),coverage='Published S01-S39 context (SG-010); S39 ends at fireplace screen 13/15; H14 remains unavailable')
    save(package/'manifest.json',contract)
    status=lib.verify(package,TEAM);assert status['status']=='current',status
    for q,expect in [('QC-033','QC-033'),('P505-09','P505-09'),('AFCI','APP-D:term:afci'),('Hartford Loop','APP-D:term:hartford-loop'),('SG-010-L1:steam_systems','SG-010-L1:steam_systems')]:
        assert lib.lookup(package,q,TEAM,limit=1)['results'][0]['record']['id']==expect,q
    save(package/'validation.json',dict(status='pass',issue=REV,records=result['records'],definitions=result['definitions'],relationships=result['relations'],pdfs=result['pdfs'],controls=['built against the published tree with no overlay','verify current against THE PERFORMANCE TEAM','QC-033, P505-09, AFCI, Hartford Loop and SG-010-L1:steam_systems exact lookup'],limits=['Screen proofs only; physical printing not tested','No full-course completeness assertion beyond the 39 identified recordings','No Seed import or vocabulary admission']))
    contract=read(package/'manifest.json');contract['files']['validation.json']=sha(package/'validation.json');save(package/'manifest.json',contract)
    assert lib.verify(package,TEAM)['status']=='current'
    save(LIBRARY_CURRENT,dict(issue=REV,package=REV,manifest_sha256=sha(package/'manifest.json'),status='current published-source index through S39'))
    print('Library published:',json.dumps(result),flush=True)
    # 4. Frozen standalone reading set in the Seed Bank + the small Dropbox issue record.
    for p in CURRENT.rglob('*'):
        if p.is_file():cp(p,BANK_ISSUE/p.relative_to(CURRENT))
    data=BANK_ISSUE/'Data'
    for ed in IDS:
        for p in (LIB/ed).rglob('*'):
            if p.is_file() and p.suffix in ('.json','.md','.html','.csv') and 'Presentation Source' not in p.parts:cp(p,data/ed/p.relative_to(LIB/ed))
    for fn in ['STUDY-GUIDE-EDITIONS.json','APPENDIX-VERSIONS.json']:cp(REG/fn,data/fn)
    cp(TEAM/'TRAINING-DOCUMENT-MAP.md',data/'TRAINING-DOCUMENT-MAP.md')
    for p in PROPERTY.glob('*.json'):cp(p,data/'Property'/p.name)
    cp(PROPERTY/'README.md',data/'Property/README.md')
    for p in package.rglob('*'):
        if p.is_file():cp(p,data/'Library'/REV/p.relative_to(package))
    cp(LIBRARY_CURRENT,data/'Library/CURRENT.json')
    records=[dict(file=p.relative_to(BANK_ISSUE).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(BANK_ISSUE.rglob('*')) if p.is_file() and p.name!='issue.json']
    issue=dict(issue_id=REV,parent_issue_id=PARENT,family=IDS,source_coverage='S01-S39',pdf_count=sum(r['file'].endswith('.pdf') for r in records),complete_reading_set=True,bank_path=str(BANK_ISSUE),pointer=str(ISSUE_PTR),assembled_at=NOW(),change=CHANGE,files=records)
    save(BANK_ISSUE/'issue.json',issue);save(ISSUE_PTR/'issue.json',issue)
    for p in (data).rglob('*'):
        if p.is_file() and 'Library' not in p.relative_to(data).parts:cp(p,ISSUE_PTR/'Data'/p.relative_to(data))
    (ISSUE_PTR/'README.md').write_text('# '+REV+'\n\nFrozen standalone SG-010 reading set. The complete PDF copy (CURRENT EDITION shape + Data) is in the Seed Bank at\n\n'+str(BANK_ISSUE)+'\n\nissue.json lists every file with its hash. Data/ here holds the small edition, registry, property and pointer records; the library package copy is bank-only. See SEED BANK LOCATION.json.\n',encoding='utf8')
    receipt=verify();save(RECEIPT,receipt);save(CURRENT/'_Maintenance/publication-receipt.json',receipt);save(backup/'publication-receipt.json',receipt);save(BANK_ISSUE/'_Maintenance/publication-receipt.json',receipt)
    print(json.dumps(receipt))
def verify():
    plan=read(PLAN)
    for r in plan['writes']:assert sha(live_path(r['target']))==r['sha256'],r['target']
    for r in plan['removals']:assert not Path(r['target']).exists(),r['target']
    m=read(CURRENT/'_Maintenance/manifest.json');assert m['published'] and sha(REG/'STUDY-GUIDE-EDITIONS.json')==m['registry_sha256']
    for r in m['files']:assert sha(CURRENT/r['file'])==r['sha256'] and len(PdfReader(CURRENT/r['file']).pages)==r['pages'],r['file']
    assert sha(CURRENT/m['directory']['file'])==m['directory']['sha256']
    assert len(list(CURRENT.rglob('*.pdf')))==len(m['files'])+1==50
    import directory_sg010;directory_sg010.validate(CURRENT,m['files'],CURRENT/m['directory']['file'])
    for ed in IDS:
        pub=read(LIB/ed/'publication.json');assert sha(LIB/ed/f'STUDY GUIDE - {ed}.pdf')==pub['pdf_sha256']==next(r['sha256'] for r in m['files'] if r.get('edition')==ed)
        for a in pub['appendices']:assert sha((LIB/ed/a['pdf']).resolve())==a['pdf_sha256'],(ed,a['id'])
    reg=read(REG/'STUDY-GUIDE-EDITIONS.json');assert reg['current_edition']=='SG-010'
    for e in reg['editions']:
        if e['id'] in IDS:assert sha(TEAM/e['path'])==e['pdf_sha256']
    for b in (BACKUP,):
        for r in plan['writes']+plan['removals']:
            if r['before_sha256'] is not None:assert sha(b/backup_rel(r['target']))==r['before_sha256']
    package=LIBRARY/REV;cur=read(LIBRARY_CURRENT);assert cur['issue']==REV and sha(package/'manifest.json')==cur['manifest_sha256']
    assert lib.verify(package,TEAM)['status']=='current'
    assert lib.verify(LIBRARY/PARENT)['status'].startswith('snapshot integrity verified')  # frozen package untouched
    issue=read(BANK_ISSUE/'issue.json')
    for r in issue['files']:assert sha(BANK_ISSUE/r['file'])==r['sha256'],r['file']
    assert read(ISSUE_PTR/'issue.json')['pdf_count']==issue['pdf_count']==50
    for p in CURRENT.rglob('*.pdf'):assert sha(p)==sha(BANK_ISSUE/p.relative_to(CURRENT))
    for fn in ['STUDY GUIDE.pdf','WALKING CUT - W1.pdf']:assert sha(TRAINING/fn)==next(r['sha256'] for r in m['files'] if r.get('edition')==('SG-010' if fn.startswith('STUDY') else 'SG-010-W1'))
    packet=read(PROPERTY/'combined-packet.json');assert sha(PROPERTY/'505 WALKER - COMBINED PROPERTY REVIEW.pdf')==packet['pdf_sha256']==next(r['sha256'] for r in m['files'] if 'COMBINED' in r['file'])
    for row in read(PROPERTY/'manifest.json')['pdfs']:assert sha(PROPERTY/row['name'])==row['sha256']==next(r['sha256'] for r in m['files'] if Path(r['file']).name==row['name']),row['name']
    return dict(status='published and verified',issue=REV,parent=PARENT,source_coverage='S01-S39',reading_set_pdfs=50,writes=plan['summary']['writes'],removals=plan['summary']['removals'],guides={'SG-010':32,'SG-010-L1':127,'SG-010-W1':8},appendix_pages=[18,86],general_cards=64,property_cards=12,walker_packet_pages=20,new_property_findings=0,backup=str(BACKUP),issue_path=str(ISSUE_PTR),issue_bank_path=str(BANK_ISSUE),library_package=str(LIBRARY/REV),physical_print_test=False,verified_at=NOW())
if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'stage'
    {'stage':stage,'plan':plan,'publish':publish,'finish':finish,'verify':lambda:print(json.dumps(verify()))}[mode]()
