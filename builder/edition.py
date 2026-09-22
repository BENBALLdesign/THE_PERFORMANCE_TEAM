"""SG-010 retrieval structure; the guide retains the established content template."""
from prepare import read,save,OUT,HERE,WORK
from glossary import TERMS
from supplements import REFERENCES,NUMBERS
from timeline import REFS as TIMELINE_REFS, SECTIONS as TIMELINE_SECTIONS
from verified_scores import records as score_records
from pathlib import Path
import copy,html,json

DOMAINS=[('inspection_method','Method, structure and moisture'),('exterior_scope','Exterior, openings and grounds'),('garage_separation','Garages'),('roof_forms','Roof coverings and drainage'),('water_supply','Plumbing and water heating'),('electric_service','Electrical systems'),('heating_controls','Heating systems'),('reporting','Reporting')]
NOTES=[
 ('N01','Basis flags','COURSE = training statement; EXAM = recorded assessment; NOTE = reviewed explanation/correction; LOCAL = jurisdiction-specific qualification. Flags describe the basis, not certainty or severity.'),
 ('N02','Numbers and units','Read value, units, application and exception together. A recorded course value is not a universal installation rule; retain the adjacent qualifier and applicable product/local reference.'),
 ('N03','Scope and access','A tool or lesson does not expand the agreed inspection service. Record the method and areas not seen; concealed construction remains unresolved.'),
 ('N04','Source time','S01–S30 identify unique recordings. Times refer to the unchanged original recording. A screenshot supports only what is visible; a transcript may contain recognition errors.'),
 ('N05','Age versus condition','Original construction year selects a packing card; later additions and replaced systems may belong to other eras. Age is not proof of material, defect, remaining life or code compliance.'),
 ('N06','Instrument limits','Check the device, instructions and suitability for the actual task. A screening result is not a complete diagnosis. APP-A records item-specific limits and pre-use checks.'),
 ('N07','Availability and competence','Packing recommendations do not imply ownership, calibration, training or permission to perform a specialist test. Unrecorded inventory/training stays unrecorded.'),
 ('N08','Exam evidence','A score is tied to its recorded attempt. Shuffled question numbers must be matched by wording. A course answer and a current field requirement can differ.'),
 ('N09','Report mentions','APP-C preserves an append-order log, not a property checklist. Select only statements supported by the actual inspection evidence.')]

ERA_REFS=[
 ('HALO-IC','Cooper Lighting: recessed-light product rating example','https://www.cooperlighting.com/global/brands/halo/11621162/lt-recessed-canless-led-downlights/ltc406fs5b-c','The manufacturer identifies this matte-white product as IC-rated. Verify the actual housing/luminaire instructions; color is not a universal rating rule.'),
 ('EPA-LEAD','EPA: identifying lead-based paint','https://www.epa.gov/lead/how-can-i-tell-if-my-home-contains-lead-based-paint','Pre-1978 construction is a screening clue; material determination is a separate service.'),
 ('EPA-VERMICULITE','EPA: vermiculite attic insulation','https://www.epa.gov/asbestos/my-attic-has-vermiculite-insulation-it-am-i-risk-should-i-take-it-out','Leave suspect vermiculite undisturbed; a year or photograph cannot establish absence of asbestos.'),
 ('CPSC-ERA','CPSC Publication 516: repairing aluminum wiring','https://www.cpsc.gov/s3fs-public/516.pdf','1965 to the mid-1970s includes original work, additions and rewiring; conductor evidence and qualified assessment control.')]

# Practical editorial planning groups, not code eras or material-presence claims.
ERAS=[
 ('E1','Before 1940','Layered alterations; older structural and masonry assemblies; retained legacy systems.',
  ['T007','T008','T009','T011','T017'],['R008','R009','R011','R013'],
  'Compare adjoining construction and repairs. Photograph accessible older wiring, pipe materials, heating equipment and wall/floor movement. Lead/asbestos identification is not inferred from age; avoid disturbing suspect material.'),
 ('E2','1940–1959','Original fabric plus later electrical, plumbing and heating replacements.',
  ['T007','T008','T009','T011','T017'],['R008','R011','R012','R013'],
  'Record which system belongs to which alteration. Use level, scale and moisture comparison to describe observations. Pre-1978 paint screening applies; a later rewire can introduce a different material era.'),
 ('E3','1960–1979','Mixed material generations; special attention to original or altered branch wiring.',
  ['T008','T009','T011','T017'],['R008','R011','R012','R013'],
  'CPSC identifies 1965 to mid-1970s installations as an aluminum branch-wiring investigation cue, including rewiring. 1960–1977 and 1978–1979 differ for the pre-1978 paint cue. Read markings; do not test by disturbing connections.'),
 ('E4','1980–1999','Multiple generations of replacement equipment and envelope repairs may now overlap.',
  ['T008','T009','T018'],['R004','R010','R011','R012','R013'],
  'Prioritize label capture, drainage details, accessible material transitions and repair records. A later original year does not rule out older additions, reused materials or suspect insulation.'),
 ('E5','2000-2009','I-code-era assemblies and product-specific equipment; local adoption dates differ.',
  ['T008','T009','T018'],['R004','R005','R010','R011','R012'],
  'Use model-specific instructions for protection devices, water heating and venting. Obtain alteration records; model-code publication year does not establish local applicability. See APP-H.'),
 ('E6','2010-2019','Residential sprinkler transition within the decade; product-specific equipment and alterations.',
  ['T008','T009','T018'],['R004','R005','R010','R011','R012'],
  'Add fuel/CO and water modules for installed systems. Capture sprinkler and equipment records within scope. The 2015 state transition falls inside this statistical group; verify the exact permit/locality dates in APP-H.'),
 ('E7','2020 onward','Recent regional adoption changes, new controls and installation details.',
  ['T008','T009','T018'],['R004','R005','R010','R011','R012'],
  'Prioritize permit and commissioning records, labels, accessible drainage/venting and EV provisions. Recent construction is not proof of correct work. The 2023 EV, regional 2024 and Howard 2025 transitions sit inside this group. See APP-H. The housing chart measures the 2024 survey vintage, not later completions.')]

CORE=['T001','T002','T003','T004','T006','T012','T019']
MODULES=[
 ('Structural deterioration','T005','Probe only where warranted and permitted; do not damage finished or suspect hazardous surfaces.'),
 ('Access plan','T010 / T017','Ladder/coveralls as access requires; equipment does not make an unsafe space accessible.'),
 ('Moisture comparison','T008 / T013','Moisture meter; thermal camera only if available and trained. Neither proves hidden cause.'),
 ('Accessible electrical screening','T020','Noncontact indicator is supplementary; it cannot prove absence of voltage or a safe panel.'),
 ('Water supply / hot water','T021 / T022','Pressure gauge and suitable temperature instrument where the agreed test and safe connection permit.'),
 ('Fuel-burning equipment','T023 / T024','Select CO and/or combustible-gas instruments for the gas and intended test; do not substitute one for the other.'),
 ('Specialist / extended service','T014 / T015 / T016','Borescope, monitoring instruments or logger only for a separately appropriate purpose. No drilling or long-term diagnosis implied.'),
 ('Training only','T025','Wire samples stay in the training kit; not a routine energized-panel inspection tool.')]

def reorganize(data):
 main=[];reference=[];exams=[]
 for p in data['pages']:
  if p['id'].startswith('exam_'):exams.append(p)
  elif p['id']=='reference_numbers' or p['id'].startswith(('numbers_','local_')):reference.append(p)
  else:main.append(p)
 data['pages']=main;data['reference_pages']=reference;data['exam_pages']=exams
 section='Method, structure and moisture'
 for p in main:
  section=dict(DOMAINS).get(p['id'],section);p['section']=section
 data['hierarchy']=dict(domains=[dict(first_topic=a,title=b) for a,b in DOMAINS],appendices={'APP-A':'Field tool register','APP-B':'Reference and record tools','APP-C':'Report mentions log','APP-D':'Terms, notes and numerical references','APP-E':'Sources and evidence register','APP-F':'Construction-era packing lists','APP-G':'Exam review','APP-H':'Codes, Standards, and General Practice Timeline'})
 data['editorial_policy']='Content-led update. Main guide holds component decisions; appendices hold detailed reference and review records. Preserve qualifiers, source identifiers and prior entry identifiers.'
 return data

def add_pages(flow,pages,data,b):
 body=''
 for p in pages:
  h=b.heading(p['title'],p['id'])
  # A heading must not try to keep an entire multi-page reference table.
  h.style=copy.copy(h.style);h.style.keepWithNext=False
  flow +=[b.CondPageBreak(180),b.Spacer(1,12),h]
  body+=f'<section id="{b.e(p["id"])}"><h2>{b.e(p["title"])}</h2>'
  for block in p['blocks']:
   if block['kind']=='text':flow.append(b.para(block['text']));body+='<p>'+b.e(block['text'])+'</p>'
   elif block['kind']=='table':flow.append(b.table(block));flow.append(b.Spacer(1,8));body+=b.html_table(block)
   elif block['kind']=='figures':
    flow.append(b.figure_flow(block['ids'],data['figures'],min(block.get('height',160),140)))
    for fid in block['ids']:
     f=data['figures'][fid];body+=f'<figure><img loading="lazy" src="../{b.e(f["asset"])}" alt="{b.e(f.get("caption",""))}"><figcaption>{b.e(f.get("caption",""))}</figcaption></figure>'
  refs='Source notes: '+' | '.join(b.reference_text(r) for r in p.get('refs',[]));flow.append(b.para(refs,b.SMALL));body+='<p class="refs">'+b.e(refs)+'</p></section>'
 return body

def extra_appendices(data,b,only=None):
 result=[]
 for aid,title in [('APP-D','Terms, notes and numerical references'),('APP-E','Sources and evidence register'),('APP-F','Construction-era packing lists'),('APP-G','Exam review'),('APP-H','Codes, Standards, and General Practice Timeline')]:
  if only and aid not in only:continue
  flow=[b.heading(aid+' v1.1 · '+title,aid)];body='<p><a href="../STUDY GUIDE.html">Main guide</a></p>';record=dict(id=aid,version='1.1',edition='SG-010',title=title)
  if getattr(b,'design_installed',False):
   from design_language import appendix_map
   flow +=[appendix_map(aid),b.Spacer(1,12)]
  def block(title,headers,rows,widths=None):
   nonlocal body
   t=b.table(dict(headers=headers,rows=rows,widths=widths));t.wrap(524,704)
   h=b.para(title,b.ParagraphStyle('ReferenceTableHeading',parent=b.H2,keepWithNext=False))
   need=h.wrap(524,704)[1]+h.getSpaceAfter()+sum(t._rowHeights[:2])+4
   flow.extend([b.CondPageBreak(min(680,need)),h,t,b.Spacer(1,10)]);body+='<h2>'+b.e(title)+'</h2>'+b.html_table(dict(headers=headers,rows=rows))
  if aid=='APP-D':
   topics={p['id']:p for key in ['pages','reference_pages','exam_pages'] for p in data[key]}
   entries=[];rows=[]
   for a,c,d,target in sorted(TERMS,key=lambda x:x[0].casefold()):
    topic=topics.get(target)
    pointer=('APP-H: definitions and official references H01-H20' if target=='APP-H' else (topic['title']+' ['+'; '.join(b.reference_text(r) for r in topic.get('refs',[])[:2])+']') if topic else 'Main guide: '+target)
    rows.append([a,c+'. '+d+'\nSource pointer: '+pointer]);entries.append(dict(term=a,expansion=c,definition=d,topic=target,source_pointer=pointer,source_refs=topic.get('refs',[]) if topic else ['APP-H']))
   flow.append(b.para('Alphabetical retrieval aid. Definitions derive from the linked topic and its evidence; paired terms show a distinction, not synonyms. The topic and cited source retain the full conditions.'))
   block('Terms and flags',['Term','Definition / distinction / source pointer'],rows);record['terms']=entries
   body+='<p>Follow a definition to its topic and source: '+ ' | '.join('<a href="'+('APP-H-v1.1.html' if x['topic']=='APP-H' else '../STUDY GUIDE.html#'+x['topic'])+'">'+b.e(x['term'])+'</a>' for x in entries)+'</p>'
   block('Footnote key',['ID / topic','Meaning'],[[a+' · '+c,d] for a,c,d in NOTES]);record['notes']=NOTES
   block('S15–S29: numerical reference chart [N02]',['Value / application','Basis and qualification'],[[a+'\n'+c,basis+' · '+source+'\n'+note] for a,c,basis,source,note in NUMBERS])
   body+=add_pages(flow,data['reference_pages'],data,b);record['pages']=data['reference_pages']
  elif aid=='APP-E':
   flow.append(b.para('S01–S30 are unique original recordings. Hashes below are abbreviated SHA-256 identifiers; complete hashes, paths, review records and selected-screen references remain in the edition JSON and evidence index. Original media have not been moved to an offline archive.',b.SMALL))
   rows=[]
   for s in data['sources']:
    hash=s.get('source_sha256',s.get('sha256',''));dur=s.get('duration_seconds',0)
    rows.append([s['id']+'\n'+(b.ts(dur) if dur else 'Duration in evidence record'),s.get('name') or Path(s.get('source_path','')).name,(hash[:16] if hash else 'See retained session record')])
   block('Original recording register',['Source / duration','Recording','SHA-256 prefix'],rows,[76,310,138]);record['sources']=data['sources']
   for rid,name,url,note in list(REFERENCES)+ERA_REFS:
    flow +=[b.KeepTogether([b.para(rid+' · '+name,b.H2),b.para(note),b.Paragraph('<link href="'+b.e(url)+'">'+b.e(url)+'</link>',b.SMALL)])]
    body+=f'<h3 id="{rid}">{b.e(rid+" · "+name)}</h3><p>{b.e(note)} <a href="{b.e(url)}">Open primary reference</a></p>'
   record['external_references']=[dict(id=a,title=c,url=d,note=f,reviewed_on=b.DATE) for a,c,d,f in list(REFERENCES)+ERA_REFS]
   flow.append(b.para('Earlier source links remain in the retained topic footnotes, session records and amendment files. This register adds the primary references used for SG-010; it does not recertify all historical local rules.',b.SMALL))
  elif aid=='APP-F':
   flow.append(b.para('Select by original construction year, then add cards/modules for additions, renovations and actual systems [N05]. These are editorial packing groups, not code eras. Tick boxes mean packed for this visit; ownership and training remain unrecorded [N07].'))
   tools={i['id']:i for i in read(OUT/'Appendices/APP-A-v1.6.json')['items']};refs={i['id']:i for i in read(OUT/'Appendices/APP-B-v1.5.json')['items']}
   body+='<p>Select by original construction year, then add for renovations and actual systems. These seven groups are packing aids, not code eras. See APP-H for exact local dates.</p>'
   block('Common kit: all seven groups',['Pack / ID','Item / use'],[['[  ] '+id,tools[id]['name']+'\n'+tools[id]['purpose']] for id in CORE])
   block('Common records',['Reference IDs','Carry or prepare'],[['R001–R008','Scope/job record, report template, evidence backup, manufacturer/local references, instrument record, measurement log and specialist contacts.']])
   block('Add by observed system and agreed service [N03, N06]',['Module / tool IDs','Selection condition'],[[a+'\n'+c,d] for a,c,d in MODULES])
   block('Seven-group packing matrix',['Original construction','Additional field items / reference emphasis'],[[name,', '.join(ids)+'\n'+', '.join(rids)] for era,name,focus,ids,rids,note in ERAS])
   flow.append(b.para('Tool IDs are defined in APP-A; reference IDs in APP-B. Identical items across groups are intentional: a different construction year changes what deserves attention more often than it changes the instrument. Specialist sampling kits and repair tools are not assumed.',b.SMALL))
   for era,name,focus,ids,rids,note in ERAS:
    flow +=[b.CondPageBreak(220),b.Spacer(1,10),b.heading(era+' · '+name,era),b.para(focus)]
    body+='<section id="'+era+'"><h2>'+b.e(era+' · '+name)+'</h2><p>'+b.e(focus)+'</p>'
    block('Select beyond the common kit',['Field items','References'],[['\n'.join('[  ] '+id+' '+tools[id]['name'] for id in ids),'\n'.join('[  ] '+id+' '+refs[id]['name'] for id in rids)]],[262,262])
    flow.append(b.para(note));body+='<p>'+b.e(note)+'</p></section>'
   packing_note='Property/year/source: __________________  Additions/renovations: __________________\nVisit date: __________  Modules/substitutes: __________________\nUnavailable item, limitation or referral: __________________\nSources: APP-A/B; CPSC-ERA, EPA-LEAD and EPA-VERMICULITE in APP-E; local chronology in APP-H. Era grouping is editorial judgment [N05-N07].'
   flow.append(b.para(packing_note,b.SMALL));body+='<p>'+b.e(packing_note)+'</p>'
   record.update(common_kit=CORE,modules=MODULES,eras=[dict(id=a,years=c,focus=d,tool_ids=f,reference_ids=g,note=h) for a,c,d,f,g,h in ERAS])
  elif aid=='APP-G':
   flow.append(b.para('Detailed exam review is preserved here to keep the component guide concise. Read corrections by question wording; scores belong to specific recorded attempts [N08]. The online edition links selected result and correction screens.'))
   results=score_records()
   block('S15-S30: visually confirmed recorded results',['Source / time','Unit / recorded attempt','Result'],[[r['source']+'\n'+r['timestamp'],r['unit'],str(r['score'])+'%\n'+str(r['correct'])+'/'+str(r['total'])] for r in results],[108,326,90])
   record['recorded_results']=results
   note='These are recorded attempts, not a complete course transcript or a question-by-question audit. Earlier and later scores remain separate. Selected corrections below are reviewed against their wording and technical context.'
   flow.append(b.para(note,b.SMALL));body+='<p>'+b.e(note)+' <a href="../reviewed-exams-S15-S29.html">Open result-screen evidence</a>.</p>'
   body+=add_pages(flow,data['exam_pages'],data,b);record['pages']=data['exam_pages']
  else:
   intro='Working area: Baltimore City and Anne Arundel, Baltimore, Carroll, Harford and Howard counties. This is a dated study/reference appendix. It preserves unresolved source conflicts and separates legal applicability from construction-age clues.'
   flow.append(b.para(intro));body+='<p>'+b.e(intro)+'</p>'
   for section_title,headers,rows in TIMELINE_SECTIONS:
    block(section_title,headers,rows,[118,203,203] if len(headers)==3 else [140,384])
   for rid,name,url,note in TIMELINE_REFS:
    flow.append(b.KeepTogether([b.para(rid+' · '+name,b.H2),b.para(note,b.SMALL),b.Paragraph('<link href="'+b.e(url)+'">'+b.e(url)+'</link>',b.SMALL)]))
    body+=f'<h3 id="{rid}">{b.e(rid+" · "+name)}</h3><p>{b.e(note)} <a href="{b.e(url)}">Official source</a></p>'
   record.update(sections=TIMELINE_SECTIONS,references=[dict(id=a,title=c,url=d,note=f,reviewed_on=b.DATE if a=='H04' else '2026-09-19') for a,c,d,f in TIMELINE_REFS],unresolved=['Harford official date/bill conflict','Statewide final 2026 NEC adoption not established by proposal minutes','H14 original source PDF unavailable; original reference retained as a documented source gap'])
  path=OUT/f'Appendices/{aid}-v1.1.pdf';doc=b.Doc(path,aid+' · '+title);doc.build(flow)
  record['page_index']=doc.positions;save(OUT/f'Appendices/{aid}-v1.1.json',record)
  (OUT/f'Appendices/{aid}-v1.1.html').write_text(b.doc_html(aid+' · '+title,body),encoding='utf-8')
  result.append(dict(id=aid,version='1.1',title=title,path=f'Appendices/{aid}-v1.1.html',pages=len(b.PdfReader(path).pages)))
 return result
