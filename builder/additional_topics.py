"""Screen-supported distinctions not safely recoverable from speech alone."""
def make(id,title,sid,seconds,rows):
 return dict(id=id,title=title,blocks=[dict(kind='table',headers=['Component / observation','Meaning / inspection response'],rows=rows)],refs=[dict(source=sid,seconds=seconds,label='Reviewed course screen sequence')])
INSERTIONS=[('water_supply',[
 make('chimney_parts','Chimneys: separate the enclosure, flue and weather protection','S18',4617.733,[
  ['Chase / flue / crown / rain cap','The chase encloses the passage; the flue carries combustion products. The crown/chase cover sheds water from the top; a rain cap covers the flue opening. Do not use one label for all four.'],
  ['Movement and support','Record leaning, separation, missing masonry and changes below a retained roof portion. Do not push or lean on a suspect chimney to test stability.'],
  ['Interior evidence','Record visible liner material and condition, open joints, deposits and limitations. An exterior view does not establish an intact liner or safe concealed clearances.'],
  ['Unlined or obscured flue','The course calls for specialist evaluation of unlined construction and cleaning/evaluation where deposits obscure the interior. Do not infer suitability from age.'],
  ['Height / fuel / vent type','The course gives a 3-foot/2-foot/10-foot chimney example. It is not a universal rule for every gas, oil or condensing vent. Match the connected appliance, listing and applicable local provision.']]),
 make('roof_drainage','Roof drainage: follow discharge beyond the downspout','S18',6313.3,[
  ['Gutters and supports','Record loose or damaged sections, visible ponding, blockage, joint leakage and overflow evidence. Use safe access; do not rely on gutter attachment for support.'],
  ['Downspouts and leaders','Trace accessible joints and outlets. A pipe entering the ground does not prove a functional drain, its destination or an approved sewer connection.'],
  ['Drywell / cistern','A drywell disperses runoff into surrounding ground; a cistern stores water. Neither label proves adequate capacity, water quality or current operation.'],
  ['Internal drains / scuppers','Look for blocked outlets, deteriorated seams and water-backup evidence. Identify visible primary/overflow arrangements without certifying concealed capacity.'],
  ['Report','State discharge location, nearby grade/foundation conditions, damage and concealed drainage limits. Seek appropriate evaluation where the route or performance remains unresolved.']])]),
 ('water_heater_identity',[
 make('plumbing_fixture_checks','Fixtures: record functional flow, drainage and leakage separately','S20',2768.067,[
  ['Before operation','Observe loose fixtures, visible leaks and drain connections first. Use normal controls within scope; rapid emptying does not prove that waste reached a proper disposal system.'],
  ['Supply response','Record pressure/flow symptoms while tested fixtures operate. A static gauge reading does not establish adequate functional flow throughout the house.'],
  ['Fixture condition','Identify damage, loose support, leaking controls, failed seals and visible connection defects. Record hot/cold response and safe test limitations without changing concealed temperature controls.'],
  ['Drainage response','Record slow drainage, backup, gurgling and visible leaks. A symptom suggests investigation; it does not locate a concealed blockage by itself.'],
  ['Private disposal','Visible components and owner statements do not constitute a septic-system evaluation. State whether a separately scoped inspection/record review is needed.']]),
 make('dwv_traps_vents','DWV: distinguish trap seals, venting and backflow protection','S20',6121.667,[
  ['Trap seal','A trap retains water to resist sewer-gas entry. Identify visible missing, leaking or improper arrangements; a trap is not a potable-water backflow device.'],
  ['S-trap / P-trap','Describe the actual configuration and vent connection. Changing the trap shape alone does not resolve every venting problem.'],
  ['Air-admittance valve','A device admitting air under appropriate conditions differs from an open vent, spring mechanical vent and backwater valve. Acceptance, access and installation depend on the product and applicable requirements.'],
  ['Wet vent','A permitted arrangement can serve drainage and venting functions. A pipe carrying both does not establish compliance with sizing/layout conditions.'],
  ['Visible pipe and terminals','Record support, damage, leaks, accessible slope concerns and improper open terminations. An attic vent opening or sewer odor needs investigation; avoid unsupported cause attribution.']]),
 make('drainage_pumps','Drainage pumps: identify the liquid and discharge route','S20',11474.1,[
  ['Groundwater sump','A sump pump commonly removes groundwater from a collection pit. Observe the cover, power, controls, discharge route and accessible condition.'],
  ['Wastewater / sewage ejector','Wastewater below the gravity sewer level may require a suitable pump. Sewage from a toilet is not ordinary sump groundwater; identify the basin and intended service.'],
  ['Discharge destination','Do not adopt the course statement that a sanitary pump may discharge to a drywell as general permission. Disposal depends on wastewater type, approved system and local requirements.'],
  ['Safe operation','Use normal controls or a suitable manufacturer-approved method only within scope. Do not reach into energized pits, force floats or flood a basin to improvise a test.'],
  ['Report / limitation','State whether tested, observed response, discharge evidence and access limits. A running motor does not prove actual discharge, backup protection or concealed line condition.']])])]
def insert(data):
 for before,pages in INSERTIONS:
  at=next(i for i,p in enumerate(data['pages']) if p['id']==before)
  data['pages'][at:at]=pages
 return data
