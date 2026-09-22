"""Eight-page, locally generated route companion; timings are workflow cues."""
import build as b
import design_language as dl
from prepare import *
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table,TableStyle
from reportlab.graphics.shapes import Drawing,Rect,Circle
from pypdf import PdfReader

MD='https://www.dllr.state.md.us/license/reahi/reahisop.shtml'
STAGES=['BEFORE','ARRIVE','OUTSIDE','LOWEST','SYSTEMS','ROOMS','UPPER','CLOSE']
PAGES=[
dict(id='before',title='30 minutes before arrival',where='PARKED / DESK',route='Records > likely assemblies > selected kit > capture setup',refs=['method','foundation_water'],md='.02-.03',steps=[
('T-30 | Set the visit','Confirm address, client, access, agreed services and report delivery arrangements. Review disclosures and stated concerns.','Property ID; scope; contact; special access.'),
('T-25 | Read the building history','Check original year, additions and claimed replacements. Select an APP-F era card; treat county housing data as a review cue.','Original vs altered; records still needed.'),
('T-20 | Choose the questions','Pick two or three interfaces worth tracing: roof-to-wall water, deck-to-house load, or old-to-new services.','Question + evidence that would resolve it.'),
('T-10 | Pack for the question','Use APP-A and the selected APP-F card. Check lights, camera storage, instrument response and access equipment.','Core kit + justified additions; missing capability.'),
('T-05 | Prepare capture','Create the property record; verify clock, address and room/elevation naming. Keep work parked; allow actual travel time.','Photo/voice naming; blank limitation and return list.')],gate='Carry a route, not an age-based verdict. Timing marks are adjustable preparation cues.',note='W1 is a route aid, not an exhaustive inspection checklist or a timed inspection limit. Apply the agreed scope and current Maryland standard; record each actual component and limitation in the report.'),
dict(id='arrive',title='At arrival: establish the route',where='ENTRY / FIRST LOOK',route='People > access > baseline > safe route',refs=['method','devices','gas_heat'],md='.02-.03',steps=[
('01 | Confirm the assignment','Confirm concerns, occupancy, access permissions and any systems already shut down. Identify pets, belongings and blocked areas.','Who supplied each history statement; access limits.'),
('02 | Orient the record','Take an address/context image. Establish consistent elevations and room names; note weather and ground conditions.','Arrival time; orientation; conditions affecting observation.'),
('03 | Identify access points','Locate roof/attic/crawl entries, panels, utility equipment and garages. Choose a continuous route that fits this building.','Entry locations; restricted or unsafe areas; return points.'),
('04 | Capture the starting state','Record settings before permitted normal-control operation. Identify existing leaks, damage and equipment status.','Initial settings; existing conditions; test omissions.'),
('05 | Screen for immediate hazards','If suspected fuel leakage, unsafe combustion, exposed electrical danger or unsafe footing is present, stop affected work and follow the appropriate emergency response.','Observed hazard; affected area; action and notification.')],gate='Change the route for safety, weather or access. Keep skipped items on the return/limitation list.',note='Suggested walking order: outside + garage / lowest level / equipment / room loop / attic / return checks / departure. Reorder spaces as needed; do not lose the coverage record.'),
dict(id='outside',title='One continuous outside loop',where='SITE / ENVELOPE / GARAGE',route='Ground > wall > opening > roof > discharge',refs=['foundation_water','walls','openings','site_decks','garage','roof_cover'],md='.05-.06 / .11',steps=[
('01 | Site and approach','Follow grades, drainage, retaining walls and walking surfaces where they affect the dwelling. Trace roof discharge away from the wall.','Direction; receiving area; trip or water concern.'),
('02 | Wall interfaces','Follow cladding transitions, penetrations, trim and flashing. Look below roof-wall junctions and at grade clearance.','Elevation + interface; visible condition; interior return.'),
('03 | Openings','Inspect exterior doors and accessible windows: operation, water paths, glazing and visible support are separate questions.','Opening ID; response; stain or support correlation.'),
('04 | Decks and stairs','Trace member > connection > bearing. Check ledger/flashing, posts, guards, handrails and stair route.','Connection evidence; deterioration; unsafe access.'),
('05 | Roof and outlets','Use a safe inspection method. Read covering, flashings, penetrations, chimneys, drainage and terminations.','Method; material; unseen areas; discharge route.'),
('06 | Garage / carport','Check separation, penetrations, appliances and the door mechanism before operation. Reversal functions require their own safe, model-specific checks.','Mechanism; method; response; tests omitted.')],gate='A compromised garage-door mechanism or unsafe roof access stops that operation. Record the limitation.',note='Bring exterior questions indoors: water below a roof-wall junction; movement near an opening; support beneath a deck. A matching stain is a lead, not proof of cause.'),
dict(id='lowest',title='Lowest accessible level',where='BASEMENT / CRAWL / SLAB',route='Access > water clues > support > altered interfaces',refs=['foundation_water','movement','load_paths'],md='.04 / .12',steps=[
('01 | Enter only where safe','Assess readily accessible basement/crawl areas and the access method. Do not force access, disturb suspect materials or enter hazardous spaces.','Entry; method; areas not seen and why.'),
('02 | Follow the water question','Compare stains, deposits, damp materials and observed readings with exterior grade, discharge, openings and visible piping.','Exact location; conditions; competing explanations.'),
('03 | Trace support','Follow floor framing through bearing, posts, beams and foundation. Check visible alterations, notches, holes and connections.','Member-to-support sequence; interruption or change.'),
('04 | Read movement in context','Record cracks, displacement, deformation and material boundaries. Relate openings and floors without declaring cause from one symptom.','Orientation; dimensions; offset; corroborating observations.'),
('05 | Check unfinished-space layers','Observe accessible insulation, vapor/moisture barriers, ventilation and exposed services. Probe suspected structural deterioration where appropriate and non-damaging.','Material; location; absent layer; access/probing limits.'),
('06 | Leave a return point','Identify any area below fixtures or equipment that should be revisited after safe operation.','Return location; trigger; what change to look for.')],gate='Do not convert a visual finding into structural adequacy, concealed-condition or environmental certification.',note='Water and load paths overlap at sill/rim areas, beam pockets and post bases. Keep the observations separate, then compare their locations.'),
dict(id='systems',title='At the equipment and services',where='UTILITY / MECHANICAL AREAS',route='Identify > inspect > safe normal control > record > restore',refs=['service','circuits','water','water_heat','gas','gas_heat','oil_heat'],md='.07-.10',steps=[
('01 | Electrical service / panels','Record service ratings, disconnects, wiring method and visible condition. Inspect accessible panel interiors only where safe; identify alternative supplies.','Panel/location; label evidence; defects; access limits.'),
('02 | Water / waste / pumps','Identify visible materials, cleanout access, main water and hose-bib shutoffs, and accessible pumps. Separate supply, drainage and disposal questions.','Materials; locations; pump type; safe test response.'),
('03 | Water heating','Capture identity and fuel. Follow visible water, relief discharge, air and vent paths; observe supports and leakage.','Device function; route; visible obstruction or defect.'),
('04 | Fuel / CSST / oil','Identify accessible fuel piping, shutoff and storage. Report CSST presence with licensed-master-electrician bonding review; identify oil-tank/line concerns.','Product evidence; location; corrosion/leakage; referral.'),
('05 | Heating','Identify fuel, system and distribution. Use safe normal controls, including applicable auxiliary/emergency modes. Keep combustion and room-air paths separate.','Starting setting; mode; response; limitation; restored state.'),
('06 | Cooling','Identify installed cooling, energy, distribution and condensate drainage. Use normal controls only under suitable conditions and instructions.','System; mode; response; or reason operation was unsafe.')],gate='No live adjustments, bypassed safeties, oil-burner resets, reactivated shut-down equipment or relief-valve tests to complete the route.',note='MD reminders supplement current lesson coverage. No universal cooling-temperature threshold is assumed. Noncontact voltage indication does not establish absence of voltage; one disconnect may leave another source energized.'),
dict(id='rooms',title='Repeat the same room loop',where='EACH ROOM / EACH LEVEL',route='Ceiling > walls/openings > floor > devices > fixtures',refs=['movement','openings','site_decks','dwv','devices','gas_heat'],md='.07-.08 / .11-.13',steps=[
('01 | Surfaces and openings','Read accessible ceilings, walls and floors; operate the applicable doors/windows. Relate stains or movement to the exterior and level below.','Room + location; operation; correlated evidence.'),
('02 | Stairs and built-ins','Inspect accessible stairs, ramps, landings, rails, cabinets and countertops. Keep fall hazards and impaired operation distinct.','Location; condition; effect on use.'),
('03 | Electrical / alarms','Inspect the applicable representative devices and GFCI/AFCI protection. Record smoke- and CO-alarm presence/absence; note alternative-energy disconnects.','Device/location; method and response; alarm observations.'),
('04 | Every accessible fixture','Check all accessible fixtures/faucets for functional flow and drainage; observe visible leakage and piping. Attend running water and stop on a problem.','Fixture; separate supply/drain results; leakage; limitations.'),
('05 | Installed appliances','Use safe normal controls for primary functions of installed oven/range, cooktop, microwave, dishwasher and disposal, as applicable.','Each appliance; function tested; result or reason omitted.'),
('06 | Delivery / exhaust / hearth','Observe accessible heating/cooling delivery and mechanical ventilation. Inspect accessible fireplaces, solid-fuel components and venting without lighting fires.','System/location; condition; accessible extent; referral.')],gate='A broad row is a route reminder. Record each component and actual test extent; do not turn a row tick into a blanket pass.',note='Restore controls you changed, unless an unsafe condition requires a different response. Describe that response and who was informed. Detailed procedures for cooling, appliances and hearths remain outside current L1 lesson coverage.'),
dict(id='upper',title='Attic, then the return checks',where='UPPER VOID / FLAGGED LOCATIONS',route='Roof outside > roof underside > ceiling below',refs=['load_paths','roof_structure','roof_cover','walls','foundation_water','dwv'],md='.04 / .06 / .12',steps=[
('01 | Establish safe access','Record attic entry and inspection method. Check footing and clearance; do not step onto unsupported ceilings or disturb insulation/suspect materials.','Entry; viewed areas; blocked/unsafe portions.'),
('02 | Roof structure and sheathing','Observe accessible framing, connections, alterations and underside moisture evidence. Compare with roof planes and penetrations seen outside.','Member/connection; location; matching exterior question.'),
('03 | Insulation / ventilation','Describe accessible insulation and vapor-control layers, ventilation and visible exhaust routes. Note absent insulation at conditioned boundaries.','Observed layers; gap; terminal; concealed route.'),
('04 | Return below operations','Revisit flagged areas beneath fixtures/equipment after appropriate operation. Compare with the starting condition.','Changed or unchanged observation; test conditions.'),
('05 | Close the three paths','Reconcile water routes, load transfers and combustion/vent routes at the locations that raised questions.','Evidence supporting the finding; remaining uncertainty.'),
('06 | Reconcile the route','Check each area and agreed service against the record. Resolve omissions while still on site, or state the limitation and next action.','Observed / operated / limited / not present; follow-up owner.')],gate='An unobserved area remains a limitation. A quiet or dry test does not verify concealed systems.',note='Use the actual room/elevation labels in both photos and findings. Return checks connect observations; they do not establish causation by location alone.'),
dict(id='close',title='Departure through +20 minutes',where='CLIENT WALK-THROUGH / PARKED',route='Reconcile > communicate > secure > preserve > draft',refs=['method'],md='.02-.03',steps=[
('BEFORE LEAVING | Reconcile','Account for agreed areas, services, test results and limitations. Complete necessary return checks before closing the visit.','Open item; disposition; person responsible.'),
('AT DEPARTURE | Explain / restore','Discuss significant findings, limitations and urgent actions. Confirm affected people were informed; check changed controls, water, access panels and locks.','Who; what; time; final settings and securing actions.'),
('D+00 to +05 | Preserve','While parked, verify photos/notes belong to this property and that local copies are readable. Confirm a second copy when available.','File count/check; backup state; missing evidence.'),
('D+05 to +12 | Draft the findings','Turn observations into location + condition + significance + recommended action. Separate uncertain cause and third-party history.','Finding linked to photo/note; exact unresolved question.'),
('D+12 to +20 | Assign follow-up','List records, product instructions or qualified reviews still needed. Confirm promised report timing and delivery arrangements.','Owner; next action; due time; report work remaining.')],gate='D = actual departure. The +20-minute window organizes closeout; it is not a deadline for a finished report.',note='W1 sequence and time windows are editorial workflow proposals. Technical cues draw from SG-010/L1 and the current Maryland standard (MD). W1 is not a code-compliance inspection or a substitute for those sources.')
]

def strip(active):
 d=Drawing(504,39)
 for i,name in enumerate(STAGES):
  x=i*63;d.add(Rect(x,13,59,24,fillColor=dl.N if i==active else dl.TINT,strokeColor=None))
  dl.label(d,name,x,30,59,7.8,True,dl.WHITE if i==active else dl.N,align='center')
 return d

def main():
 dl.install(b);idx=read(OUT/'page-index.json');short=read(OUT/'study-guide.json');byid={p['id']:p for p in short['pages']}
 for p in PAGES:
  assert set(p['refs'])<=set(byid),(p['id'],set(p['refs'])-set(byid))
 body=ParagraphStyle('WalkingBody',parent=b.BODY,fontSize=11,leading=13.6,spaceAfter=4)
 head=ParagraphStyle('WalkingStep',parent=body,fontName='Helvetica-Bold',spaceAfter=5)
 note=ParagraphStyle('WalkingNote',parent=b.SMALL,fontSize=9,leading=11.5)
 flow=[];html='<nav><a href="STUDY GUIDE - SG-010-W1.pdf">Print W1 (8 pages / 4 sheets duplex)</a><a href="index.html">Edition library</a></nav><p>Experimental route companion. T = arrival; D = departure. Site work follows the property, with no imposed inspection duration.</p>'
 for k,p in enumerate(PAGES):
  if k:flow.append(b.PageBreak())
  flow +=[strip(k),b.heading(p['title'],p['id']),b.para(p['where']+' / '+p['route'],note)]
  rows=[]
  for j,(title,act,capture) in enumerate(p['steps']):
   box=Drawing(13,20);box.add(Rect(1,6,9,9,fillColor=None,strokeColor=dl.N,strokeWidth=.7))
   rows.append([box,[b.para(title,head),b.para(act,body)],b.para(capture,body)])
  t=Table([[b.para('',b.HEAD),b.para('DO / OBSERVE',b.HEAD),b.para('CAPTURE / RESOLVE',b.HEAD)]]+rows,colWidths=[22,298,184])
  t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),dl.N),('BACKGROUND',(-1,1),(-1,-1),dl.TINT),('LINEBELOW',(0,1),(-1,-1),.6,dl.GRAY),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
  flow +=[t,b.Spacer(1,9),b.para(p['gate'],head),b.para(p['note'],note)]
  refs='; '.join(byid[r]['title'].split('  ',1)[-1]+' p. '+str(idx[r]) for r in p['refs'])
  pointer='SG-010: '+refs+'. MD: COMAR 09.36.07 '+p['md']+'.'
  flow.append(b.para(pointer,note))
  html+='<section id="'+p['id']+'"><h2>'+str(k+1)+' / '+b.e(p['title'])+'</h2><p>'+b.e(p['route'])+'</p>'+b.html_table(dict(headers=['Step','Do / observe','Capture / resolve'],rows=p['steps']))+'<p><strong>'+b.e(p['gate'])+'</strong></p><p>'+b.e(p['note'])+'</p><p>'+''.join('<a href="STUDY GUIDE.html#'+r+'">'+b.e(byid[r]['title'])+'</a> / ' for r in p['refs'])+'<a href="'+MD+'">MD '+p['md']+'</a></p></section>'
  if k==7:flow.append(b.para('MD source: Maryland Department of Labor, Minimum Standards of Practice; chapter revised 22 Dec 2025, checked 20 Sep 2026. Digital W1 provides the live link.',note))
 doc=b.Doc(OUT/'STUDY GUIDE - SG-010-W1.pdf','SG-010-W1 - Walking Cut');doc.build(flow)
 n=len(PdfReader(OUT/'STUDY GUIDE - SG-010-W1.pdf').pages);assert n==8,(n,doc.positions)
 assert all(doc.positions[p['id']]==i+1 for i,p in enumerate(PAGES)),doc.positions
 save(OUT/'walking-cut.json',dict(edition='SG-010-W1',status='Experimental route aid',presentation_revision='experimental-R1',pages=PAGES,page_index=doc.positions,print_pages=n,duplex_sheets=4,timing='T is arrival; D is actual departure. Preparation and closeout are suggested windows; inspection duration is unrestricted.',sources=[dict(id='MD',url=MD,checked='2026-09-20',revision_effective='2025-12-22'),dict(id='SG-010',path='study-guide.json'),dict(id='SG-010-L1',path='study-guide-L1.json')],limits='Not an exhaustive checklist. Apply current standards and agreed scope. Cooling, appliances and hearth prompts supplement detailed lesson coverage.'))
 (OUT/'STUDY GUIDE - SG-010-W1.html').write_text(b.doc_html('SG-010-W1 / Walking Cut',html),encoding='utf-8')
 print('W1:',n,'pages',flush=True)

if __name__=='__main__':main()

