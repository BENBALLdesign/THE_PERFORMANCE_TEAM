"""SG-010 navigation (Part A step 5): derived retrieval data, PDF page links, glossary bookmarks and FIND A SUBJECT.

Adapted from BB_CODE/.scratch/sg010/navigation.py + finish_navigation.py: APP-D v1.3, staged layered renders, staged
card and Walker data, shelf rows from shelf_sg010.plan(). Writes only to the Seed Bank work folder `navigation`.
Definitions stay owned by APP-D; aliases are retrieval routes, not admitted equivalences.
"""
from prepare import *
import re,html,unicodedata,pdfplumber
from pypdf import PdfReader,PdfWriter
from pypdf.annotations import Link
from pypdf.generic import NumberObject
from urllib.parse import quote
import shelf_sg010
LAYER=OUT/'layered';NAV=WORK/'navigation';CARDS=WORK/'field-cards-64-sg010'
PARENT=shelf_sg010.PARENT;IDS=shelf_sg010.IDS
ALIASES={
 '3-way switches':'electric_devices','4-way switches':'electric_devices','Three-way switches':'electric_devices','Four-way switches':'electric_devices',
 'Light switches':'electric_devices','Switches':'electric_devices','Multi-location lighting':'electric_devices','Outlets':'electric_devices','Receptacles':'electric_devices',
 'Aluminum wiring':'electric_legacy','Knob-and-tube wiring':'electric_legacy','Main panel':'electric_panels',
 'Arc-fault protection':'electric_devices','Ground-fault protection':'electric_devices','Carbon monoxide':'furnace_safety',
 'Basement':'foundation_types','Cracks':'movement','Water stains':'interior_moisture','Leaks':'moisture','Peeling paint':'siding_coatings',
 'Sump pump':'drainage_pumps','Water heater':'water_heater_identity','Attic':'attic_environment','Deck ledger':'deck_connections',
 'Heat pump backup':'heatpump_modes','Plaster':'interior_facings','Condensation':'window_glazing','Flashing':'roof_flashing',
 'Grounding':'electric_service','Bonding':'electric_service','Furnace':'furnace_types','Roof leaks':'roof_flashing',
 # SG-010 subjects (S33-S39): familiar words that lead to the new topics.
 'Boiler':'hydronic_systems','Radiators':'hydronic_systems','Steam heat':'steam_systems','Baseboard heat':'electric_heat_delivery','Electric heat':'electric_heat_delivery',
 'Condensate':'cooling_water_air','Air conditioning':'cooling_scope','Insulation':'insulation_materials','R-value':'insulation_materials','Vapor barrier':'air_vapor_thermal',
 'Bathroom fan':'ventilation_exhaust','Dryer vent':'bath_laundry','Smoke alarm':'interior_life_safety','CO alarm':'interior_life_safety','GFCI':'interior_life_safety',
 'Dishwasher':'kitchen_waste','Garbage disposal':'kitchen_waste','Range':'kitchen_appliances','Tempered glass':'safety_glazing','Egress window':'egress_openings',
 'Stairs':'interior_stairs','Handrail':'interior_stairs','Fireplace':'fireplace_masonry','Gas logs':'fireplace_factory_gas','Chimney':'chimney_parts',
 'Radon':'special_service_boundaries','Mold':'special_service_boundaries','Lead paint':'special_service_boundaries','Scope':'professional_scope','Report':'report_workflow'}
SWITCH_ALIASES=['3-way switches','4-way switches','Three-way switches','Four-way switches','Light switches','Switches','Multi-location lighting']
def norm(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).casefold()).strip()
def term_id(term):return 'APP-D:term:'+re.sub('[^a-z0-9]+','-',term.lower()).strip('-')
def locate(pdf_path,glossary):
    """Exact APP-D long-cut pages for every term and numbered note, read from the layered PDF itself."""
    terms={};notes={}
    with pdfplumber.open(pdf_path) as pdf:
        for pn,p in enumerate(pdf.pages,1):
            left=norm(p.crop((40,40,172,750)).extract_text() or '');full=norm(p.extract_text() or '')  # same label-column crop as render_sg010.stage_terms
            for t in glossary['terms']:
                if t['term'] not in terms and re.search(r'\b'+re.escape(norm(t['term']))+r'\b',left):terms[t['term']]=pn
            for n in glossary['notes']:
                if n[0] not in notes and re.search(r'\b'+re.escape(norm(n[0]))+r'\b',full):notes[n[0]]=pn
    missing=[t['term'] for t in glossary['terms'] if t['term'] not in terms]+[n[0] for n in glossary['notes'] if n[0] not in notes]
    assert not missing,missing
    return terms,notes
def page_link(writer,page_index,box,target):
    page=writer.pages[page_index];h=float(page.mediabox.height)
    writer.add_annotation(page_index,Link(rect=(box[0],h-box[3],box[2],h-box[1]),target_page_index=target-1))
def link_target(reader,annot):
    dest=annot.get('/Dest') or annot['/A']['/D'];d=dest[0]
    return int(d)+1 if isinstance(d,(int,NumberObject)) else reader.get_page_number(d.get_object())+1
def check_links(reader,doc,i,column=None):
    """Every link on page i must sit on a printed number equal to its target page (column limits the x range)."""
    p=doc.pages[i];h=float(p.height);words=p.extract_words();bad=[];n=0
    for a in (reader.pages[i].get('/Annots') or []):
        a=a.get_object()
        if a.get('/Subtype')!='/Link':continue
        n+=1;rect=[float(x) for x in a['/Rect']];top,bottom=h-rect[3],h-rect[1]
        inside=[w['text'].strip(',') for w in words if w['x0']>=rect[0]-1 and w['x1']<=rect[2]+1 and w['top']>=top-1 and w['bottom']<=bottom+1 and re.fullmatch(r'\d{1,3},?',w['text']) and (column is None or column[0]<=w['x0']<column[1])]
        if str(link_target(reader,a)) not in inside:bad.append((i+1,rect,inside,link_target(reader,a)))
    return n,bad
def pdf_links(ed,src,dst):
    """Intra-document links on the printed page numbers of the compact finder and the L1 subject index.
    The compact location table (p.1) and the L1 contents leaves are already linked by contents_sg010; those are verified, not re-linked."""
    reader=PdfReader(src);writer=PdfWriter();writer.clone_document_from_reader(reader);count=0;pages=[];existing=dict(links=0,pages=[])
    with pdfplumber.open(src) as doc:
        for i,p in enumerate(doc.pages):
            text=p.extract_text() or '';head=(text.split('\n')+[''])[1]
            if ed=='SG-010' and i==0 or ed=='SG-010-L1' and head.startswith('CONTENTS / '):
                n,bad=check_links(reader,doc,i,column=(495,528));assert n and not bad,(ed,i+1,n,bad[:3])
                existing['links']+=n;existing['pages'].append(i+1);continue
            if ed=='SG-010' and 'Quick finder and appendix shelf' in text:
                words=p.extract_words();stop=min(w['top'] for w in words if w['text']=='Compact' and w['top']>200)
                regions=[(262,300,70,stop-5),(514,555,70,stop-5)]
            elif ed=='SG-010-L1' and head in ('Subject index','Subject index (continued)'):regions=[(249,306,65,742),(501,559,65,742)]
            else:continue
            assert not (reader.pages[i].get('/Annots') or []),('page already linked',ed,i+1)
            pages.append(i+1)
            for w in p.extract_words():
                if re.fullmatch(r'\d{1,3},?',w['text']) and any(x0<=w['x0']<x1 and top<=w['top']<bottom for x0,x1,top,bottom in regions):
                    target=int(w['text'].strip(','))
                    if 1<=target<=len(reader.pages):page_link(writer,i,(w['x0']-2,w['top']-2,w['x1']+2,w['bottom']+2),target);count+=1
    writer.add_metadata({'/NavigationRevision':REV});dst.parent.mkdir(parents=True,exist_ok=True);writer.write(dst)
    out=PdfReader(dst)
    assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(reader.pages,out.pages))
    with pdfplumber.open(dst) as doc:
        for i in [q-1 for q in pages]:
            n,bad=check_links(out,doc,i);assert not bad,(ed,i+1,bad[:3])
    return dict(links=count,pages=pages,contents_layer_links=existing)
def bookmarks(src,dst,term_pages,note_pages):
    reader=PdfReader(src);writer=PdfWriter();writer.clone_document_from_reader(reader)
    parent=writer.add_outline_item('Glossary / meanings and distinctions',0)
    for label,pn in sorted(term_pages.items(),key=lambda x:x[0].casefold()):writer.add_outline_item(label,pn-1,parent=parent)
    notes=writer.add_outline_item('Numbered notes',min(note_pages.values())-1)
    for label,pn in sorted(note_pages.items()):writer.add_outline_item(label,pn-1,parent=notes)
    writer.add_metadata({'/NavigationRevision':REV,'/Subject':'Definitions remain unchanged; alphabetic bookmarks locate the authoritative glossary entries and numbered notes.'})
    writer.write(dst)
    assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(reader.pages,PdfReader(dst).pages))
def doc(title,body):return '<!doctype html><meta charset="utf-8"><title>'+html.escape(title)+'</title><style>body{font:17px system-ui;max-width:960px;margin:35px auto;color:#1a1a5e}p,li{line-height:1.5}article{padding:20px 0;border-top:1px solid #bbb}h2{margin:6px 0}input{display:block;width:95%;padding:12px;font:inherit;margin-top:8px}small{color:#555}[hidden]{display:none}</style><h1>'+html.escape(title)+'</h1>'+body
def browse(data,routes_line,packet=False):
    # A small local page; filtering is entirely in-browser and never sends a query.
    def file_link(route):
        if 'edition' in route:
            ed=route['edition'];file=f'STUDY GUIDE - {ed}.pdf';prefix='' if packet or ed=='SG-010' else '../'+ed+'/'
        else:
            file=route['file'];prefix=''
            if not packet:
                if file.startswith('Long Appendices/'):file=file.replace('Long Appendices/','Appendices/',1)
                elif file.startswith('Compact Appendices/'):file=file.replace('Compact Appendices/','Appendices/Compact/',1)
                elif file.startswith('Field Cards/'):file=file.replace('Field Cards/','Appendices/Quick Charts - 64 Cards/',1)
                elif file.startswith(('Property Review/','Source PDFs/','Source Diagrams/')):return '../../CURRENT EDITION/'+quote(file)+'#page='+str(route['page'])
            return prefix+quote(file)+'#page='+str(route['page'])
        return prefix+quote(file)+'#page='+str(route['page'])
    body='<p>Contents locate a subject. The glossary explains meaning. The index accepts familiar words and abbreviations. Source IDs identify evidence.</p><label>Find a subject, term, card or source <input id="find" type="search" placeholder="Try boiler, switches, smoke alarm, radon, water stains..."></label><p id="count" aria-live="polite"></p><p>'+html.escape(routes_line)+'</p>'
    for x in sorted(data['entries'],key=lambda x:x['title'].casefold()):
        terms=' '.join([x['title'],x['kind'],x['id']]+x.get('search_labels',[]));body+='<article id="'+html.escape(x['id'],quote=True)+'" data-find="'+html.escape(terms.casefold(),quote=True)+'"><small>'+html.escape(x['kind'].upper())+'</small><h2>'+html.escape(x['title'])+'</h2>'
        if x.get('meaning'):body+='<p>'+html.escape(x['meaning'])+'</p>'
        if x.get('paired_terms'):body+='<p>Paired terms retain their distinctions; they are not synonyms.</p>'
        if x.get('qualification'):body+='<p>'+html.escape(x['qualification'])+'</p>'
        for r in x['routes']:
            label=r.get('edition',r.get('document'))+' / '+('sheet '+str(r['sheet']) if 'sheet' in r else 'p. '+str(r['page']))
            body+='<p><a href="'+file_link(r)+'">'+html.escape(label)+'</a>'+(' - '+html.escape(r.get('title','')) if r.get('title') else '')+'</p>'
        body+='<small>Reference: '+html.escape(x['id'])+'</small></article>'
    body+='''<script>const input=document.querySelector('#find'),items=[...document.querySelectorAll('article')],count=document.querySelector('#count');function filter(){const words=input.value.toLowerCase().replace(/[^a-z0-9]+/g,' ').trim().split(/\\s+/).filter(Boolean);let n=0;for(const a of items){const text=a.dataset.find.replace(/[^a-z0-9]+/g,' ');a.hidden=!words.every(w=>text.includes(w));if(!a.hidden)n++}count.textContent=n+' matching entries'}input.addEventListener('input',filter);filter();</script>'''
    return doc('Find a subject, meaning or source',body)
def main():
    NAV.mkdir(parents=True,exist_ok=True)
    long=read(OUT/'study-guide-L1.json');guide=read(OUT/'study-guide.json');w=read(OUT/'walking-cut.json');index=read(OUT/'page-index-L1.json')
    short={p['id']:p for p in guide['pages']};compact=guide['long_cut_topic_map'];topics={p['id'] for p in long['pages']}
    bad=[a for a,t in ALIASES.items() if t not in topics];assert not bad,('alias targets missing',bad)
    apd=next(a for a in long['appendices'] if a['id']=='APP-D');apd_pdf=f"Long Appendices/{Path(apd['pdf']).name}"
    glossary=read(OUT/apd['path'].replace('.html','.json'));cc=read(CARDS/'concordance.json');cards=read(CARDS/'cards.json')['cards']
    loc=read(LAYER/'contents-locations-SG-010.json');import palette_sg010;palette=palette_sg010.palette_record()
    term_pages,note_pages=locate(LAYER/'Appendices'/Path(apd['pdf']).name,glossary)
    rendered=read(HERE/'navigation.json')['glossary_pages']
    assert rendered==term_pages,('APP-D term pages moved between render and layer',{k:(rendered.get(k),term_pages.get(k)) for k in set(rendered)|set(term_pages) if rendered.get(k)!=term_pages.get(k)})
    entries=[]
    for p in long['pages']:
        tid=p['id'];ct=compact[tid];card_ids=[c['card_id'] for c in cc['cards'] if 'SG-010-L1:'+tid in c['related_l1_topic_ids']]
        routes=[dict(edition='SG-010',title=short[ct]['title'],page=short[ct]['printed_page'],topic_id=ct),dict(edition='SG-010-L1',title=p['title'],page=index[tid],topic_id=tid)]
        routes.extend(dict(edition='SG-010-W1',title=q['title'],page=w['page_index'][q['id']],topic_id=q['id'],relationship='route context; not an equivalent treatment') for q in w['pages'] if ct in q['refs'])
        e=dict(id='SG-010-L1:'+tid,kind='subject',title=p['title'],section=p['section'],search_labels=[tid.replace('_',' ')]+[a for a,t in ALIASES.items() if t==tid],routes=routes,card_ids=card_ids,source_refs=p.get('refs',[]))
        rec=loc.get('SG-010-L1:'+tid)
        if rec:e.update(area_ids=rec['area_ids'],location_labels=[palette[str(a)]['label'] for a in rec['area_ids']],location_relationship='Typical location; not an installation guarantee or a property finding')
        entries.append(e)
    for t in glossary['terms']:
        parts=t['term'].split(' / ')
        entries.append(dict(id=term_id(t['term']),kind='definition',title=t['term'],search_labels=list(dict.fromkeys(parts+[t['expansion']])),meaning=t['definition'],paired_terms=parts if len(parts)>1 else [],label_relationship='Expanded name or component of a paired definition; paired terms are not asserted synonyms.',owner=f"APP-D-v{apd['version']}",topic_id=t['topic'],related_topics=t.get('related_topics',[]),routes=[dict(document='APP-D long cut',page=term_pages[t['term']],file=apd_pdf)]))
    for n in glossary['notes']:
        entries.append(dict(id='APP-D:'+n[0],kind='numbered note',title=n[1],search_labels=[n[0],n[2]],meaning=n[2],routes=[dict(document='APP-D long cut',page=note_pages[n[0]],file=apd_pdf)]))
    for c in cards:
        entries.append(dict(id=c['id'],kind='field card',title=' / '.join(c['title']),search_labels=[c['area_short'],c['cue']],routes=[dict(document='5 x 7 cards',page=c['card_number'],file='Field Cards/QUICK CHARTS - 64 CARDS - 5x7.pdf'),dict(document='Letter card sheets',page=(c['card_number']+1)//2,file='Field Cards/QUICK CHARTS - 64 CARDS - LETTER PRINT.pdf')],area_number=c['area_number'],area_ids=[c['area_number']],location_labels=[c['area_short'],c['area_title']],location_relationship='Typical relevance; not a property finding or exclusive installation location'))
    kinds={'compact':'compact appendix','long':'long appendix','source':'original source','property':'property evidence'}
    for r in shelf_sg010.plan():
        if r['kind'] in kinds:entries.append(dict(id=r.get('id',r['file']),kind=kinds[r['kind']],title=r['title'],search_labels=[r['file']],routes=[dict(document=r['title'],page=1,file=r['file'])]))
    entries.append(dict(id='CC-S32-01',kind='historical illustration',title='3-way & 4-way switches',search_labels=SWITCH_ALIASES+['Code Check','switching diagram'],routes=[dict(document='Source Diagrams',sheet=1,page=1,file='Source Diagrams/CC-S32-01 - 3-Way and 4-Way Switches.pdf')],related_topics=['SG-010-L1:electric_devices'],card_ids=['QC-033','QC-047'],qualification='Source illustration, not a glossary definition or installation instruction.',publisher='Code Check',source_id='S32'))
    assert len({(e['id'],e['kind']) for e in entries})==len(entries)  # APP-x ids repeat across compact/long; the library keys those by kind
    # PDF layer: links on the compact location table + finder and the L1 subject index; bookmarks on the APP-D long cut.
    links={ed:pdf_links(ed,LAYER/f'STUDY GUIDE - {ed}.pdf',NAV/f'STUDY GUIDE - {ed}.pdf') for ed in ['SG-010','SG-010-L1']}
    bookmarks(LAYER/'Appendices'/Path(apd['pdf']).name,NAV/Path(apd['pdf']).name,term_pages,note_pages)
    finder=[p for p in links['SG-010']['pages'] if p!=1][0];idx=links['SG-010-L1']['pages']
    routes_line=f"Printed routes: SG-010 location table p.1 and finder p.{finder}; L1 contents pp.2-7 and subject index pp.{idx[0]}-{idx[-1]}; APP-D long glossary pp.{min(term_pages.values())}-{max(term_pages.values())}, numbered notes pp.{min(note_pages.values())}-{max(note_pages.values())}. Diagram: 3-way & 4-way switches, Source Diagrams, sheet 1."
    pins={str(p):sha(p) for p in [OUT/'study-guide.json',OUT/'study-guide-L1.json',OUT/'walking-cut.json',OUT/'page-index-L1.json',OUT/apd['path'].replace('.html','.json'),CARDS/'concordance.json',CARDS/'cards.json',LAYER/'contents-locations-SG-010.json']}
    nav=dict(schema='study-guide-navigation/1',issue=REV,parent=PARENT,derived=True,authority='Existing edition topics, APP-D definitions and notes, Field Card Concordance and the staged shelf rows; no global vocabulary admission',
        print_policy='Contents by subject/route; glossary explains meanings and distinctions; index accepts familiar words and abbreviations. Every printed cross-reference gives document title and page/sheet; source IDs remain secondary.',
        entries=entries,glossary_pages=term_pages,note_pages=note_pages,source_pins=pins,location_routes='contents-locations.json',visual_language='visual-language.json',pdf_internal_links=links,printed_routes=routes_line)
    save(NAV/'navigation.json',nav)
    (NAV/'FIND A SUBJECT.html').write_text(browse(nav,routes_line,packet=True),encoding='utf-8')
    (NAV/'navigation.html').write_text(browse(nav,routes_line),encoding='utf-8')
    kinds_count={k:sum(e['kind']==k for e in entries) for k in sorted({e['kind'] for e in entries})}
    policy=dict(issue=REV,parent=PARENT,roles={'contents':'Subject and physical route; exact titles from the edition','glossary':'APP-D owns definitions; paired terms retain distinct meanings','index':'Familiar search labels resolve to subjects and exact glossary pages','evidence':'Descriptive title first; stable recording/chart IDs secondary'},
        aliases_are='retrieval routes, not newly admitted definitions or equivalences',shared_entries=len(entries),entries_by_kind=kinds_count,glossary_bookmarks=len(term_pages),note_bookmarks=len(note_pages),subject_labels_added=len(ALIASES),
        PDF_internal_links_added={k:v['links'] for k,v in links.items()},linked_pages={k:v['pages'] for k,v in links.items()},print_growth_pages=0,
        acceptance_examples=['boiler -> Hydronic heat (L1) / chart 21 / APP-D Hartford Loop','switches -> electrical devices -> 3-way & 4-way switches, Source Diagrams 1','smoke alarm -> Rooms and alarms (L1) / QC-047 / N10','radon -> specialist boundary; does not assert a result'],
        governance='Derived from existing terms and records, following librarian distinction of location versus meaning; no global vocabulary or RTS admission')
    save(NAV/'navigation-review.json',policy);print(json.dumps(policy,indent=1))
if __name__=='__main__':main()
