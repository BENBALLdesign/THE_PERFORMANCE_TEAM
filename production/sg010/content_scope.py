"""Scope audit: recorded outline is a coverage map, never a field-risk ranking."""
from prepare import *
REFS=[
 ('S36-NHIE','NHIE policies, procedures and content outline','https://nationalhomeinspectorexam.org/download/22502/?tmstv=1728326281','Use the published task families as a coverage check. Exam weighting is not the probability or consequence of a field defect.'),
 ('S35-MOLD','EPA: Is sampling/testing for mold necessary?','https://www.epa.gov/mold/samplingtesting-mold-necessary','Visible growth often does not need sampling to establish a moisture/remediation question; no federal mold or spore concentration limit establishes a pass/fail.'),
 ('S35-RADON','EPA: Home buyer and seller guide to radon','https://www.epa.gov/sites/production/files/2015-05/documents/hmbuygud.pdf','Testing addresses the individual building. A regional map, another house or a visible mitigation fan cannot establish its radon concentration.'),
 ('S35-RADON-FIX','EPA: Consumer guide to radon reduction','https://www.epa.gov/sites/default/files/2016-12/documents/2016_consumers_guide_to_radon_reduction.pdf','Soil-gas extraction and safe fan/discharge placement require a complete system; the gauge is not a radon test.'),
 ('S35-MD-LEAD','Maryland MDE: Inspections for rental housing','https://mde.maryland.gov/programs/Land/LeadPoisoningPrevention/Pages/rentalowners_inspections.aspx','Pre-1978 rental-property lead duties are a separate regulated process; use MDE-accredited inspection services and actual property records.')]
def refs():return [dict(source='S36',seconds=0,label='Recorded inspector-role / task outline')]+[dict(source=a,label=b,url=c) for a,b,c,n in REFS]
def topic(id,title,rows,section='Inspection scope, communication and reporting'):
 return dict(id=id,title=title,section=section,blocks=[dict(kind='table',headers=['Decision','Evidence / action','Boundary / next step'],rows=rows,widths=[104,220,180])],refs=refs())
NEW=[topic('professional_scope','Define the assignment before entering the property',[
 ['Agreement / people','Identify client, property, included systems, services, report delivery and agreed timing. Explain access and normal operating methods.','Confirm changes to scope explicitly; do not imply that a home inspection certifies code compliance or guarantees future performance.'],
 ['Independence','Separate observable condition from sales pressure, seller statements and unverified repair assurances. Disclose relevant interests and limitations.','Keep professional judgment independent; avoid promises, specialist conclusions or work outside competence and authorization.'],
 ['Access / consent','Arrange utilities, keys, occupants, animals, ladders and accessible areas; clarify authorization to operate controls and capture evidence.','An available opening or supplied ladder does not establish safe access. Record the exact area and system not inspected.'],
 ['Privacy / records','Retain dated agreement, notes, photos, communication and issued report with the correct property and revision.','Share only as authorized; distinguish property evidence from unrelated personal material captured on site.'],
 ['Urgent communication','Promptly communicate an observed immediate concern and its location, action and recipient; carry it into the written report.','Do not rely on the routine report delivery window for an urgent hazard. Document the boundary of any protective action.'],
 ['Insurance / competence','Confirm the applicable professional requirements and the service actually offered before accepting specialized work.','A course certificate, trade experience, insurance policy or basic home-inspection license does not establish every specialist credential.']]),
 topic('special_service_boundaries','Observe the condition; define the specialist question',[
 ['Pools / spas','Observe accessible barrier, gate, cover, electrical and visible leakage/structural concerns within the agreed scope.','A home inspection is not a pool-safety certification. Do not enter water or manipulate unsafe electrical equipment to prove a defect.'],
 ['Irrigation','Identify visible controls, leaks, deterioration and cross-connection protection where included.','Do not infer concealed performance, use brittle valves, or treat irrigation plumbing as potable-water distribution.'],
 ['Wood damage / organisms','Describe affected member, visible damage, moisture and access; distinguish a structural question from pest identification or treatment.','General inspection evidence does not establish species, activity, concealed extent or treatment effectiveness. Refer with an explicit question.'],
 ['Radon','Recommend an appropriate building-specific test when included or advised; retain device, location, dates, conditions and protocol.','A county map, active fan or pressure gauge cannot establish concentration. Do not adopt lecture equipment prices, blanket test rankings or state-license generalizations.'],
 ['Moisture / possible growth','Record visible material, location, moisture evidence and extent of inspection; address the source and appropriate remediation evaluation.','Appearance does not identify species or health risk. Do not use a ten-times-outdoor rule as a universal mold threshold or assume air testing is always needed.'],
 ['Lead / suspect asbestos','Record suspected material and disturbance concern without scraping, sampling or certifying absence. Check the separate service and qualified referral.','Maryland pre-1978 rental lead obligations are not satisfied by a routine home inspection; a build year or paint swab is not a whole-property clearance.']]),
 topic('report_workflow','Turn a field observation into a traceable conclusion',[
 ['Observe','Name the component and location; record the visible condition, test conditions and photograph or measurement.','Keep client history, third-party statements and direct observation separately attributed.'],
 ['Explain','State why the observed condition matters in practical terms and which related system should be checked.','A plausible cause remains a hypothesis until supported; avoid hiding the defect under a generic recommendation.'],
 ['Recommend','Name the needed next action, appropriate qualified party and urgency supported by the condition.','Do not imply a specialist has confirmed a diagnosis, dictate an unverified repair design, or substitute a price guess for the decision.'],
 ['Describe limitations','Locate the inaccessible or untested part and state why it was omitted and what remains unresolved.','Do not turn a general disclaimer into a false statement that every part of a system was inspected.'],
 ['Reconcile / issue','Match summary to body, photo to location, terminology to glossary, and final report to the correct property/version.','Restore controls, record urgent communications and preserve the issued copy; subsequent corrections get a traceable revision.']])]
COVERAGE=[
 ('D1-T1','Site','exterior_site grading_vegetation retaining_wall_drainage'),
 ('D1-T2','Exterior','exterior_scope siding_assembly openings_report'),
 ('D1-T3','Roof','roof_cover_condition roof_flashing roof_drainage'),
 ('D1-T4','Structure','foundation_types supports wall_systems roof_frame'),
 ('D1-T5','Electrical','electric_service electric_panels electric_devices electric_alternative'),
 ('D1-T6','Cooling','cooling_scope heatpump_inspection'),
 ('D1-T7','Heating','heating_controls furnace_safety oil_storage'),
 ('D1-T8','Insulation / ventilation','insulation_materials air_vapor_thermal ventilation_exhaust'),
 ('D1-T9','Mechanical exhaust / distribution','furnace_airflow ventilation_exhaust kitchen_appliances'),
 ('D1-T10','Plumbing','water_supply plumbing_fixture_checks dwv_traps_vents water_heater_relief'),
 ('D1-T11','Interior','interior_facings interior_moisture kitchen_appliances bath_laundry'),
 ('D1-T12','Fireplaces / solid fuel','chimney_parts venting'),
 ('D1-T13','Life safety','interior_life_safety rails_guards garage_separation'),
 ('D2-T1','Describe systems / components','inspection_method report_workflow'),
 ('D2-T2','Identify significant conditions','movement moisture reporting report_workflow'),
 ('D2-T3','Communicate findings / implications','reporting report_workflow'),
 ('D2-T4','Explain limitations / follow-up','site_access_limits heat_exchanger_limits report_workflow'),
 ('D3-T1','Agreement / business scope','professional_scope special_service_boundaries'),
 ('D3-T2','Professional conduct / records','professional_scope report_workflow')]
def apply(d,compact,apps,walk):
 d['pages'][0:0]=[copy.deepcopy(NEW[0])]
 i=next(i for i,p in enumerate(d['pages']) if p['id']=='reporting');d['pages'][i:i]=copy.deepcopy(NEW[1:])
 topics={p['id']:p for p in d['pages']};coverage=[]
 for id,label,ids in COVERAGE:
  keys=ids.split();assert all(k in topics for k in keys)
  status='mapped to retained guide topics; edition review required'
  if id=='D1-T7':status='S38 hydronic/electric heating incorporation pending'
  if id=='D1-T11':status='S39 recovered floor/stair lessons incorporation pending'
  if id=='D1-T12':status='S39 recovered fireplace lessons incorporation pending; existing roof/vent coverage alone is incomplete'
  coverage.append(dict(id=id,task_family=label,topic_ids=keys,status=status,weight_is_not_field_risk=True))
 save(OUT/'scope-coverage.json',dict(edition='SG-010',source='S36 opening outline plus official NHIE content outline',status='working audit; open recovered-source incorporations must be closed before final publication',families=coverage,source_refs=refs()))
 compact.append(dict(id='scope',title='26  Scope, evidence and follow-through',route='Agree > observe > explain > act > document',topics=['professional_scope','special_service_boundaries','report_workflow'],rows=[
 ['Before access','Agree systems/services, safe access, utilities, timing, privacy and report recipient.','A course outline checks coverage; it does not define the contract or certify every condition.'],
 ['During the circuit','Describe the actual component, location, method, observed response and limit.','Distinguish direct observation, reported history and a hypothesis.'],
 ['Connect the evidence','Return across water, load and energy paths when one observation raises a related question.','COMBUSTION includes this guide\'s full electrical/energy inspection route; the label does not mean every system burns fuel.'],
 ['Specialist boundary','Record the visible concern and the specific unanswered question.','Pool, pest, lead, asbestos, mold or radon services require their own scope, method and qualifications.'],
 ['Communicate urgency','State concern, location, appropriate next action and recipient promptly.','Carry the same concern and limitation into the written record.'],
 ['Close the assignment','Restore controls, reconcile summary/photos/locations, and retain the issued revision.','Never let an omitted area, unverified repair or uncertain cause become an implied assurance.']],discuss='What can the client decide from this observation, and which question is still unanswered?',note='S35/S36 / N12. Scope outline is a completeness check, not a local defect-frequency chart. Maryland scope and separate lead duties retain their own references.',figure=None))
 for a,b,c,n in REFS:apps['APP-E']['external_references'].append(dict(id=a,title=b,url=c,note=n,reviewed_on='2026-09-21'))
 apps['APP-B']['scope_coverage']=coverage
 apps['APP-D']['notes'].append(['N12','Scope versus specialist assurance','Exam weighting is not field risk. A routine inspection, regional risk map, species guess or operating mitigation fan does not substitute for a separately scoped specialist inspection or measurement.'])
 terms=[('Scope / limitation','Agreed service / actual constraint','The assignment defines what is included; the field record identifies the specific inaccessible, unsafe or untested part and remaining question.','professional_scope'),('Radon manometer','Pressure indication','Indicates a pressure difference in a mitigation system; it does not measure radon concentration or establish a passing test.','special_service_boundaries')]
 for term,exp,definition,tid in terms:apps['APP-D']['terms'].append(dict(term=term,expansion=exp,definition=definition,topic=tid,source_pointer=topics[tid]['title'],source_refs=refs()))
 apps['APP-G']['pages'].append(topic('S35_scope_qualifications','S35: separate service, evidence and assurance',[
 ['Radon','Test the actual house under a suitable protocol; verify qualification and device requirements.','Do not describe a basement fan as a generic correct installation, a gauge as a concentration test, or repeat lecture regional cancer or price claims.'],
 ['Mold','Describe moisture, visible material and the question requiring evaluation.','No universal ten-times-outdoor pass/fail; no color-based species, toxicity or harmlessness claim.'],
 ['Lead / wood damage','Preserve material condition, disturbance risk, affected members and access.','A pre-1978 rental has separate Maryland duties. Avoid diagnosing pest activity, prescribing pesticides or blaming housekeeping from appearance.'],
 ['Insulation / services','Check depth relative to the actual ruler zero and assembly; note separate attics and knee-wall boundaries.','Do not infer installer intent, impose a universal foam-lift thickness, or improvise pool electrical repairs.']]))
 apps['APP-H']['sections'].append(['Maryland lead: occupancy changes the task',['Evidence / trigger','What it changes'],[['Pre-1978 rental dwelling','Check current MDE registration, inspection/certificate and occupancy requirements. Route to an MDE-accredited lead inspection service; this guide does not issue a lead certificate.'],['Original year / later paint work','Year is a screening cue. Condition, records, intended disturbance and appropriate testing determine the next action; visual inspection does not prove absence.']]])
 apps['APP-H']['references'].append(dict(id='H22',title=REFS[-1][1],url=REFS[-1][2],note='Checked 21 September 2026; separate regulated service.'))
