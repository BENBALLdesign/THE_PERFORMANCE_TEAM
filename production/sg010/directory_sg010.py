"""SG-010 Start Here directory (Part B step 8): three pages, every shelf PDF linked.

Follows the SG-009 C1 `00 - START HERE.pdf` layout (START HERE / TAKE WHAT YOU NEED / KEEP THE EVIDENCE) with the
SG-010 rows read from the staged manifest rows, not hardcoded. Local GoToR links open the shelf PDFs in a desktop
reader; the footer legend repeats the shared visual language. validate() re-reads the finished PDF and checks that
every link resolves to a shelf file and page and that every manifest row is linked.
"""
from prepare import *
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ArrayObject,BooleanObject,DictionaryObject,NameObject,NumberObject,TextStringObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
sys.path.insert(1,str(REPO));sys.path.insert(2,str(BUILDER))
import card_brand
NAVY=HexColor('#1a1a5e');CRIMSON=HexColor('#8b1a1a');PALE=HexColor('#f3f3f8');REF=HexColor('#424956');RED=HexColor('#B3262E')
DATE='22 SEPTEMBER 2026';PAGES=3
LINKS=[]
def text(c,value,x,y,size=11,bold=False,color=NAVY):
    c.setFillColor(color);c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.drawString(x,y,value)
def right(c,value,x,y,size=10):
    c.setFillColor(NAVY);c.setFont('Helvetica',size);c.drawRightString(x,y,value)
def paragraph(c,body,x,y,width,size=11,leading=14):
    p=Paragraph(body,ParagraphStyle('body',fontName='Helvetica',fontSize=size,leading=leading,textColor=NAVY));_,h=p.wrap(width,700);p.drawOn(c,x,y-h);return y-h
def heading(c,label,y):
    text(c,label,36,y,13,True);c.setStrokeColor(NAVY);c.setLineWidth(.7);c.line(36,y-8,576,y-8)
def local_link(c,label,record,x,y,size=11,page=0):
    text(c,label,x,y,size,True);w=c.stringWidth(label,'Helvetica-Bold',size)
    c.setStrokeColor(NAVY);c.setLineWidth(.35);c.line(x,y-2,x+w,y-2)
    token='LOCALPDF:'+str(len(LINKS));LINKS.append(dict(token=token,file=record['file'],page=page))
    c.linkURL(token,(x,y-3,x+w,y+size+2),relative=0,thickness=0)
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
    c.setFillColor(RED);bar=size*.28;c.rect(x-bar/2,y-size/2,bar,size,fill=1,stroke=0);c.rect(x-size/2,y-bar/2,size,bar,fill=1,stroke=0)
def legend(c,y=38):
    c.setFillColor(NAVY);c.setFont('Helvetica',7.8);c.drawString(54,y,'COLOR = HOUSE AREA')
    pattern(c,150,y-1,15,7,'limit');c.setFillColor(NAVY);c.drawString(169,y,'HATCH = LIMIT / QUALIFICATION')
    pattern(c,300,y-1,15,7,'reference');c.setFillColor(NAVY);c.drawString(319,y,'DOTS = SOURCE / REFERENCE')
    cross(c,452,y+2.5,6.5);c.setFillColor(NAVY);c.drawString(460,y,'CROSS = SAFETY-RELATED')
def header(c,title,sub,page):
    d=Drawing(25,57);card_brand.mark(d,0,0,25);renderPDF.draw(d,c,550,718)
    c.setFillColor(NAVY);c.setFont('Times-Bold',29);c.drawString(36,747,title);text(c,sub,36,724,11)
    text(c,'HOME INSPECTION / SG-010 / '+DATE,36,699,9,True)
    c.setStrokeColor(CRIMSON);c.setLineWidth(2);c.line(36,688,576,688)
    text(c,'BEN-Ball | SG-010 / R1 + V2 + MD1 | Through S39 / cumulative edition',36,27,8);text(c,f'{page} / {PAGES}',552,27,8);legend(c)
def build(files,dest,raw):
    """files: manifest rows with pages; dest: final PDF path; raw: scratch path for the unlinked canvas."""
    LINKS.clear();kind=lambda k:[r for r in files if r['kind']==k]
    c=canvas.Canvas(str(raw),pagesize=(612,792),pageCompression=1,invariant=1)
    c.setTitle('Home Inspection - Current Edition - Start Here');c.setAuthor('BEN-Ball')
    guides={r['edition']:r for r in kind('guide')}
    # Page 1
    header(c,'START HERE','Choose the cut. Print only what earns its place.',1)
    heading(c,'THE THREE GUIDES',662)
    for i,(ed,label) in enumerate([('SG-010','Field study + colleague discussion'),('SG-010-W1','Walking cut: -30 to +20 minutes'),('SG-010-L1','Long cut: component detail')]):
        r=guides[ed];y=630-i*51;local_link(c,ed,r,36,y,15);text(c,label,185,y,12,True);text(c,f"{r['pages']} pages / {(r['pages']+1)//2} sheets duplex",185,y-19,11)
    compact=guides['SG-010'];l1=guides['SG-010-L1']
    nav=read(WORK/'navigation/navigation-review.json');finder=nav['linked_pages']['SG-010'][0];idx=nav['linked_pages']['SG-010-L1']
    paragraph(c,'SG-010 is the cumulative edition through S39. It adds kitchen and bath appliances, alarms and life safety, insulation and ventilation, professional scope and reporting, hydronic, steam and electric heat, cooling water and air, and interior floors, glazing, egress, doors, stairs and fireplaces. Existing lessons, definitions and evidence are retained.',36,478,540,10.5,14)
    paragraph(c,f'Find a subject in the contents, a familiar word in the index, and its meaning in the glossary. Compact location table: p.1; finder: p.{finder}. Long-cut contents: pp.2-7; index: pp.{idx[0]}-{idx[-1]}, with glossary page references. Walking cut: follow the visit route.',36,426,540,10.5,14)
    heading(c,'APPENDICES / SAME SUBJECT, TWO DEPTHS',358)
    text(c,'Subject',36,334,10,True);text(c,'Compact',370,334,10,True);text(c,'Long cut',482,334,10,True)
    labels=['Field tools','Reference + record tools','Report prompts + mentions','Glossary + numbered notes','Sources + evidence','Construction-era packing','Exam + lesson corrections','Codes + practice timeline']
    small=sorted(kind('compact'),key=lambda r:r['id']);large=sorted(kind('long'),key=lambda r:r['id']);assert [r['id'] for r in small]==[r['id'] for r in large]==['APP-'+x for x in 'ABCDEFGH']
    for i,(s,l,title) in enumerate(zip(small,large,labels)):
        y=309-i*24
        if i%2==0:c.setFillColor(PALE);c.rect(32,y-6,548,22,fill=1,stroke=0)
        text(c,s['id'][-1],40,y,11,True);text(c,title,65,y,11);local_link(c,f"{s['pages']} pp",s,370,y);local_link(c,f"{l['pages']} pp",l,482,y)
    cp=sum(r['pages'] for r in small);lp=sum(r['pages'] for r in large)
    text(c,f'{cp} compact appendix pages / {lp} long-cut pages. Select what you need.',36,104,10.5)
    paragraph(c,'Click an underlined title or page count to open its PDF in a desktop reader. Keep this directory with its folders. Previous editions remain in Study Guide Editions; this shelf contains the matching current set.',36,86,540,10,13)
    # Page 2
    c.showPage();header(c,'TAKE WHAT YOU NEED','Area cards and a property-specific working packet.',2)
    cards=kind('cards');five=next(r for r in cards if '5x7' in r['file']);letter=next(r for r in cards if 'LETTER' in r['file'])
    local_link(c,f"{five['pages']} cards / 5 x 7",five,36,660,13);local_link(c,f"Letter print / {letter['pages']} sheets",letter,300,660,13)
    paragraph(c,'Red cross = safety relevance. Blue crab / MD = Maryland-specific detail. Ring = detail to examine. These are reference cues, not findings. Letter: landscape, actual size, single-sided; cut at marks. Backs remain blank. SG-010 rebinds 22 cards to the new facts; card wording and IDs are unchanged.',36,642,540,10.5,14)
    text(c,'House area',36,574,10,True);text(c,'5 x 7 pages',375,574,10,True);text(c,'Letter pages',480,574,10,True)
    areas=['Approach, grounds + drainage','Walls, openings + decks','Garage','Basement + crawl space','Mechanical + electrical','Interior rooms + stairs','Kitchen, baths + laundry','Attic, roof + chimney']
    for i,area in enumerate(areas):
        y=550-i*22
        if i%2==0:c.setFillColor(PALE);c.rect(32,y-5,548,21,fill=1,stroke=0)
        text(c,f'{i+1:02}  {area}',40,y,11);local_link(c,f'{i*8+1}-{i*8+8}',five,383,y,11,page=i*8);local_link(c,f'{i*4+1}-{i*4+4}',letter,492,y,11,page=i*4)
    text(c,'One area = eight cards / four Letter sheets.',36,366,11,True)
    diagram=kind('diagram')[0];local_link(c,'3-WAY & 4-WAY SWITCHES / Source Diagrams, sheet 1',diagram,36,344,11)
    heading(c,'505 WALKER AVE / DESKTOP PREPARATION',312)
    props=kind('property');combined=[r for r in props if 'COMBINED' in r['file']];others=[r for r in props if 'COMBINED' not in r['file']]
    for i,r in enumerate(combined+others):local_link(c,r['title'],r,36,283-i*22,11.5)
    y=283-len(props)*22-4
    y=paragraph(c,'City year: 1895. Addition permit: 5 March 2018, one story over an existing basement. Overhead evidence brackets the south roof change to 2017-2018; the front dormer remains within the 2013-2019 facade window. Finals and completion dates remain unverified.',36,y,540,10.5,14)
    paragraph(c,'The combined packet adds two SG-010 pages: card routes to the current charts, and conditional prompts from the new course material. They cite only the retained findings and add no observed condition. Visual R2 imagery, the outline and the 12 property cards carry forward; card footers now name SG-010.',36,y-10,540,10.5,14)
    # Page 3
    c.showPage();header(c,'KEEP THE EVIDENCE','Original source PDFs, beside the current study material.',3)
    paragraph(c,'These are copies of the cited editions, retrieved 20-21 September 2026. A manual belongs to its named product; a code date needs the correct jurisdiction and permit context. Web-only sources remain linked in APP-E and APP-H.',36,661,540,11,15)
    text(c,'Source ID',36,596,10,True);text(c,'Document',126,596,10,True)
    sources=kind('source');assert len(sources)<=22
    for i,r in enumerate(sources):
        y=575-i*19
        if i%2==0:c.setFillColor(PALE);c.rect(32,y-5,548,18,fill=1,stroke=0)
        text(c,r['id'],40,y,8.5,True);local_link(c,r['title'],r,126,y,9.5);right(c,str(r['pages'])+' pp',576,y,9.5)
    y=575-len(sources)*19-10
    heading(c,'SOURCE GAP / H14',y)
    paragraph(c,'The cited Fire Prevention Commission minutes from 16 April 2015 return 404. No verified PDF copy was recovered. The source ID and uncertainty remain visible; no substitute was presented as the original. H04 lists the 2026 NEC effective 1 September 2026 for Baltimore County only; the Harford source conflict remains identified.',36,y-18,540,10,13)
    c.save()
    writer=PdfWriter();writer.clone_document_from_reader(PdfReader(raw));tokens={x['token']:x for x in LINKS}
    for page in writer.pages:
        for ann in page.get('/Annots',[]):
            item=ann.get_object();a=item.get('/A',{});token=str(a.get('/URI',''))
            if token in tokens:
                v=tokens[token];item[NameObject('/A')]=DictionaryObject({NameObject('/S'):NameObject('/GoToR'),NameObject('/F'):TextStringObject(v['file']),NameObject('/D'):ArrayObject([NumberObject(v['page']),NameObject('/Fit')]),NameObject('/NewWindow'):BooleanObject(True)})
    dest.parent.mkdir(parents=True,exist_ok=True);writer.write(dest);Path(raw).unlink();return dest
def validate(shelf,files,dest):
    """Every GoToR link in the directory opens an existing shelf PDF at a valid page; every manifest row is linked."""
    reader=PdfReader(dest);linked=set();links=0;pages={r['file']:r['pages'] for r in files}
    for page in reader.pages:
        for ann in page.get('/Annots',[]):
            a=ann.get_object().get('/A',{})
            if a.get('/S')!='/GoToR':continue
            f=str(a['/F']);assert (shelf/f).is_file(),f;assert f in pages,f
            assert 0<=int(a['/D'][0])<pages[f],(f,a['/D'][0]);linked.add(f);links+=1
    assert linked==set(pages),set(pages)^linked
    assert len(reader.pages)==PAGES
    return dict(links=links,linked_pdfs=len(linked),pages=PAGES)
