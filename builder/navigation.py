"""Derived retrieval labels. Definitions remain owned by existing APP-D entries."""
from setup import *
import unicodedata
import pdfplumber
ALIASES={
 '3-way switches':'electric_devices','4-way switches':'electric_devices','Three-way switches':'electric_devices','Four-way switches':'electric_devices',
 'Light switches':'electric_devices','Switches':'electric_devices','Multi-location lighting':'electric_devices','Outlets':'electric_devices','Receptacles':'electric_devices',
 'Aluminum wiring':'electric_legacy','Knob-and-tube wiring':'electric_legacy','Main panel':'electric_panels',
 'Arc-fault protection':'electric_devices','Ground-fault protection':'electric_devices','Carbon monoxide':'furnace_safety',
 'Basement':'foundation_types','Cracks':'movement','Water stains':'interior_moisture','Leaks':'moisture','Peeling paint':'siding_coatings',
 'Sump pump':'drainage_pumps','Water heater':'water_heater_identity','Attic':'attic_environment','Deck ledger':'deck_connections',
 'Heat pump backup':'heatpump_modes','Plaster':'interior_facings','Condensation':'window_glazing','Flashing':'roof_flashing',
 'Grounding':'electric_service','Bonding':'electric_service','Furnace':'furnace_types','Roof leaks':'roof_flashing'}
SWITCH_ALIASES=['3-way switches','4-way switches','Three-way switches','Four-way switches','Light switches','Switches','Multi-location lighting']
def norm(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).casefold()).strip()
def locate_terms():
    terms=read(OUT/'Appendices/APP-D-v1.2.json')['terms'];found={}
    with pdfplumber.open(OUT/'Appendices/APP-D-v1.2.pdf') as pdf:
        for pn,p in enumerate(pdf.pages,1):
            crop=p.crop((52,40,176,746));text=norm(crop.extract_text() or '')
            for t in terms:
                if re.search(r'\b'+re.escape(norm(t['term']))+r'\b',text):
                    found.setdefault(t['term'],pn)
    missing=[t['term'] for t in terms if t['term'] not in found]
    assert not missing,missing
    return found
def main():
    long=read(OUT/'study-guide-L1.json');guide=read(OUT/'study-guide.json');w=read(OUT/'walking-cut.json')
    index=read(LIB/'SG-010-L1/page-index.json');short={p['id']:p for p in guide['pages']};compact=guide['long_cut_topic_map']
    glossary=read(OUT/'Appendices/APP-D-v1.2.json');cc=read(HERE/'card-baseline/concordance.json');cards=read(HERE/'card-baseline/cards.json')['cards'];term_pages=locate_terms()
    entries=[]
    for p in long['pages']:
        tid=p['id'];ct=compact[tid];card_ids=[c['card_id'] for c in cc['cards'] if 'SG-010-L1:'+tid in c['related_l1_topic_ids']]
        routes=[dict(edition='SG-010',title=short[ct]['title'],page=short[ct]['printed_page'],topic_id=ct),dict(edition='SG-010-L1',title=p['title'],page=index[tid],topic_id=tid)]
        routes.extend(dict(edition='SG-010-W1',title=q['title'],page=w['page_index'][q['id']],topic_id=q['id'],relationship='route context; not an equivalent treatment') for q in w['pages'] if ct in q['refs'])
        entries.append(dict(id='SG-010-L1:'+tid,kind='subject',title=p['title'],search_labels=[tid.replace('_',' ')]+[a for a,t in ALIASES.items() if t==tid],routes=routes,card_ids=card_ids,source_refs=p.get('refs',[])))
    for t in glossary['terms']:
        parts=t['term'].split(' / ')
        entries.append(dict(id='APP-D:term:'+re.sub('[^a-z0-9]+','-',t['term'].lower()).strip('-'),kind='definition',title=t['term'],search_labels=list(dict.fromkeys(parts+[t['expansion']])),meaning=t['definition'],paired_terms=parts if len(parts)>1 else [],label_relationship='Expanded name or component of a paired definition; paired terms are not asserted synonyms.',owner='APP-D-v1.2',topic_id=t['topic'],routes=[dict(document='APP-D long cut',page=term_pages[t['term']],file='Long Appendices/APP-D-v1.2.pdf')]))
    for c in cards:entries.append(dict(id=c['id'],kind='field card',title=' / '.join(c['title']),search_labels=[c['area_short'],c['cue']],routes=[dict(document='5 x 7 cards',page=c['card_number'],file='Field Cards/QUICK CHARTS - 64 CARDS - 5x7.pdf'),dict(document='Letter card sheets',page=(c['card_number']+1)//2,file='Field Cards/QUICK CHARTS - 64 CARDS - LETTER PRINT.pdf')],area_number=c['area_number']))
    m=read(TEAM/'Home Inspection Training/CURRENT EDITION/_Maintenance/manifest.json')
    for r in m['files']:
        if r['kind'] not in ['compact','long','source','property']:continue
        entries.append(dict(id=r.get('id',r['file']),kind={'compact':'compact appendix','long':'long appendix','source':'original source','property':'property evidence'}[r['kind']],title=r['title'],search_labels=[r['file']],routes=[dict(document=r['title'],page=1,file=r['file'])]))
    entries.append(dict(id='CC-S32-01',kind='historical illustration',title='3-way & 4-way switches',search_labels=SWITCH_ALIASES+['Code Check','switching diagram'],routes=[dict(document='Source Diagrams',sheet=1,page=1,file='Source Diagrams/CC-S32-01 - 3-Way and 4-Way Switches.pdf')],related_topics=['SG-010-L1:electric_devices'],card_ids=['QC-033','QC-047'],qualification='Source illustration, not a glossary definition or installation instruction.',publisher='Code Check',source_id='S32'))
    save(HERE/'navigation.json',dict(schema='study-guide-navigation/1',issue=REV,parent=PARENT,derived=True,authority='Existing edition topics, APP-D definitions, Field Card Concordance and current PDF manifest; no global vocabulary admission',print_policy='Contents by subject/route; glossary explains meanings and distinctions; index accepts familiar words and abbreviations. Every printed cross-reference gives document title and page/sheet; source IDs remain secondary.',entries=entries,glossary_pages=term_pages,source_pins={str(p):sha(p) for p in [LIB/'SG-010/study-guide.json',LIB/'SG-010-L1/study-guide.json',LIB/'SG-010-W1/study-guide.json',LIB/'SG-010/Appendices/APP-D-v1.2.json']}))
    print(json.dumps(dict(entries=len(entries),definitions=len(term_pages),added_subject_labels=len(ALIASES),max_index_entries=229+len(ALIASES))))
if __name__=='__main__':main()
