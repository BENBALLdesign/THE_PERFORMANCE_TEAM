"""Eight individual visual forms derived from the unchanged first card set."""
from pathlib import Path
import json,hashlib,math,re,html,sys
from reportlab.graphics.shapes import Drawing,Line,Rect,String,Polygon,Circle,PolyLine
from reportlab.graphics import renderPDF,renderSVG
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader
import pdfplumber

HERE=Path(__file__).resolve().parent
BASE=HERE/'field-cards'
OUT=HERE/'field-cards-layer2';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(HERE.parent/'tools'))
import team_paths
TOKENS=team_paths.brand('tokens/palette.json')
PALETTE=json.loads(TOKENS.read_text())['color']
NAVY=HexColor(PALETTE['navy']['primary']['$value']);INK=HexColor('#111111');GRAY=HexColor('#888888');WHITE=HexColor('#FFFFFF')
SOURCE=json.loads((BASE/'cards.json').read_text(encoding='utf-8'))
CARDS=SOURCE['cards']
FORMS={'1A':'Route spine','1B':'Three evidence windows','2A':'Bearing sketch','2B':'Four movement profiles','3A':'Separate pipe routes','3B':'Two process tracks','4A':'Four function tiles','4B':'Proportional rise chart'}
PDF='QUICK CHARTS - LAYER 2 - 5x7.pdf'
LETTER='QUICK CHARTS - LAYER 2 - LETTER PRINT.pdf'
W,H=360,504

def txt(d,s,x,y,size=14,bold=False,color=INK,align='start',width=None,leading=None):
    font='Helvetica-Bold' if bold else 'Helvetica';leading=leading or size+3
    for i,line in enumerate(s.split('\n')):
        assert all(ord(c)<128 for c in line),line
        if width:assert stringWidth(line,font,size)<=width,(line,size,width)
        d.add(String(x,y-i*leading,line,fontName=font,fontSize=size,fillColor=color,textAnchor=align))

def wrap(s,width,size=14,bold=False):
    font='Helvetica-Bold' if bold else 'Helvetica';lines=[]
    for para in s.split('\n'):
        line=''
        for word in para.split():
            candidate=(line+' '+word).strip()
            if line and stringWidth(candidate,font,size)>width:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
    assert all(stringWidth(line,font,size)<=width for line in lines)
    return '\n'.join(lines)

def line(d,x1,y1,x2,y2,weight=1,color=INK,dash=None):
    d.add(Line(x1,y1,x2,y2,strokeColor=color,strokeWidth=weight,strokeDashArray=dash))

def rect(d,x,y,w,h,weight=1,fill=None,color=INK):
    d.add(Rect(x,y,w,h,strokeColor=color,strokeWidth=weight,fillColor=fill))

def arrow(d,x1,y1,x2,y2,weight=1.3,color=INK):
    line(d,x1,y1,x2,y2,weight,color)
    a=math.atan2(y2-y1,x2-x1);s=4.5
    pts=[x2,y2,x2-s*math.cos(a-.5),y2-s*math.sin(a-.5),x2-s*math.cos(a+.5),y2-s*math.sin(a+.5)]
    d.add(Polygon(pts,fillColor=color,strokeColor=None))

def icon(d,kind,x,y):
    """Small topic marks repeat the actual card geometry; no stock icon library."""
    if kind=='1A':
        line(d,x-10,y+10,x+9,y-10,1.4)
        for xx,yy in [(x-10,y+10),(x,y),(x+9,y-10)]:d.add(Circle(xx,yy,3.5,fillColor=WHITE,strokeColor=NAVY,strokeWidth=1.4))
    elif kind=='1B':
        d.add(Polygon([x,y+13,x-8,y-2,x-6,y-9,x,y-12,x+6,y-9,x+8,y-2],fillColor=None,strokeColor=NAVY,strokeWidth=1.4))
    elif kind=='2A':
        rect(d,x-13,y+5,26,5,1.4);rect(d,x-3,y-8,6,13,1.4);rect(d,x-10,y-12,20,4,1.4)
    elif kind=='2B':
        d.add(PolyLine([x-14,y+5,x-7,y-4,x,y-7,x+7,y-4,x+14,y+5],strokeColor=NAVY,strokeWidth=1.7))
    elif kind=='3A':
        for i in range(3):line(d,x-14,y+8-i*8,x+14,y+8-i*8,1.4,NAVY,[3,2] if i==2 else None)
    elif kind=='3B':
        arrow(d,x-14,y+7,x+14,y+7,color=NAVY);arrow(d,x-14,y-7,x+14,y-7,color=NAVY)
    elif kind=='4A':
        for i in range(4):rect(d,x-12+(i%2)*14,y-12+(i//2)*14,10,10,1.2,color=NAVY)
    else:
        for i,h in enumerate([4,8,15,26]):rect(d,x-14+i*8,y-13,5,h,0,fill=NAVY,color=None)

def shell(c):
    d=Drawing(W,H);rect(d,0,0,W,H,0,WHITE,None)
    txt(d,'BEN BALL / QUICK CHARTS',20,482,10.5,True,NAVY)
    txt(d,c['id'],340,480,17,True,NAVY,align='end')
    line(d,20,470,340,470,2,NAVY)
    # Common corner identity; large distinctive drawings occupy the reading field.
    txt(d,c['title'][0],20,443,24,True,NAVY,width=281)
    txt(d,c['title'][1],20,416,24,True,NAVY,width=320)
    icon(d,c['id'],322,443)
    txt(d,c['cue'],20,391,13,width=320)
    line(d,20,143,340,143,1.2)
    txt(d,c['write'],20,125,11.5,True,width=320)
    for y in (94,61):line(d,20,y,340,y,.45,GRAY)
    txt(d,c['source'],20,27,10,width=320)
    txt(d,'5 x 7 in. / LAYER 2 / 20 SEP 2026',20,12,8.5,color=NAVY)
    return d

def routes(d,c):
    line(d,34,361,34,212,2,NAVY)
    for i,(label,route) in enumerate(c['rows']):
        y=355-i*43
        d.add(Circle(34,y,10,fillColor=WHITE,strokeColor=NAVY,strokeWidth=2))
        txt(d,str(i+1),34,y-4,12,True,NAVY,align='middle')
        txt(d,label,55,y,13,True,width=270)
        txt(d,route,55,y-19,14,width=280)
        rect(d,320,y-3,12,12,1.2)
    txt(d,c['note'],20,158,13,width=320)

def water(d,c):
    txt(d,'YOU SEE',20,363,11.5,True)
    for i,(clue,question) in enumerate(c['rows']):
        x=20+i*110
        rect(d,x,301,100,48,1.4)
        label=wrap(clue.replace('\n',' '),84,14,True)
        txt(d,label,x+8,330,14,True,width=84)
        arrow(d,x+50,296,x+50,279)
        txt(d,wrap(question.replace('\n',' '),96,14),x+2,248,14,width=96)
    txt(d,'CHECK NEXT',20,268,11.5,True)
    txt(d,c['note'],20,158,13,width=320)

def structure(d,c):
    # Concept sketch shows relationships only, never an inferred existing assembly.
    rect(d,28,342,116,9,1.6)
    for x in (38,61,84,107,130):line(d,x,342,x,331,1.2)
    rect(d,42,295,90,13,1.8)
    rect(d,80,242,14,53,1.8)
    rect(d,63,228,48,14,1.6)
    line(d,24,221,143,221,1.5)
    for x in range(28,140,13):line(d,x,221,x-7,211,.8)
    arrow(d,54,330,54,310);arrow(d,120,282,120,246)
    levels=[350,305,253,209]
    targets=[(144,347),(132,302),(111,237),(143,221)]
    for (a,b),y,(xx,yy) in zip(c['rows'],levels,targets):
        line(d,xx,yy,156,y-4,.75,GRAY)
        txt(d,a,165,y,13,True,width=175)
        txt(d,wrap(b,175,13),165,y-17,13,width=175)
    txt(d,'CONCEPT / NTS',30,189,10.5)
    txt(d,c['note'],20,158,13,width=320)

def movement(d,c):
    for i,(label,meaning) in enumerate(c['rows']):
        x=20+(i%2)*165;top=375-(i//2)*88
        txt(d,label.upper(),x,top-18,14,True,width=155)
        y=top-43
        line(d,x,y,x+130,y,.55,GRAY,[3,2])
        if i==0:line(d,x,y+7,x+130,y-7,2)
        elif i==1:d.add(PolyLine([x,y,x+32,y,x+43,y+7,x+59,y-6,x+73,y+4,x+88,y,x+130,y],strokeColor=INK,strokeWidth=2))
        elif i==2:d.add(PolyLine([x,y+7,x+22,y+1,x+44,y-4,x+66,y-6,x+88,y-4,x+110,y+1,x+130,y+7],strokeColor=INK,strokeWidth=2))
        else:
            line(d,x,y,x+130,y,2);arrow(d,x+65,y+3,x+65,y+13);arrow(d,x+65,y-3,x+65,y-13)
        txt(d,wrap(meaning,150,13),x,top-69,13,width=150)
    txt(d,c['note'],20,177,13,width=320)

def pipes(d,c):
    for i,(name,purpose) in enumerate(c['rows']):
        y=356-i*46
        txt(d,name,112,y,13,True,width=226)
        txt(d,wrap(purpose,226,14),112,y-19,14,width=226)
        if i==0:
            line(d,23,y-11,78,y-11,3);arrow(d,78,y-11,101,y-11,2)
        elif i==1:
            line(d,23,y-3,49,y-3,2);line(d,49,y-3,49,y-14,2);line(d,49,y-14,80,y-14,2);arrow(d,80,y-14,101,y-14,2)
        else:
            line(d,23,y-11,98,y-11,1.6,dash=[5,4]);d.add(Circle(23,y-11,4,fillColor=WHITE,strokeColor=INK,strokeWidth=1.2))
    line(d,20,229,340,229,.6)
    txt(d,'SUMP',20,213,12,True);txt(d,'EJECTOR',187,213,12,True)
    txt(d,'Groundwater',20,194,14);txt(d,'Wastewater',187,194,14)
    txt(d,c['note'],20,175,13,width=320)

def heat(d,c):
    for i,(name,process) in enumerate(c['rows']):
        y=356-i*69
        txt(d,name,20,y,13,True,width=320)
        chunks=[x.strip() for x in process.split('>')]
        w=(320-(len(chunks)-1)*16)/len(chunks)
        for j,chunk in enumerate(chunks):
            x=20+j*(w+16)
            rect(d,x,y-43,w,30,1.3)
            txt(d,chunk,x+w/2,y-33,14,align='middle',width=w-10)
            if j<len(chunks)-1:arrow(d,x+w+2,y-28,x+w+14,y-28)
    txt(d,c['note'],20,202,13,width=320)

def electrical(d,c):
    for i,(name,purpose) in enumerate(c['rows']):
        x=20+(i%2)*165;y=283-(i//2)*92
        rect(d,x,y,155,89,1.1)
        # Upper corner cutout gives each function an independent place to mark.
        txt(d,name,x+9,y+67,14,True,width=137)
        txt(d,wrap(purpose.replace('\n',' '),137,13),x+9,y+42,13,width=137)
        rect(d,x+134,y+67,10,10,.8)
    txt(d,c['note'],20,177,13,width=320)

def slope(d,c):
    txt(d,'RISE OVER 12 IN. OF HORIZONTAL RUN',20,363,11.5,True,width=320)
    baseline=225
    line(d,20,baseline,340,baseline,1)
    for i,((rise,pct),value) in enumerate(zip(c['rows'],[.125,.25,.5,1])):
        x=32+i*80;height=value*95
        rect(d,x+8,baseline,40,height,0,NAVY,None)
        txt(d,pct,x+28,baseline+height+10,18,True,align='middle',width=74)
        txt(d,rise,x+28,205,14,True,align='middle',width=74)
    txt(d,c['note'],20,177,13,width=320)

DRAW={'1A':routes,'1B':water,'2A':structure,'2B':movement,'3A':pipes,'3B':heat,'4A':electrical,'4B':slope}

def make(c):
    d=shell(c);DRAW[c['id']](d,c);return d

def norm(s):return re.sub(r'\s+','',s).lower()

def build():
    base_hash=hashlib.sha256((BASE/'cards.json').read_bytes()).hexdigest()
    drawings=[make(c) for c in CARDS]
    pdf=Canvas(str(OUT/PDF),pagesize=(W,H),pageCompression=1,invariant=1)
    pdf.setTitle('Quick charts / Layer 2 / eight topic forms')
    for c,d in zip(CARDS,drawings):
        pdf.bookmarkPage(c['id']);pdf.addOutlineEntry(c['id']+' / '+c['title'][0],c['id'])
        renderPDF.draw(d,pdf,0,0);pdf.showPage();renderSVG.drawToFile(d,str(OUT/(c['id']+'.svg')))
    pdf.save()
    pdf=Canvas(str(OUT/LETTER),pagesize=(792,612),pageCompression=1,invariant=1)
    pdf.setTitle('Quick charts / Layer 2 / Letter print layout')
    order=[(0,2),(3,1),(4,6),(7,5)]
    for n,pair in enumerate(order):
        pdf.setFont('Helvetica',9);pdf.setFillColor(INK)
        pdf.drawString(27,585,'LAYER 2 / 100% ACTUAL SIZE / Landscape Letter / Duplex: flip on SHORT EDGE')
        pdf.drawRightString(765,585,f'Sheet {n//2+1} / '+('FRONT' if n%2==0 else 'BACK'))
        for x,i in zip((27,405),pair):
            renderPDF.draw(drawings[i],pdf,x,54)
            pdf.setStrokeColor(GRAY);pdf.setLineWidth(.5)
            for xx in (x,x+W):
                for yy in (54,558):
                    pdf.line(xx-5,yy,xx-1,yy);pdf.line(xx+1,yy,xx+5,yy)
                    pdf.line(xx,yy-5,xx,yy-1);pdf.line(xx,yy+1,xx,yy+5)
        pdf.setStrokeColor(INK);pdf.line(27,30,99,30);pdf.line(27,27,27,33);pdf.line(99,27,99,33)
        pdf.setFont('Helvetica',9);pdf.drawString(105,27,'This line measures 1 inch. Cut at corner marks; cards remain 5 x 7 inches.')
        pdf.showPage()
    pdf.save()
    checks=[]
    for fn,size,count in [(PDF,(W,H),8),(LETTER,(792,612),4)]:
        with pdfplumber.open(OUT/fn) as pdf:
            assert len(pdf.pages)==count
            for page in pdf.pages:
                assert (page.width,page.height)==size
                assert all(0<=c['x0']<=c['x1']<=page.width and 0<=c['top']<c['bottom']<=page.height for c in page.chars)
                assert not any(c['text'] in ('\ufffd','\x7f','\u25a0') for c in page.chars)
        checks.append(dict(file=fn,pages=count,points=list(size),sha256=hashlib.sha256((OUT/fn).read_bytes()).hexdigest()))
    doc=PdfReader(OUT/PDF)
    for i,c in enumerate(CARDS):
        extracted=norm(doc.pages[i].extract_text())
        required=c['title']+[c['cue'],c['note'],c['write'],c['source']]
        for row in c['rows']:
            for value in row:required.extend(x.strip() for x in value.split('>'))
        for value in required:assert norm(value) in extracted,(c['id'],value)
    assert [round(100*x/12,1) for x in [.125,.25,.5,1]]==[1.0,2.1,4.2,8.3]
    data=dict(SOURCE,layer=2,title='Quick charts / eight individual forms',base=dict(path='../Quick Charts - Trial/cards.json',sha256=base_hash),forms=FORMS,content_policy='Original rows, cautions, source pointers and handwriting prompts retained. Content reflows into category-specific diagrams.',cards=CARDS)
    (OUT/'cards.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    parts=[]
    for c in CARDS:
        id=c['id'];parts.append('<section><h2>'+id+' / '+c['title'][0]+'</h2><p>'+FORMS[id]+'</p><div class="pair"><figure><figcaption>Base</figcaption><img src="../Quick Charts - Trial/'+id+'.svg" alt="Original '+c['title'][0]+' card"></figure><figure><figcaption>Layer 2</figcaption><img src="'+id+'.svg" alt="'+FORMS[id]+'"></figure></div></section>')
    page='''<!doctype html><html><head><meta charset="utf-8"><title>Quick charts / Layer 2</title><style>body{max-width:1050px;margin:40px auto;padding:0 20px;font:18px system-ui;color:#111}a{color:#1A1A5E}h1,h2{color:#1A1A5E}p{line-height:1.5}.pair{display:flex;gap:22px;flex-wrap:wrap}figure{margin:0 0 24px}img{width:360px;max-width:100%;border:1px solid #aaa}figcaption{font-weight:bold;margin:8px 0}</style></head><body><h1>Same eight topics. Eight individual visual forms.</h1><p>Layer 2 uses the first card set as its content base. IDs, notes, source pointers and white handwriting areas remain. The structure sketch is conceptual and not to scale; the slope bars compare rise per horizontal foot. All figures are locally generated vectors.</p><p><a href="'''+PDF+'''">5 x 7 cards</a> / <a href="'''+LETTER+'''">Letter print layout</a> / <a href="cards.json">Editable data</a> / <a href="../Quick Charts - Trial/index.html">Original set</a></p><p>Print at 100% / Actual Size on uncoated stock. Letter version: landscape, short-edge duplex. Eight faces make four cards; carry the ones you need. This is a topic aid, not a complete inspection checklist.</p>'''+''.join(parts)+'''</body></html>'''
    (OUT/'index.html').write_text(page,encoding='utf-8')
    (OUT/'README.md').write_text('''# Quick charts: Layer 2

Eight visual forms built from the first eight card topics, unchanged 5 x 7 inch portrait format. Four duplex cards. The original set remains beside this folder and is shown alongside Layer 2 in index.html.

1A route spine; 1B evidence windows; 2A bearing sketch; 2B movement profiles; 3A separate pipe routes; 3B process tracks; 4A independent function tiles; 4B proportional rise chart. Outline, position and geometry carry the differentiation in monochrome. Typography and notes use the common BBDF family.

Working words are 14 pt; diagram labels/qualifications 13 pt; source references 10 pt. White crayon strip and original prompts remain unchanged. Source data are inherited from the original cards.json; this layer does not reauthor technical content. Sketches are conceptual, not depictions of a surveyed property or repair instructions.

The 5x7 PDF has eight faces. Landscape Letter has four pages, two cards per page, mirrored back order: 1A/2A, 2B/1B, 3A/4A, 4B/3B. Print Actual Size, short-edge duplex; check the one-inch line and the first sheet front/back. Use matte uncoated stock for marks. Actual flashlight/crayon usability still needs a physical field test.

Local builder: BB_CODE/.scratch/sg009/field_cards_layer2.py. It reads the published first-set cards.json, validates every inherited text claim against final PDF extraction, and emits the PDFs, SVGs and metadata. SVGs and JSON remain editable. No image model is used. Current BBDF palette tokens are read at build time. Not a canonical design-category admission or a conference-room action.
''',encoding='utf-8')
    result=dict(status='mechanical checks passed',pdfs=checks,base_sha256=base_hash,base_topics=8,distinct_layouts=len(set(FORMS.values())),inherited_text_preserved=True,visual_review='pending',physical_test='not performed')
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':build()
