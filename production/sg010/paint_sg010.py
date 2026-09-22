"""SG-010 colour/pattern/area cues + safety crosses + Maryland crab (post-render layer 2).

Stages only; never freezes, packages or publishes. Adapted from
BB_CODE/.scratch/sg009-color-language/paint.py, .scratch/sg010/edition_inspection_layer.py (cross
only; no card sketch bands) and .scratch/sg010/mark_maryland.py (no import-time side effects).
Inputs: contents-staged guides in output/layered/_stage (run contents_sg010.py first), the W1
render and the current long/compact appendices in output. Outputs: output/layered/<same paths>
plus output/layered/layers-report.json. Unlayered renders are left untouched.
Flags are cues, not findings or risk scores. Guides and appendices only (field cards excluded).
Usage: python -X utf8 -B paint_sg010.py
"""
import sys,io,re,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from prepare import OUT,BUILDER,read,save,sha
sys.path.insert(1,str(BUILDER))
import pdfplumber
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream,FloatObject,NameObject
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor,Color,white
from maryland_marker import crab,MEANING as MD_MEANING

LAYER=OUT/'layered';STAGE=LAYER/'_stage'
from palette_sg010 import AREA,label_ink   # P1: C1 hues re-tuned in lightness so every band separates in grayscale
NAVY=HexColor('#1A1A5E');REF=HexColor('#424956')
SAFETY_COLOR='#B3262E';RED=HexColor(SAFETY_COLOR)
SAFETY_MEANING='Red cross = safety-related topic; assess the actual condition. An unmarked item is not a safety clearance.'
VERSIONS=dict(A='1.8',B='1.7',C='1.9',D='1.3',E='1.4',F='1.3',G='1.3',H='1.2')
# L1 table-row labels flagged as safety-relevant (SG-009 set carried + SG-010 topics).
LONG_FLAGS={
 'post_tension':['Tendon protection'],'supports':['Column or post','Base and footing'],
 'roof_ties':['Rafter tie','Collar tie'],'roof_trusses':['Modification','Bearing / orientation'],
 'window_glazing':['Cracked or broken glass','Tempered and laminated glass'],
 'rails_guards':['Handrail','Guard','Connections'],
 'garage_doors':['Stop condition','Two safety functions','Testing'],
 'backflow_dwv':['Potable protection'],'dwv_traps_vents':['Trap seal'],
 'water_heater_relief':['Purpose','Discharge','Watts 210','Action'],
 'electric_panels':['Before access','Protection'],
 'electric_alternative':['Multiple supplies'],'furnace_safety':['Warning signs','High limit'],
 'oil_burners':['Controls','Failed ignition'],
 'drainage':['Electrical concern or unsafe access'],'water_supply':['Access hazard'],
 'insulation_materials':['Heat / wiring / foam','Vermiculite concern'],
 'ventilation_exhaust':['Bathroom / dryer / hood'],
 'hydronic_systems':['Pressure / expansion'],'steam_systems':['Water level / protection'],
 'electric_heat_delivery':['Clearance / protection'],
 'kitchen_appliances':['Range stability'],'bath_laundry':['Hydromassage tub','Dryer exhaust'],
 'interior_life_safety':['GFCI / controls','Smoke / CO','Alarm placement'],
 'safety_glazing':['Doors / sidelights','Large panels / wet areas','Stairs / guards'],
 'egress_openings':['Clear opening','Covers / bars / locks'],
 'interior_doors':['Locks / orientation'],
 'interior_stairs':['Handrail','Guard / balusters','Winders / spiral'],
 'fireplace_masonry':['Hearth / extension','Combustible clearance','Flue / chimney'],
 'fireplace_factory_gas':['Vent type','Vent-free units'],
 'special_service_boundaries':['Radon','Lead / suspect asbestos'],
}
# Compact chart tile titles: a narrow safety vocabulary, reported for review in layers-report.json.
COMPACT_SAFE=re.compile(r'\b(backflow|relief|T&P|panel access|combustion|spillage|smoke|CO|alarms?|GFCI|AFCI|glazing|escape|stairs?|guards?|handrails?|ledger|springs?|reversal|photoeye|fireplaces?|hearths?|range|dryer|locks?|CSST|vent-free|carbon)\b',re.I)
MD_WORDS={'Maryland','MD','Baltimore','COMAR','Harford','Howard','Carroll','Arundel'}
# Exact compact tiles whose title is too general for the vocabulary (a trapping lock on an interior door).
COMPACT_SAFE_TILES={('interior_routes','Doors')}
MD_CAP=3
# APP-H compact is a jurisdiction lookup: every row that leads with a jurisdiction gets its crab where there is space.
MD_ROW_DOCS={('compact','APP-H')}

def rgb(a):return tuple(HexColor(AREA[a][0]).rgb())
def tint(a,p=.19):return tuple(1-p+p*x for x in rgb(a))
def normalized(s):return re.sub(r'[^a-z0-9]','',s.casefold())
def point(m,x,y):return m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]
def mul(a,b):return (a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5])
def typical(ids):return 5 if 5 in ids else 4 if 4 in ids else ids[0] if ids else 0
def overlaps(a,b):return min(a['x1'],b['x1'])-max(a['x0'],b['x0'])>.1 and min(a['bottom'],b['bottom'])-max(a['top'],b['top'])>.1

def pattern(c,x,y,w,h,kind):
    c.saveState();p=c.beginPath();p.rect(x,y,w,h);c.clipPath(p,stroke=0,fill=0)
    if kind=='limit':
        c.setFillColor(Color(.97,.92,.72));c.rect(x,y,w,h,stroke=0,fill=1);c.setStrokeColor(HexColor('#8A6810'));c.setLineWidth(.65)
        for v in range(-int(h)-4,int(w)+5,5):c.line(x+v,y,x+v+h,y+h)
    else:
        c.setFillColor(Color(.90,.92,.95));c.rect(x,y,w,h,stroke=0,fill=1);c.setFillColor(REF)
        for xx in range(2,int(w),4):
            for yy in range(2,int(h),4):c.circle(x+xx,y+yy,.55,fill=1,stroke=0)
    c.restoreState()

def cross(c,x,y,size=7):
    c.setFillColor(RED);bar=size*.28
    c.rect(x-bar/2,y-size/2,bar,size,fill=1,stroke=0);c.rect(x-size/2,y-bar/2,size,bar,fill=1,stroke=0)

def rewrite_vectors(page,owner,selector):
    """Recolour navy/pale table and tile backgrounds only; never text, images, logos or marks."""
    cs=ContentStream(page.get_contents(),owner);out=[];m=(1,0,0,1,0,0);fill=(0,0,0);stack=[];pts=[];count=0
    for operands,op in cs.operations:
        if op==b'q':stack.append((m,fill))
        elif op==b'Q':
            if stack:m,fill=stack.pop()
        elif op==b'cm':m=mul(m,tuple(map(float,operands)))
        elif op==b'rg':fill=tuple(map(float,operands))
        elif op==b'g':fill=(float(operands[0]),)*3
        elif op==b're':
            x,y,w,h=map(float,operands);pts+=[point(m,x,y),point(m,x+w,y),point(m,x+w,y+h),point(m,x,y+h)]
        elif op in [b'm',b'l']:pts.append(point(m,*map(float,operands)))
        elif op in [b'c',b'v',b'y']:pts=[]
        if op in [b'f',b'f*',b'B',b'B*',b'b',b'b*',b'S',b's',b'n']:
            colour=None
            if pts and op in [b'f',b'f*',b'B',b'B*']:
                xs=[p[0] for p in pts];ys=[p[1] for p in pts];x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys);w=x1-x0;h=y1-y0
                rect=len(set((round(x,2),round(y,2)) for x,y in pts))==4 and all(abs(x-x0)<.1 or abs(x-x1)<.1 for x,y in pts) and all(abs(y-y0)<.1 or abs(y-y1)<.1 for x,y in pts)
                inside=53<=x0<x1<=559 and 52<=y0<y1<=750
                if rect and inside and w>65 and 10<h<200:
                    a=selector((x0+x1)/2,(y0+y1)/2)
                    navy=max(abs(fill[i]-rgb(5)[i]) for i in range(3))<.04
                    pale=min(fill)>.82 and max(fill)-min(fill)<.10 and min(fill)<.995
                    if navy:colour=rgb(a)
                    elif pale:colour=tint(a,.14)
            if colour:
                out.append(([FloatObject(v) for v in colour],b'rg'));out.append((operands,op));out.append(([FloatObject(v) for v in fill],b'rg'));count+=1
            else:out.append((operands,op))
            pts=[];continue
        out.append((operands,op))
    cs.operations=out;page[NameObject('/Contents')]=cs;return count

def find_start(lines,title):
    key=normalized(title);prefix=key[:min(34,len(key))]
    for l in lines:
        s=normalized(l['text'])
        if prefix and (prefix in s or (len(s)>20 and key.startswith(s))):return l
    return None

def documents():
    docs=[dict(file='STUDY GUIDE - SG-010.pdf',src=STAGE/'STUDY GUIDE - SG-010.pdf',kind='guide',edition='SG-010'),
          dict(file='STUDY GUIDE - SG-010-L1.pdf',src=STAGE/'STUDY GUIDE - SG-010-L1.pdf',kind='guide',edition='SG-010-L1'),
          dict(file='STUDY GUIDE - SG-010-W1.pdf',src=OUT/'STUDY GUIDE - SG-010-W1.pdf',kind='guide',edition='SG-010-W1')]
    for x,v in VERSIONS.items():
        docs.append(dict(file=f'Appendices/APP-{x}-v{v}.pdf',src=OUT/f'Appendices/APP-{x}-v{v}.pdf',data=OUT/f'Appendices/APP-{x}-v{v}.json',kind='long',id='APP-'+x))
        docs.append(dict(file=f'Appendices/Compact/APP-{x}-v{v}-C1.pdf',src=OUT/f'Appendices/Compact/APP-{x}-v{v}-C1.pdf',data=OUT/f'Appendices/Compact/APP-{x}-v{v}-C1.json',kind='compact',id='APP-'+x))
    return docs

W1_AREAS={'before':[0],'arrive':[1],'outside':[1,2,3],'lowest':[4],'systems':[5],'rooms':[6,7],'upper':[8],'close':[0]}

def page_profile(r,n,p,ctx):
    lines=p.extract_text_lines(layout=False);segments=[];areas=[];limits=[];reference=[];safety=[]
    loc=ctx['loc']
    def segment(title,ids):
        l=find_start(lines,title)
        if l:segments.append(dict(top=l['top'],area_ids=ids,title=title))
    if r['kind']=='guide':
        ed=r['edition']
        if ed in ['SG-010','SG-010-L1']:
            in_toc=(ed=='SG-010' and n==1) or (ed=='SG-010-L1' and n in ctx['leaves'])
            for rec in loc.values():
                if rec['edition']==ed and (in_toc or rec['page']==n):segment(rec['title'],rec['area_ids'])
            areas=list(dict.fromkeys(a for s in segments for a in s['area_ids']))
            if ed=='SG-010-L1' and not in_toc and not segments:
                # P1: a continuation page (no topic starts here) carries the tab of the topic that continues onto it.
                prev=max((x for x in loc.values() if x['edition']==ed and x['page']<n),key=lambda x:x['page'],default=None)
                if prev:areas=list(prev['area_ids'])
            if ed=='SG-010' and not in_toc:
                rec=next((x for x in ctx['compact']['pages'] if x['printed_page']==n),None)
                if rec:
                    for row in rec['rows']:
                        if len(row)>2:
                            l=find_start(lines,row[2])
                            if l:limits.append(dict(line=l,source='compact qualification (Limit / question)'))
                        if COMPACT_SAFE.search(row[0]) or (rec['id'],row[0]) in COMPACT_SAFE_TILES:
                            hits=[h for h in (p.search(re.escape(row[0]),regex=True) or []) if 75<h['top']<747]
                            if hits:safety.append(dict(hit=hits[0],label=row[0],source=rec['id']))
            if ed=='SG-010-L1' and not in_toc:
                for rec in loc.values():
                    if rec['edition']!=ed:continue
                    if rec['page'] in (n,n-1):
                        for label in LONG_FLAGS.get(rec['topic_id'],[]):
                            words=label.split();hits=[]
                            # Cell labels can wrap: fall back to the leading words at the label column.
                            for k in range(len(words),0,-1):
                                if k<len(words) and len(' '.join(words[:k]))<5:break
                                pat=r'\s+'.join(re.escape(w) for w in words[:k])
                                hits=[h for h in (p.search(pat,regex=True) or []) if 75<h['top']<747 and abs(h['x0']-61)<2.5]
                                if hits:break
                            if hits and (rec['topic_id'],label) not in ctx['flagged']:
                                ctx['flagged'].add((rec['topic_id'],label));safety.append(dict(hit=hits[0],label=label,source=rec['topic_id']))
        else:
            wp=ctx['walk']['pages'][n-1];ids=W1_AREAS.get(wp['id'],[0]);areas=ids
            segments=[dict(top=0,area_ids=ids,title='Walking route')]
            for st in wp.get('steps',[]):
                if len(st)>2:
                    l=find_start(lines,st[2])
                    if l:limits.append(dict(line=l,source='walking step record / gate'))
    else:
        data=read(r['data'])
        if r['id']=='APP-D' and r['kind']=='long':
            labels=p.crop((54,0,182,p.height)).extract_text_lines(layout=False)
            for t in data.get('terms',[]):
                ids=loc.get('SG-010-L1:'+t.get('topic',''),{}).get('area_ids',[0])
                l=next((q for q in labels if normalized(q['text'])==normalized(t['term'])),None)
                if l:segments.append(dict(top=l['top'],area_ids=ids,title=t['term']))
        for item in data.get('items',[]):
            if isinstance(item,dict) and item.get('limit'):
                l=find_start(lines,item['limit'])
                if l:limits.append(dict(line=l,source=item.get('id','')+':limit'))
        reference.append(dict(top=45,bottom=740,source='appendix reference context'))
    for l in lines:
        if re.match(r'^(Source notes|Source:|Sources:|L1 pp\.|Full records:)',l['text']):reference.append(dict(top=l['top'],bottom=l['bottom'],source='printed source pointer'))
        if l['text'].startswith(('NOTE:','Limit:','LIMIT:','Limits:','Unresolved:','SOURCE GAP /')):limits.append(dict(line=l,source='explicit printed qualification heading'))
    if not segments:segments=[dict(top=0,area_ids=areas or [0],title='Reference / shared')]
    segments.sort(key=lambda s:s['top'])
    return dict(segments=segments,areas=areas,limits=limits,reference=reference,safety=safety)

def protected_symbol(o):
    for key in ['non_stroking_color','stroking_color']:
        col=o.get(key)
        if isinstance(col,(tuple,list)) and len(col)==3:
            r,g,b=col
            if r>.35 and r>g*1.6 and r>b*1.6:return True
            if g>.25 and b>.3 and g>r*1.6 and b>r*1.6:return True
    return False

def legend(c,y=38):
    c.setFillColor(NAVY);c.setFont('Helvetica',7.8);c.drawString(54,y,'COLOR = HOUSE AREA')
    pattern(c,150,y-1,15,7,'limit');c.setFillColor(NAVY);c.drawString(169,y,'HATCH = LIMIT / QUALIFICATION')
    pattern(c,300,y-1,15,7,'reference');c.setFillColor(NAVY);c.drawString(319,y,'DOTS = SOURCE / REFERENCE')
    cross(c,452,y+2.5,6.5);c.setFillColor(NAVY);c.drawString(460,y,'CROSS = SAFETY-RELATED')

def overlay(c,r,n,p,pr):
    h=float(p.height);kind=r['kind'];areas=pr['areas'];marks=dict(safety=[],md=[],limit=0,reference=0,legend=False)
    occupied=[ch for ch in p.chars if ch['text'].strip()]+[o for o in p.rects+p.curves+p.lines if protected_symbol(o)]
    # 1. Safety crosses first, in the left gutter beside the flagged label.
    for s in pr['safety']:
        hit=s['hit'];cy=(hit['top']+hit['bottom'])/2
        # Beside its own label: left gutter for column-one labels, the tile pad for column two.
        for cx in ([47,40] if hit['x0']<100 else [hit['x0']-8,hit['x0']-13]):
            box=dict(x0=cx-4,x1=cx+4,top=cy-4,bottom=cy+4)
            if not any(overlaps(box,o) for o in occupied):
                cross(c,cx,h-cy,7);occupied.append(box);marks['safety'].append(dict(label=s['label'],source=s['source']));break
    tagged=set()
    def safe_pattern(x,y,w,hh,role):
        key=(round(x,2),round(y,2),round(w,2),round(hh,2),role)
        if key in tagged:return
        tagged.add(key)
        for xx in dict.fromkeys([x,34,31,24]):
            box=dict(x0=xx,x1=xx+w,top=h-y-hh,bottom=h-y)
            if not any(overlaps(box,o) for o in occupied):
                pattern(c,xx,y,w,hh,role);occupied.append(box);marks[role]+=1;return
    # 2. Area edge tabs (left edge; the brand and appendix letter tabs are on the right).
    if areas:
        usable=[a for a in areas if a!=0] or [0];top=h-60
        for j,a in enumerate(usable[:8]):
            y=top-j*30;c.setFillColor(HexColor(AREA[a][0]));c.rect(18,y-24,14,26,fill=1,stroke=0)
            occupied.append(dict(x0=18,x1=32,top=h-y-2,bottom=h-y+24))
            c.setFillColor(white if label_ink(a)=='white' else HexColor(label_ink(a)));c.setFont('Helvetica-Bold',8);c.drawCentredString(25,y-15,f'{a:02}' if a else '*')
    # 3. Topic bars carry area identity into the body.
    for s in pr['segments']:
        if s['title']=='Reference / shared':continue
        y=h-s['top']-2;ids=s['area_ids'];w=504/max(1,len(ids))
        for j,a in enumerate(ids):
            c.setFillColor(HexColor(AREA[a][0]))
            if kind in ['compact','long']:c.rect(44,y-10+j*4,5,4,fill=1,stroke=0)
            else:c.rect(54+j*w,y+4,w,2.2,fill=1,stroke=0)
    for ref in pr['reference']:
        if ref['source']=='appendix reference context':
            pattern(c,22,54,8,h-110,'reference');occupied.append(dict(x0=22,x1=30,top=56,bottom=h-54));marks['reference']+=1
        else:safe_pattern(43,h-ref['bottom'],6,max(6,ref['bottom']-ref['top']),'reference')
    for q in pr['limits']:
        l=q['line'];safe_pattern(max(35,l['x0']-9),h-l['bottom'],5,max(9,l['bottom']-l['top']),'limit')
    key_box=dict(x0=54,x1=558,top=h-47,bottom=h-35)
    if not any(overlaps(key_box,o) for o in occupied):legend(c);marks['legend']=True
    # 4. Maryland crab: explicit jurisdiction words only, collision-checked, capped per page.
    used=[];per_row=(kind,r.get('id'))in MD_ROW_DOCS
    lines=p.extract_text_lines(layout=False) if per_row else []
    def leads(w):  # jurisdiction within the first three words of its own line (row label / card heading)
        l=next((l for l in lines if abs(l['top']-w['top'])<2 and l['x0']<=w['x0']+.5 and w['x1']<=l['x1']+.5),None)
        return bool(l) and w['text'] in l['text'].split()[:3]
    for w in p.extract_words():
        if len(marks['md'])>=MD_CAP and not per_row:break
        word=w['text'].strip('.,:;()')
        if not (word in MD_WORDS or re.fullmatch(r'MD-\d+',word)) or not (75<w['top']<735):continue
        y=(w['top']+w['bottom'])/2
        if any(abs(y-v)<14 for v in used):continue
        if per_row and not leads(w):continue
        if not per_row and any(abs(w['x0']-m['x0'])<2 for m in marks['md']):continue  # one crab per column list (e.g. a jurisdiction table)
        if n==1 and r['kind']=='guide' and r['edition']=='SG-010':break  # cover crab placed by contents layer
        for x in ([43,38] if per_row else [43,38,w['x0']-10] if kind in ('long','compact') else [w['x0']-10,43,38]):  # per-row docs: one gutter column; appendices prefer the gutter (P1), guides sit beside the word
            if x<38:continue
            box=dict(x0=x-7,x1=x+7,top=y-7,bottom=y+6)
            if not any(overlaps(box,o) for o in occupied):
                crab(c,x,h-y,12);occupied.append(box);used.append(y);marks['md'].append(dict(term=w['text'],x=round(x,1),x0=w['x0'],top=round(w['top'],1)));break
    return marks

def render_document(r,ctx):
    src=r['src'];reader=PdfReader(src);w=PdfWriter();w.clone_document_from_reader(reader);profiles=[];recoloured=0
    with pdfplumber.open(src) as doc:
        for i,page in enumerate(w.pages):
            p=doc.pages[i];buf=io.BytesIO();c=Canvas(buf,pagesize=(p.width,p.height),invariant=1)
            pr=page_profile(r,i+1,p,ctx)
            def selector(x,y):
                top=p.height-y;el=[s for s in pr['segments'] if s['top']<=top+3]
                return typical((el[-1] if el else pr['segments'][0])['area_ids'])
            recoloured+=rewrite_vectors(page,w,selector);marks=overlay(c,r,i+1,p,pr)
            profiles.append(dict(page=i+1,areas=pr['areas'],segments=len(pr['segments']),**marks))
            c.showPage();c.save();page.merge_page(PdfReader(buf).pages[0])
    w.add_metadata({'/VisualLanguageRevision':'SG-010 staged colour/pattern/safety/MD layer','/MarylandMarkerMeaning':MD_MEANING,'/SafetyMarkMeaning':SAFETY_MEANING})
    dest=LAYER/r['file'];dest.parent.mkdir(parents=True,exist_ok=True)
    with open(dest,'wb') as f:w.write(f)
    new=PdfReader(dest);assert len(new.pages)==len(reader.pages)
    for a,b in zip(reader.pages,new.pages):
        t=a.extract_text().strip()
        assert all(x in b.extract_text() for x in t.split()[:40]),(r['file'],'text lost')
    return dict(file=r['file'],source=str(src),pages=len(new.pages),pdf_sha256=sha(dest),source_sha256=sha(src),backgrounds_recoloured=recoloured,
        safety_marks=sum(len(x['safety']) for x in profiles),md_marks=sum(len(x['md']) for x in profiles),page_profiles=profiles)

def build():
    ctx=dict(loc=read(LAYER/'contents-locations-SG-010.json')['records'],leaves=set(read(LAYER/'contents-layout.json')['long_leaves']),
             compact=read(OUT/'study-guide.json'),walk=read(OUT/'walking-cut.json'),flagged=set())
    reports=[]
    for r in documents():
        rep=render_document(r,ctx);reports.append(rep)
        print(f"{rep['file']}: {rep['pages']} pp, {rep['backgrounds_recoloured']} fills, {rep['safety_marks']} safety, {rep['md_marks']} MD",flush=True)
    missing=[(t,l) for t,ls in LONG_FLAGS.items() for l in ls if (t,l) not in ctx['flagged']]
    save(LAYER/'layers-report.json',dict(meaning=dict(safety=SAFETY_MEANING,maryland=MD_MEANING,color='house area (contents-locations-SG-010.json)',hatch='limit / qualification',dots='source / reference'),
        policy='Cues, not findings or risk scores. Guides and appendices only; field cards excluded. Unlayered renders unchanged.',
        long_flags_not_found=missing,documents=reports))
    print('L1 safety labels not found:',missing)

if __name__=='__main__':build()
