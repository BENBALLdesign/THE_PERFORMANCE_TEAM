"""Experimental SG-010 presentation: vendored brand tokens (assets/brand), distinct chart forms."""
from pathlib import Path
import sys,json,re,hashlib,textwrap,copy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import team_paths
from types import SimpleNamespace
from reportlab.lib.colors import HexColor,Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph,Table,TableStyle,Frame,PageTemplate,Flowable
from reportlab.graphics.shapes import Drawing,Rect,String,Line,PolyLine,Circle,Polygon
from reportlab.graphics import renderSVG
from prepare import OUT,HERE,read,save

_assets=team_paths.brand()   # vendored print tokens and canonical logo
_tokens=_assets/'tokens';_palette=json.loads((_tokens/'palette.json').read_text(encoding='utf-8'))['color']
def token(key):
 value=_palette
 for part in key.split('.'):value=value[part]
 return value['$value']
BRAND=SimpleNamespace(hex=token,tokens_dir=_tokens,logo_path=_assets/'logos/BENBALL_A_logo.png')
N=HexColor(BRAND.hex('navy.primary'));R=HexColor(BRAND.hex('crimson.accent'))
GRAY=HexColor(BRAND.hex('structural.rule'));TINT=HexColor(BRAND.hex('structural.alt-row'));WHITE=HexColor(BRAND.hex('structural.white'))
DARK=HexColor(BRAND.hex('footer.dark'));LIGHT=HexColor(BRAND.hex('footer.text'))
W=504
PROFILE={'APP-A':('FIELD KIT','Selection matrix'),'APP-B':('RECORD ROUTES','Question / evidence'),
 'APP-C':('REPORT LOGIC','Observation / meaning / action'),'APP-D':('DISTINCTIONS','Paired concepts'),
 'APP-E':('EVIDENCE TRAIL','Claim / source / limits'),'APP-F':('ERA CARDS','Age / alterations / kit'),
 'APP-G':('REVIEW LAB','Claim / correction'),'APP-H':('LOCAL TIMELINE','Model year / effective date')}
CHARTS=[]

def clean(s):
 return str(s).replace('→',' > ').replace('≠',' is not ').replace('≤',' <= ').replace('≥',' >= ').replace('•',' / ').replace('–','-').replace('—','-').replace('\u2011','-').replace('\u00a0',' ')

def label(d,text,x,top,width,size=11,bold=False,color=N,leading=None,max_lines=None,align='left'):
 text=clean(text);font='Helvetica-Bold' if bold else 'Helvetica';leading=leading or size*1.25
 lines=[]
 for par in text.split('\n'):
  line=''
  for word in par.split():
   candidate=(line+' '+word).strip()
   if pdfmetrics.stringWidth(candidate,font,size)>width and line:lines.append(line);line=word
   else:line=candidate
  lines.append(line)
 if max_lines:assert len(lines)<=max_lines,(text,width,size,lines)
 for j,line in enumerate(lines):
  px=x+width/2 if align=='center' else x
  d.add(String(px,top-size-j*leading,line,fontName=font,fontSize=size,fillColor=color,textAnchor='middle' if align=='center' else 'start'))
 return len(lines)*leading

def rule(d,x,y,w,color=GRAY,thick=.7):d.add(Line(x,y,x+w,y,strokeColor=color,strokeWidth=thick))
def arrow(d,x1,y1,x2,y2,dashed=False,color=N):
 d.add(Line(x1,y1,x2,y2,strokeColor=color,strokeWidth=1,strokeDashArray=[3,3] if dashed else None))
 import math
 a=math.atan2(y2-y1,x2-x1);sz=4
 d.add(Polygon([x2,y2,x2-sz*math.cos(a-.55),y2-sz*math.sin(a-.55),x2-sz*math.cos(a+.55),y2-sz*math.sin(a+.55)],fillColor=color,strokeColor=color))

def tile(d,x,top,w,h,title,text='',fill=WHITE,tag=None):
 d.add(Rect(x,top-h,w,h,fillColor=fill,strokeColor=GRAY,strokeWidth=.7))
 yy=top-10
 if tag:label(d,tag,x+10,yy,w-20,9,True,color=R);yy-=17
 hh=label(d,title,x+10,yy,w-20,11.5,True);yy-=hh+6
 if text:
  hh=label(d,text,x+10,yy,w-20,10.5);assert yy-hh>=top-h+7,(title,text,yy-hh,top-h)

def publish_chart(d,id):
 folder=OUT/'DesignCharts';folder.mkdir(exist_ok=True)
 renderSVG.drawToFile(d,str(folder/(id+'.svg')))
 if id not in CHARTS:CHARTS.append(id)
 return d

def chain(nodes,id,width=W,height=65,caption=None):
 d=Drawing(width,height);gap=18;cw=(width-gap*(len(nodes)-1))/len(nodes)
 for i,node in enumerate(nodes):
  x=i*(cw+gap);tile(d,x,height-3,cw,height-(22 if caption else 6),node,fill=TINT)
  if i<len(nodes)-1:arrow(d,x+cw+2,height/2,x+cw+gap-3,height/2)
 if caption:label(d,caption,0,14,width,8.5)
 return publish_chart(d,id)

LINKS={
 'method':(['Evidence','Observation','Meaning','Action'], 'Keep each statement at its own level.'),
 'foundation_water':(['Roof discharge','Ground / grade','Wall / opening','Interior clue'],'Possible investigation route; a stain does not establish the source.'),
 'load_paths':(['Member','Connection','Bearing','Foundation'],'Trace continuity at the interfaces.'),
 'walls':(['Interruption','Flashing lap','Drainage path','Outlet'],'The visible face is only one part of water management.'),
 'roof_cover':(['Roof plane','Intersection','Drain / gutter','Discharge'],'Follow water beyond the roof covering.'),
 'water':(['Source','Distribution','Fixture response','Waste route'],'Supply, flow and drainage require separate observations.'),
 'dwv':(['Fixture','Trap / seal','Drain + vent','Outlet / pump'],'A successful fixture test leaves concealed piping unresolved.'),
 'water_heat':(['Label / energy','Water path','Relief path','Air / vent'],'Identify the device before applying an installation detail.'),
 'service':(['Supply','Disconnect','Distribution','Branch circuit'],'Trace accessible components without entering energized space.'),
 'gas_heat':(['Combustion air','Burner','Heat exchanger','Vent'],'Combustion path; room-air circulation is a separate path.'),
 'oil_heat':(['Tank / lines','Burner','Draft / vent','Heat delivery'],'Fuel, combustion and distribution are separate inspection questions.')}

def topic_chart(p):
 """Retain all reviewed words; choose a structure suited to the comparison."""
 import build as b
 rows=p['rows'];flow=[]
 if p['id'] in LINKS:
  nodes,note=LINKS[p['id']];flow +=[chain(nodes,'topic-'+p['id'],height=73,caption=note),b.Spacer(1,9)]
 # A route uses successive numbered bands. A comparison uses a small matrix.
 # Other topics use paired cards, with the same reviewed words and limits.
 if p['id'] in {'method','service','oil_heat'}:
  bands=[];routehead=ParagraphStyle('RouteHead',parent=b.H2,fontSize=11.5,leading=14,spaceAfter=4)
  for i,(term,evidence,qualifier) in enumerate(rows):
   bands.append([b.para(str(i+1).zfill(2),routehead),[b.para(term,routehead),b.para(evidence,b.BODY)],[b.para(qualifier,b.BODY)]])
  t=Table(bands,colWidths=[31,253,220],hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(0,-1),TINT),('LINEAFTER',(0,0),(0,-1),1,N),('LINEBELOW',(0,0),(-1,-1),.5,GRAY),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));flow.append(t);return flow
 if p['id'] in {'movement','openings','devices','load_paths'}:
  flow.append(b.table(dict(headers=['Distinction','What the evidence supports','What remains separate'],rows=rows,widths=[99,210,195])));return flow
 # Three paired rows of cards. The headings carry the subjects; the rule
 # separates evidence from qualification without implying causation.
 cards=[];style=ParagraphStyle('ChartBody',parent=b.BODY,fontSize=10.8,leading=13.2,spaceAfter=5)
 head=ParagraphStyle('ChartHead',parent=b.H2,fontSize=11.5,leading=14,spaceAfter=5)
 for i,(term,evidence,qualifier) in enumerate(rows):
  card=[b.para(term,head),b.para(evidence,style),b.para('Limit / question',ParagraphStyle('QualifierTag',parent=style,fontSize=8.5,leading=10.5,fontName='Helvetica-Bold',textColor=R)),b.para(qualifier,style)]
  cards.append(card)
 cells=[]
 for i in range(0,len(cards),2):cells.append([cards[i],cards[i+1] if i+1<len(cards) else []])
 table=Table(cells,colWidths=[252,252],hAlign='LEFT');table.setStyle(TableStyle([
  ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),11),
  ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
  ('LINEBEFORE',(1,0),(1,-1),.5,GRAY),('LINEBELOW',(0,0),(-1,-1),.6,GRAY)]))
 flow.append(table);return flow

def housing_chart():
 import housing
 data=housing.dataset();d=Drawing(W,273);left=105;col=57
 for k,t in enumerate(['pre-1940','1940-59','1960-79','1980-99','2000-09','2010-19','2020+']):label(d,t,left+k*col,268,col,8.4,True,align='center')
 for j,c in enumerate(data['counties']):
  y=228-j*33;label(d,c['name'].replace(' County','').replace('city','City'),0,y+19,102,10.5,True)
  for k,v in enumerate(c['groups']):
   x=left+k*col;d.add(Rect(x+4,y,49,27,fillColor=TINT,strokeColor=None));bw=v['percent']/50*49
   d.add(Rect(x+4,y, min(bw,49),3,fillColor=N,strokeColor=None));label(d,str(round(v['percent']))+'%',x,y+21,col,10.3,align='center')
 label(d,'Each cell: share of housing units. The small bar uses a common 0-50% scale.',0,22,W,9)
 return publish_chart(d,'county-age-small-multiples')

def stock_routes():
 d=Drawing(W,423)
 entries=[('Baltimore City','68% pre-1960','Alteration layers','Water + load paths'),('Baltimore County','29% in 1960-79','Material generations','Wiring + pipe IDs'),('Anne Arundel','29% in 1980-99','Mixed replacements','Roof-wall / deck'),('Carroll','81% detached','Actual site services','Access / well scope'),('Harford','34% in 1980-99','Original vs replaced','Drainage + equipment'),('Howard','41% in 1980-99','Repair interfaces','Labels + records')]
 for j,(place,stock,question,route) in enumerate(entries):
  y=414-j*65;tile(d,0,y,153,54,place,stock,fill=TINT);arrow(d,158,y-27,176,y-27,True)
  tile(d,181,y,151,54,question);arrow(d,337,y-27,355,y-27,True);tile(d,360,y,144,54,route)
 label(d,'Dashed arrows = editorial review cues. No defect rates or age/form cross-tabulation are inferred.',0,18,W,9)
 return publish_chart(d,'stock-to-review-routes')

def timeline_chart(id='local-adoption-timeline',height=220):
 from datetime import date
 d=Drawing(W,height);left=124;right=483;top=height-29;span=(date(2026,1,1)-date(2022,1,1)).days
 def xp(s):return left+(date.fromisoformat(s)-date(2022,1,1)).days/span*(right-left)
 for year in range(2022,2027):
  x=xp(str(year)+'-01-01');d.add(Line(x,28,x,top+5,strokeColor=GRAY,strokeWidth=.6));label(d,str(year),x-16,height-2,38,9,align='center')
 rows=[('Baltimore City','2024-05-22','2021'),('Anne Arundel','2024-06-23','2021'),('Baltimore County','2024-09-03','2021'),('Carroll','2024-01-01','2021'),('Harford','2024-05-29','2021*'),('Howard','2025-09-07','2024')]
 step=(top-42)/5
 for j,(name,date_,edition) in enumerate(rows):
  y=top-j*step;label(d,name,0,y+7,118,9.5,True);x=xp(date_)
  d.add(Circle(x,y,3.3,fillColor=N,strokeColor=N));label(d,edition,x+7,y+8,66,9.5,True)
  if name=='Howard':
   x0=xp('2022-01-03');d.add(Circle(x0,y,2.6,fillColor=WHITE,strokeColor=N));label(d,'2021',x0+6,y+8,48,9)
  if name=='Harford':
   d.add(Line(xp('2024-05-20'),y-6,x,y-6,strokeColor=R,strokeWidth=2))
 label(d,'Labels = I-code model year; position = local transition. *Harford dates conflict (May 20 / 29).',0,19,W,8.5)
 return publish_chart(d,id)

def appendix_map(aid):
 graphs={
 'APP-A':['Observation','Question','Tool','Limit'],
 'APP-B':['Question','Record','Match to item','Resolve / qualify'],
 'APP-C':['Observed','Meaning','Action','Location + limit'],
 'APP-D':['Similar label','Different function','Different inference'],
 'APP-E':['Claim','Source type','Exact locator','Qualification'],
 'APP-F':['Original year','Alterations','Installed systems','Selected kit'],
 'APP-G':['Recorded answer','Reviewed concept','Field conditions'],
 }
 if aid=='APP-H':return timeline_chart(height=200)
 return chain(graphs[aid],aid+'-reference-route',height=61)

def reference_cover(b):
 d=Drawing(W,296)
 lanes=[('WATER',['Roof / opening','Wall / cavity','Grade / foundation','Interior evidence']),('LOAD',['Member','Connection','Bearing','Ground']),('COMBUSTION',['Air + fuel','Burner','Heat exchanger','Vent / discharge'])]
 for j,(name,nodes) in enumerate(lanes):
  top=279-j*86;label(d,name,0,top,W,10,True);cw=112;gap=18
  for k,node in enumerate(nodes):
   x=k*(cw+gap);tile(d,x,top-22,cw,47,node,fill=TINT)
   if k<3:arrow(d,x+cw+2,top-46,x+cw+gap-3,top-46)
 label(d,'Conceptual routes for inquiry. Arrows do not establish a hidden defect or a diagnosis.',0,12,W,9)
 publish_chart(d,'three-system-paths')
 return [b.Spacer(1,8),b.para('HOME INSPECTION',ParagraphStyle('DesignCover',parent=b.H1,fontSize=28,leading=33)),b.para('SG-010-L1 / The long cut',b.H1),b.para('Three paths connect the component lessons',b.H2),d,b.Spacer(1,10),b.para('32 source recordings | 118 component topics | 8 long-cut appendices',b.BODY),b.para('COURSE = recorded lesson. EXAM = assessment concept. NOTE = reviewed interpretation. LOCAL = jurisdiction-specific qualification. Product and local conditions remain attached to their source.',b.SMALL),b.para('Compact comparisons: SG-010. Terms and numerical references: APP-D. Sources: APP-E. Seven-era packing: APP-F. Code dates: APP-H.',b.SMALL)]

def compact_pages(data,b):
 aid=data['id'];flow=[]
 body=ParagraphStyle('CompactChartBody',parent=b.BODY,fontSize=11.2,leading=14.6,spaceAfter=6)
 head=ParagraphStyle('CompactChartHead',parent=b.H2,fontSize=12,leading=15,spaceAfter=6)
 for n,p in enumerate(data['pages'],1):
  if n>1:flow.append(b.PageBreak())
  title=p['title'].replace('Era cards 7–7','Era card 7')
  flow +=[b.heading(title,aid+'-'+str(n)),b.para(data['title']+' | '+data['version']+' | experimental R1',b.SMALL)]
  if aid in ['APP-A','APP-B','APP-C','APP-E','APP-G'] and n==1:flow +=[appendix_map(aid),b.Spacer(1,12)]
  if aid=='APP-F':
   labels=['pre-1940','1940-59','1960-79','1980-99','2000-09','2010-19','2020+'];d=Drawing(W,40)
   for j,year in enumerate(labels):
    x=j*72;active=j//2==n-1;d.add(Rect(x,4,70,30,fillColor=N if active else TINT,strokeColor=None));label(d,year,x+1,26,68,9.3,True,color=WHITE if active else N,align='center')
   flow +=[publish_chart(d,'era-selector-'+str(n)),b.Spacer(1,11)]
  if aid=='APP-H' and n==1:flow +=[timeline_chart(height=191),b.Spacer(1,8)]
  if p['intro']:flow +=[b.para(p['intro'],b.SMALL)]
  items=p['items']
  if aid=='APP-D' and n<3:
   cells=[]
   for i in range(0,len(items),2):
    row=[]
    for h,t in items[i:i+2]:row.append([b.para(h,head),b.para(t,body)])
    if len(row)==1:row.append([])
    cells.append(row)
   table=Table(cells,colWidths=[252,252]);table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('BOX',(0,0),(-1,-1),.5,GRAY),('INNERGRID',(0,0),(-1,-1),.5,GRAY)]));flow.append(table)
  elif aid=='APP-G':
   rows=[[h,[b.para(t,body)]] for h,t in items]
   table=Table([[b.para(h,head),v] for h,v in rows],colWidths=[150,354]);table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(0,-1),TINT),('LINEBEFORE',(1,0),(1,-1),1,R),('LINEBELOW',(0,0),(-1,-1),.5,GRAY),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)]));flow.append(table)
  else:
   rows=[]
   for i,(h,t) in enumerate(items):
    # Different navigational shapes: selection squares, record numbers,
    # reporting steps, evidence letters, and era/timeline side labels.
    marker='[  ]' if aid=='APP-A' else str(i+1).zfill(2) if aid in ['APP-B','APP-C'] else chr(65+i) if aid=='APP-E' else ''
    rows.append([b.para(marker,head),[b.para(h,head),b.para(t,body)]])
   table=Table(rows,colWidths=[31,473]);style=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),.5,GRAY)]
   if aid in ['APP-B','APP-C','APP-E']:style.append(('LINEAFTER',(0,0),(0,-1),1,N))
   if aid in ['APP-F','APP-H']:style.append(('ROWBACKGROUNDS',(0,0),(-1,-1),[TINT,WHITE]))
   table.setStyle(TableStyle(style));flow.append(table)
  flow +=[b.Spacer(1,10),b.para(p['note'],b.SMALL)]
 return flow

def topic_html(p,b):
 chart='<img class="design-chart" src="DesignCharts/topic-'+p['id']+'.svg" alt="'+b.e(LINKS[p['id']][1])+'">' if p['id'] in LINKS else ''
 if p['id'] in {'movement','openings','devices','load_paths'}:return chart+b.html_table(dict(headers=['Distinction','What the evidence supports','What remains separate'],rows=p['rows']))
 role='route-steps' if p['id'] in {'method','service','oil_heat'} else 'topic-cards'
 return chart+'<div class="'+role+'">'+''.join('<article><h3>'+b.e(term)+'</h3><p>'+b.e(evidence)+'</p><p class="qualification"><strong>Limit / question:</strong> '+b.e(qualifier)+'</p></article>' for term,evidence,qualifier in p['rows'])+'</div>'

def compact_html(data,b):
 aid=data['id'];body='<p>Experimental R1 / compact appendix. <a href="'+data['long_cut']+'">Complete reference cut</a></p>'
 for n,p in enumerate(data['pages'],1):
  body+='<section id="'+aid+'-'+str(n)+'"><h2>'+b.e(p['title'])+'</h2>'
  id='era-selector-'+str(n) if aid=='APP-F' else 'local-adoption-timeline' if aid=='APP-H' and n==1 else aid+'-reference-route' if aid in ['APP-A','APP-B','APP-C','APP-E','APP-G'] and n==1 else None
  if id:body+='<img class="design-chart" src="../../DesignCharts/'+id+'.svg" alt="'+b.e(PROFILE[aid][1])+'">'
  body+='<p>'+b.e(p['intro'])+'</p><div class="'+('topic-cards' if aid=='APP-D' and n<3 else 'route-steps')+'">'
  body+=''.join('<article><h3>'+b.e(h)+'</h3><p>'+b.e(t)+'</p></article>' for h,t in p['items'])+'</div><p class="refs">'+b.e(p['note'])+'</p></section>'
 return body

def install(b):
 if getattr(b,'design_installed',False):return
 b.design_installed=True;b.design_context='L1'
 # Mutate existing styles too: default arguments elsewhere retain these objects.
 for style in [b.BODY,b.SMALL,b.H1,b.H2,b.HEAD,b.CELL]:
  style.fontName='Helvetica-Bold' if 'Bold' in style.fontName else 'Helvetica';style.textColor=N
 b.BODY.fontSize=10;b.BODY.leading=13
 b.SMALL.fontSize=8.5;b.SMALL.leading=10.6
 b.H1.fontSize=16;b.H1.leading=19;b.H1.spaceAfter=12
 b.CELL.fontSize=10;b.CELL.leading=12.4
 b.HEAD.fontSize=9;b.HEAD.leading=11;b.HEAD.textColor=WHITE
 old_para=b.para
 b.para=lambda s,style=b.BODY:old_para(clean(s),style)
 old_heading=b.heading
 def heading(title,id):
  if id.startswith('APP-'):b.design_context=id[:5]
  p=old_heading(clean(title),id);return p
 b.heading=heading
 def table(block):
  headers=block.get('headers',[]);rows=block.get('rows',[]);n=len(headers) or max(map(len,rows))
  widths=block.get('widths') or {2:[124,380],3:[105,125,274],4:[100,100,150,154],5:[75,90,75,100,164]}.get(n,[W/n]*n)
  widths=[w*W/sum(widths) for w in widths]
  data=[[b.para(v,b.HEAD) for v in headers]] if headers else []
  for row in rows:data.append([b.para(v,b.CELL) for v in row])
  t=Table(data,colWidths=widths,repeatRows=1 if headers else 0,hAlign='LEFT')
  styles=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,0),(-1,-1),.4,GRAY)]
  if headers:styles +=[('BACKGROUND',(0,0),(-1,0),N),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,TINT])]
  if b.design_context in ['APP-A','APP-D','APP-F']:styles.append(('LINEAFTER',(0,1),(0,-1),1,N))
  if b.design_context=='APP-C':styles.append(('LINEBEFORE',(-1,1),(-1,-1),.6,R))
  t.setStyle(TableStyle(styles));return t
 b.table=table
 OldDoc=b.Doc
 class DesignDoc(OldDoc):
  def __init__(self,path,title):
   super().__init__(path,title);self.design_id=next((k for k in PROFILE if k in title),'W1' if 'SG-010-W1' in title else 'L1' if 'SG-010-L1' in title else 'SG-010');self.current_topic=''
   self.compact='compact' in title.lower() or self.design_id in ['SG-010','W1']
   self.leftMargin=54;self.rightMargin=54;self.width=W
   self.pageTemplates=[];self.addPageTemplates(PageTemplate(id='main',frames=[Frame(54,43,W,704,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.header))
  def afterFlowable(self,f):
   super().afterFlowable(f)
   if isinstance(f,Paragraph) and hasattr(f,'topic_id'):self.current_topic=f.getPlainText()
  def header(self,c,doc):
   c.saveState();c.setFillColor(N);c.setFont('Helvetica-Bold',8.5)
   c.drawString(54,772,'BEN BALL / HOME INSPECTION')
   from reportlab.graphics import renderPDF
   import card_brand
   mark=Drawing(12,28);card_brand.mark(mark,0,0,12);renderPDF.draw(mark,c,575,759)
   label_=PROFILE.get(self.design_id,('WALKING CUT' if self.design_id=='W1' else 'FIELD GUIDE' if self.design_id=='SG-010' else 'REFERENCE VOLUME',''))[0]
   c.setFont('Helvetica-Bold',9);c.drawRightString(558,772,label_)
   c.setStrokeColor(R);c.setLineWidth(1.5);c.line(54,761,558,761)
   if self.design_id in PROFILE:
    # Appendix letters occupy different positions on the edge for retrieval.
    j=ord(self.design_id[-1])-65;y=705-j*37
    c.setFillColor(N);c.rect(572,y,22,27,fill=1,stroke=0);c.setFillColor(WHITE);c.setFont('Helvetica-Bold',14);c.drawCentredString(583,y+8,self.design_id[-1])
   if self.compact:
    c.setStrokeColor(N);c.setLineWidth(.7);c.line(54,32,558,32);c.setFillColor(N)
   else:c.setStrokeColor(N);c.setLineWidth(.7);c.line(54,32,558,32);c.setFillColor(N)
   c.setFont('Helvetica',8);c.drawString(54,17,self.design_id+' | '+('COMPACT' if self.compact else 'LONG CUT')+' | SG-010 / 21 SEP 2026')
   c.drawRightString(558,17,str(doc.page));c.restoreState()
 b.Doc=DesignDoc
 b.CSS=b.CSS.replace('#193b42',BRAND.hex('navy.primary')).replace('#213337',BRAND.hex('navy.primary')).replace('#14716e',BRAND.hex('navy.primary')).replace('#e8efec',BRAND.hex('structural.alt-row')).replace('#89a36a',BRAND.hex('crimson.accent'))
 b.CSS+='\nheader{background:white;color:'+BRAND.hex('navy.primary')+';border-bottom:3px solid '+BRAND.hex('crimson.accent')+'}header a{color:inherit}.design-chart{width:100%;height:auto}th{background:'+BRAND.hex('navy.primary')+';color:white}section{border-left:0;border-right:0}body{background:white}@media print{section{break-before:auto}}'
 b.CSS+='\n.topic-cards{display:grid;grid-template-columns:1fr 1fr;gap:0}.topic-cards article{margin:0;border:1px solid '+BRAND.hex('structural.rule')+';padding:18px}.route-steps article{margin:0;border:0;border-bottom:1px solid '+BRAND.hex('structural.rule')+';border-left:3px solid '+BRAND.hex('navy.primary')+';padding:14px 20px}.qualification{border-top:1px solid '+BRAND.hex('structural.rule')+';padding-top:8px}.qualification strong{color:'+BRAND.hex('crimson.accent')+'}@media(max-width:650px){.topic-cards{grid-template-columns:1fr}}'
 old_html=b.doc_html
 def doc_html(title,body):
  aid=next((a for a in PROFILE if title.startswith(a)),None)
  if aid and 'compact' not in title.lower():
   chart='local-adoption-timeline' if aid=='APP-H' else aid+'-reference-route'
   body='<img class="design-chart" src="../DesignCharts/'+chart+'.svg" alt="'+PROFILE[aid][1]+'">'+body
  return old_html(title,body)
 b.doc_html=doc_html
 save(OUT/'design-provenance.json',dict(revision='experimental-R1',basis='Current BBDF Design System, checked locally; print palette, typography, canonical logo and live tokens.',tokens_dir=str(BRAND.tokens_dir),token_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BRAND.tokens_dir.glob('*.json') if p.name in ['palette.json','typography.json','spacing.json']},profiles=PROFILE,first_pass='Preserved in Presentation History/First Pass',chart_policy='Show process and comparison using chart geometry. Dashed connections mean editorial review cues, not measured defect rates. Source figures and technical qualifications retained.',scope='Internal experimental study-guide presentation; no external distribution.'))
