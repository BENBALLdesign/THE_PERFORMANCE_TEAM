from editorial import page,PAGES
REFERENCES=[
 ('MD','Maryland minimum standards of practice','https://www.dllr.state.md.us/license/reahi/reahisop.shtml','Scope, exclusions, CSST and alternative-energy reporting; reviewed September 19, 2026.'),
 ('CPSC','CPSC: Repairing Aluminum Wiring','https://www.cpsc.gov/s3fs-public/AL_0.pdf','Publication 516; distinguish connection overheating evidence and qualified permanent repairs.'),
 ('DOOR','Chamberlain: Safety reversal test','https://support.chamberlaingroup.com/s/article/How-do-I-test-the-Safety-Reversal-System-1484145519301','Model instructions control the obstruction-reversal test.'),
 ('WATTS','Watts 210-5 installation instructions','https://www.watts.com/dfsmedia/0533dbba17714b1ab581ab07a4cbb521/11902-source/1910217-pdf.pdf','Separate pressure protection remains necessary; no valve between relief valve and heater.'),
 ('WATTS-STATUS','Watts 210-5 product record','https://www.watts.com/products/plumbing-flow-control-solutions/water-heater-accessories/shutoff-valves/210-5','Manufacturer identifies this existing-equipment example as discontinued.'),
 ('AGE','Bradford White serial date-code reference','https://www.bradfordwhite.com/bw-faq/how-to-read-the-serial-number-date-code-reference-chart/','Manufacturer-specific year/month coding; distinguish manufacture from installation.'),
 ('AFUE','DOE: Furnace and boiler efficiency','https://www.energy.gov/sites/default/files/2013/11/f5/hvac_guide.pdf','AFUE measures useful annual heat relative to fuel energy, not the fraction of fuel chemically burned.'),
 ('TC','Fluke: Thermocouple fundamentals','https://www.fluke.com/en-us/learn/blog/calibration/thermocouple-app-notes-series-part-1','Thermoelectric voltage from dissimilar conductors and a temperature difference.'),
 ('OIL','Beckett burner manual: startup safety','https://www.beckettcorp.com/wp-content/uploads/2022/05/6104-Burner_Manual_092120.pdf','Do not start with accumulated oil, vapor-filled appliance or very hot chamber; qualified service boundary.')]
REFMAP={'garage_doors':['DOOR'],'gas_piping':['MD'],'electric_legacy':['CPSC','MD'],'electric_alternative':['MD'],'heating_controls':['MD'],'furnace_types':['AFUE'],'furnace_safety':['TC','MD'],'oil_burners':['OIL','MD'],'water_heater_relief':['WATTS','WATTS-STATUS'],'water_heater_identity':['AGE'],'roof_forms':['MD']}
TOOLS_A=[
 ('Receptacle/GFCI tester','Evaluate accessible receptacle indications and appropriate GFCI response.','Does not prove all wiring is safe, detect every bootleg ground or replace device instructions.','S24 electrical scope; S25 protection; S27 receptacles'),
 ('Noncontact voltage indicator','Recognize possible energized wiring from a safe position.','A negative result does not establish absence of voltage. Keep hands and samples outside energized equipment.','S26 22:11–24:30'),
 ('Water-pressure gauge','Record pressure at an appropriate accessible connection where included in scope.','One reading is not a complete hydraulic diagnosis; do not operate shutoffs merely to attach it.','S18 2:28:34; S22 13:37'),
 ('Suitable temperature instrument','Record accessible water or air temperature with location, mode and units.','A spot reading does not certify scald protection, combustion safety or system capacity.','S24 mixing valves; S28 heating'),
 ('CO instrument suited to the intended test','Support separately defined CO measurements when trained and equipped.','A combustible-gas detector is not a CO analyzer. Follow instrument limits and calibration; do not use it to certify a heat exchanger.','S28 1:13:20; reviewed correction'),
 ('Combustible-gas detector','Investigate an accessible indication within instrument and training limits.','Not a substitute for CO testing, a leak-tightness test, utility emergency response or qualified repair.','S28 1:13:36; reviewed correction'),
 ('Labeled de-energized wire samples','Learn AWG conductor sizes away from energized equipment.','Do not insert the sample set into a panel; material/application/markings matter.','S24 2:41:03; S25 28:14')]
TOOLS_B=[
 ('Equipment identification and serial-date references','Retain model, serial, label photo, manufacturer lookup and stated installation date.','Do not use a standards edition or a generic first-two-digits shortcut as proof of equipment age.','S21 00:22–17:35'),
 ('Electrical product and repair references','Keep panel/terminal listings and the CPSC aluminum-wiring guidance with the source date.','A connector color or anecdote is not proof of a listed, complete repair.','S25 labels; S26 aluminum wiring'),
 ('Fuel and heating service records','Collect available tank, burner, venting and maintenance records with attribution.','Records do not replace visible inspection or certify concealed tank integrity.','S29 oil heat and gravity furnaces')]
MENTIONS=[
 ('Garage/dwelling separation openings','Location of holes, penetrations, altered access or damaged finish and areas not visible.','S15'),
 ('Garage passage door','Observed construction/label, closing and latching response, weather stripping and alterations; applicable follow-up.','S15'),
 ('Vehicle door mechanism and safety response','Condition before operation; beam/contact test method and response or specific reason not tested.','S15–S16'),
 ('Garage appliance exposure','Ignition source, vehicle impact protection, visible leak protection and relevant local qualification.','S15'),
 ('Roof inspection method and covering','Material and each observed plane; method of access and obscured or unsafe areas.','S17; COMAR .06'),
 ('Roof water-entry evidence','Precise flashing, boot, valley, scupper or chimney condition; observed staining and uncertainty about active leakage.','S17–S18'),
 ('Main plumbing controls and cleanouts','Accessible main water, hose-bibb and fuel shutoff locations; waste cleanout access.','S19–S24; COMAR .07'),
 ('Supply and drain materials and condition','Visible materials, active leakage/mineral evidence, support, damaged joints and inaccessible routing.','S19–S20'),
 ('Functional flow and drainage','Fixture tested, simultaneous flow conditions, observed drainage, nonoperation and reason for limitations.','S20; COMAR .07'),
 ('Cross-connection protection','Visible air gap/backflow arrangement, hose-bibb protection and precise observed concern; no unsupported function guarantee.','S20'),
 ('Water-heater identity and age basis','Model, serial, fuel, capacity and manufacture-date source; distinguish installation date and uncertain decoding.','S21'),
 ('Water-heater relief and discharge','Valve identification, missing/reduced/capped/trapped piping, route and termination; recommend correction of observed hazards.','S20–S24'),
 ('Pan, thermal expansion and condensate','Separate each pipe/device and its observed support, discharge destination, leakage and limitations.','S21–S24'),
 ('Water-heater vent and combustion-air concerns','Damaged hood, loose joints, inappropriate clearance, blocked openings or termination concerns as observed.','S21–S24'),
 ('Visible fuel-gas defects and CSST','Product identification, unused outlet cap, shutoff and damage; record CSST and required Maryland bonding-review recommendation.','S23–S24; COMAR .07/.08'),
 ('Electrical service description','Amperage/voltage basis, service and main-disconnect locations, visible conductor/equipment concerns and uncertainty.','S24–S25; COMAR .08'),
 ('Panel limitations and visible connections','Restricted/unsafe access, label information, visible damaged connections and conductor/protection concerns.','S24–S26'),
 ('Solid aluminum branch wiring','Observed presence/location and qualified-electrician recommendation; do not equate all aluminum conductors with the historic hazard.','S26; COMAR .08'),
 ('Older wiring and physical damage','Knob-and-tube, deteriorated covering, suspect splices, missing protection and access limitations.','S26–S27'),
 ('Device protection and alarms','Observed GFCI/AFCI response and limitations; smoke/CO alarm presence or absence, distinct from a system certification.','S25–S27; COMAR .08'),
 ('Alternative energy and disconnects','Presence of solar/generator/other alternative energy and visible disconnect locations; limits of specialist testing.','S24–S25; COMAR .08'),
 ('Heating equipment and normal-control response','System/energy/distribution type, modes tested, startup/shutdown observations, original control settings restored and limitations.','S28–S29; COMAR .09'),
 ('Heating combustion and venting concern','Scorching, soot, rollout, damaged vents or suspected exhaust leakage; qualified follow-up without a fabricated cause.','S28–S29'),
 ('Accessible oil storage and supply','Tank/support condition, stains, fill/vent evidence, damaged supply tube and concealed areas.','S29'),
 ('Possible underground tank or suspect insulation','Describe clues and specialist recommendation; no claim of confirmed buried condition, contamination or asbestos solely from appearance.','S29'),
 ('Sealed firebox and safety lockout','Record sealed/inaccessible chamber or nonresponsive/locked-out burner, reason not disturbed, and service recommendation.','S29')]
NUMBERS=[
 ('6 in','Garage photoeyes','COURSE','S15','Maximum-height example; verify opener instructions.'),
 ('18 in','Garage ignition source','COURSE','S15','Elevation example; product/FVIR and local conditions matter.'),
 ('1/2 in; 5/8 in Type X','Garage gypsum','COURSE','S15','Wall/ceiling and habitable-space conditions differ; not an assembly certification.'),
 ('1-3/8 in; 20 min','Garage passage door','COURSE','S15','Material/thickness or rating alternatives need exact applicable rule.'),
 ('4:12','Roof slope','COURSE','S17','4 inches rise per 12 inches horizontal run.'),
 ('30 in','Chimney cricket trigger','COURSE','S18','Width/configuration-dependent example; confirm applicable rule.'),
 ('M/red; L/blue; K/green','Copper tubing','COURSE','S20','Increasing wall thickness; verify marking and application.'),
 ('150 psi; 210°F','T&P relief example','COURSE','S21','Read actual valve rating; not normal operating pressure or safe tap temperature.'),
 ('6 in versus 24 in','Relief discharge termination','COURSE','S22','Lecture contrasts codes; no universal rule is issued here.'),
 ('3/4 in','Relief discharge example','COURSE','S23','Do not reduce below the required valve outlet/discharge capacity; verify exact product.'),
 ('1,000 ft³','Heat-pump water-heater room','COURSE','S24','One manufacturer example; current product may have different ducting/air-volume rules.'),
 ('No. 14 / 15 A; No. 12 / 20 A; No. 10 / 30 A','Copper branch examples','COURSE','S24–S25','Not a complete ampacity/design table; material, temperature and load exceptions matter.'),
 ('55 times','Historic aluminum-wiring finding','NOTE','S26','CPSC comparison concerns connections reaching fire-hazard conditions, not houses burning; not 550%.'),
 ('6 ft / 12 ft','General wall receptacle spacing','COURSE','S27','Qualifying wall-space rule; not a universal countertop or bathroom rule.'),
 ('50 ft³ per 1,000 Btu/h','Combustion-air volume method','COURSE','S28','Conditional method using total appliance input and applicable air-source/infiltration assumptions.'),
 ('40,000 Btu/h → 2,000 ft³','Combustion-air calculation','NOTE','S28','40 × 50; 200 ft² only at a 10-ft ceiling.'),
 ('150,000 Btu/h → 7,500 ft³','Combined input calculation','NOTE','S28','750 ft² at 10-ft ceiling; 750/1,200 = 62.5%, correcting the spoken three-quarters claim.'),
 ('1/4 in per ft','Natural-draft connector rise','COURSE','S28–S29','Keep appliance/vent context; not a universal condensing-vent slope.'),
 ('660 gal','Indoor oil tank example','COURSE','S29','Not verified as current local permitted storage; use applicable requirements.'),
 ('18 in','Boiler relief termination example','COURSE','S29','Different lecture context from water heater; do not generalize without product/local confirmation.')]

def augment():
 for p in PAGES:
  for rid in REFMAP.get(p['id'],[]):
   x=next(x for x in REFERENCES if x[0]==rid);p['refs'].append(dict(source=rid,label=x[1],url=x[2]))
 return PAGES
