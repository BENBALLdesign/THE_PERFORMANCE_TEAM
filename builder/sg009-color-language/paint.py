"""Local, source-preserving colour and pattern layer for the complete SG-009 family."""
from pathlib import Path
import json,hashlib,shutil,io,re,sys,math,datetime
from collections import Counter
import pdfplumber
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream,FloatObject,NameObject
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor,Color,white

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[1]/'tools'));import team_paths;TEAM=team_paths.installation()
TRAINING=TEAM/'Home Inspection Training';LIB=TRAINING/'Study Guide Editions';CURRENT=TRAINING/'CURRENT EDITION'
PARENT='S32-N2-2026-09-21';REV='S32-C1-2026-09-21'
sys.path.insert(0,str(HERE.parents[1]/'tools'))
import home_inspection_storage as storage
ARTIFACT_ROOT=storage.work_root(HERE.name)
BASE=ARTIFACT_ROOT/'baseline';OUT=ARTIFACT_ROOT/'output/pdf';STAGE=ARTIFACT_ROOT/'stage';ISSUE=ARTIFACT_ROOT/'frozen-issue'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cp(a,b):
 b=Path(b);b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
def freeze():
 assert not BASE.exists()
 assert read(CURRENT/'_Maintenance/issue.json')['current_issue']==PARENT
 m=read(CURRENT/'_Maintenance/manifest.json');docs=[dict(r) for r in m['files'] if r['kind'] in ['guide','cards','compact','long']]
 docs.append(dict(file='00 - START HERE.pdf',source=str(CURRENT/'00 - START HERE.pdf'),kind='directory',pages=3))
 assert len(docs)==22
 files=[]
 for r in docs:cp(CURRENT/r['file'],BASE/'pdf'/r['file']);files += [CURRENT/r['file'],Path(r['source'])]
 for ed in ['SG-009','SG-009-L1','SG-009-W1']:
  for p in (LIB/ed).glob('*.json'):cp(p,BASE/'data'/ed/p.name);files.append(p)
 for p in (LIB/'SG-009/Appendices').rglob('*.json'):
  if 'Quick Charts - Trial' not in str(p):cp(p,BASE/'data/SG-009/Appendices'/p.relative_to(LIB/'SG-009/Appendices'));files.append(p)
 cards=LIB/'SG-009/Appendices/Quick Charts - 64 Cards'
 for p in cards.glob('*.svg'):cp(p,BASE/'svg'/p.name);files.append(p)
 for p in [TEAM/'STUDY-GUIDE-EDITIONS.json',TEAM/'APPENDIX-VERSIONS.json',CURRENT/'_Maintenance/manifest.json']:
  cp(p,BASE/'registry'/p.name);files.append(p)
 for p in (CURRENT).rglob('*'):
  if p.is_file():files.append(p)
 save(HERE/'baseline.json',dict(parent=PARENT,files={str(p):sha(p) for p in dict.fromkeys(files)}))
 save(HERE/'documents.json',docs)

AREA={0:('#424956','Throughout'),1:('#43624E','Site'),2:('#8C523A','Exterior'),3:('#655673','Garage'),4:('#245B70','Lowest'),5:('#1A1A5E','Systems'),6:('#775238','Rooms'),7:('#216865','Wet rooms'),8:('#635B26','Attic / roof')}
NAVY=HexColor('#1A1A5E');NOTE=HexColor('#D4AC0D');REF=HexColor('#424956')
LIMIT_CARDS=set(range(1,65))-{3,4,24,27,35,43,48,50,51,53,57,62}
def rgb(a):return tuple(HexColor(AREA[a][0]).rgb())
def tint(a,p=.19):return tuple(1-p+p*x for x in rgb(a))
def normalized(s):return re.sub(r'[^a-z0-9]','',s.casefold())
def point(m,x,y):return m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]
def mul(a,b):
 return (a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5])
def typical(ids):return 5 if 5 in ids else 4 if 4 in ids else ids[0] if ids else 0

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

def rewrite_vectors(page,owner,selector,kind,sheet=False):
 """Recolour vector backgrounds; never text, image XObjects, logos or safety marks."""
 cs=ContentStream(page.get_contents(),owner);out=[];m=(1,0,0,1,0,0);fill=(0,0,0);stack=[];pts=[];count=0
 for operands,op in cs.operations:
  if op==b'q':stack.append((m,fill))
  elif op==b'Q':
   if stack:m,fill=stack.pop()
  elif op==b'cm':m=mul(m,tuple(map(float,operands)))
  elif op==b'rg':fill=tuple(map(float,operands))
  elif op==b'g':fill=(float(operands[0]),)*3
  elif op==b're':
   x,y,w,h=map(float,operands);pts += [point(m,x,y),point(m,x+w,y),point(m,x+w,y+h),point(m,x,y+h)]
  elif op in [b'm',b'l']:pts.append(point(m,*map(float,operands)))
  elif op in [b'c',b'v',b'y']:pts=[] # Curved objects are not table rectangles.
  if op in [b'f',b'f*',b'B',b'B*',b'b',b'b*',b'S',b's',b'n']:
   colour=None
   if pts and op in [b'f',b'f*',b'B',b'B*']:
    xs=[p[0] for p in pts];ys=[p[1] for p in pts];x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys);w=x1-x0;h=y1-y0
    # Four orthogonal corners only. Small logos, symbols and diagrams are protected.
    rect=len(set((round(x,2),round(y,2)) for x,y in pts))==4 and all(abs(x-x0)<.1 or abs(x-x1)<.1 for x,y in pts) and all(abs(y-y0)<.1 or abs(y-y1)<.1 for x,y in pts)
    inside=(54-1<=x0<x1<=559 and 52<=y0<y1<=750) if kind!='card' else ((27<=x0<x1<=766 and 253<=y0<y1<=559) if sheet else (0<=x0<x1<=361 and 199<=y0<y1<=505))
    if rect and inside and w>65 and 10<h<200:
     a=selector((x0+x1)/2,(y0+y1)/2)
     navy=max(abs(fill[i]-rgb(5)[i]) for i in range(3))<.04
     pale=min(fill)>.82 and max(fill)-min(fill)<.10 and min(fill)<.995
     white_fill=min(fill)>.995 and w<505 and kind=='card'
     if navy:colour=rgb(a)
     elif pale:colour=tint(a,.18 if kind=='card' else .14)
     elif white_fill:colour=tint(a,.07)
   if colour:
    out.append(([FloatObject(v) for v in colour],b'rg'));out.append((operands,op));out.append(([FloatObject(v) for v in fill],b'rg'));count+=1
   else:out.append((operands,op))
   pts=[];continue
  out.append((operands,op))
 cs.operations=out;page[NameObject('/Contents')]=cs;return count

def source_data():
 loc=read(BASE/'data/SG-009/contents-locations.json')['records']
 cards=read(BASE/'data/SG-009/Appendices/Quick Charts - 64 Cards/cards.json')['cards']
 return loc,cards

def find_start(lines,title):
 key=normalized(title);prefix=key[:min(34,len(key))]
 for l in lines:
  s=normalized(l['text'])
  if prefix in s or (len(s)>20 and key.startswith(s)):return l
 return None

def page_profile(r,n,p,loc,cards):
 lines=p.extract_text_lines(layout=False);kind=r['kind'];segments=[];areas=[];limits=[];reference=[]
 def segment(title,ids):
  l=find_start(lines,title)
  if l:segments.append(dict(top=l['top'],area_ids=ids,title=title));return l
 if kind=='guide':
  ed=r['edition']
  if ed in ['SG-009','SG-009-L1']:
   in_toc=(ed=='SG-009' and n==1) or (ed=='SG-009-L1' and 2<=n<=6)
   for record in loc.values():
    if record['edition']==ed and (in_toc or record['page']==n):segment(record['title'],record['area_ids'])
   if segments:areas=list(dict.fromkeys(a for s in segments for a in s['area_ids']))
   if ed=='SG-009' and n>=4 and n<=25:
    d=read(BASE/'data/SG-009/study-guide.json');rec=next(x for x in d['pages'] if x['printed_page']==n)
    # Third compact column is the authored qualification, never an inferred defect.
    for row in rec['rows']:
     if len(row)>2:
      l=find_start(lines,row[2])
      if l:limits.append(dict(line=l,source='compact third-column qualification'))
  else:
   ids={1:[0],2:[1],3:[1,2],4:[4],5:[5],6:[6,7],7:[8],8:[0]}[n];areas=ids;segments=[dict(top=0,area_ids=ids,title='Walking route')]
   d=read(BASE/'data/SG-009-W1/study-guide.json')['pages'][n-1]
   l=find_start(lines,d['gate'])
   if l:limits.append(dict(line=l,source='authored walking gate'))
 elif kind in ['compact','long']:
  data=read(BASE/'data/SG-009'/Path(r['source']).relative_to(LIB/'SG-009').with_suffix('.json'))
  if r['id']=='APP-D' and kind=='long':
   labels=p.crop((54,0,182,p.height)).extract_text_lines(layout=False)
   for t in data['terms']:
    ids=loc.get('SG-009-L1:'+t.get('topic',''),{}).get('area_ids',[0])
    # Only the term column owns the row; mentions inside definitions are not headings.
    l=next((q for q in labels if normalized(q['text'])==normalized(t['term'])),None)
    if l:segments.append(dict(top=l['top'],area_ids=ids,title=t['term']))
  for item in data.get('items',[]):
   if isinstance(item,dict) and item.get('limit'):
    l=find_start(lines,item['limit'])
    if l:limits.append(dict(line=l,source=item.get('id','')+':limit'))
  # A dot spine marks appendices as reference. Avoid inventing spatial categories.
  reference.append(dict(top=45,bottom=740,source='appendix reference context'))
 # Existing source lines, explicit notes and restrictions receive visible pattern tags.
 for l in lines:
  if re.match(r'^(Source notes|Source:|Sources:|L1 pp\.|Full records:)',l['text']):reference.append(dict(top=l['top'],bottom=l['bottom'],source='printed source pointer'))
  if l['text'].startswith(('NOTE:','Limit:','LIMIT:','Limits:','Unresolved:','SOURCE GAP /')):limits.append(dict(line=l,source='explicit printed qualification heading'))
 if not segments:segments=[dict(top=0,area_ids=areas or [0],title='Reference / shared')]
 segments.sort(key=lambda s:s['top'])
 return dict(segments=segments,areas=areas,limits=limits,reference=reference,lines=lines)

def overlaps(a,b):
 return min(a['x1'],b['x1'])-max(a['x0'],b['x0'])>.1 and min(a['bottom'],b['bottom'])-max(a['top'],b['top'])>.1

def protected_symbol(obj):
 for key in ['non_stroking_color','stroking_color']:
  col=obj.get(key)
  if isinstance(col,(tuple,list)) and len(col)==3:
   r,g,b=col
   if r>.35 and r>g*1.6 and r>b*1.6:return True
   if g>.25 and b>.3 and g>r*1.6 and b>r*1.6:return True
 return False

def legend(c,y=39):
 c.setFillColor(NAVY);c.setFont('Helvetica',8.5);c.drawString(54,y,'COLOR = HOUSE AREA')
 pattern(c,159,y-1,17,7,'limit');c.drawString(181,y,'HATCH = LIMIT / QUALIFICATION')
 pattern(c,349,y-1,17,7,'reference');c.drawString(371,y,'DOTS = SOURCE / REFERENCE')

def overlay_guide(c,r,n,p,pr):
 h=float(p.height);kind=r['kind'];areas=pr['areas']
 occupied=[ch for ch in p.chars if ch['text'].strip()]+[o for o in p.rects+p.curves+p.lines if protected_symbol(o)]
 tagged=set()
 def safe_pattern(x,y,w,hh,role):
  key=(round(x,2),round(y,2),round(w,2),round(hh,2),role)
  if key in tagged:return
  tagged.add(key)
  for xx in dict.fromkeys([x,34,31,24]):
   box=dict(x0=xx,x1=xx+w,top=h-y-hh,bottom=h-y)
   if not any(overlaps(box,o) for o in occupied):
    pattern(c,xx,y,w,hh,role);occupied.append(box);return
 # Wide, quiet edge tabs remain outside text and protected safety/MD glyphs.
 if areas:
  usable=[a for a in areas if a!=0] or [0];top=h-60
  for j,a in enumerate(usable[:8]):
   y=top-j*30;c.setFillColor(HexColor(AREA[a][0]));c.rect(18,y-24,14,26,fill=1,stroke=0)
   occupied.append(dict(x0=18,x1=32,top=h-y-2,bottom=h-y+24))
   c.setFillColor(white);c.setFont('Helvetica-Bold',8);c.drawCentredString(25,y-15,f'{a:02}' if a else '*')
 # Topic bars carry the same area identity into the actual body, not just the TOC.
 for s in pr['segments']:
  if s['title']=='Reference / shared':continue
  y=h-s['top']-2;ids=s['area_ids'];w=504/max(1,len(ids))
  for j,a in enumerate(ids):
   c.setFillColor(HexColor(AREA[a][0]))
   if kind in ['compact','long']:c.rect(44,y-10+j*4,5,4,fill=1,stroke=0)
   else:c.rect(54+j*w,y+4,w,2.2,fill=1,stroke=0)
 for ref in pr['reference']:
  if ref['source']=='appendix reference context':
   pattern(c,22,54,8,h-110,'reference');occupied.append(dict(x0=22,x1=30,top=56,bottom=h-54))
  else:safe_pattern(43,h-ref['bottom'],6,max(6,ref['bottom']-ref['top']),'reference')
 # Pattern tags sit in available gutter space; never lay texture under body type.
 for q in pr['limits']:
  l=q['line'];x=max(35,l['x0']-9);y=h-l['bottom'];w=5;hh=max(9,l['bottom']-l['top'])
  safe_pattern(x,y,w,hh,'limit')
 # A repeated key yields to existing source notes on crowded leaves.
 key_box=dict(x0=54,x1=558,top=h-48,bottom=h-36)
 if not any(overlaps(key_box,o) for o in occupied):legend(c)
 if kind=='directory' and n==2:
  for i in range(8):
   c.setFillColor(HexColor(AREA[i+1][0]));c.rect(32,557-i*22,5,21,fill=1,stroke=0)

def card_note_lines(card):
 from reportlab.pdfbase.pdfmetrics import stringWidth
 lines=0
 for par in card['note'].split('\n'):
  line='';lines+=1
  for word in par.split():
   proposed=(line+' '+word).strip()
   if line and stringWidth(proposed,'Helvetica',13)>320:lines+=1;line=word
   else:line=proposed
 return lines

def card_overlay(c,card,x=0,y=0):
 c.saveState();c.translate(x,y);a=card['area_number'];colour=HexColor(AREA[a][0])
 c.setFillColor(colour);c.rect(0,149,9,355,fill=1,stroke=0)
 c.rect(20,404,320,3,fill=1,stroke=0)
 c.setFillColor(Color(*tint(a,.34)));c.rect(20,367,320,3,fill=1,stroke=0)
 if card['card_number'] in LIMIT_CARDS:
  pattern(c,10,154,6,14+16*(card_note_lines(card)-1),'limit')
 pattern(c,53,36,287,5,'reference')
 c.setFillColor(NAVY);c.setFont('Helvetica',8.5);c.drawString(53,44,'Color: area   /   Hatch: limits   /   Dots: source')
 c.restoreState()

def render_document(r,loc,cards):
 src=BASE/'pdf'/r['file'];reader=PdfReader(src);w=PdfWriter();w.clone_document_from_reader(reader);profiles=[];recoloured=0
 with pdfplumber.open(src) as doc:
  for i,page in enumerate(w.pages):
   p=doc.pages[i];buf=io.BytesIO();c=Canvas(buf,pagesize=(p.width,p.height),invariant=1)
   if r['kind']=='cards':
    native=p.width<400;selected=[cards[i]] if native else cards[i*2:i*2+2]
    def selector(x,y):return selected[0 if native or x<400 else 1]['area_number']
    # The Letter file embeds the same coordinates with translations. Treat each face.
    if native:recoloured+=rewrite_vectors(page,w,selector,'card')
    else:recoloured+=rewrite_card_sheet(page,w,selected)
    for j,card in enumerate(selected):card_overlay(c,card,0 if native else (27 if j==0 else 405),0 if native else 54)
    profiles.append(dict(page=i+1,cards=[x['id'] for x in selected],areas=[x['area_number'] for x in selected]))
   else:
    pr=page_profile(r,i+1,p,loc,cards)
    def selector(x,y):
     top=p.height-y;eligible=[s for s in pr['segments'] if s['top']<=top+3]
     return typical((eligible[-1] if eligible else pr['segments'][0])['area_ids'])
    recoloured+=rewrite_vectors(page,w,selector,r['kind']);overlay_guide(c,r,i+1,p,pr)
    profiles.append(dict(page=i+1,areas=pr['areas'],segments=pr['segments'],limit_tags=[{'text':q['line']['text'],'source':q['source']} for q in pr['limits']],source_tags=len(pr['reference'])))
   c.showPage();c.save();page.merge_page(PdfReader(buf).pages[0])
 w.add_metadata({'/VisualLanguageRevision':REV});dest=OUT/r['file'];dest.parent.mkdir(parents=True,exist_ok=True);w.write(dest)
 return dict(file=r['file'],source=r['source'],kind=r['kind'],pages=len(w.pages),pdf_sha256=sha(dest),baseline_sha256=sha(src),backgrounds_recoloured=recoloured,page_profiles=profiles)

def rewrite_card_sheet(page,w,selected):
 return rewrite_vectors(page,w,lambda x,y:selected[0 if x<400 else 1]['area_number'],'card',sheet=True)

def build():
 loc,cards=source_data();reports=[]
 for r in read(HERE/'documents.json'):
  reports.append(render_document(r,loc,cards));print(r['file'],reports[-1]['backgrounds_recoloured'],flush=True)
 save(HERE/'render-report.json',dict(issue=REV,parent=PARENT,documents=reports))

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='freeze':freeze()
 else:build()
