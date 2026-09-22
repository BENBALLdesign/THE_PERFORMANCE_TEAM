from pathlib import Path
import json,copy,html,hashlib,datetime,re
import sys
from PIL import Image as PILImage
from prepare import OLD,OUT,HERE,BASE,WORK,read,save
from supplements import augment,REFERENCES,REFMAP,TOOLS_A,TOOLS_B,MENTIONS,NUMBERS
from glossary import TERMS
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether,CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents,SimpleIndex
from edition import reorganize,extra_appendices,DOMAINS,ERA_REFS
from timeline import REFS as TIMELINE_REFS
from additional_topics import insert as insert_screen_topics
import housing
from pypdf import PdfReader
DATE='2026-09-21'
def ts(t):
 t=int(t);return f'{t//3600:02}:{t//60%60:02}:{t%60:02}'
def e(x):return html.escape(str(x))

# Coordinates refer to the full, unchanged recorded screen. Rejected images stay
# in staging until final packaging selects only retained evidence.
CROPS={
 'garage_separation':((.17,.09,.82,.64),'Pet-door alteration in the garage passage door; assess the complete separation assembly.'),
 'garage_appliances':((.285,.14,.71,.69),'Course garage water-heater diagram: ignition, impact, restraint and relief details have distinct purposes and conditions.'),
 'garage_doors':((.165,.09,.83,.66),'Visible gap in a torsion spring. Stop operation and refer to a trained door technician.'),
 'roof_forms':((.16,.24,.84,.71),'Course butterfly-roof example; follow drainage toward the internal low point.'),
 'roof_cover_condition':((.17,.23,.84,.72),'Roof-covering damage beside accumulated debris. Describe the visible opening without promising remaining life.'),
 'roof_flashing':((.27,.165,.74,.54),'Chimney and roof intersection. Follow the flashing overlap and upslope water route.'),
 'roof_penetrations':((.16,.12,.84,.60),'Flexible boot at a plumbing penetration; inspect the collar and surrounding water-shedding detail.'),
 'water_supply':((.22,.115,.73,.64),'Well pressure tank, controls and filter. Visible equipment does not establish water quality or well yield.'),
 'plumbing_materials':((.16,.115,.83,.62),'Water-heater pipe connections: distinguish connection materials, leakage and corrosion.'),
 'backflow_dwv':((.16,.115,.83,.62),'Frost-resistant hose-bibb example. Drainability and backflow protection are separate considerations.'),
 'water_heater_identity':((.18,.34,.83,.83),'Equipment label: retain model, serial, capacity, fuel and installation conditions.'),
 'water_heater_relief':((.285,.17,.72,.65),'Watts 210 temperature-actuated gas shutoff. This does not replace required pressure protection.'),
 'water_heater_installation':((.17,.28,.85,.77),'Corroded water-heater top and draft-hood connection: describe the condition and recommend qualified correction.'),
 'water_heater_variants':((.195,.18,.795,.66),'Heat-pump water heater. Check the actual model’s air, filter and condensate provisions.'),
 'gas_piping':((.23,.46,.75,.87),'Course CSST manifold example; distinguish distribution tubing from appliance connectors.'),
 'electric_multiwire':((.27,.315,.73,.70),'Shared-neutral circuit diagram. Opposite legs and the appropriate disconnect arrangement matter.'),
 'electric_wiring_methods':((.24,.47,.87,.65),'EMT fittings shown for different exposures. Verify the fitting’s listing rather than shape alone.'),
 'electric_legacy':((.19,.35,.79,.66),'Older conductor connections shown in the course; identify material and obtain qualified evaluation.'),
 'heating_controls':((.155,.41,.875,.79),'Normal thermostat controls; record and restore the original settings.'),
 'combustion_air':((.29,.525,.74,.85),'Indoor combustion-air diagram: opening location and net free area belong to a specific method.'),
 'furnace_types':((.255,.30,.775,.765),'Primary and secondary heat exchangers, inducer and circulating blower have different functions.'),
 'oil_storage':((.17,.25,.84,.695),'Corroded outdoor oil tank on improvised supports. Do not disturb suspect tank surfaces.'),
 'oil_burners':((.16,.335,.84,.79),'Oil-burner components: nozzle, ignition assembly, pump, motor and fan.'),
 'gravity_furnaces':((.16,.27,.84,.70),'Older gravity furnace. Record condition and limitations; do not infer hidden integrity from age.'),
 'exam_sg008_concepts':((.04,.085,.96,.70),'Recorded correction: rake means the overhang at the gable end, not the board at the eaves.')}

CSS='''body{font:16px/1.55 Arial,sans-serif;color:#213337;background:#edf1ef;margin:0}header{padding:34px max(24px,calc((100vw - 1060px)/2));background:#193b42;color:white}main{max-width:1060px;margin:auto;padding:24px}section,article{background:white;padding:28px;margin:20px 0;border:1px solid #d6dedb}h1{line-height:1.12}h2{color:#193b42}a{color:#14716e}header a{color:#d5eee5}table{border-collapse:collapse;width:100%;font-size:14px}td,th{vertical-align:top;text-align:left;border-bottom:1px solid #d7e0dd;padding:10px}th{background:#e8efec}.figures{display:flex;gap:18px;align-items:flex-start}figure{margin:12px 0;flex:1;min-width:0}figure img{display:block;max-width:100%;max-height:360px;object-fit:contain;margin:auto}figcaption,.refs{font-size:12px;color:#4b5d60}.note{padding:12px;background:#f1f5ec;border-left:3px solid #89a36a}input{padding:12px;width:calc(100% - 28px);font:inherit}nav a{display:inline-block;margin:4px 10px 4px 0}@media print{body{background:white}header{background:white;color:black}input,nav{display:none}section{break-before:page;border:0;padding:0}tr,figure{break-inside:avoid}}'''
def doc_html(title,body):return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{e(title)}</title><style>{CSS}</style><header><h1>{e(title)}</h1><p>BEN BALL · Home Inspection Training · SG-010 · {DATE}</p></header><main>{body}</main></html>'

pdfmetrics.registerFont(TTFont('Arial',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold',r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic',r'C:\Windows\Fonts\ariali.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
BODY=ParagraphStyle('Body',fontName='Arial',fontSize=9.4,leading=12.3,spaceAfter=7,textColor=colors.HexColor('#24373b'))
SMALL=ParagraphStyle('Small',parent=BODY,fontSize=7.3,leading=9.4,spaceAfter=5)
H1=ParagraphStyle('Heading1',parent=BODY,fontName='Arial-Bold',fontSize=16,leading=19,spaceAfter=10,keepWithNext=True)
H2=ParagraphStyle('Heading2',parent=BODY,fontName='Arial-Bold',fontSize=11,leading=14,spaceAfter=8,keepWithNext=True)
HEAD=ParagraphStyle('TH',parent=SMALL,fontName='Arial-Bold',fontSize=8.5,leading=11)
CELL=ParagraphStyle('Cell',parent=BODY,fontSize=9.4,leading=11.8,spaceAfter=0)
def para(s,style=BODY):return Paragraph(e(s).replace('\n','<br/>'),style)
class Doc(BaseDocTemplate):
 def __init__(self,path,title):
  self.edition_label='SG-010-L1' if 'SG-010-L1' in title else 'SG-010 / L1'
  super().__init__(str(path),pagesize=(612,792),leftMargin=44,rightMargin=44,topMargin=45,bottomMargin=43,title=title,author='BEN BALL | Home Inspection Training')
  self.addPageTemplates(PageTemplate(id='main',frames=[Frame(44,43,524,704,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.header))
  self.positions={}
 def header(self,c,d):
  c.saveState();c.setStrokeColor(colors.HexColor('#b4c9c5'));c.line(44,758,568,758);c.setFont('Arial',7.4);c.setFillColor(colors.HexColor('#456065'));c.drawString(44,768,'BEN BALL  /  HOME INSPECTION TRAINING');c.drawRightString(568,768,self.edition_label+'  •  '+DATE);c.line(44,33,568,33);c.drawString(44,22,'Study guide • Course / Exam / Note / Local');c.drawRightString(568,22,str(d.page));c.restoreState()
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and hasattr(f,'topic_id'):
   key=f.topic_id;level=getattr(f,'toc_level',0);self.canv.bookmarkPage(key);self.canv.addOutlineEntry(f.getPlainText(),key,level,False);self.notify('TOCEntry',(level,f.getPlainText(),self.page,key));self.positions[key]=self.page
def heading(title,id):
 p=para(title,H1);p.topic_id=id;return p
def table(block):
 headers=block.get('headers',[]);rows=block.get('rows',[]);n=len(headers) or max(map(len,rows));widths=block.get('widths') or {2:[124,400],3:[105,125,294],4:[100,100,160,164],5:[80,100,80,100,164]}.get(n,[524/n]*n)
 data=[[para(v,HEAD) for v in headers]] if headers else []
 for row in rows:data.append([para(v,CELL) for v in row])
 t=Table(data,colWidths=widths,repeatRows=1 if headers else 0,hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eeea')),('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#cfdbd6'))]));return t
def reference_text(r):
 return f"{r.get('source','')} {ts(r['seconds']) if 'seconds' in r else 'frame '+str(r['frame']) if 'frame' in r else ''} · {r.get('label','')}".strip()
def figure_flow(ids,figures,height):
 out=[];w=(504-12*(len(ids)-1))/len(ids)
 for id in ids:
  f=figures[id];im=PILImage.open(OUT/f['asset']);iw,ih=im.size;scale=min(w/iw,min(height,210)/ih);out.append([Image(str(OUT/f['asset']),iw*scale,ih*scale),para(f.get('caption',''),SMALL),para(f"{f.get('source','')} · {f.get('timestamp','')}",SMALL)])
 t=Table([out],colWidths=[w+12]*(len(ids)-1)+[w],hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(-1,0),(-1,-1),0)]));return t
def render_guide(data):
 flow=[Spacer(1,60),para('HOME INSPECTION',ParagraphStyle('Cover',parent=H1,fontSize=32,leading=37)),para('Study guide · SG-010',H1),para('Structure, exterior, garages, roofing, plumbing, electrical systems and heating',H2),Spacer(1,20),para('A cumulative topic guide built from 29 unique recorded sessions. This edition adds S15-S29, including the September 19 oil-heating recording.'),para('Read COURSE as the training source, EXAM as a recorded exam concept, NOTE as reviewed interpretation, and LOCAL as a jurisdiction-specific qualification. Numerical examples retain their conditions. The guide does not turn the course into a current code-compliance checklist.'),para('Eight separately versioned appendices support the component guide. Earlier editions and original recordings remain preserved.'),para('Sources and selected images are linked in the searchable HTML and evidence index. Definitions point back to their supporting topics. Similar terms retain their distinct functions. Unclear or conflicting source statements are qualified instead of silently guessed.'),PageBreak(),para('Contents',H1)]
 flow[6:6]=[para('Quick routes: APP-A/B = tools and records; APP-C = report mentions; APP-D = terms, notes and numerical/local references; APP-E = sources; APP-F = seven construction-era packing lists; APP-G = detailed exam review; APP-H = Codes, Standards, and General Practice Timeline for Baltimore City and the five surrounding counties.',SMALL)]
 if globals().get('design_installed'):
  from design_language import reference_cover
  flow=reference_cover(sys.modules[__name__])+[PageBreak(),para('Contents',H1)]
 toc=TableOfContents();toc.levelStyles=[ParagraphStyle('TOC',fontName='Arial-Bold',fontSize=9.4,leading=12.2,spaceBefore=6,leftIndent=0,rightIndent=28),ParagraphStyle('TOC-sub',fontName='Arial',fontSize=8.6,leading=11,spaceBefore=2,leftIndent=12,rightIndent=28)];flow +=[toc]
 flow +=[PageBreak()]+housing.frontmatter(sys.modules[__name__])
 index=SimpleIndex(style=ParagraphStyle('Index',fontName='Arial',fontSize=9,leading=12),headers=True,dot=' . ')
 section_starts=dict(DOMAINS)
 for p in data['pages']:
  if p['id'] in section_starts:flow +=[PageBreak(),heading(section_starts[p['id']],'section_'+p['id'])]
  else:flow +=[CondPageBreak(150),Spacer(1,12)]
  terms=[p['id'].replace('_',' ').capitalize()]+[alias.strip() for t in TERMS if t[3]==p['id'] for alias in t[0].split(' / ')]
  tags=''.join('<index item="'+e(term)+'"/>' for term in terms)
  h=Paragraph(tags+e(p['title']),H2);h.topic_id=p['id'];h.toc_level=1;flow.append(h)
  for b in p['blocks']:
   if b['kind']=='text':flow.append(para(b['text']))
   elif b['kind']=='table':
    if b.get('title'):flow.append(para(b['title'],H2))
    flow.append(table(b));flow.append(Spacer(1,8))
   elif b['kind']=='figures':flow.append(figure_flow(b['ids'],data['figures'],b.get('height',200)));flow.append(Spacer(1,8))
  if p.get('refs'):
   ref=para('Source notes [N01-N04]: '+' | '.join(reference_text(r) for r in p['refs']),SMALL)
   i=len(flow)-1
   while i>0 and isinstance(flow[i],Spacer):i-=1
   while i>0 and getattr(flow[i-1],'getKeepWithNext',lambda:False)():i-=1
   flow[i:]=[KeepTogether(flow[i:]+[ref])]
 flow +=[PageBreak(),heading('Subject index','subject_index'),para('L1 = page in this volume. D = page in the APP-D long glossary: 81 / D4 means topic p.81, definition p.4. Switching illustration: Source Diagrams, sheet 1. Sources: APP-E; packing: APP-F; corrections: APP-G; local history: APP-H.',SMALL),index]
 flow[2]=para('SG-010-L1 · The long cut',H1)
 second_flow=copy.deepcopy(flow)
 d=Doc(OUT/'STUDY GUIDE - SG-010-L1.pdf','Home Inspection Study Guide - SG-010-L1');d.multiBuild(flow,maxPasses=8,canvasmaker=index.getCanvasMaker())
 # A two-column alphabetical finder uses the actual topic page positions and
 # avoids six largely empty index pages or orphaned alphabet headings.
 subjects={}
 for p in data['pages']:
  names=[p['id'].replace('_',' ').capitalize()]+[alias.strip() for term in TERMS if term[3]==p['id'] for alias in term[0].split(' / ')]
  for name in names:subjects.setdefault(name,set()).add(d.positions[p['id']])
 from navigation import ALIASES
 for label,tid in ALIASES.items():subjects.setdefault(label,set()).add(d.positions[tid])
 merged={}
 for label,pages in subjects.items():
  key=label.casefold()
  if key not in merged:merged[key]=[label,set()]
  merged[key][1].update(pages)
 subjects={v[0]:v[1] for v in merged.values()}
 nav=read(HERE/'navigation.json');definitions={part.casefold():pn for label,pn in nav['glossary_pages'].items() for part in label.split(' / ')}
 def locator(name):
  value=', '.join(map(str,sorted(subjects[name])));pn=definitions.get(name.casefold())
  return value+(' / D'+str(pn) if pn else '')
 terms=sorted(subjects,key=str.casefold)
 style=ParagraphStyle('IndexCell',parent=SMALL,fontSize=8.7,leading=10.8,spaceAfter=0)
 index_flow=[]
 for start in range(0,len(terms),68):
  subset=terms[start:start+68];half=(len(subset)+1)//2;rows=[]
  for j in range(half):
   row=[]
   for k in [j,j+half]:row.extend([subset[k],locator(subset[k])]) if k<len(subset) else row.extend(['',''])
   rows.append(row)
  entries=[[para(x,HEAD) for x in ['Subject','L1 / D','Subject','L1 / D']]]+[[para(x,style) for x in row] for row in rows]
  compact_index=Table(entries,colWidths=[196,56,196,56],repeatRows=1,hAlign='LEFT');compact_index.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('BACKGROUND',(0,0),(-1,0),H1.textColor),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#DDDDDD'))]))
  if start:index_flow +=[PageBreak(),para('Subject index (continued)',H1)]
  index_flow.append(compact_index)
 flow=second_flow;flow[-1:]=index_flow
 d=Doc(OUT/'STUDY GUIDE - SG-010-L1.pdf','Home Inspection Study Guide - SG-010-L1');d.multiBuild(flow,maxPasses=8,canvasmaker=index.getCanvasMaker());save(OUT/'page-index-L1.json',d.positions)
 h='<nav><a href="STUDY GUIDE - SG-010.pdf">Download PDF</a><a href="evidence.html">Evidence index</a><a href="intake-review.html">New session review</a><a href="numbers-S15-S29.html">Numerical references</a><a href="reviewed-exams-S15-S29.html">Exam review</a></nav><p>37 source recordings through S37; source roles and assessment results are distinguished in APP-E/G. COURSE / EXAM / NOTE / LOCAL distinguish the basis and limits of a statement. Appendix versions are pinned below.</p>'
 h+='<nav>'+''.join(f'<a href="Appendices/{a["id"]}-v{a["version"]}.html">{a["id"]} v{a["version"]}</a>' for a in data['appendices'])+'</nav><input id="search" placeholder="Find a topic, component or term"><details><summary>Contents</summary><ol>'+''.join(f'<li><a href="#{e(p["id"])}">{e(p["title"])}</a></li>' for p in data['pages'])+'</ol></details>'
 for p in data['pages']:
  h+=f'<section class="topic" id="{e(p["id"])}"><h2>{e(p["title"])}</h2>'
  for b in p['blocks']:
   if b['kind']=='text':h+='<p class="note">'+e(b['text'])+'</p>'
   elif b['kind']=='table':h+=html_table(b)
   elif b['kind']=='figures':
    h+='<div class="figures">'
    for fid in b['ids']:
     f=data['figures'][fid];h+=f'<figure><a href="{e(f["asset"])}"><img loading="lazy" src="{e(f["asset"])}" alt="{e(f["caption"])}"></a><figcaption>{e(f["caption"])}<br>{e(f.get("source",""))} · {e(f.get("timestamp",""))}</figcaption></figure>'
    h+='</div>'
  h+='<p class="refs">Evidence: '+' | '.join(f'<a href="{e(r.get("url") or "evidence.html#"+r.get("source","")+ ("-F"+str(r["frame"]) if "frame" in r else ""))}">{e(reference_text(r))}</a>' for r in p.get('refs',[]))+'</p></section>'
 h+='<section><h2>Reference and exam topics</h2><ul>'+''.join(f'<li id="{e(p["id"])}"><a href="Appendices/APP-{letter}-v1.3.html#{e(p["id"])}">{e(p["title"])}</a></li>' for letter,pages in [('D',data['reference_pages']),('G',data['exam_pages'])] for p in pages)+'</ul></section>'
 h+='''<script>document.getElementById('search').addEventListener('input',function(){let q=this.value.toLowerCase();document.querySelectorAll('.topic').forEach(s=>s.hidden=!s.textContent.toLowerCase().includes(q));});</script>'''
 h='<p><a href="regional-field-focus.html">Regional housing chart and discussion routes</a></p>'+h
 h=h.replace('STUDY GUIDE - SG-010.pdf','STUDY GUIDE - SG-010-L1.pdf')
 h='<p><a href="STUDY GUIDE.html">SG-010: concise field and discussion guide</a></p>'+h
 (OUT/'STUDY GUIDE - SG-010-L1.html').write_text(doc_html('SG-010-L1 · The long cut',h),encoding='utf-8')
def html_table(b):return ('<h3>'+e(b.get('title',''))+'</h3>' if b.get('title') else '')+'<table><thead><tr>'+''.join('<th>'+e(v)+'</th>' for v in b.get('headers',[]))+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(v)+'</td>' for v in row)+'</tr>' for row in b.get('rows',[]))+'</tbody></table>'
def appendices():
 result=[]
 for id,oldv,newv,added in [('APP-A','1.5','1.6',TOOLS_A),('APP-B','1.4','1.5',TOOLS_B),('APP-C','1.6','1.7',MENTIONS)]:
  d=read(OLD/f'Appendices/{id}-v{oldv}.json');d.update(version=newv,date=DATE,edition='SG-010')
  for j,vals in enumerate(added,len(d['items'])+1):
   if id=='APP-C':
    name,note,source=vals;item=dict(id=f'M{j:04}',added=DATE,mention=name,note=note,source=source,links=[dict(label='SG-010 topic guide',url='../STUDY GUIDE.html')],status='Report-entry mention; review for the actual inspection and scope',checklist_status='Not organized into a checklist')
   else:
    name,purpose,limit,basis=vals;item=dict(id=('T' if id=='APP-A' else 'R')+f'{j:03}',added=DATE,level='Scope-dependent',name=name,purpose=purpose,limit=limit,basis=basis,sources=['SG-010'],pre_use_check='Check instructions, condition and suitability; verify required competence and calibration where applicable.',availability='Not recorded',training='Not recorded',last_revision=newv)
   d['items'].append(item)
  save(OUT/f'Appendices/{id}-v{newv}.json',d)
  flow=[heading(f'{id} v{newv} · {d["title"]}',id),para('Pinned to SG-010. Entry identifiers and prior history are retained. Availability and training have not been inferred.' if id!='APP-C' else 'A running list of report-entry mentions, retained in append order. This is not a checklist and does not imply any finding at an actual property.')]
  if globals().get('design_installed'):
   from design_language import appendix_map
   flow[1:1]=[appendix_map(id),Spacer(1,12)]
  body='<p>Pinned to SG-010. '+('Running report-mentions list; not a checklist.' if id=='APP-C' else 'Tools remain scope-dependent; availability and training are not inferred.')+'</p>'
  rows=[]
  if id!='APP-C':
   shared=para('Availability and training are not recorded unless an entry states otherwise. Limits and pre-use checks apply to each item. Stable entry IDs support references from the guide.',SMALL);flow.append(shared)
  for item in d['items']:
   title=item['id']+' · '+item.get('name',item.get('mention',''))
   if id=='APP-C':
    row=[title,item['note'],item.get('source','')]
   else:
    use=item.get('purpose','')+'\nLimit: '+item.get('limit','')+'\nCheck: '+item.get('pre_use_check','')
    for field in ['availability','training']:
     if item.get(field) and item[field]!='Not recorded':use+='\n'+field.capitalize()+': '+item[field]
    row=[title+'\n'+item.get('level',''),use,item.get('basis','')]
   rows.append(row)
  block=dict(headers=['ID / mention','Record / qualification','Source'] if id=='APP-C' else ['ID / tool','Purpose / limits / pre-use','Basis'],rows=rows,widths=[115,275,134])
  flow.append(table(block));body+=html_table(block)
  Doc(OUT/f'Appendices/{id}-v{newv}.pdf',f'{id} v{newv} · {d["title"]}').build(flow)
  (OUT/f'Appendices/{id}-v{newv}.html').write_text(doc_html(f'{id} v{newv} · {d["title"]}',body),encoding='utf-8')
  result.append(dict(id=id,version=newv,entries=len(d['items'])))
 return result
def main():
 data=read(OLD/'study-guide.json');new=copy.deepcopy(augment());candidates=read(HERE/'figure-candidates.json')
 for p in new:
  if p['id'] not in CROPS:continue
  f=next(f for f in candidates if f['id']==p['id']);box,caption=CROPS[p['id']];im=PILImage.open(OUT/f['asset']);w,h=im.size;px=tuple(round(x*(w if j%2==0 else h)) for j,x in enumerate(box));crop=im.crop(px);fid='sg008_'+p['id'];path=OUT/f'figures/{fid}.jpg';crop.save(path,quality=93)
  data['figures'][fid]=dict(source=f['source'],seconds=f['seconds'],timestamp=ts(f['seconds']),asset=str(path.relative_to(OUT)).replace('\\','/'),caption=caption,box=box,crop_pixels=px,source_sha256=f['source_sha256'],full_frame=f['asset'],full_frame_sha256=f['sha256'],sha256=hashlib.sha256(path.read_bytes()).hexdigest())
  if p['id'] in {'garage_doors','roof_flashing','water_heater_relief','electric_multiwire','combustion_air','furnace_types','oil_burners','gravity_furnaces'}:
   p['blocks'].insert(0,dict(kind='figures',ids=[fid],height=140))
 # Topic additions precede reporting, exam and numerical reference material.
 pos=next(i for i,p in enumerate(data['pages']) if p['id']=='reporting')
 newtopics=[p for p in new if not p['id'].startswith('exam_')];newexams=[p for p in new if p['id'].startswith('exam_')]
 data['pages'][pos:pos]=newtopics
 pos=next(i for i,p in enumerate(data['pages']) if p['id']=='local_amendments');data['pages'][pos:pos]=newexams
 extras=HERE/'screen-additions.json'
 if extras.exists():data['pages'].extend(read(extras))
 data.update(edition='SG-010',date=DATE,title='Home Inspection Study Guide',appendices=appendices(),coverage='29 unique sessions; S01–S14 retained from SG-007; S15–S29 added by topic.',new_session_review='intake-review.json')
 for s in read(WORK/'sources.json'):
  probe=read(Path(s['audio'])/'probe.json');dur=probe.get('format',{}).get('duration',0)
  data['sources'].append(dict(id=s['session'],name=Path(s['source']).name,source_path=s['source'],source_sha256=s['sha256'],duration_seconds=float(dur),kind='video',date=Path(s['source']).name[10:20],audio_evidence=s['audio'],machine_evidence_cache=str(WORK/('Visual-'+s['session']))))
 for s in data['sources'][:14]:
  session_file=OLD/('Session '+s['id']+'.json')
  if session_file.exists():
   older=read(session_file).get('source',{})
   original=older.get('manifest',{}).get('source',{})
   if original.get('sha256'):s['source_sha256']=original['sha256']
   if original.get('duration_seconds'):s['duration_seconds']=original['duration_seconds']
   for field in ['source_sha256','duration_seconds','source_path']:
    if older.get(field):s[field]=older[field]
  prior=s.get('source_path','');candidate=BASE/'Sound Recordings'/s['name']
  if candidate.is_file() and str(candidate)!=prior:s['prior_source_path']=prior;s['source_path']=str(candidate)
 data=insert_screen_topics(data)
 retain={'schema','edition','date','title','appendices','purpose','coverage','figures','pages','sources','process','growth','authorities','new_session_review'}
 data['prior_edition_metadata']={k:data.pop(k) for k in list(data) if k not in retain}
 data.update(edition_date=DATE,edition_change='Adds S15-S29, reviews vocabulary and retrieval structure, and issues eight pinned appendices including seven construction-era packing groups and a six-jurisdiction timeline.')
 data=reorganize(data);data['appendices']+=extra_appendices(data,sys.modules[__name__])
 housing.publish_data(sys.modules[__name__])
 data['edition']='SG-010-L1';data['edition_family']='SG-010';data['companion']='SG-010: concise field and discussion guide'
 save(OUT/'study-guide-L1.json',data);save(OUT/'external-references.json',[dict(id=x[0],title=x[1],url=x[2],note=x[3],reviewed_on=DATE) for x in list(REFERENCES)+ERA_REFS+TIMELINE_REFS])
 save(OUT/'numbers-S15-S29.json',[dict(value=a,topic=b,basis=c,source=d,qualification=f) for a,b,c,d,f in NUMBERS])
 (OUT/'numbers-S15-S29.html').write_text(doc_html('SG-010 · numerical references',html_table(dict(headers=['Value','Topic','Basis/source','Qualification'],rows=[[a,b,c+' / '+d,f] for a,b,c,d,f in NUMBERS]))),encoding='utf-8')
 render_guide(data)
 print(json.dumps(dict(topics=len(data['pages']),figures=len(data['figures']),pages=len(PdfReader(OUT/'STUDY GUIDE - SG-010-L1.pdf').pages),appendices=data['appendices'])))
if __name__=='__main__':main()
