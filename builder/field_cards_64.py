"""64 separate field cards; eight area packs, generated from reviewed content."""
from pathlib import Path
import json,hashlib,re,math,html
from reportlab.graphics.shapes import Drawing,Rect,Polygon,Circle,Line,Group
from reportlab.graphics import renderPDF,renderSVG
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader
import pdfplumber
import field_cards_layer2 as v
from field_cards_64_content import catalog,PACKS
import field_card_concordance as concordance
import field_use
import card_brand
import card_inspection_layer as inspection
import card_inspection_drawings as sketches
from reportlab.lib.colors import HexColor,Color

HERE=Path(__file__).resolve().parent
from prepare import WORK
OUT=WORK/'field-cards-64';OUT.mkdir(exist_ok=True)
CARDS,CONCORDANCE=concordance.compile_cards(catalog())
INSPECTION=inspection.attach(CARDS,CONCORDANCE)
SOURCE=concordance.SOURCE
GUIDE=json.loads(SOURCE.read_text(encoding='utf-8'))
TOPICS={p['id']:p for p in GUIDE['pages']}
PAGES=json.loads((concordance.SOURCE.parent/'page-index.json').read_text())
PDF='QUICK CHARTS - 64 CARDS - 5x7.pdf'
LETTER='QUICK CHARTS - 64 CARDS - LETTER PRINT.pdf'
W,H=360,504
# Experimental area accents, local to these cards. Number/title/house locator
# repeat the meaning so color is never the only cue. Body text remains navy.
AREA_COLORS=['#43624E','#8C523A','#655673','#245B70','#1A1A5E','#775238','#216865','#635B26']
STYLE=dict(name='Field Card Concordance / visual grammar 0.2',
    status='experimental extension; not a global BBDF palette revision',
    area_colors={str(i+1):x for i,x in enumerate(AREA_COLORS)},
    typography={'term':'Times-Bold 25 pt','action':'Helvetica-Bold 23 pt','working':'Helvetica 14 pt','label':'Helvetica-Bold 13 pt','qualification':'Helvetica 13 pt','source':'Helvetica 10 pt'},
    layers={'area':'accent + number + house locator','relevance':'clock/history, eye/observe, open book/reference','expression':'term/action/qualification type hierarchy','evidence':'edition page and footnote IDs; concordance holds full lineage'},
    severity_encoding=False,
    inspection_revision=inspection.REVISION,
    safety=dict(symbol='small red cross plus SAFETY label',color=inspection.SAFETY_COLOR,
        meaning=inspection.SAFETY_MEANING,flagged_cards=INSPECTION['flagged_count']),
    inspection_sketches=dict(symbol='blue ring at the detail to examine',
        meaning=inspection.SKETCH_MEANING,cards=INSPECTION['sketched_count']),
    branding=dict(source=str(card_brand.LOGO),sha256=card_brand.SHA256,
        artwork='Canonical BEN-Ball vector; original geometry, colors and aspect ratio',
        corners=['upper right','lower left'],width_points=22,height_points=22*655/289,
        revision='B1',source_copies=2))

def relevance_icon(d,kind,x,y,color):
    if kind=='history':
        d.add(Circle(x+5,y+5,5,fillColor=None,strokeColor=color,strokeWidth=1.2))
        v.line(d,x+5,y+5,x+5,y+8,1.2,color);v.line(d,x+5,y+5,x+8,y+4,1.2,color)
    elif kind=='observe':
        d.add(Polygon([x-1,y+5,x+5,y+9,x+11,y+5,x+5,y+1],fillColor=None,strokeColor=color,strokeWidth=1.2))
        d.add(Circle(x+5,y+5,1.7,fillColor=color,strokeColor=None))
    else:
        d.add(Polygon([x,y+1,x,y+10,x+5,y+8,x+10,y+10,x+10,y+1,x+5,y-1],fillColor=None,strokeColor=color,strokeWidth=1.2))
        v.line(d,x+5,y-1,x+5,y+8,1,color)

def locator(d,area):
    """An area locator icon, not property geometry; visual keys survive grayscale."""
    x,y=306,435
    v.line(d,x,y,x+30,y,1.1,v.NAVY)
    v.line(d,x,y,x,y+18,1.1,v.NAVY);v.line(d,x+30,y,x+30,y+18,1.1,v.NAVY)
    d.add(Polygon([x-3,y+18,x+15,y+29,x+33,y+18],fillColor=None,strokeColor=v.NAVY,strokeWidth=1.1))
    if area==1:v.line(d,x-6,y-5,x+36,y-5,3,v.NAVY)
    elif area==2:
        v.line(d,x,y,x,y+18,3,v.NAVY);v.line(d,x+30,y,x+30,y+18,3,v.NAVY)
    elif area==3:v.rect(d,x+20,y,15,13,1,v.NAVY,v.NAVY)
    elif area==4:v.rect(d,x+2,y+1,26,6,0,v.NAVY,None)
    elif area==5:
        v.rect(d,x+18,y+1,8,13,1,v.NAVY,v.NAVY);v.line(d,x+21,y+14,x+21,y+25,2,v.NAVY)
    elif area==6:v.rect(d,x+3,y+9,12,7,0,v.NAVY,None)
    elif area==7:v.rect(d,x+18,y+9,9,7,0,v.NAVY,None)
    else:d.add(Polygon([x+2,y+19,x+15,y+27,x+28,y+19],fillColor=v.NAVY,strokeColor=None))

def shell(c):
    d=Drawing(W,H);v.rect(d,0,0,W,H,0,v.WHITE,None)
    accent=HexColor(AREA_COLORS[c['area_number']-1])
    tint=Color(*[.93+.07*x for x in (accent.red,accent.green,accent.blue)])
    v.rect(d,0,470,W,34,0,tint,None)
    v.txt(d,f'{c["area_number"]:02d} / '+c['area_short'],20,482,11,True,accent,width=250)
    v.txt(d,c['display_id'],307,480,15,True,v.NAVY,align='end')
    v.line(d,20,470,309,470,2,accent)
    v.rect(d,313,441,33,60,0,v.WHITE,None)
    card_brand.mark(d,318,447)
    from reportlab.graphics.shapes import String
    assert v.stringWidth(c['title'][0],'Times-Bold',25)<=281,c['title'][0]
    d.add(String(20,443,c['title'][0],fontName='Times-Bold',fontSize=25,fillColor=v.NAVY))
    v.txt(d,c['title'][1],20,416,23,True,v.NAVY,width=320)
    house=Drawing(W,H);locator(house,c['area_number'])
    marker=Group(*house.contents);marker.transform=(.55,0,0,.55,232-.55*306,477-.55*435)
    d.add(marker)
    v.txt(d,c['cue'],20,391,13,width=320)
    relevance_icon(d,c['relevance'],22,373,accent)
    v.txt(d,{'history':'HISTORY','observe':'OBSERVE NOW','reference':'CHECK REFERENCE'}[c['relevance']],39,375,9.5,True,accent,width=150)
    form={'check':'SCAN / RECORD','compare':'COMPARE','sequence':'DISTINGUISH','record':'CAPTURE','route':'TRACE','evidence':'READ EVIDENCE','bearing':'FOLLOW LOAD','profiles':'NAME GEOMETRY','pipes':'SEPARATE PATHS','heat':'TWO PATHS','tiles':'NAME FUNCTION','slope':'CONVERT'}[c['kind']]
    v.txt(d,form,340,375,9.5,True,accent,align='end')
    if c['safety']['marked']:
        red=HexColor(inspection.SAFETY_COLOR)
        v.rect(d,158,374,3,11,0,red,None)
        v.rect(d,154,378,11,3,0,red,None)
        v.txt(d,'SAFETY',171,375,9.5,True,red)
    v.line(d,20,143,340,143,1.2)
    v.txt(d,c['write'],20,125,11.5,True,width=320)
    for y in [94,61]:v.line(d,20,y,340,y,.45,v.GRAY)
    card_brand.mark(d,20,7)
    v.txt(d,c['source'],53,27,10,width=287)
    v.txt(d,f'FIELD CARD CONCORDANCE / {c["id"]} / 5 x 7',53,12,8.5,color=v.NAVY)
    v.rect(d,350,453-(c['area_number']-1)*25,4,17,0,accent,None)
    return d

def check(d,c):
    assert len(c['rows'])==4
    for i,(label,detail) in enumerate(c['rows']):
        y=355-i*43
        v.rect(d,22,y-4,12,12,1.2)
        v.txt(d,label,45,y,13,True,width=292)
        v.txt(d,detail,45,y-19,14,width=292)

def compare(d,c):
    assert len(c['rows'])==2
    for i,(label,detail) in enumerate(c['rows']):
        x=20+i*165
        accent=HexColor(AREA_COLORS[c['area_number']-1])
        tint=Color(*[.87+.13*q for q in (accent.red,accent.green,accent.blue)])
        v.rect(d,x,319,155,46,0,tint,None)
        v.rect(d,x,210,155,155,1.2)
        label=v.wrap(label,135,14,True)
        v.txt(d,label,x+10,342,14,True,width=135)
        desc=v.wrap(detail,135,14)
        assert len(desc.splitlines())<=6,(c['id'],detail)
        v.txt(d,desc,x+10,291,14,width=135)

def sequence(d,c):
    assert len(c['rows'])==3
    for i,(label,detail) in enumerate(c['rows']):
        x=20+i*110
        v.line(d,x,361,x+100,361,3,v.NAVY)
        title=v.wrap(label,96,13,True)
        assert len(title.splitlines())<=3,(c['id'],label)
        v.txt(d,title,x+2,340,13,True,width=96)
        detail=v.wrap(detail,96,14)
        assert len(detail.splitlines())<=6,(c['id'],detail)
        v.txt(d,detail,x+2,281,14,width=96)

def record(d,c):
    assert len(c['rows'])==4
    for i,(label,prompt) in enumerate(c['rows']):
        y=355-i*43
        v.txt(d,f'{i+1:02d}',20,y,12,True,v.NAVY)
        v.txt(d,label,44,y,13,True,width=294)
        v.txt(d,prompt,44,y-18,13,width=294)
        v.line(d,44,y-26,340,y-26,.45,v.GRAY)

def tiles(d,c):
    accent=HexColor(AREA_COLORS[c['area_number']-1])
    tint=Color(*[.87+.13*q for q in (accent.red,accent.green,accent.blue)])
    for i,(name,purpose) in enumerate(c['rows']):
        x=20+(i%2)*165;y=283-(i//2)*92
        v.rect(d,x,y+62,155,27,0,tint,None)
        v.rect(d,x,y,155,89,1.1)
        v.txt(d,name,x+9,y+67,14,True,width=137)
        v.txt(d,v.wrap(purpose.replace('\n',' '),137,13),x+9,y+42,13,width=137)

LAYOUTS={'check':check,'compare':compare,'sequence':sequence,'record':record,
         'route':v.routes,'evidence':v.water,'bearing':v.structure,'profiles':v.movement,
         'pipes':v.pipes,'heat':v.heat,'tiles':tiles,'slope':v.slope}

def make(c):
    d=shell(c)
    # Very light structural field; handwriting area stays white.
    accent=HexColor(AREA_COLORS[c['area_number']-1])
    if c['kind'] in ('check','record'):
        for i in (0,2):v.rect(d,18,331-i*43,324,38,0,HexColor('#F3F4F8'),None)
    if c['kind'] in ('compare','sequence'):v.line(d,20,365,340,365,1.5,accent)
    no_note=dict(c,note='')
    LAYOUTS[c['kind']](d,no_note)
    sketches.draw(d,c)
    note=v.wrap(c['note'],320,13)
    assert len(note.splitlines())<=3,(c['id'],note)
    v.txt(d,note,20,158+16*(len(note.splitlines())-1),13,width=320,leading=16)
    # Preserve BBDF body navy without changing the shared prototype helpers.
    for shape in d.contents:
        if getattr(shape,'fillColor',None)==v.INK:shape.fillColor=v.NAVY
        if getattr(shape,'text',None) in ('YOU SEE','RISE OVER 12 IN. OF HORIZONTAL RUN'):
            shape.y-=4
    return d

def norm(s):return re.sub(r'\s+','',s).lower()

def build():
    concordance.export(CONCORDANCE,CARDS,OUT)
    concordance.save(OUT/'inspection-layer.json',INSPECTION)
    field_use.build(CARDS,OUT)
    concordance.save(OUT/'visual-grammar.json',STYLE)
    for c in CARDS:
        assert set(c['refs'])<=set(TOPICS),(c['id'],c['refs'])
        nums=sorted({PAGES[t] for t in c['refs']})
        if 'source' not in c:c['source']='SG-010 '+('p. ' if len(nums)==1 else 'pp. ')+', '.join(map(str,nums))+' / APP-D terms'
        c['source_topics']=[dict(id=t,title=TOPICS[t]['title'],page=PAGES[t]) for t in c['refs']]
        c['source_edition']='SG-010'
        c['vector']=c['id']+'.svg'
    drawings=[]
    for c in CARDS:
        try:drawings.append(make(c))
        except Exception as e:raise ValueError(f'{c["display_id"]} / {c["title"]}: {e}') from e
    pdf=Canvas(str(OUT/PDF),pagesize=(W,H),pageCompression=1,invariant=1)
    pdf.setTitle('64 quick-reference field cards / eight areas of the house')
    for c,d in zip(CARDS,drawings):
        if c['slot']==1:
            key='area-'+str(c['area_number']);pdf.bookmarkPage(key);pdf.addOutlineEntry(c['area_title'],key,level=0)
        pdf.bookmarkPage(c['id']);pdf.addOutlineEntry(c['display_id']+' / '+' - '.join(c['title']),c['id'],level=1)
        renderPDF.draw(d,pdf,0,0);pdf.showPage();renderSVG.drawToFile(d,str(OUT/c['vector']))
    pdf.save()
    pdf=Canvas(str(OUT/LETTER),pagesize=(792,612),pageCompression=1,invariant=1)
    pdf.setTitle('64 field cards / single-sided Letter cutting layout')
    for start in range(0,64,2):
        area=CARDS[start]['area_number'];title=CARDS[start]['area_short']
        if start%8==0:
            key='area-'+str(area);pdf.bookmarkPage(key);pdf.addOutlineEntry(CARDS[start]['area_title'],key)
        pdf.setFont('Helvetica',9);pdf.setFillColor(v.INK)
        pdf.drawString(27,585,f'{area:02d} / {title} / ACTUAL SIZE / Landscape Letter / SINGLE-SIDED: backs stay blank')
        pdf.drawRightString(765,585,f'Print page {start//2+1} of 32')
        pdf.setFont('Helvetica',8.5)
        pdf.drawString(27,572,'+ SAFETY = safety-related topic. Ring = detail to examine. Concept sketches / not to scale / not installation details.')
        for x,i in zip((27,405),(start,start+1)):
            renderPDF.draw(drawings[i],pdf,x,54)
            pdf.setStrokeColor(v.GRAY);pdf.setLineWidth(.5)
            for xx in (x,x+W):
                for yy in (54,558):
                    pdf.line(xx-5,yy,xx-1,yy);pdf.line(xx+1,yy,xx+5,yy)
                    pdf.line(xx,yy-5,xx,yy-1);pdf.line(xx,yy+1,xx,yy+5)
        pdf.setStrokeColor(v.INK);pdf.line(27,30,99,30);pdf.line(27,27,27,33);pdf.line(99,27,99,33)
        pdf.setFont('Helvetica',9);pdf.drawString(105,27,'Proof line: 1 inch. Cut at marks. 5 x 7 cards; print only the areas needed.')
        pdf.showPage()
    pdf.save()
    textcheck=[]
    for c,page in zip(CARDS,PdfReader(OUT/PDF).pages):
        text=norm(page.extract_text())
        required=c['title']+[c['cue'],c['note'],c['write'],c['source']]
        for row in c['rows']:
            for value in row:required.extend(s.strip() for s in value.split('>'))
        for part in required:assert norm(part) in text,(c['id'],part)
        textcheck.append(c['id'])
    checks=[]
    for fn,size,count in [(PDF,(W,H),64),(LETTER,(792,612),32)]:
        with pdfplumber.open(OUT/fn) as doc:
            assert len(doc.pages)==count
            for page in doc.pages:
                assert (page.width,page.height)==size
                assert all(0<=x['x0']<=x['x1']<=page.width and 0<=x['top']<x['bottom']<=page.height for x in page.chars)
                assert not any(x['text'] in ('\ufffd','\x7f','\u25a0') for x in page.chars)
        checks.append(dict(file=fn,pages=count,points=list(size),sha256=hashlib.sha256((OUT/fn).read_bytes()).hexdigest()))
    packs=[dict(number=i,title=t,short=s,cards=[(i-1)*8+1,i*8],letter_pages=[(i-1)*4+1,i*4]) for i,(s,t,_) in enumerate(PACKS,1)]
    data=dict(title='Quick charts / 64 area cards',status='internal field trial',layer=2,physical_card_count=64,faces_per_card=1,backs='blank',size_inches=[5,7],date='2026-09-20',print_pdf=PDF,letter_pdf=LETTER,packs=packs,cards=CARDS,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),base_eight_preserved={c['base_card']:c['id'] for c in CARDS if c.get('base_card')},layouts=sorted(LAYOUTS),conference_room_action='none')
    (OUT/'cards.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    # Offline selector: data and filtering are inline; no server or network dependency.
    buttons=''.join('<button data-area="'+str(p['number'])+'">'+str(p['number']).zfill(2)+' '+p['short']+'</button>' for p in packs)
    sections=''
    for p in packs:
        first,last=p['cards'];lfirst,llast=p['letter_pages']
        sections+='<section class="area" data-area="'+str(p['number'])+'"><h2>'+str(p['number']).zfill(2)+' / '+html.escape(p['title'])+'</h2><p class="print">Eight cards. 5 x 7 PDF: pages '+str(first)+'-'+str(last)+'. Letter PDF: pages '+str(lfirst)+'-'+str(llast)+' (four single-sided sheets). <a href="'+PDF+'#page='+str(first)+'">Open these cards</a> / <a href="'+LETTER+'#page='+str(lfirst)+'">Open cutting layout</a></p><div class="grid">'
        for c in CARDS[first-1:last]:
            sections+='<article><h3>'+c['display_id']+' / '+html.escape(' - '.join(c['title']))+'</h3><img loading="lazy" src="'+c['vector']+'" alt="'+html.escape(' - '.join(c['title']))+'"><p><a href="concordance.html#'+c['id']+'">Facts, qualifications, terms and references</a></p><p>'+''.join('<a href="../../STUDY GUIDE.html#'+t+'">'+html.escape(TOPICS[t]['title'])+'</a><br>' for t in c['refs'])+'</p></article>'
        sections+='</div></section>'
    page='''<!doctype html><html><head><meta charset="utf-8"><title>64 cards / choose an area</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{max-width:1180px;margin:30px auto;padding:0 20px;font:17px system-ui;color:#111}h1,h2,a{color:#1A1A5E}p{line-height:1.5}nav{display:flex;gap:8px;flex-wrap:wrap;position:sticky;top:0;background:white;padding:14px 0;border-bottom:1px solid #ccc}button{font:inherit;padding:9px 12px;background:white;border:1px solid #1A1A5E;border-radius:3px;cursor:pointer}button.active{background:#1A1A5E;color:white}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:28px}img{width:360px;max-width:100%;border:1px solid #aaa}h3{font-size:17px}.print{padding:16px;border-left:4px solid #1A1A5E;background:#f5f5f5}article p{font-size:14px}[hidden]{display:none!important}@media print{nav{display:none}}</style></head><body><h1>64 field cards / choose an area</h1><p>Eight packs of eight separate 5 x 7 cards. The original eight topics are retained within the area packs, with distinct diagrams, comparison panels, route charts and observation records. Blank backs and the white front strips are for hand notes.</p><p><a href="'''+PDF+'''">All 64 cards</a> / <a href="'''+LETTER+'''">Letter cutting layout</a> / <a href="cards.json">Data and source map</a> / <a href="../Quick Charts - Trial/index.html">Original eight-face set</a></p><p>Print only the area you need using the ranges below. Landscape Letter: <strong>100% / Actual Size / single-sided</strong>. Four sheets make eight cards. Check the one-inch line; use matte uncoated stock. A topic aid, not a complete inspection checklist. Sources and fuller definitions remain in SG-010 and Appendix D.</p><nav><button class="active" data-area="all">All areas</button>'''+buttons+'''</nav>'''+sections+'''<script>document.querySelectorAll('button[data-area]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===b));document.querySelectorAll('section.area').forEach(s=>s.hidden=b.dataset.area!=='all'&&s.dataset.area!==b.dataset.area);document.querySelector('nav').scrollIntoView({block:'start'});}));</script></body></html>'''
    page=page.replace('<nav>','<p><a href="field-use.html">Routine / Tasks / Steps and the property timeline</a> / <a href="concordance.html">Field Card Concordance</a></p><p>Area color repeats the numbered house locator. Clock: history. Eye: observe now. Open book: check the reference. Red cross / SAFETY: '+inspection.SAFETY_MEANING+' Blue ring: '+inspection.SKETCH_MEANING+'</p><nav>')
    (OUT/'index.html').write_text(page,encoding='utf-8')
    ranges='\n'.join(f'| {p["number"]:02d} {p["title"]} | {p["cards"][0]}-{p["cards"][1]} | {p["letter_pages"][0]}-{p["letter_pages"][1]} |' for p in packs)
    readme='''# 64 quick-reference cards / Layer 2

64 separate portrait cards, 5 x 7 inches each. Eight area packs of eight. Each physical card has one printed face and a blank back. The front preserves a broad unfilled notes area. Select the pack needed for a visit; this library is not an instruction to carry all 64.

| Area | 5 x 7 PDF pages | Letter PDF pages |
| --- | --- | --- |
'''+ranges+'''

Print the Letter layout in landscape, single-sided, at Actual Size / 100%. Two cards fit each Letter sheet; cut at the corner marks. Four single-sided Letter sheets produce eight cards with blank backs. The one-inch proof line detects unwanted scaling. This differs deliberately from the original four-double-sided-card trial. That first set remains intact.

Working text is generally 14 points; diagram labels, prompts and cautions 13; source references 10. The notes strips, 33-point line spacing, matte uncoated stock and blank backs support hand/crayon use. Field performance with a flashlight remains a physical test, not a screen-render claim.

The original eight cards map into this catalog via base_eight_preserved in cards.json. Technical content is condensed from the reviewed SG-010 topic records; every card carries source topics and printed-page pointers. The slope chart is arithmetic, not an acceptance standard. All diagrams are conceptual, not surveyed geometry or repair designs. A card pack does not define a complete inspection scope.

Read index.html offline to filter by area and obtain print ranges. Every card is an editable SVG; cards.json holds the content and source map. Local authoring: field_cards_64_content.py defines the editorial records; field_cards_64.py combines them with shared linework helpers from field_cards_layer2.py. These files live in BB_CODE/.scratch/sg009. No remote model or raster-image generation is required. No automatic type shrinking is used.

This is an additive experimental appendix collection. No canonical vocabulary, main-edition page budget or conference-room authorization changes.
'''
    readme+='''\n## Field Card Concordance\n\nThe named translation layer is Field Card Concordance. It is an experimental design name assigned at Ben's request, not an admission to BBDF's canonical vocabulary register. Source definitions remain in their existing editions and APP-D. Exact source rows (statement plus qualification), printed expressions, footnotes, terms and related L1 recording references have separate IDs. Emphasis is explicitly editorial; a lexical match does not establish source bolding. A source reference attached to a topic is not claimed as proof of every sentence.\n\nThe renderer consumes the validated concordance before producing cards. A changed source row, qualification, term, reference, or card expression invalidates the review lock and withholds rendering until reviewed. Reverse indexes identify affected cards. The data contains pointers and hashes, not media copies. Read concordance.html offline; concordance.json is portable structured data. field-use.html and field-use.json describe RTS composition, four synthetic property scenarios, reusable human steps and five separate time dimensions. Unknown presence/access is never converted to inspection completion.\n\nThe local RTS registry has no generic human-physical-action kind. HUMAN_GATE means terminate an agent chain and hand to Ben, not inspect a room. No live registry, scheduler or coordination database is modified. W1 connections are mappings to its staged content, not a claim that W1 has been published.\n\nvisual-grammar.json records the shared color, icon and typography meanings. Eight experimental area accents extend the BBDF navy-based treatment locally. Numbers, names and locator shapes repeat the colors. Clock / history, eye / observe now and open book / check reference are relevance cues, never hazard scores. Every card keeps 14-point working text, qualifications, source pointers and writable space.\n'''
    readme=readme.replace('W1 connections are mappings to its staged content, not a claim that W1 has been published.',
        'W1 connections resolve the published experimental SG-010-W1 route companion when its publication record is present.')
    readme+='\n## Branding B1\n\nThe canonical BEN-Ball vector logo appears in the upper-right and lower-left corners of every card, at 22 points wide and its original aspect ratio. Original geometry and colors are retained; no new raster artwork is generated. The source artwork path and SHA-256 are recorded in visual-grammar.json. Working type, source references, writing rules, cut dimensions and blank backs remain unchanged. The header house locator and ID move to make room for the mark.\n'
    readme+='\n## Inspection layer V2\n\n'+inspection.SAFETY_MEANING+' '+inspection.SKETCH_MEANING+'\n\nExplicit editorial selections mark '+str(INSPECTION['flagged_count'])+' safety-related cards; '+str(INSPECTION['sketched_count'])+' cards gain inspection sketches or examination rings. The original words, qualifications and layout sizes remain. inspection-layer.json and the concordance bind each flag/sketch to existing fact IDs, qualifications and source hashes. There are no hazard scores, age-based flags or unmarked=passed inference. The cross also has the word SAFETY so meaning survives grayscale. Blue rings select a detail, not an observed defect. Geometry remains separate from actual Property Linework records.\n'
    (OUT/'README.md').write_text(readme,encoding='utf-8')
    result=dict(status='mechanical checks passed',pdfs=checks,cards=64,packs=8,cards_per_pack=8,all_card_text_verified=True,source_topics_valid=True,base_eight_present=True,geometry='5 x 7 inches',letter_print='single-sided',physical_test='not performed',visual_review='pending')
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':build()
