"""SG-010 location-based contents pages (post-render layer 1). Stages only; never publishes.

Adapted from BB_CODE/.scratch/sg009-location-contents/contents.py (no freeze/package steps).
Reads the unlayered renders + page-index JSONs in the Seed Bank `output`; writes
`output/layered/_stage/` PDFs and `output/layered/contents-locations-SG-010.json`.
Pages are derived from the current page indexes and the L1 outline, never old positions.
Only the compact cover (p.1) and the L1 contents leaves (the pages before the housing chart)
are replaced; every other page is byte-checked unchanged.
Usage: python -X utf8 -B contents_sg010.py
"""
import sys,io,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from prepare import OUT,REPO,BUILDER,read,save,sha
sys.path.insert(1,str(REPO));sys.path.insert(2,str(BUILDER))
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor,white
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject
from pypdf.annotations import Link
import team_paths
import card_brand
from maryland_marker import crab

LAYER=OUT/'layered';STAGE=LAYER/'_stage'
_pal=json.loads(team_paths.brand('tokens/palette.json').read_text(encoding='utf-8-sig'))['color']
NAVY=HexColor(_pal['navy']['primary']['$value']);CRIMSON=HexColor(_pal['crimson']['accent']['$value'])
GRAY=HexColor('#D0D0D0');TINT=HexColor('#F3F3F7')
FONT='Helvetica';BOLD='Helvetica-Bold'
DATE='SG-010 / 21 SEP 2026'

# The eight existing Field Card Concordance area packs, plus a broad-scope marker (not a ninth pack).
AREAS={1:'Site',2:'Exterior',3:'Garage',4:'Lowest level',5:'Systems',6:'Rooms / stairs',7:'Wet rooms',8:'Attic / roof',0:'Throughout'}
SHORT={0:'Throughout',1:'Site',2:'Exterior',3:'Garage',4:'Lowest',5:'Systems',6:'Rooms',7:'Wet',8:'Roof'}
# Compact charts. A location is a finding route, never a guarantee of installation or access.
LOC={
 'method':[0],'foundation_water':[4,1],'load_paths':[0],'movement':[0],
 'roof_structure':[8],'walls':[2],'openings':[2,6],'site_decks':[1,2],
 'garage':[3],'roof_cover':[8,1],'water':[5,7],'dwv':[7,4],
 'water_heat':[5],'gas':[5,2],'service':[2,5],'circuits':[0],
 'devices':[0],'gas_heat':[5,8],'furnace_service':[5],'oil_heat':[5],
 'cooling':[2,5,6],'heatpumps':[1,5,6],
 # SG-010 charts (S33-S39)
 'hydronic_electric':[5,6],'insulation':[8,4],'appliances':[7],'life_safety':[6],
 'interior_routes':[6],'scope':[0]}
# Finer L1 locations override the compact chart they belong to.
OVERRIDES={
 'inspection_method':[0],'reporting':[0],'exterior_scope':[2,1],
 'site_exterior_report':[2,1],'site_access_limits':[1],'seasonal_and_pool_scope':[1],
 'foundation_types':[4],'moisture':[4],'drainage':[4,1],
 'crawl_access':[4],'crawl_moisture':[4],'crawl_openings':[4],
 'access_and_services':[4],'slab_evidence':[4],'post_tension':[4],
 'supports':[4],'notches_and_holes':[4,8],'engineered_and_connections':[0],
 'wall_systems':[2,6],'stud_cuts':[2,6],'special_walls':[2],
 'cantilevers_openings':[2,6],'masonry_systems':[2],'masonry_distress':[2],
 'floor_terms':[6,4],'floor_layers':[6,4],'interior_facings':[6],
 'interior_moisture':[6,7],'manufactured_structure':[0],
 'roof_forms':[8],'roof_cover_condition':[8],'roof_flashing':[8,2],
 'roof_penetrations':[8],'chimney_parts':[8,5],
 'siding_kickout_path':[2,8],'steps_stoops':[2],'rails_guards':[2,6],
 'porch_supports':[2],'deck_condition':[2],'deck_connections':[2],
 'balcony_connections':[2],'walks_patios':[1],'grading_vegetation':[1],
 'window_wells':[4,1],'retaining_wall_types':[1],'retaining_wall_drainage':[1],
 'water_supply':[5,1],'plumbing_materials':[5,7],'backflow_dwv':[7,5],
 'plumbing_fixture_checks':[7],'dwv_traps_vents':[7,8],'drainage_pumps':[4],
 'electric_service':[2,5],'electric_panels':[5],'electric_conductors':[5],
 'electric_alternative':[2,5,8],'heating_controls':[5,6],
 'combustion_air':[5],'furnace_types':[5],'furnace_safety':[5],
 'furnace_airflow':[5,6],'oil_storage':[1,5],'ductless_cooling':[6,2],
 'geothermal':[1,5],
 # SG-010 topics
 'professional_scope':[0],'special_service_boundaries':[0,1],'report_workflow':[0],
 'insulation_materials':[8,4],'air_vapor_thermal':[8,2],'ventilation_exhaust':[8,7],
 'hydronic_systems':[5,6],'steam_systems':[5,6],'electric_heat_delivery':[5,6],
 'cooling_scope':[5,2],'cooling_water_air':[5,2],
 'kitchen_appliances':[7],'kitchen_waste':[7],'bath_laundry':[7],'interior_life_safety':[6,7],
 'floor_finishes':[6],'safety_glazing':[6,7],'egress_openings':[6,4],'interior_doors':[6],
 'interior_stairs':[6],'fireplace_masonry':[6,8],'fireplace_factory_gas':[6,5]}
LABELS={(4,1):'Lowest + site',(2,6):'Exterior + rooms',(1,2):'Site + exterior',(8,1):'Roof + site',
 (5,7):'Systems + wet',(7,4):'Wet + lowest',(5,2):'Systems + outside',(2,5):'Outside + systems',
 (5,8):'Systems + roof',(2,5,6):'Outside + inside',(1,5,6):'Site + inside',(2,1):'Exterior + site',
 (4,8):'Lowest + attic',(6,4):'Rooms + lowest',(2,8):'Exterior + roof',(5,1):'Systems + site',
 (7,5):'Wet + systems',(7,8):'Wet + roof',(2,5,8):'Outside + systems',(5,6):'Systems + rooms',
 (1,5):'Site + systems',(6,2):'Rooms + outside',(6,7):'Rooms + wet',(8,2):'Roof + exterior',
 (8,5):'Roof + systems',(8,4):'Attic + lowest',(8,7):'Attic + wet',
 (0,1):'Throughout + site',(6,8):'Rooms + chimney',(6,5):'Rooms + systems'}
def location_label(ids):
    if len(ids)==1:return AREAS[ids[0]]
    return LABELS.get(tuple(ids),' + '.join(SHORT[i] for i in ids))

def locations():
    s=read(OUT/'study-guide.json');l=read(OUT/'study-guide-L1.json')
    sm=read(OUT/'page-index.json');lm=read(OUT/'page-index-L1.json')
    tmap=s['long_cut_topic_map'];records={}
    missing=[p['id'] for p in s['pages'] if p['id'] not in LOC]+[p['id'] for p in l['pages'] if p['id'] not in OVERRIDES and tmap.get(p['id']) not in LOC]
    assert not missing,missing
    for p in s['pages']:
        assert sm[p['id']]==p['printed_page'],p['id']
        records['SG-010:'+p['id']]=dict(edition='SG-010',topic_id=p['id'],title=p['title'],area_ids=LOC[p['id']],page=sm[p['id']],
            companion_page=min(lm[t] for t in p['topics']),companion_topic_ids=p['topics'],
            companion_relationship='entry page to linked L1 treatment; related topics can be elsewhere')
    for p in l['pages']:
        target=tmap[p['id']]
        records['SG-010-L1:'+p['id']]=dict(edition='SG-010-L1',topic_id=p['id'],title=p['title'],area_ids=OVERRIDES.get(p['id'],LOC[target]),
            page=lm[p['id']],companion_page=sm[target],companion_topic_ids=[target],companion_relationship='related compact synthesis; not equivalent detail')
    data=dict(schema='study-guide-contents-locations/1',issue='SG-010 staged layer (unpublished)',parent='SG-009 S32-C1-2026-09-21',derived=True,
        basis='Editorial location mapping to the eight existing Field Card Concordance area packs; no property findings, definitions or global vocabulary admission.',
        meaning='Typical places to look; systems can cross locations. Throughout means broad or distributed relevance. Markers do not establish access or installation.',
        areas=[dict(id=i,label=AREAS[i]) for i in AREAS],
        terminology={'Systems':'Mechanical and electrical equipment locations, including distributed equipment where installed','Wet rooms':'Kitchen, baths and laundry','Lowest level':'Slab, basement and crawl-space foundations','Rooms / stairs':'Habitable rooms, interior doors, glazing, stairs and room-side fireplaces','Throughout':'Broad or distributed relevance; not an additional card pack'},
        records=records,source_pins={n:sha(OUT/n) for n in ['study-guide.json','study-guide-L1.json','page-index.json','page-index-L1.json','STUDY GUIDE - SG-010.pdf','STUDY GUIDE - SG-010-L1.pdf']})
    save(LAYER/'contents-locations-SG-010.json',data);return data

def house(c,x,y,area,size=17):
    c.saveState();c.translate(x,y);c.scale(size/42,size/42)
    c.setStrokeColor(NAVY);c.setFillColor(NAVY);c.setLineWidth(1.6)
    c.line(6,5,36,5);c.line(6,5,6,23);c.line(36,5,36,23)
    p=c.beginPath();p.moveTo(3,23);p.lineTo(21,34);p.lineTo(39,23);p.close();c.drawPath(p)
    c.setLineWidth(3.4)
    if area==1:c.line(0,0,42,0)
    elif area==2:c.line(6,5,6,23);c.line(36,5,36,23)
    elif area==3:c.rect(26,5,15,13,fill=1,stroke=0)
    elif area==4:c.rect(8,6,26,6,fill=1,stroke=0)
    elif area==5:c.rect(24,6,8,13,fill=1,stroke=0);c.line(27,19,27,30)
    elif area==6:c.rect(9,14,12,7,fill=1,stroke=0)
    elif area==7:c.rect(24,14,9,7,fill=1,stroke=0)
    elif area==8:
        p=c.beginPath();p.moveTo(8,24);p.lineTo(21,32);p.lineTo(34,24);p.close();c.drawPath(p,fill=1,stroke=0)
    else:
        c.setLineWidth(1.8);c.line(10,9,32,9);c.line(10,16,32,16);c.line(15,25,27,25)
    c.restoreState()

def txt(c,t,x,y,size=9.5,bold=False,color=NAVY):
    c.setFillColor(color);c.setFont(BOLD if bold else FONT,size);c.drawString(x,y,t)
def wrap(t,w=280,size=9.5,bold=False):
    out=[];line=''
    for word in t.split():
        n=(line+' '+word).strip()
        if line and stringWidth(n,BOLD if bold else FONT,size)>w:out.append(line);line=word
        else:line=n
    if line:out.append(line)
    return out

def frame(c,compact,n):
    """Same geometry as the SG-010 DesignDoc header/footer, including the live vector brand."""
    c.saveState();c.setFillColor(NAVY);c.setFont(BOLD,8.5);c.drawString(54,772,'BEN BALL / HOME INSPECTION')
    mark=Drawing(12,28);card_brand.mark(mark,0,0,12);renderPDF.draw(mark,c,575,759)
    c.setFont(BOLD,9);c.drawRightString(558,772,'FIELD GUIDE' if compact else 'REFERENCE VOLUME')
    c.setStrokeColor(CRIMSON);c.setLineWidth(1.5);c.line(54,761,558,761)
    c.setStrokeColor(NAVY);c.setLineWidth(.7);c.line(54,32,558,32);c.setFillColor(NAVY)
    c.setFont(FONT,8);c.drawString(54,17,('SG-010 | COMPACT | ' if compact else 'L1 | LONG CUT | ')+DATE)
    c.drawRightString(558,17,str(n));c.restoreState()

def key(c,top):
    for j,(a,label) in enumerate(AREAS.items()):
        row,col=divmod(j,5);x=54+col*103;y=top-row*19
        house(c,x,y-2,a,16);txt(c,label,x+20,y+2,8.6)
    txt(c,'Systems = mechanical / electrical; wet rooms = kitchen / baths / laundry; lowest = slab / basement / crawl.',54,top-36,8.4)
    return top-46

def table_head(c,y,compact):
    c.setFillColor(NAVY);c.rect(54,y-20,504,20,fill=1,stroke=0)
    for x,t in [(61,'Topic'),(354,'Where to look'),(501,'SG' if compact else 'L1'),(533,'L1' if compact else 'SG')]:txt(c,t,x,y-13.5,9.3,True,white)
    return y-20

def row_height(r,single,size,lead):
    if r.get('group'):return 20
    return max(single,len(wrap(r['title'],284,size))*lead+6.5)

def row(c,y,r,idx,links,single=18,size=9,lead=10.6):
    group=r.get('group',False);lines=wrap(r['title'],284,size,group);height=row_height(r,single,size,lead)
    c.setFillColor(HexColor('#E6E6EF') if group else (TINT if idx%2 else white));c.rect(54,y-height,504,height,fill=1,stroke=0)
    first=y-height/2-3+(len(lines)-1)*lead/2
    for j,t in enumerate(lines):txt(c,t,61,first-j*lead,size,group)
    mid=y-height/2
    if r.get('area_ids') is not None:
        ids=r['area_ids'];sz=14 if len(ids)==1 else 11.5;step=12.5
        for n,a in enumerate(ids):house(c,353+n*step,mid-5.5,a,sz)
        label=location_label(ids);lx=372 if len(ids)==1 else 353+len(ids)*step+4;ls=8.6
        while stringWidth(label,FONT,ls)>496-lx and ls>7.4:ls-=.2
        assert stringWidth(label,FONT,ls)<=496-lx,(label,ls)
        txt(c,label,lx,mid-3,ls)
    txt(c,str(r['page']),501,mid-3,9.3,True)
    if r.get('companion_page'):txt(c,str(r['companion_page']),533,mid-3,9.3)
    links.append(dict(rect=[54,y-height,528,y],target=r['page']))
    c.setStrokeColor(GRAY);c.setLineWidth(.3);c.line(54,y-height,558,y-height)
    return y-height

def compact_page(data):
    buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(612,792),invariant=1);frame(c,True,1)
    recs=[x for x in data['records'].values() if x['edition']=='SG-010']
    last=max(r['page'] for r in recs)+1
    txt(c,'HOME INSPECTION · SG-010',54,731,16,True)
    txt(c,'Field comparisons and colleague discussions',54,707,11,True)
    intro='For an experienced construction professional working in Baltimore City and Anne Arundel, Baltimore, Carroll, Harford and Howard counties. Start with the local stock on pp. 2-3; use the component charts to sharpen an observation, comparison or conversation.'
    for j,t in enumerate(wrap(intro,504,9.5)):txt(c,t,54,688-j*12,9.5)
    crab(c,43,691,12)
    n=len(PdfReader(OUT/'STUDY GUIDE - SG-010.pdf').pages)
    txt(c,f'{n} pages / {n//2} sheets duplex. Print at actual size. Each topic stays on one page. SG-010-L1 holds the complete topic',54,648,8.9)
    txt(c,'treatment; the eight appendices print separately.',54,637,8.9)
    y=table_head(c,628,True);links=[]
    for j,r in enumerate(recs):y=row(c,y,r,j,links,single=16.6,size=9,lead=10.4)
    notes=['SG = this guide. L1 = entry page to the fuller treatment; related topics may be elsewhere.',
     'House markers show typical places to look, not installation or access; systems cross areas. Throughout = broad relevance.',
     'Systems = mechanical / electrical; wet rooms = kitchen / baths / laundry; lowest = slab / basement / crawl; rooms incl. stairs.',
     f'Subject finder and appendix routes: p. {last}. COURSE / EXAM / NOTE / LOCAL distinguish source basis; terms and notes: APP-D.']
    for j,t in enumerate(notes):txt(c,t,54,y-13-j*10.6,8.2)
    bottom=y-13-(len(notes)-1)*10.6
    assert bottom>40,bottom
    c.showPage();c.save();return PdfReader(buf).pages[0],links,bottom

def long_rows(data,reader):
    bytitle={r['title']:r for r in data['records'].values() if r['edition']=='SG-010-L1'}
    sm=read(OUT/'page-index.json');rows=[]
    def flatten(xs):
        for o in xs:
            if isinstance(o,list):flatten(o);continue
            pg=reader.get_destination_page_number(o)+1
            if o.title in bytitle:rows.append(dict(bytitle[o.title]))
            elif o.title.startswith('Where the housing'):rows.append(dict(title=o.title,page=pg,companion_page=sm['regional_focus'],area_ids=[0]))
            elif o.title.startswith('From local stock'):rows.append(dict(title=o.title,page=pg,companion_page=sm['field_routes'],area_ids=[0]))
            elif o.title.startswith('Subject index'):rows.append(dict(title=o.title,page=pg,companion_page=sm['subject_index'],area_ids=[0]))
            else:rows.append(dict(title=o.title,page=pg,group=True))
    flatten(reader.outline)
    got={r['topic_id'] for r in rows if 'topic_id' in r}
    assert got==set(r['topic_id'] for r in bytitle.values()),set(r['topic_id'] for r in bytitle.values())-got
    return rows

def paginate(rows,capacity):
    h=lambda r:row_height(r,18,9,10.6)
    pages=[];pending=rows[:];section=None
    while pending:
        used=0;page=[]
        if section and not pending[0].get('group'):
            cont=dict(section,title=section['title']+' (continued)');page.append(cont);used=h(cont)
        while pending:
            r=pending[0];need=h(r)
            if r.get('group'):need+=sum(h(x) for x in pending[1:3])
            if used+need>capacity:break
            page.append(pending.pop(0));used+=h(r)
            if r.get('group'):section=r
        assert page;pages.append(page)
    return pages

def long_pages(data):
    reader=PdfReader(OUT/'STUDY GUIDE - SG-010-L1.pdf');pl=read(OUT/'page-index-L1.json')
    rows=long_rows(data,reader)
    # Contents leaves: from page 2 up to (not including) the first outline page (housing chart).
    first_body=min(r['page'] for r in rows);leaves=list(range(2,first_body));count=len(leaves)
    MAX=566;assert len(paginate(rows,MAX))<=count,('contents need more leaves than rendered',len(paginate(rows,MAX)),count)
    cap=MAX
    while cap>300 and len(paginate(rows,cap-4))<=count:cap-=4   # balance the leaves
    pages=paginate(rows,cap)
    while len(pages)<count:pages.append([])
    buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(612,792),invariant=1);all_links=[]
    for i,page in enumerate(pages):
        frame(c,False,leaves[i]);txt(c,f'CONTENTS / {i+1} OF {count}',54,736,17,True)
        txt(c,'L1 = this volume. SG = related compact chart; not equivalent detail.',54,717,9.3)
        txt(c,'Typical locations, not installation guarantees. Use the labels with the house symbols.',54,704,9.1)
        y=key(c,680);y=table_head(c,y,False);links=[]
        for j,r in enumerate(page):y=row(c,y,r,j,links)
        assert y>=40,(i,y)
        all_links.append(links);c.showPage()
    c.save();return PdfReader(buf),all_links,pages,leaves

def patch_pdf(src,dest,replacements,links):
    old=PdfReader(src);w=PdfWriter();w.clone_document_from_reader(old)
    for index,new in replacements.items():
        for k in ['/Contents','/Resources']:w.pages[index][NameObject(k)]=new.raw_get(k).clone(w)
        w.pages[index].pop(NameObject('/Annots'),None)
        for link in links[index]:w.add_annotation(index,Link(rect=link['rect'],target_page_index=link['target']-1))
    w.add_metadata({'/ContentsRevision':'SG-010 location contents (staged)'});dest.parent.mkdir(parents=True,exist_ok=True)
    with open(dest,'wb') as f:w.write(f)
    new=PdfReader(dest);assert len(new.pages)==len(old.pages)
    for i,(a,b) in enumerate(zip(old.pages,new.pages)):
        if i not in replacements:assert a.get_contents().get_data()==b.get_contents().get_data(),(dest,i)
    return len(new.pages)

def build():
    data=locations()
    page,clinks,bottom=compact_page(data)
    n1=patch_pdf(OUT/'STUDY GUIDE - SG-010.pdf',STAGE/'STUDY GUIDE - SG-010.pdf',{0:page},{0:clinks})
    doc,links,pages,leaves=long_pages(data)
    n2=patch_pdf(OUT/'STUDY GUIDE - SG-010-L1.pdf',STAGE/'STUDY GUIDE - SG-010-L1.pdf',{p-1:doc.pages[i] for i,p in enumerate(leaves)},{p-1:links[i] for i,p in enumerate(leaves)})
    save(LAYER/'contents-layout.json',dict(compact_bottom=bottom,compact_links=len(clinks),long_leaves=leaves,
        long_pages=[{'page':leaves[i],'rows':len(pg),'titles':[r['title'] for r in pg]} for i,pg in enumerate(pages)],pages={'SG-010':n1,'SG-010-L1':n2}))
    print('contents: SG-010',n1,'pp (p.1 replaced); L1',n2,'pp (leaves',leaves,'rows',[len(p) for p in pages],')')

if __name__=='__main__':build()
