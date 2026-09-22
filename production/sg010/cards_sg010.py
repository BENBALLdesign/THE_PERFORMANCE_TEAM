"""SG-010 general field cards: 64 cards, native 5x7 + Letter (32 sheets), painted.

Performance Team work, not BBDF. Stages only into the Seed Bank work area
(WORK/'field-cards-64-sg010'); never writes CURRENT EDITION or Study Guide Editions.

Basis: the published SG-009 deck (baseline cards.json / concordance.json, incl.
E1 QC-033 four-path card and S32 QC-047 note). Every prior fact binding is carried
through an explicit SG-009 -> SG-010 alias map; new SG-010 (S38/S39 and later)
chart rows are ADDED to cards whose existing text they qualify. Card text and all
64 IDs / area groups are unchanged; source lines, footnotes, terms, pages and
safety emphasis are rebuilt from SG-010 data.

  python cards_sg010.py              build (fails closed if the review lock is stale)
  python cards_sg010.py --establish  re-review: replace this folder's review lock
"""
from pathlib import Path
import sys,json,copy,types,importlib.util,io,hashlib,shutil
PROD=Path(__file__).resolve().parent
from prepare import WORK,OUT as DATA,BUILDER,REPO,read,save,sha
sys.path.insert(0,str(BUILDER))
BASE=WORK/'baseline/SG-009'
PRIOR=BASE/'Appendices/Quick Charts - 64 Cards'
DEST=WORK/'field-cards-64-sg010'
PAINTED=DEST/'painted'
LOCK=PROD/'field-card-review-lock.json'
ALIAS_FILE=PROD/'field-card-fact-aliases-SG009-to-SG010.json'
REV='SG-010-C1-2026-09-21'
for forbidden in ('CURRENT EDITION','Study Guide Editions','Dropbox'):
    assert forbidden not in str(DEST),DEST

# ---- editorial additions (reviewed against SG-010 chart rows; text unchanged) ----
# card number -> {row index | 'note': [SG-010 topic:row-slug]}
ADD={
 1:{0:['scope:before-access']},
 6:{1:['interior_routes:escape-opening'],'note':['interior_routes:escape-opening']},
 8:{3:['scope:specialist-boundary'],'note':['scope:specialist-boundary']},
 18:{1:['interior_routes:doors']},
 23:{1:['life_safety:gfci-controls']},
 25:{2:['hydronic_electric:hot-water']},
 27:{0:['insulation:find-the-boundary'],1:['insulation:separate-controls']},
 33:{2:['hydronic_electric:hydro-air'],3:['hydronic_electric:heat-pump-backup'],'note':['hydronic_electric:heat-pump-backup']},
 44:{0:['interior_routes:safety-glazing'],'note':['interior_routes:safety-glazing']},
 45:{1:['interior_routes:doors'],'note':['interior_routes:doors']},
 46:{0:['interior_routes:stairs-guards'],1:['interior_routes:stairs-guards'],2:['interior_routes:stairs-guards'],'note':['interior_routes:stairs-guards','life_safety:fan-stair-route']},
 47:{1:['life_safety:gfci-controls'],2:['life_safety:gfci-controls','life_safety:smoke-co'],3:['life_safety:gfci-controls'],'note':['life_safety:gfci-controls']},
 48:{1:['scope:communicate-urgency'],2:['scope:communicate-urgency'],'note':['scope:communicate-urgency']},
 50:{0:['appliances:bath-return-below'],1:['appliances:bath-return-below'],2:['appliances:bath-return-below','interior_routes:floors']},
 53:{0:['appliances:dishwasher']},
 54:{3:['appliances:laundry-exhaust']},
 56:{0:['appliances:basin-disposal']},
 57:{2:['insulation:respect-material-access']},
 60:{0:['insulation:find-the-boundary','insulation:trace-ventilation'],1:['insulation:separate-controls'],'note':['insulation:find-the-boundary']},
 63:{3:['insulation:trace-ventilation','appliances:laundry-exhaust']},
 64:{0:['interior_routes:gas-factory-built'],1:['interior_routes:masonry-hearth'],'note':['interior_routes:masonry-hearth']},
}
ADD_TERMS={6:['Emergency escape and rescue opening'],27:['Air barrier'],33:['AUX / emergency heat','Hydro-air'],
 44:['Safety glazing'],46:['Winder / walkline'],47:['Smoke alarm / CO alarm'],53:['High loop / dishwasher air gap'],
 60:['Air barrier'],63:['Recirculating / exterior exhaust'],64:['Hearth extension','Factory-built fireplace']}
ADD_NOTES={6:['N14'],8:['N12'],18:['N14'],25:['N13'],27:['N11'],33:['N13'],44:['N14'],45:['N14'],46:['N14'],
 47:['N10'],48:['N12'],50:['N10'],53:['N10'],54:['N10'],56:['N10'],57:['N11'],60:['N11'],63:['N10'],64:['N14']}
# Safety emphasis: SG-009 E1 additions (33, 42) carried; SG-010 extends 44-46 and adds 47.
SAFETY_EXTRA={
 33:('Combustion / electrical inspection',['gas_heat:warning-signs','gas_heat:normal-control-sequence','service:before-panel-access','devices:pv-and-generators']),
 42:('Loose ceiling / movement',['movement:wall-shape','movement:crack-pattern']),
 44:('Damaged / safety glazing',['openings:read-the-glazing','interior_routes:safety-glazing']),
 45:('Exit function',['openings:doors-and-exits','interior_routes:doors']),
 46:('Falls',['site_decks:stairs-handrails-guards','interior_routes:stairs-guards']),
 47:('Alarms / protective devices',['life_safety:smoke-co','life_safety:gfci-controls']),
}

def load(name,path,patches=()):
    src=Path(path).read_text(encoding='utf-8')
    for a,b in patches:
        assert a in src,(name,a);src=src.replace(a,b)
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(src,str(path),'exec'),m.__dict__);return m

def pages_text(nums):
    nums=sorted(set(nums));out=[];i=0
    while i<len(nums):
        j=i
        while j+1<len(nums) and nums[j+1]==nums[j]+1:j+=1
        out.append(str(nums[i]) if j==i else (f'{nums[i]},{nums[j]}' if j==i+1 else f'{nums[i]}-{nums[j]}'));i=j+1
    return ','.join(out)

def main(establish=False):
    DEST.mkdir(parents=True,exist_ok=True)
    content=load('field_cards_64_content',BUILDER/'field_cards_64_content.py',
        [("HERE/'field-cards/cards.json'","HERE/'data/sg009/field-cards/cards.json'")])
    import field_card_bindings as bind
    import field_card_concordance as cc
    cc.LOCK=LOCK
    guide=read(cc.SOURCE);prior=read(PRIOR/'concordance.json');raw=read(PRIOR/'cards.json')['cards']
    oldguide=read(BASE/'study-guide.json')
    assert [c['id'] for c in raw]==[f'QC-{n:03d}' for n in range(1,65)]
    areas_before=[(c['id'],c['area_number'],c['area_short']) for c in raw]
    # Generic per-chart codes (same scheme as the S32 carry-forward).
    bind.ALIASES.clear();codes={};current={}
    for n,p in enumerate(guide['pages']):
        alias=f't{n:02}_';bind.ALIASES[alias]=p['id']
        for i,row in enumerate(p['rows']):
            fid='SG-010:'+p['id']+':'+cc.slug(row[0]);codes[fid]=alias+str(i);current[fid]=row
    bind.ALIASES['d']='dwv'  # pipes-card diagram labels bind d4 directly
    oldrows={'SG-009:'+p['id']+':'+cc.slug(r[0]):r for p in oldguide['pages'] for r in p['rows']}
    # ---- previous -> current alias map for every fact the SG-009 deck used ----
    aliases={}
    for fid,f in prior['facts'].items():
        new='SG-010:'+fid.split(':',1)[1]
        assert new in current,('stranded fact',fid)
        same=cc.digest(current[new])==cc.digest(oldrows[fid])
        aliases[fid]=dict(current=new,status='unchanged row' if same else 'same row label; SG-010 text revised',
            printed_page=dict(previous=f['printed_page'],current=next(p['printed_page'] for p in guide['pages'] if p['id']==f['topic_id'])))
    groups={};terms={};notes={};before={}
    for c,b in zip(raw,prior['cards']):
        n=c['card_number'];before[n]=dict(source=c['source'],terms=[prior['terms'][t]['term'] for t in b['term_ids']],footnotes=b['footnote_ids'])
        g=[next(x['fact_ids'] for x in b['expressions'] if x['path']==f'/rows/{i}/0') for i in range(len(c['rows']))]+[next(x['fact_ids'] for x in b['expressions'] if x['path']=='/note')]
        g=[[aliases[f]['current'] for f in grp] for grp in g]
        added=[]
        for key,fs in ADD.get(n,{}).items():
            k=len(c['rows']) if key=='note' else key
            for f in fs:
                fid='SG-010:'+f;assert fid in current,(n,fid)
                if fid not in g[k]:g[k].append(fid);added.append(fid)
        groups[n]=g
        terms[n]=list(dict.fromkeys(before[n]['terms']+ADD_TERMS.get(n,[])))
        notes[n]=sorted(dict.fromkeys([x.split(':')[-1] for x in b['footnote_ids']]+ADD_NOTES.get(n,[])))
    bind.BINDINGS[:]=[';'.join(' '.join(codes[f] for f in grp) for grp in groups[c['card_number']]) for c in raw]
    bind.NOTES[:]=[' '.join(x[1:] for x in notes[c['card_number']]) for c in raw]
    bind.TERMS.clear();bind.TERMS.update({n:t for n,t in terms.items() if t})
    content.catalog=lambda:copy.deepcopy(raw)
    if establish:
        if LOCK.exists():LOCK.unlink()
        cc.compile_cards(raw,establish_review=True)
        lock=read(LOCK);lock.update(review_date='2026-09-21',edition='SG-010',
            basis='SG-009 published deck (E1 QC-033, S32 QC-047) carried through the explicit fact alias map; SG-010 S38/S39/closing chart rows added where they qualify existing card text (see ADD in cards_sg010.py). No card wording changed.',
            prior_review_lock_sha256=sha(PRIOR/'review-lock.json'))
        save(LOCK,lock)
    import card_inspection_layer as inspection
    for n,v in SAFETY_EXTRA.items():inspection.SAFETY[n]=v
    # Shared linework helpers: read the SG-009 base eight; no import-time mkdir in Dropbox.
    load('field_cards_layer2',BUILDER/'field_cards_layer2.py',[
        ("BASE=HERE/'field-cards'","BASE=HERE/'data/sg009/field-cards'"),
        ("OUT=HERE/'field-cards-layer2';OUT.mkdir(exist_ok=True)","OUT=None  # SG-010 driver: layer-2 build() is never called")])
    r=load('field_cards_64',BUILDER/'field_cards_64.py',[
        ("OUT=WORK/'field-cards-64';OUT.mkdir(exist_ok=True)","OUT=WORK/'field-cards-64-sg010';OUT.mkdir(exist_ok=True)"),
        ("date='2026-09-20'","date='2026-09-21'"),
        ("These files live in BB_CODE/.scratch/sg009.","Builder modules live in the THE_PERFORMANCE_TEAM checkout (builder/); the SG-010 driver is production/sg010/cards_sg010.py.")])
    assert r.OUT==DEST
    # Compressed page ranges keep every source line on one 10 pt line.
    from reportlab.pdfbase.pdfmetrics import stringWidth
    for c in r.CARDS:
        b=next(x for x in r.CONCORDANCE['cards'] if x['card_id']==c['id'])
        nums=sorted({r.CONCORDANCE['facts'][f]['printed_page'] for e in b['expressions'] for f in e['fact_ids']})
        c['source']='SG-010 '+pages_text(nums)+' / '+','.join(x.split(':')[-1] for x in b['footnote_ids'])
        assert stringWidth(c['source'],'Helvetica',10)<=287,c['source']
    # QC-033 E1 four-path layout and MD marks (33, 34), carried from the SG-009 E1 build.
    from maryland_marker import drawing
    v=r.v
    def route(d,text,y):
        parts=text.split(' > ');gap=13;w=(320-gap*(len(parts)-1))/len(parts)
        for j,s in enumerate(parts):
            x=20+j*(w+gap);v.rect(d,x,y,w,19,1.2)
            v.txt(d,s,x+w/2,y+5,13,align='middle',width=w-5)
            if j<len(parts)-1:v.arrow(d,x+w+2,y+10,x+w+gap-2,y+10,1.1)
    def electrical_heat(d,c):
        rows=c['rows'];v.txt(d,rows[0][0],20,356,13,True,width=320);route(d,rows[0][1],330)
        v.txt(d,rows[1][0],20,315,13,True,width=320)
        lines=rows[1][1].splitlines();route(d,lines[0],291)
        v.txt(d,lines[1],20,278,12,width=320);v.txt(d,lines[2],20,264,12,width=320)
        v.txt(d,rows[2][0],20,246,13,True,width=320);route(d,rows[2][1],219)
        v.txt(d,rows[3][0],20,205,13,True,width=320);route(d,rows[3][1],181)
    r.LAYOUTS['heat']=electrical_heat
    base_make=r.make
    def make(c):
        d=base_make(dict(c,note='') if c['card_number']==33 else c)
        if c['card_number']==33:v.txt(d,c['note'],20,167,13,color=v.NAVY,width=320,leading=16)
        for s in d.contents:
            if getattr(s,'text',None)=='TWO PATHS':s.text='FOUR PATHS'
        if c['card_number'] in [33,34]:d.add(drawing(245,379,14));v.txt(d,'MD',256,375,9.5,True,r.HexColor('#007A9E'))
        return d
    r.make=make
    r.build()
    assert [(c['id'],c['area_number'],c['area_short']) for c in r.CARDS]==areas_before
    # ---- paint layer (SG-009 C1 visual language, card mode only) ----
    spec=importlib.util.spec_from_file_location('paint_sg009',BUILDER/'sg009-color-language/paint.py')
    paint=importlib.util.module_from_spec(spec);spec.loader.exec_module(paint)
    import palette_sg010;paint.AREA=palette_sg010.AREA   # P1: band tones re-tuned for grayscale separation
    import pdfplumber
    from pypdf import PdfReader,PdfWriter
    from reportlab.pdfgen.canvas import Canvas
    PAINTED.mkdir(exist_ok=True);painted=[]
    for fn,native in [(r.PDF,True),(r.LETTER,False)]:
        src=DEST/fn;reader=PdfReader(src);w=PdfWriter();w.clone_document_from_reader(reader);count=0
        with pdfplumber.open(src) as doc:
            for i,page in enumerate(w.pages):
                p=doc.pages[i];buf=io.BytesIO();cv=Canvas(buf,pagesize=(p.width,p.height),invariant=1)
                sel=[r.CARDS[i]] if native else r.CARDS[i*2:i*2+2]
                if native:count+=paint.rewrite_vectors(page,w,lambda x,y:sel[0]['area_number'],'card')
                else:count+=paint.rewrite_card_sheet(page,w,sel)
                for j,card in enumerate(sel):paint.card_overlay(cv,card,0 if native else (27 if j==0 else 405),0 if native else 54)
                cv.showPage();cv.save();page.merge_page(PdfReader(buf).pages[0])
        w.add_metadata({'/VisualLanguageRevision':REV,'/Title':reader.metadata.get('/Title','')})
        w.write(PAINTED/fn)
        out=PdfReader(PAINTED/fn);assert len(out.pages)==len(reader.pages)
        for a,b in zip(reader.pages,out.pages):
            ta=r.norm(a.extract_text());tb=r.norm(b.extract_text());assert ta in tb or all(t in tb for t in ta.split())
        painted.append(dict(file=fn,pages=len(out.pages),backgrounds_recoloured=count,sha256=sha(PAINTED/fn)))
    # ---- alias map, Walker check, change report ----
    after={b['card_id']:b for b in r.CONCORDANCE['cards']}
    new_facts={}
    for c in r.CARDS:
        for f in {f for e in after[c['id']]['expressions'] for f in e['fact_ids']}:
            if f not in {a['current'] for a in aliases.values()}:new_facts.setdefault(f,[]).append(c['id'])
    walker=[]
    for root in [BASE.parent/'SG-009-W1',BASE.parent/'505 Walker Ave']:
        for p in root.rglob('*.json'):
            t=p.read_text(encoding='utf-8',errors='ignore')
            for fid in aliases:
                if fid in t:walker.append(dict(file=str(p),fact=fid,current=aliases[fid]['current']))
            for c in r.CARDS:
                if c['id'] in t:walker.append(dict(file=str(p),card=c['id'],preserved=True))
    changes=[]
    for c in r.CARDS:
        n=c['card_number'];b=after[c['id']]
        changes.append(dict(card=c['id'],title=' / '.join(c['title']),source=dict(previous=before[n]['source'],current=c['source']),
            added_facts=sorted({f for e in b['expressions'] for f in e['fact_ids']}-{aliases[f]['current'] for f in prior['facts'] if f in aliases and any(f in e['fact_ids'] for e in next(x for x in prior['cards'] if x['card_id']==c['id'])['expressions'])}),
            revised_carried_facts=sorted({f for e in b['expressions'] for f in e['fact_ids'] if any(a['current']==f and a['status']!='unchanged row' for a in aliases.values())}),
            added_terms=[t for t in terms[n] if t not in before[n]['terms']],
            added_footnotes=[x for x in notes[n] if 'APP-D:'+x not in before[n]['footnotes']],
            safety=c['safety'].get('focus') if c['safety']['marked'] else None))
    amap=dict(schema='field-card-fact-aliases/1',previous_edition='SG-009',current_edition='SG-010',
        rule='Every SG-009 card fact resolves to exactly one SG-010 fact (same chart id + row label slug). New SG-010 facts have no predecessor and are listed separately. Card IDs QC-001..QC-064 and area groups are unchanged.',
        previous_to_current={k:v['current'] for k,v in aliases.items()},details=aliases,
        new_sg010_facts={k:dict(cards=sorted(v),row=current[k]) for k,v in sorted(new_facts.items())},
        card_id_map={c['id']:c['id'] for c in r.CARDS},walker_references=walker,
        stranded=[k for k,v in aliases.items() if v['current'] not in current])
    save(ALIAS_FILE,amap);shutil.copy2(ALIAS_FILE,DEST/ALIAS_FILE.name)
    report=dict(revision=REV,edition='SG-010',cards=64,painted=painted,unpainted=[str(DEST/r.PDF),str(DEST/r.LETTER)],
        changed_bindings=[x for x in changes if x['added_facts'] or x['added_terms'] or x['added_footnotes'] or x['revised_carried_facts']],
        all_cards=changes,safety_flagged=sorted(k for k in inspection.SAFETY),alias_map=str(ALIAS_FILE),
        maryland_marks=['QC-033','QC-034'],publish='not performed; staged in Seed Bank only')
    save(DEST/'sg010-card-update.json',report)
    print(json.dumps(dict(painted=painted,changed=len(report['changed_bindings']),new_facts=len(new_facts),walker_refs=len(walker),stranded=amap['stranded'])))

if __name__=='__main__':main('--establish' in sys.argv)
