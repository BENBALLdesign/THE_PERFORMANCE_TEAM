"""S38 review: retain system relationships, qualify lecture shortcuts."""
from prepare import *

BOILER='https://www.weil-mclain.com/wp-content/uploads/EG-Series-7-Boiler-Manual-0425.pdf'

def refs(t):return [dict(source='S38',seconds=t,label='Hydronic, steam, electric heating and cooling lessons')]
def topic(id,title,rows,t):
    return dict(id=id,title=title,section='Heating, cooling and distribution',blocks=[dict(kind='table',headers=['Identify / follow','Evidence to record','Interpretation / limit'],rows=rows,widths=[106,216,182])],refs=refs(t))

NEW=[topic('hydronic_systems','Hydronic heat: follow water, controls and delivery',[
    ['Identify the loop','Record boiler or combination appliance, fuel, visible rating, expansion arrangement, circulators and distribution.','A boiler is not interchangeable with an ordinary water heater. Trace connections; an absent visible pump does not prove steam.'],
    ['Pressure / expansion','Record indicated pressure/temperature, leakage, corrosion and visible expansion/relief components.','Use the actual system and manufacturer data. A classroom pressure value or discharge height is not a universal installation rule.'],
    ['Zones / response','Match thermostat, visible zone valve or circulator, piping and served area. Observe a normal call for heat and allow response time.','Record untested zones and reasons. Avoid repeated cycling, control adjustment or opening hot/pressurized components.'],
    ['Radiant / concealed','Look for manifolds, accessible tubing, floor finish, leakage and compatible temperature-pattern evidence under known conditions.','Thermal mass delays response. An infrared pattern alone cannot prove loop layout, leakage or adequate heating after an arbitrary ten minutes.'],
    ['Hydro-air','Distinguish the water heating coil, refrigerant coil, blower and condensate route within the same air handler.','Nearby pipes can carry different fluids and serve different seasons. Preserve the complete water/air/energy relationship.'],
    ['Older material / referral','Record suspect pipe or boiler insulation from safe access; leave it undisturbed.','Color, age or a trade name cannot establish asbestos content. Relief discharge and pressure problems need qualified evaluation, not a generic tank-draining instruction.']],160),
    topic('steam_systems','Steam heat: water level, pressure and condensate return',[
    ['Recognize the system','Record boiler identity, gauge glass where present, pressure controls, low-water cutoff, safety valve and visible piping.','Use the actual appliance rating. The EG/PEG manufacturer example specifies a 15-psi steam safety valve; the lecture\'s blanket 30-psi steam value must not be generalized.'],
    ['Supply / return','Follow steam mains, radiator connections and accessible condensate return; distinguish one-pipe from two-pipe arrangements where visible.','Document pitch concerns, leakage and audible hammering. Sound alone does not locate the fault or establish a repair.'],
    ['Water level / protection','Observe gauge condition and indicated level without adding/draining water or forcing a safety control.','A Hartford Loop and low-water cutoff have different purposes. Visible piping is not proof that the cutoff or pressure controls function.'],
    ['Radiator / room','Observe accessible radiator, supply valve, vent or trap arrangement, support, leakage and response.','Hot surfaces and delayed response change the method. Do not open vents or use the inspection as a balancing/service operation.'],
    ['Visible installation','Compare accessible components to the actual manual when identifying a concern; describe missing identification or inaccessible sections.','One manufacturer diagram is not a universal near-boiler piping design. Refer with the observed symptom and specific unanswered question.']],7594),
    topic('electric_heat_delivery','Electric heat: resistance, heat pump and backup are different',[
    ['Resistance element','Identify baseboard, wall heater, radiant cable or air-handler heat strips from labels and visible configuration.','It converts electrical energy to heat locally. Operating cost and whole-system efficiency are different questions.'],
    ['Heat pump / backup','Record equipment identification, operating mode, thermostat indications and whether auxiliary heat is observed.','A large breaker, cabinet brand or warm outlet cannot alone identify a heat pump or prove all heating stages operate.'],
    ['Clearance / protection','Observe listed clearances, combustible storage, damage, support, guarding and accessible electrical connections.','Use the actual product instructions and circuit application. No universal 60-amp/#6-conductor or five-kilowatt-stage shortcut.'],
    ['Normal operation','Use ordinary controls within permitted conditions; record served areas, response, delay and restored settings.','Do not remove energized guards, force stages, bypass controls or certify capacity from a brief temperature observation.'],
    ['Cross-system connection','Follow electricity through the heater or compressor to the delivery medium and room.','COMBUSTION is this guide\'s electrical/energy route as well as fuel-burning equipment; the route label does not imply every source burns fuel.']],9866),
    topic('cooling_water_air','Cooling: connect refrigerant, airflow and condensate',[
    ['Refrigerant circuit','In cooling mode: compressor > outdoor heat rejection > metering device > indoor heat absorption > return vapor.','A heat pump reverses coil roles by mode. Line temperature, diameter or a frost pattern alone does not establish refrigerant charge.'],
    ['Airflow / observation','Record filters, accessible coil/blower condition, returns, supplies, test conditions and measured response where within scope.','A 15-20 degree split is not a universal pass/fail or capacity test. Icing can have more than one cause; do not adjust blower speed or refrigerant charge.'],
    ['Condensate route','Distinguish primary drain, overflow provision, auxiliary pan, pump and shutdown/alarm device where present. Trace accessible discharge.','Evaluate the permitted product/installation arrangement. Two visible wires do not establish a working interlock; do not defeat it or deliberately overflow the system.'],
    ['Electrical nameplate','Record equipment voltage/phase, minimum circuit ampacity, maximum permitted protective-device rating and accessible device identification.','Disconnect enclosure rating is not fuse size. Read labels safely; do not pull energized fuses merely to identify them or infer time-delay class from shape alone.'],
    ['Outdoor relationships','Observe support, level, line strain, coil obstruction, dryer lint, snow exposure and nearby vent/exhaust terminations.','Clearance and termination suitability depend on actual instructions. A furnace vent near the unit is not automatically acceptable because of assumed operating seasons.'],
    ['Duct / building','Record disconnected/crushed duct, failed jackets, unsuitable support, leakage evidence and contamination in accessible returns or below-slab ducts.','Do not sit on flex duct, stretch brittle jackets or assume a cavity return is universally permitted/prohibited. Product, assembly and adopted requirements govern.']],12547)]

QUALIFICATIONS=[
    ['Steam pressure / safety','Use the appliance rating and actual manufacturer instructions; distinguish safety valve, low-water cutoff and Hartford Loop.','S38 02:06:34 onward'],
    ['Hydronics / radiant response','No universal cold pressure, discharge height, ten-minute heat response, or visual asbestos clearance.','S38 hydronic and radiant lessons'],
    ['Cooling rating / measurement','Keep MCA, maximum protective-device rating and disconnect enclosure capacity separate; model decoding is manufacturer-specific.','S38 04:14:19 onward'],
    ['Fuse / live equipment','No energized fuse removal merely for reading; no appearance-only fuse-class identification or claim that 60.1 A instantly opens every 60 A fuse.','S38 04:25:23 onward'],
    ['Clearance / ducts / drains','Match product and governing requirements. No universal one-foot clearance, six-foot disconnect distance, R-8 requirement or blanket cavity-return prohibition.','S38 cooling and distribution demonstrations'],
    ['Efficiency / diagnosis','Temperature split, frost, a brand, cabinet color or one dirty coil does not establish capacity, charge, installed age or microbial health risk.','S38 cooling examples']]

def apply(d,compact,apps,walk):
    i=next(i for i,p in enumerate(d['pages']) if p['id']=='cooling_scope');d['pages'][i:i]=copy.deepcopy(NEW[:3])
    i=next(i for i,p in enumerate(d['pages']) if p['id']=='cooling_scope')+1;d['pages'][i:i]=copy.deepcopy(NEW[3:])
    topics={p['id']:p for p in d['pages']}
    topics['steam_systems']['refs'].append(dict(source='S38-BOILER',label='Weil-McLain EG Series 7 manual: manufacturer-specific steam example',url=BOILER))
    compact.append(dict(id='hydronic_electric',title='27  Hydronic, steam and electric heat',route='Energy > control > medium > delivery > return',topics=[p['id'] for p in NEW[:3]],rows=[
        ['Hot water','Boiler / expansion / pump or gravity / zones / radiators or radiant loop.','Record visible pressure, leakage and normal response; use actual appliance data.'],
        ['Steam','Boiler / level and pressure protection / steam supply / radiator / condensate return.','Safety valve, low-water cutoff and Hartford Loop serve different purposes. No blanket 30-psi steam rule.'],
        ['Hydro-air','Water heating coil + blower; refrigerant coil may share the cabinet.','Trace the correct fluid, control and condensate path.'],
        ['Electric resistance','Element / circuit / control / clearance / served room or air stream.','A breaker rating does not prove heater type or all-stage performance.'],
        ['Heat pump / backup','Identify model and mode; distinguish moved heat from auxiliary resistance heat.','Record conditions and limits; do not force controls or infer capacity from temperature alone.'],
        ['Close the loop','Return to leakage, condensate, pressure concerns and observed response; restore controls.','Refer a specific unanswered question. Leave suspect insulation and service adjustments to qualified work.']],discuss='Which medium delivers the heat, and where does its return or drainage path go?',note='S38 / N13. Manufacturer-specific numbers remain attached to the actual model; COMBUSTION includes the electrical/energy route.',figure=None))
    for p in compact:
        if p['id']=='cooling':
            p['topics']=list(dict.fromkeys(p.get('topics',[])+['cooling_water_air']))
            p['note']=p.get('note','')+' S38: read equipment limits separately from disconnect rating; trace overflow protection and returns. A temperature split alone is not a capacity or refrigerant-charge test.'
    for term,exp,definition,tid in [
        ('Hydro-air','Water coil plus forced air','A water heating circuit supplies a coil in an air handler; the blower distributes heat. Refrigeration and condensate paths may share the cabinet.','hydronic_systems'),
        ('Low-water cutoff','Boiler water-level protection','A protective control intended to stop firing when boiler water is below its safe level; visible presence does not prove operation.','steam_systems'),
        ('Hartford Loop','Steam-boiler return-piping arrangement','A near-boiler return connection associated with limiting loss of boiler water through a return leak; it does not replace the low-water cutoff.','steam_systems'),
        ('MCA / maximum protective rating','Minimum circuit ampacity / equipment protection limit','Separate nameplate values with different uses. Neither is the disconnect enclosure rating, and neither alone proves the installed circuit is suitable.','cooling_water_air'),
        ('Auxiliary condensate protection','Response to primary drainage failure','A permitted drain, pan, shutdown or alarm arrangement appropriate to the actual installation; presence alone does not prove function.','cooling_water_air')]:
        apps['APP-D']['terms'].append(dict(term=term,expansion=exp,definition=definition,topic=tid,source_pointer=topics[tid]['title'],source_refs=topics[tid]['refs']))
    apps['APP-D']['notes'].append(['N13','Heating and cooling identification','Follow the actual energy, fluid and air paths. Product limits and operating conditions stay with each number; a label, symptom or short operating check is not system certification.'])
    apps['APP-E']['external_references'].append(dict(id='S38-BOILER',title='Weil-McLain EG Series 7 boiler manual',url=BOILER,note='Manufacturer-specific example for steam pressure protection and piping; not a generic specification for other appliances.',reviewed_on='2026-09-21'))
    apps['APP-G']['pages'].append(dict(id='S38_course_qualifications',title='S38: system relationships and lecture qualifications',blocks=[dict(kind='table',headers=['Topic','Retained qualification','Locator'],rows=QUALIFICATIONS,widths=[106,287,111])],refs=refs(7594)))
    for title,note,tid in [('Hydronic / steam system trace','Record heat source, expansion or water-level protection, distribution, response and visible return; distinguish unseen function from absence.','hydronic_systems'),('Condensate failure route','Record primary discharge, overflow provision, pan/pump and affected space below; do not claim shutdown functionality without an appropriate observed test.','cooling_water_air')]:
        apps['APP-C']['items'].append(dict(id=f'M{len(apps["APP-C"]["items"])+1:04}',added='2026-09-21',mention=title,note=note,source='S38 / '+tid,links=[dict(label='SG-010-L1 topic',url='../../SG-010-L1/STUDY GUIDE.html#'+tid)],status='Prompt; requires actual property evidence',checklist_status='Not a property finding'))
    apps['APP-F']['modules'].append(['Hydronic / steam / electric heat','Existing flashlight, mirror, camera and scoped temperature tools; no specialist servicing kit.','Equipment type can differ from original building era. Observe labels, routes and response; suspect insulation, pressure and electrical exposure limit the method.'])
    coverage=read(OUT/'scope-coverage.json')
    for r in coverage['families']:
        if r['id']=='D1-T7':r['topic_ids']+=['hydronic_systems','steam_systems','electric_heat_delivery'];r['status']='S38 full speech review incorporated; publication QA pending'
        if r['id'] in ['D1-T6','D1-T9']:r['topic_ids']+=['cooling_water_air'];r['status']='S38 full speech review incorporated; publication QA pending'
    save(OUT/'scope-coverage.json',coverage);apps['APP-B']['scope_coverage']=coverage['families']
