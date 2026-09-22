"""Reviewed S33 incorporation; source statements and field guidance stay distinct."""
from prepare import *
MD='https://www.labor.maryland.gov/license/reahi/reahisop.shtml'
REFS=[
 ('S33-MD','Maryland minimum home-inspection standards',MD,'Local scope: normal-control appliance functions, alarm presence and inspection limits; COMAR 09.36.07.'),
 ('S33-DW','Whirlpool dishwasher drain-loop guidance','https://producthelp.whirlpool.com/Dishwashers/Product_Info/Dishwasher_Product_Assistance/Checking_the_Drain_Loop_Height','A model-specific reference example. Match the actual installation manual and local plumbing requirements.'),
 ('S33-ALARM','USFA smoke-alarm guidance','https://www.usfa.fema.gov/prevention/home-fires/prepare-for-fire/smoke-alarms/','Locations, replacement and testing guidance; distinguish best protection from jurisdiction-specific legal minimums.'),
 ('S33-MD-ALARM','Maryland Public Safety 9-104','https://mgaleg.maryland.gov/2026RS/Statute_Web/gps/9-104.pdf','Existing-occupancy smoke-alarm requirements depend on construction history and power source. Read the statute with local requirements.'),
 ('S33-TIP','CPSC range stability','https://www.cpsc.gov/s3fs-public/5007.pdf','Verify the required anti-tip provision for the actual range without an improvised tipping test.'),
 ('S33-DRYER','CPSC overheated clothes dryers','https://www.cpsc.gov/s3fs-public/5022.pdf','Lint and restricted exhaust can create a fire hazard in gas and electric dryers. Follow product duct and maintenance instructions.')]
def refs(t,*keys):
 return [dict(source='S33',seconds=t,label='Reviewed course recording')]+[dict(source=a,label=b,url=c) for a,b,c,d in REFS if a in keys]
def topic(id,title,rows,t,*keys):
 return dict(id=id,title=title,section='Interior, appliances and life safety',blocks=[dict(kind='table',headers=['Check / distinction','Evidence and action','Qualification'],rows=rows,widths=[105,225,174])],refs=refs(t,*keys))
NEW=[
 topic('kitchen_appliances','Kitchen appliances: identify, operate, observe, restore',[
 ['Define the appliance','Match model, fuel, installation and normal controls. Inspect accessible supply, drain, cord/connector, support and clearances before operation.','MD includes the primary function of installed cooking appliances, microwave, dishwasher and disposal. Record any omitted operation and reason.'],
 ['Cooking equipment','Check the empty oven before heating; observe ordinary bake/broil and cooktop response as applicable. Confirm controls off before leaving.','No self-clean cycle, prolonged maximum-load challenge or deliberate breaker trip. Follow the model instructions; induction needs a suitable vessel.'],
 ['Rating / circuit','Capture nameplate and accessible circuit identification when a mismatch is suspected. Refer unresolved supply/conductor/overcurrent compatibility.','Watts / volts estimates current; it does not by itself select a dwelling-range breaker. Demand rules, conductor conditions and listing matter. Never upsize a breaker as a shortcut.'],
 ['Range stability','Seek visible evidence of the model-required anti-tip device and engagement using a safe allowed method. Record what could not be verified.','Do not pull a connected appliance, stand on a door or rock the range to create a demonstration.'],
 ['Microwave / hood','Use a microwave-safe water vessel and ordinary controls; verify heating without touching hot water. Identify recirculating or exterior-exhaust configuration.','Do not run an empty microwave or promise radiation-leakage testing. Fan sound alone does not verify an outdoor termination.'],
 ['Refrigerator / compactor','State agreed scope. Observe accessible leaks, seals and normal response if included; keep hands away from the compactor mechanism.','Dispensed ice does not prove ice production; ice shape or frozen food does not establish temperature performance. Do not add waste or bypass interlocks.']],2468,'S33-MD','S33-TIP'),
 topic('kitchen_waste','Kitchen water and waste: observe the whole short cycle',[
 ['Basin / joints','Inspect visible cabinet and joints before use. Use a modest supervised fill where safe, then watch accessible connections during drainage.','Do not fill to an overflow as a proof test. One dry observation does not prove absence of intermittent leakage.'],
 ['Disposal','Check visible corrosion, support, enclosed connections and cable restraint. Use normal operation only when clear and safe, with water as instructed.','Never put a hand or a test object into the chamber. Report exposed wiring or damaged fittings before operating.'],
 ['Dishwasher cycle','Check attachment, door/rack condition and accessible connections. Start a suitable primary-function cycle while able to observe; record stage reached and drainage.','Do not start and leave the property/interior unattended. Incomplete cycles and obscured connections remain explicit limitations.'],
 ['Drain arrangement','Trace hose to its connection upstream of the trap. Identify a secured high loop or air gap and compare with the actual model and local rule.','A hidden factory loop is not assumed, and a high loop is not universally interchangeable with an air gap. Do not pull the dishwasher to prove it.'],
 ['After operation','Recheck visible joints and cabinet floor, then restore controls. Separate present leakage, staining and the occupant\'s repair history.','A bucket or old stain is a clue; report the actual observed liquid, source and test response.']],1716,'S33-DW'),
 topic('bath_laundry','Bathrooms and laundry: follow water across levels',[
 ['Supply / drainage','Check hot and cold response separately. State the simultaneous-use conditions, drainage behavior and locations actually observed.','Functional flow, pressure and drainage are different results. Do not open shut-down valves to complete a test.'],
 ['Toilet / wet enclosure','Observe flush/refill, accessible leakage, support and adjacent finishes. Check relevant glazing marks, doors and visible joints.','Appearance does not prove concealed waterproofing, a toilet seal or safety glazing where markings cannot be read.'],
 ['Return below','After safe fixture operation, return to accessible ceilings, framing and rooms below; correlate changes with the fixture and test timing.','A stain has several possible causes. No observed leak during a short test is not a watertightness warranty.'],
 ['Hydromassage tub','Confirm scope, instructions, water level and safe access before operation. Observe accessible GFCI, pump and bonding provisions without live work.','An attached bond disappearing from view does not verify the remote connection. Do not run a pump dry or remove sealed access.'],
 ['Washer connections','Observe hoses, valves, standpipe and visible leakage. Distinguish a water-hammer arrester from a thermal-expansion tank.','Braided hoses are not burst-proof or permanent. No disconnection or unsafely operated unused valve is implied.'],
 ['Dryer exhaust','Trace accessible duct and termination for crushing, disconnection, lint and blocked damper. Identify fuel and follow model requirements.','Fire risk applies to gas and electric dryers; combustion/CO concerns apply to fuel-burning equipment. Unseen duct runs remain unverified.']],7343,'S33-DRYER'),
 topic('interior_life_safety','Rooms and alarms: function, placement and evidence',[
 ['Lighting / storage','Record exposed hot lamps near storage, damaged fixtures and unprotected connections. Match closet and wet-area fixtures to their listing and location.','Historical Code Check dimensions need edition/application context. A working lamp does not establish safe clearances.'],
 ['Fans / stairs','Distinguish a moving fan attachment from blade wobble. Record stair headroom, continuity, handrails and guards from safe access.','Stop operating unstable equipment; do not catch a falling fan. Building age does not make an observable fall hazard disappear.'],
 ['GFCI / controls','Identify the protection and reset location; test by an appropriate method where safe and restore the affected controls.','A plain receptacle can have upstream protection. A successful receptacle test does not prove concealed wiring or every protective function.'],
 ['Smoke / CO','Record presence, location, type, power and readable manufacture/replacement date; distinguish these two alarm functions.','MD requires presence/absence reporting. A test-button response, where tested, is not a calibrated sensitivity or full-system certification.'],
 ['Alarm placement','Compare actual installation with the model instructions and applicable rules; note missing or obstructed protection and follow-up.','Do not turn the instructor\'s approximate one-foot corner/peak advice into a universal mounting rule.'],
 ['Existing-building duty','Review applicable smoke-alarm upgrades independently from the original building-code era. See APP-H for Maryland milestones.','Original construction, later work, occupancy and existing power configuration matter; do not replace required hardwired protection with battery-only devices.']],9148,'S33-MD','S33-ALARM','S33-MD-ALARM')]
TERMS=[
 ('Anti-tip device','Range restraint','A product-specific restraint intended to reduce range tip-over risk; seeing a bracket is different from verifying engagement.','kitchen_appliances'),
 ('High loop / dishwasher air gap','Different drainage arrangements','An elevated hose route and a physical air separation are different arrangements; use the actual appliance instructions and jurisdiction.','kitchen_waste'),
 ('Recirculating / exterior exhaust','Different hood configurations','A recirculating hood returns air indoors through its intended filter path; exterior exhaust conveys it outdoors.','kitchen_appliances'),
 ('Hydromassage tub','Indoor jetted bathing fixture','A bathing fixture with a circulation pump; operating conditions, electrical protection, bonding and agreed scope remain separate checks.','bath_laundry'),
 ('Water-hammer arrester','Transient pressure control','A device that cushions rapid flow-stoppage pressure changes; it does not perform the same job as thermal-expansion control.','bath_laundry'),
 ('Smoke alarm / CO alarm','Different life-safety functions','Smoke sensing and carbon-monoxide sensing address different hazards; one function does not establish the other.','interior_life_safety'),
 ('Functional flow / functional drainage','Supply response / waste response','Record supply under stated simultaneous use separately from the fixture\'s ability to drain without backup; neither proves every concealed pipe.','plumbing_fixture_checks')]
COMPACT=[dict(id='appliances',title='23  Kitchen, bath and laundry checks',route='Identify > safe operation > observe > return below',topics=['kitchen_appliances','kitchen_waste','bath_laundry'],rows=[
 ['Cooking / power','Record model, ordinary response and controls restored. Seek safe evidence of required range restraint.','No deliberate overload, breaker upsizing, self-clean cycle or improvised tip test.'],
 ['Basin / disposal','Observe visible joints before, during and after supervised fill/drain. Check accessible waste and electrical connections.','Do not load to overflow, reach into a disposal or infer an old stain is active leakage.'],
 ['Dishwasher','Observe primary-function cycle and accessible drainage; record stage reached, connection and loop/air-gap evidence.','Do not assume a hidden factory loop or leave a running unit unattended. Match model and local rule.'],
 ['Bath / return below','Separate hot/cold, flow, drainage and leakage. Return below fixtures after safe operation.','Visible tile or a dry short test does not verify concealed waterproofing.'],
 ['Laundry / exhaust','Check accessible hoses, duct, termination and lint. Arrester and expansion control are different devices.','Braided hose is not permanent. Both dryer fuels carry lint/fire risk; CO is a combustion concern.'],
 ['Scope / evidence','Name included appliances, safe test method, response and unresolved access. Photograph model and observed defect.','Refrigerator ice or an operating motor does not prove complete performance.']],discuss='Which observed response answers the question, and where must we return after operation?',note='S33 review [N10]. Maryland scope, source limits and product references: APP-D/E. Full procedures: L1. These are inspection cues, not repair instructions.',figure=None),
 dict(id='life_safety',title='24  Rooms, alarms and the exit route',route='Locate > identify protection > record response and limits',topics=['interior_life_safety'],rows=[
 ['Lamps / storage','Look for hot exposed lamps, combustible storage and damaged fixtures.','Closet and wet-area listing/clearances depend on actual fixture and governing requirements.'],
 ['Fan / stair route','Record insecure support, headroom, handrails, guards and impaired escape.','Do not operate unstable equipment or load-test suspect guards.'],
 ['GFCI / controls','Record protection, response, reset location and restored state.','Upstream protection can serve an outlet without buttons; operation does not certify hidden wiring.'],
 ['Smoke / CO','Record the two functions separately: location, visible type, power and date.','A button test is not a calibrated sensitivity test. Missing protection needs a defined action.'],
 ['Placement / age','Match alarm instructions and replacement information. Consider the whole sleeping/escape route.','An approximate course corner/peak dimension is not a universal installation rule.'],
 ['Maryland overlay','Check existing-occupancy smoke-alarm obligations as well as original construction era.','APP-H records the statutory milestones; occupancy and later work can change applicability.']],discuss='Would an occupant recognize the warning and have a usable way out?',note='Safety emphasis is not a defect score. Blue crab = Maryland-specific detail. S33 [N10]; APP-H local timeline; APP-D definitions.',figure=None)]
CORRECTIONS=[
 ['Maximum-load cooking test','Use ordinary controls and model instructions; no intentional overload challenge or blanket watts/volts breaker selection.','S33 00:41:08-00:44:20 / 01:14:30-01:16:10'],
 ['Dishwasher factory loop','Verify accessible arrangement and product documentation; a hidden loop is not assumed or universally equivalent to an air gap.','S33 00:35:44-00:37:21 / 01:32:38-01:34:26'],
 ['Braided washer hoses','Braiding does not mean burst-proof or lifetime service. Record visible deterioration and follow product replacement instructions.','S33 00:38:05-00:39:30'],
 ['Alarm mounting / bonding','Use actual instructions for alarms; an unseen bond end remains unverified. Do not adopt blanket one-foot spacing or assume bond continuity.','S33 02:30:05-02:35:55'],
 ['Appliance / fixture shortcuts','No hot-water finger test, frozen-food performance proof, assumed ice production or claim that a dry short test proves no leak.','S33 kitchen and bath demonstrations'],
 ['Dryer fuel distinction','Lint/fire concerns apply to both fuels. CO is not a normal product of electric resistance drying.','S33 02:37:06-02:37:55']]
def apply(d,compact,apps,walk):
    where=next(i for i,p in enumerate(d['pages']) if p['id']=='reporting')
    d['pages'][where:where]=copy.deepcopy(NEW)
    topics={p['id']:p for p in d['pages']}
    for tid,text,t in [
     ('plumbing_fixture_checks','S33 FIELD SEQUENCE: observe accessible joints before use; test hot and cold separately; use a modest supervised fill/drain where safe; recheck cabinet and the accessible level below. Retain stains, present wetness and reported repair history as different evidence.',7343),
     ('electric_devices','S33 CONTEXT: a receptacle without buttons can be protected upstream. Record reset location and restore safely. Closet storage, tub/shower fixture listings and insecure fan support need their own observations; successful operation does not establish safe installation.',0),
     ('backflow_dwv','S33 QUALIFICATION: do not assume a concealed factory dishwasher loop. Identify the accessible drain route and match the actual model instructions and local requirement.',2144)]:
        topics[tid]['blocks'].append(dict(kind='text',text=text));topics[tid]['refs']+=refs(t)
    compact.extend(copy.deepcopy(COMPACT))
    for p in compact:
        if p['id']=='dwv':p['rows'][0][1]='Observe joints before, during and after a supervised fixture test; separate hot/cold, supply response, drainage and leakage. Return below after operation.'
    for term,exp,definition,tid in TERMS:
        if term=='Functional flow / functional drainage':merge_term(apps,'Functional flow / drainage','S33: '+definition,tid,topics[tid]['title']+' / S33 review',topics[tid]['refs']);continue
        apps['APP-D']['terms'].append(dict(term=term,expansion=exp,definition=definition,topic=tid,source_pointer=topics[tid]['title']+' / S33 review',source_refs=topics[tid]['refs']))
    apps['APP-D']['notes'].append(['N10','Final interior / appliance review','S33 demonstrations were reviewed with their limits. Inspection uses safe normal controls and visible evidence; no deliberate overload, assumed concealed bond/loop, universal alarm offset or watertightness warranty.'])
    apps['APP-E']['external_references'] +=[dict(id=a,title=b,url=c,note=e,reviewed_on='2026-09-21') for a,b,c,e in REFS]
    for name,note,tid in [
     ('Kitchen primary-function record','Record actual appliance, model/fuel, operating stage, observed response, omission reason and restored controls.','kitchen_appliances'),
     ('Range restraint evidence','State visible device/engagement evidence and safe access limit; do not create a tipping demonstration.','kitchen_appliances'),
     ('Dishwasher route and return check','Identify accessible drain arrangement; record cycle stage, leakage and post-operation return below.','kitchen_waste'),
     ('Bath and laundry relationships','Keep flow, drainage, leakage, hose condition, dryer termination and hidden-access limitations separate.','bath_laundry'),
     ('Smoke / CO and lighting','Record separate alarm functions and presence, dates/power where visible, relevant placement concern and follow-up; note storage or fixture hazards.','interior_life_safety')]:
        n=len(apps['APP-C']['items'])+1;apps['APP-C']['items'].append(dict(id=f'M{n:04}',added='2026-09-21',mention=name,note=note,source='S33 / '+tid,links=[dict(label='SG-010-L1 topic',url='../../SG-010-L1/STUDY GUIDE.html#'+tid)],status='Prompt; requires actual property evidence',checklist_status='Not a property finding'))
    for id,name,purpose,limit in [('T027','Sink stoppers / microwave-safe test vessel','A modest supervised drainage observation and scoped microwave primary-function check.','No overflow loading, use of occupant dishes, hot-water contact or unattended filling.')]:
        apps['APP-A']['items'].append(dict(id=id,name=name,added='2026-09-21',level='Scope-dependent',purpose=purpose,limit=limit,basis='S33 / N10',pre_use_check='Clean, intact and suitable for fixture or microwave; observe model instructions.',availability='Not recorded',training='Not recorded',last_revision='1.8'))
    apps['APP-F']['modules'].append(['Kitchen / bath / laundry','T001 / T002 / T019 / T022 / T027; R004','Add for installed systems in every era. Use safe normal controls and accessible evidence; record appliance replacement separately from original building age.'])
    apps['APP-H']['sections'].append(['Smoke alarms: age is not the whole rule',['Milestone / evidence','Field implication'],[
     ['Before July 1975 / 1975-1990 / from July 1990','Maryland 9-104 distinguishes permitted power arrangements and adds battery backup for the later group. Retain existing required AC protection; read the complete law for the occupancy.'],
     ['2013 changes / January 2018 upgrade deadline','Existing homes can have alarm obligations independent of their original building-code edition. Original year is a lookup cue, not a compliance decision.'],
     ['Current inspection','Record location, visible date and power; match installation instructions and the authority for the actual address. Separate smoke from CO.']]])
    apps['APP-H']['references'].append(dict(id='H21',title='Maryland Public Safety 9-104 / smoke alarms',url=REFS[3][2],note='Checked 21 September 2026; age and power-source provisions require full occupancy context.'))
    apps['APP-G']['pages'].append(dict(id='S33_course_qualifications',title='S33: useful demonstrations and necessary qualifications',blocks=[dict(kind='table',headers=['Course topic','Retained field qualification','Recording locator'],rows=CORRECTIONS,widths=[105,290,109])],refs=refs(2468)))
    room=next(p for p in walk if p['id']=='rooms');room['refs']+=['appliances','life_safety']
    room['note']='Observe appliance stages while present; return below wet fixtures after operation. Record alarm functions, dates/power where visible and access limits. Restore water, heat and electrical controls before leaving.'
