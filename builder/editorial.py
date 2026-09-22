"""SG-010 authored content. Times are seconds in the unchanged original recording."""
PAGES=[]
def page(id,title,source,start,rows,note='',figtime=None):
    PAGES.append(dict(id=id,title=title,section='SG-010',blocks=[dict(kind='table',title='Study and inspection distinctions',headers=['Topic','What to retain'],rows=rows)]+([dict(kind='text',text=note)] if note else []),refs=[dict(source=source,seconds=start,label='Course discussion')],figure_request=dict(source=source,seconds=figtime if figtime is not None else start)))

page('garage_separation','Garages: follow the separation from the dwelling','S15',551,[
 ['Assembly','Trace the wall and ceiling separating the garage from living space. Look for holes, unprotected penetrations, missing finish and attic access openings. A surface that resembles drywall does not establish the rating of a complete assembly.'],
 ['Doors','Record door construction or labels, closing and latching behavior, missing hardware, gaps and alterations such as pet doors. Verify the applicable door assembly requirements; a metal skin alone does not establish compliance.'],
 ['Conversions','A former exterior window or changed roofline can suggest an addition or converted carport. Describe that evidence and request records; do not declare the work unpermitted solely from its appearance.'],
 ['Report','Identify the opening, its location and the possible fire or exhaust pathway. Recommend correction by an appropriate qualified contractor, with concealed construction and access limits stated.']],
 'COURSE: gypsum thickness, door thickness/rating and self-closing requirements in the lecture are installation examples. LOCAL: confirm the adopted requirements and assembly before applying a number. Use “garage/dwelling separation” unless a fire-resistance-rated assembly is established.',1695)
page('garage_appliances','Garages: distinguish ignition, impact and leak protection','S15',1260,[
 ['Ignition','Recognize appliances exposed to flammable vapors. The course discusses an 18-inch ignition-source elevation and FVIR equipment; the installed product and local requirements control the actual arrangement.'],
 ['Impact','An appliance in a vehicle path may need impact protection. Record its position and observed protection; a short decorative post does not establish protective capacity.'],
 ['Water damage','A pan and a functioning drain serve different purposes from a relief-valve discharge. Trace each visible termination rather than assuming every small pipe is a drain.'],
 ['Restraint','Seismic strapping is a regional installation issue. Identify anchors and straps where visible and use the applicable local standard, not a blanket national requirement.']],
 'NOTE: vehicle exhaust and combustion-appliance exhaust can both be dangerous. The instructor’s comparison of their CO concentrations is not a safe exposure threshold or permission to operate with a disconnected vent.',1310)
page('garage_doors','Garage doors: inspect the mechanism before operating','S15',3090,[
 ['Counterbalance','Springs and cables support the door’s weight; the powered opener moves the balanced door. Observe damaged springs, loose cables, bent tracks, damaged panels and attachment/strut defects.'],
 ['Stop condition','A visibly damaged or unstable door needs a trained door systems technician. Do not operate a door with a broken spring or release a raised door to demonstrate the defect.'],
 ['Two safety functions','Photoelectric obstruction sensing and contact reversal are separate functions. A passed beam test does not establish that contact reversal works.'],
 ['Testing','Use the installed opener’s instructions and only test a door that can be operated safely. Do not substitute hands or body weight for the prescribed obstruction.'],
 ['Documentation','Record the device, test method, response, any skipped test and its reason. Keep children and others clear of the door path.']],
 'NOTE: Chamberlain’s published reversal test uses a board under the fully open door and calls for a trained technician if reversal fails. Follow the specific model’s instructions. The course’s hand-resistance shortcut is not adopted here.',3190)
page('roof_forms','Roof coverings: identify each plane and drainage route','S17',706,[
 ['Vocabulary','Distinguish gable, hip, shed, gambrel, mansard and butterfly forms. Identify ridge, valley, rake, eave and dormer rather than using “edge” for every location.'],
 ['Slope','A 4:12 slope rises 4 inches in 12 inches of horizontal run. Match covering and underlayment to the actual slope and product; do not infer suitability from appearance alone.'],
 ['Drainage','Butterfly roofs concentrate drainage at an internal low point. Low-slope upper mansard planes can behave differently from steep lower planes. Inspect each drainage route and outlet.'],
 ['Access','Choose a safe viewing method for steep, fragile or slippery roofs. Slate and other brittle coverings can be damaged by foot traffic. Record the method and unseen areas.'],
 ['Attachments','A patio cover attached only to fascia warrants attention to its load path. Describe visible attachment and recommend evaluation without certifying hidden structural capacity.']],figtime=980)
page('roof_cover_condition','Roof coverings: separate condition from age estimates','S17',1277,[
 ['History','Use installation records and owner information with attribution. Multiple layers, building age or a neighboring storm do not prove the installation date of the visible roof.'],
 ['Asphalt','Look for exposed substrate, cracking, curling, damaged tabs, misplaced fasteners and granule loss. Granules in gutters alone do not distinguish installation debris from accelerated wear.'],
 ['Starter and edges','Missing starter protection may leave deck or underlayment exposed through shingle slots. Check edges, drip details and gutter relationships together.'],
 ['Hail','Dents in metal and localized impact patterns can support further investigation. They do not, by themselves, prove the cause, event date or insurance coverage.'],
 ['Remaining life','Report visible condition and limitations. The lecture’s lifespan ranges are broad examples, not a warranty or a precise remaining-life calculation.']],figtime=1585)
page('roof_flashing','Flashing: follow water through overlaps and terminations','S18',20,[
 ['Wall intersection','Step flashing interleaves with individual shingles; counterflashing protects the upper edge. A kick-out at the lower end directs water away from the wall. Tile assemblies may use a different pan detail.'],
 ['Valleys','Identify open or closed construction before calling metal “missing.” Corroded reused flashing beneath a newer covering deserves evaluation. Sealant patches alone do not establish a durable repair.'],
 ['Chimney','Look upslope for diverted flow, debris traps and cricket/saddle details. The course’s 30-inch chimney-width trigger belongs to a particular rule and configuration; verify that scope.'],
 ['Parapet and scupper','Inspect outlets, seams, patches and adjacent staining. Correlate exterior evidence with accessible interior areas; a patch does not prove an active leak.']],figtime=830)
page('roof_penetrations','Roof penetrations: identify the device and its flashing','S18',1200,[
 ['Plumbing boot','Check the size and condition of the flexible collar, splits, water-shedding overlap and fasteners. Product labels such as “no-caulk” do not authorize arbitrary sealants or repairs.'],
 ['Different terminals','Distinguish plumbing vents, attic vents, exhaust outlets and concentric combustion terminals. Their termination and clearance requirements are not interchangeable.'],
 ['Chimney evidence','Cracked crowns, loose masonry and spalling deserve precise reporting. Exterior distress does not reveal the condition of an inaccessible flue interior.'],
 ['Solar penetrations','Even when specialist solar testing is outside the agreed service, visible roof penetrations, attachment concerns and water entry evidence remain relevant.']],
 'NOTE: do not turn a regional anecdote about flashing overlap into a universal geographic rule. Use the actual roof and flashing manufacturer’s instructions and the applicable assembly.',1600)
page('water_supply','Plumbing: identify the supply, controls and materials','S19',199,[
 ['Public or private','Record visible evidence and the stated source. A meter or pressure tank is a clue; explain uncertainty where the complete system cannot be traced.'],
 ['Well components','Recognize the well head, pressure switch, gauge, pressure tank, filter and shutoff. Observation does not establish well yield, water quality or potability.'],
 ['Leaks versus sweating','Cold well-water equipment may develop condensation. Check the distribution of moisture and visible fittings before diagnosing a leak or dismissing wetness.'],
 ['Access hazard','An unsecured well pit or opening is a fall hazard. Record it from a safe position; do not enter a pit or disturb an unstable cover.'],
 ['Controls','Identify the main shutoff and report it. A closed utility or supply valve is a limitation to resolve through the owner/qualified provider; the lecture’s “roll the dice” reactivation advice is not adopted.']],figtime=210)
page('plumbing_materials','Plumbing materials: read the marking and intended use','S20',74,[
 ['Separate applications','Service pipe, interior distribution, drain/waste/vent and relief discharge have different material requirements. Identify markings; PVC and CPVC are not interchangeable names.'],
 ['Copper','The lecture identifies M/red, L/blue and K/green markings, with increasing wall thickness M to L to K. Verify the actual marking and application.'],
 ['Corrosion','Dissimilar metal connections may corrode. Mineral deposits, active droplets and damaged fittings are stronger evidence of leakage than color alone. Do not infer the exact cause solely from a photograph.'],
 ['Dielectric connection','Thread tape seals threads; it is not a substitute for a listed dielectric connection. Some water-heater nipples provide integral separation; verify the installed product before calling a union missing.'],
 ['Valves and manifolds','Recognize gate, ball and globe valves and distribution manifolds. Explain their purpose without exercising neglected isolation valves as an experiment.']],figtime=335)
page('backflow_dwv','Backflow and drainage: keep the water paths distinct','S20',3300,[
 ['Potable protection','An air gap or appropriate backflow device protects the potable supply against a cross-connection. A hose-bibb vacuum breaker is not the same as a drainage backwater valve.'],
 ['Frost-resistant hose bibb','The valve seat is inside the protected area and the outer barrel must drain as designed. A connected hose, poor slope or exposed installation can defeat the intended protection.'],
 ['Dishwasher','Trace the drain connection, high loop or air-gap arrangement and connection relative to the trap. Verify the appliance instructions and local requirements rather than treating a high loop as universally equivalent to an air gap.'],
 ['Traps and condensate','An open waste connection or dry trap can allow sewer gas into the building. A condensate connection must preserve the required separation and trap protection; convenience does not establish suitability.'],
 ['Support and joints','Look for displaced joints, damaged piping and unsuitable supports. Identify the listed transition coupling and its application; a brand name alone does not establish approval.']],
 'COURSE: some S20 speech is obscured or garbled. Do not reconstruct numerical air-gap, support-spacing or drainage-slope requirements from those passages. Use the legible screen evidence and applicable reference.',3550)
page('water_heater_identity','Water heaters: record identity before interpreting condition','S21',22,[
 ['Data plate','Record manufacturer, model, serial, fuel, capacity and input rating. Distinguish rated input, recovery and tank capacity; none is interchangeable with the others.'],
 ['Date','Use a manufacturer-specific serial-number reference. The manufacture date is not the installation date. A standards edition printed on the label is not proof of a manufacture-year window.'],
 ['Fuel','Compare the appliance’s listed fuel with the installed supply. Do not assume any appliance can be converted between natural gas and propane; refer a mismatch for qualified evaluation.'],
 ['Clearances','Read the installed unit’s label, including conditions for closet/alcove installations and the closed door position. Vent-connector clearance is a separate measurement.'],
 ['Capacity and age','The lecture’s 40-gallon gas/50-gallon electric examples and 10–15-year life range are context, not a sizing assessment or replacement deadline.']],figtime=300)
page('water_heater_relief','Relief protection: distinguish temperature, pressure and drainage','S21',2097,[
 ['Purpose','A T&P relief valve protects against excessive temperature and pressure. The tank drain valve, pan drain and condensate drain perform different functions.'],
 ['Discharge','Look for missing, capped, reduced, trapped, uphill or damaged discharge piping and an unsafe or concealed termination. Use a suitable listed material and the applicable installation requirements.'],
 ['Rating','The lecture’s familiar example is 150 psi and 210°F. Read the installed valve rating; pressure settings and applications vary.'],
 ['Watts 210','A temperature-actuated gas shutoff does not itself provide pressure relief. The manufacturer’s installation instructions require separate pressure protection in the relevant arrangements.'],
 ['Action','Report observed defects and recommend qualified correction. Do not cap a leaking discharge, reset a safety shutoff to conceal its cause, or use an improvised test.']],
 'NOTE: Watts lists the 210-5 as discontinued. Retain this as recognition of existing equipment, not a recommendation to purchase it. The 6-inch discharge termination cited in the course is conditional; do not transfer it to every code, boiler or product.',3024)
page('water_heater_installation','Water heaters: inspect the whole installation','S22',601,[
 ['Draft path','Identify the draft hood, vent connector, listed double-wall vent and visible termination. Look for loose joints, corrosion, poor support, damaged hood and clearance concerns.'],
 ['Separate pipes','Trace relief discharge and pan drainage independently. A pan with an open, unconnected outlet provides little protection for nearby finishes.'],
 ['Gas and electrical','Distinguish the appliance shutoff from the gas control valve. Record absent shutoff, damaged connector, exposed or unsupported wiring and missing retention/protection without altering the equipment.'],
 ['FVIR','Recognize the combustion-air inlet and flame-arresting design. Blocked inlet screens warrant maintenance according to the specific product; FVIR does not make gasoline storage or vapor exposure safe.'],
 ['Expansion','A closed water system needs an appropriate means to accommodate thermal expansion. Check visible devices, support and leakage. A relief valve is not normal expansion control.']],
 'NOTE: do not infer that every regulator has identical check-valve behavior, that every expansion tank has the same orientation, or that a foam spacer proves adequate support. Verify the installed equipment.',1137)
page('water_heater_variants','Water-heating variants: identify the energy and circulation paths','S24',1635,[
 ['Tankless','Recognize demand-controlled heating, venting, electrical supply and relief protection. Replacement of a tank heater may change fuel demand; a qualified installer must verify sizing and listing.'],
 ['Heat pump','Heat transfers from surrounding air to water. Review the model’s ambient-temperature, air-volume/ducting, filter, condensate and clearance requirements; the lecture’s 1,000-cubic-foot example is not universal.'],
 ['Solar thermal','Identify storage, collector circulation and backup heating separately. A solar collector pump is not necessarily a domestic recirculation pump.'],
 ['Tempering','A mixing valve blends hot and cold water. Record observed delivery temperature where measured and limitations; do not change a neglected valve or treat 120°F as a no-scald guarantee.'],
 ['Recirculation','A continuously running loop can waste heat. Record controls and insulation as observed without promising the lecture’s claimed cost multiplier or reprogramming the system.']],figtime=2550)
page('gas_piping','Fuel gas: distinguish piping, connectors and bonding','S24',5048,[
 ['Identify','Read product markings and trace visible piping. CSST distribution tubing and a flexible appliance connector are different products with different installation rules.'],
 ['Shutoff and unused outlet','Identify appliance shutoffs and visibly uncapped unused outlets. A closed valve alone does not provide the same protection as a proper cap or plug.'],
 ['Bonding','Identify the CSST product and visible concerns. A clamp in one photograph does not prove continuity or compliance throughout a system. Manufacturer requirements differ among products.'],
 ['Sediment trap','Recognize the collection leg and gas-flow arrangement. Whether a trap is required and how it is installed depends on the appliance and applicable rule.'],
 ['Buried or concealed','Observe visible sleeve/vent arrangements without claiming hidden integrity. Do not uncover, pressure-test or repair a gas line during an ordinary visual inspection.']],
 'LOCAL: COMAR .07B(5) requires reporting CSST presence and recommending bonding review by a licensed master electrician; .08C separately addresses non-arc-resistant CSST. Identify the actual product. Do not use a hand to stop a gas leak or reactivate locked-off gas service; the lecture’s informal emergency description is not an inspection method.',5212)
page('electric_service','Electrical service: follow the supply and identify limits','S24',10363,[
 ['Overhead','Observe service drop, attachment, weatherhead, drip loops, exposed splices and deteriorated insulation from a safe distance. Never contact conductors to measure clearance.'],
 ['Underground','“Service lateral” identifies an underground supply. Concealed routing and conductor condition remain unknown unless separately established.'],
 ['Rating','Compare available evidence for service conductors, main overcurrent device and equipment rating. Record the basis and uncertainty; adding all branch-breaker numbers does not yield service size.'],
 ['Multiple panels','Distinguish a feeder-supplied panel from separate service equipment. Two panels are not automatically additive, and a breaker marked “main” does not alone establish the bonding location.'],
 ['Clearances','Retain voltage, pedestrian/vehicle use, roof slope and exception conditions with any clearance number. The recording’s garbled street-clearance passage is not a usable field rule.']],figtime=10447)
page('electric_panels','Panels: use labels and visual evidence without reaching inside','S25',244,[
 ['Before access','Check for unsafe conditions and restricted access. Arrange legitimate access to locked equipment; do not cut locks or encourage others to damage them to avoid a revisit.'],
 ['Observe','Read accessible labels, breaker ratings and visible conductor markings. Do not move wires, remove additional internal guards or put comparison samples inside energized equipment.'],
 ['Connections','Neutrals and equipment grounds have distinct termination requirements. Multiple equipment-grounding conductors are permitted only where the terminal listing allows the particular combination; do not transfer that permission to neutrals.'],
 ['Bonding','The service disconnect/bonding point and downstream panels have different neutral/ground arrangements. Identify the actual system, including upstream disconnects, rather than relying on a box’s familiar name.'],
 ['Protection','Identify AFCI, GFCI and dual-function devices by their labels. Button color alone is not a reliable identification across brands or generations.']],
 'NOTE: the instructor explicitly says the extra internal cover removed for demonstration is not normally removed during inspection. Preserve that boundary.',1575)
page('electric_conductors','Conductors: keep wire size, material and application together','S24',8707,[
 ['AWG','Within the ordinary AWG sequence, larger gauge numbers indicate smaller conductors. After No. 1, sizes include 1/0, 2/0, 3/0 and 4/0.'],
 ['Separate tables','Dwelling service/feeder allowances are conditional and are not a universal branch-circuit ampacity table. Material, insulation, terminals, temperature and application all matter.'],
 ['Course examples','The lecture pairs ordinary copper branch circuits with No. 14/15 A, No. 12/20 A and No. 10/30 A. These study examples do not resolve motor/HVAC exceptions or every installation.'],
 ['Samples','A labeled, de-energized wire sample set can help learn sizes away from equipment. Read markings where possible and report uncertainty; visual diameter comparison is approximate.'],
 ['Defect','An apparent conductor/protection mismatch warrants qualified evaluation. Do not describe a wire as melting immediately at a particular ampere value from the lecture.']],figtime=8730)
page('electric_multiwire','Multiwire circuits: understand the shared neutral','S26',133,[
 ['Principle','A multiwire branch circuit can share a neutral between ungrounded conductors on opposite legs of a single-phase system. It is a legitimate arrangement when correctly installed.'],
 ['Hazard','Same-leg connections can overload the shared neutral; an open neutral can create damaging voltages. Record visible concerns without disconnecting conductors to demonstrate them.'],
 ['Disconnect','Distinguish simultaneous manual disconnection from automatic common-trip operation. A suitable handle tie may serve particular arrangements; “always a common-trip 240 V breaker” is too broad.'],
 ['Split receptacle','Two feeds to a split receptacle require correct tab and circuit arrangements. A half-switched receptacle does not by itself prove that two separate branch circuits are present.'],
 ['Inspection','Recognize visible paired conductors and shared neutral arrangements. Full concealed circuit tracing and electrical diagnosis are separate from a normal visual inspection.']],figtime=294)
page('electric_wiring_methods','Wiring methods: identify cable, raceway and exposure','S26',386,[
 ['Terms','Distinguish SE, NM, UF, AC and MC cable from EMT, rigid, flexible metallic and nonmetallic raceways. Trade names do not replace the actual product identification.'],
 ['Connectors','Use the correct listed connector, bushing and grounding arrangement for the product and location. Do not assume every metal armor is an equipment-grounding conductor.'],
 ['Wet locations','A fitting intended only for dry locations is not established as suitable outdoors by appearance. Read markings; not every compression fitting is automatically wet-location rated.'],
 ['Physical protection','Observe damage and exposure at attic access routes, storage areas and basement framing. Protecting wiring does not authorize drilling engineered framing without its requirements.'],
 ['Identification','Color and bend radius can be clues, but markings and listing establish whether a raceway is electrical equipment; avoid a color-only diagnosis.']],figtime=515)
page('electric_legacy','Older wiring: describe the hazard without overstating the evidence','S26',1331,[
 ['Knob-and-tube','Recognize separate conductors on knobs and through tubes. Look for deterioration, unsafe splices, missing supports/protection and inappropriate surrounding insulation. A new panel does not prove all old wiring was replaced.'],
 ['Voltage indicator','A noncontact indicator can suggest energized wiring but cannot establish absence of voltage or make a wire safe to touch. Report limitations rather than guaranteeing an abandoned circuit.'],
 ['Aluminum','Distinguish older solid aluminum branch-circuit conductors from modern aluminum service/feeder conductors. Report the observed material and location.'],
 ['Repair','Refer older solid aluminum branch wiring to a qualified electrician. CPSC discusses replacement, COPALUM and AlumiConn repairs; connector color alone is not evidence of a complete permanent repair.']],
 'NOTE: the CPSC finding concerns connections reaching fire-hazard conditions, not a claim that 55 times as many houses burn down. “55 times” is also not “550 percent.” Do not repeat either distortion. Knob-and-tube originally had insulation; “cloth is not insulation” is an inaccurate generalization.',2325)
page('electric_devices','Devices: separate protection, location and operation','S27',75,[
 ['Bathroom','Record receptacles or switches at wet locations and the relevant protection. The course’s “immediately outside the tub plane is fine” statement is not a universal current clearance rule.'],
 ['Recessed lights','Identify insulation-contact and air-sealing characteristics from labels where accessible. A recessed shape alone does not establish that insulation may cover the fixture.'],
 ['Receptacle spacing','The course introduces the 6-foot/12-foot wall-space concept. Keep qualifying wall spaces and separate kitchen/countertop rules with the rule; do not apply it indiscriminately.'],
 ['Doorbell','A transformer separates line voltage from the lower-voltage circuit. Exposed line-voltage connections need enclosure. Recognizing a low-voltage device is not permission to touch its terminals.'],
 ['Scope and restoration','Test accessible devices to the applicable scope, explain limitations, and restore normal controls. Describe an observed response without claiming all concealed wiring is correct.']],figtime=1119)
page('electric_alternative','Alternative power: recognize additional energy sources','S25',65,[
 ['PV','Photovoltaic panels generate electricity; solar thermal collectors heat a fluid. Identify labels, visible disconnect locations and the system type.'],
 ['Generator','A transfer arrangement isolates sources and controls how loads are supplied. An ordinary inspection does not include improvised transfer testing or generator repair.'],
 ['Multiple supplies','A utility main switch does not establish that every component is de-energized where solar, storage or generator supplies are present.'],
 ['Scope','Visible roof/electrical defects remain relevant even if specialist performance testing is excluded. Record what was and was not inspected.']],
 'LOCAL: Maryland requires reporting the presence of alternative energy systems, including disconnect locations. The lecture’s general exclusion of solar and generators must not erase this reporting duty.',72)
page('heating_controls','Heating: operate through normal controls and record the response','S28',663,[
 ['Identify','Distinguish furnace, boiler, electric resistance and heat-pump systems by their equipment and distribution. Record energy source and the controls used.'],
 ['Thermostat','Photograph or record original mode, setpoint and fan state. Make only the normal operating adjustment needed for the test, then restore the original state; avoid altering schedules or accounts.'],
 ['Sequence','A demand for heat initiates a model-specific sequence. Observe startup, sustained operation and shutdown without defeating interlocks or adjusting service controls.'],
 ['Limitations','Record nonoperation, a shut-down appliance, inaccessible areas or a condition making operation unsafe. A temperature-only rule cannot establish that every furnace or heat pump is safe to run.'],
 ['Local scope','Maryland includes normal heating controls, including emergency/auxiliary modes when applicable. Inspection is not a certification of heat-system adequacy or balanced distribution.']],figtime=760)
page('combustion_air','Combustion air: preserve the configuration and units','S28',1660,[
 ['Principle','A fuel-burning appliance needs combustion air and an appropriate exhaust path. Enclosing equipment that formerly stood in an open basement can change that air supply.'],
 ['Volume example','COURSE: 50 ft³ per 1,000 Btu/h of combined appliance input. A 40,000-Btu/h heater gives 2,000 ft³; at a 10-ft ceiling this is 200 ft².'],
 ['Combined input','COURSE: 40,000 + 110,000 = 150,000 Btu/h; 150 × 50 = 7,500 ft³. At a 10-ft ceiling, 750 ft². This is 62.5% of 1,200 ft², not three quarters.'],
 ['Openings','Indoor communication, outdoor openings and vertical/horizontal ducts use different methods. Net free area is not the same as grille face area; all appliances and the permitted air source matter.'],
 ['Qualification','These calculations illustrate a course method. They do not establish actual infiltration, depressurization safety or permission to use any attic/crawl space as combustion air.']],figtime=2148)
page('furnace_types','Furnaces: distinguish circulation from combustion venting','S28',3113,[
 ['Two air paths','House air passes over the heat exchanger and into distribution ducts. Combustion products follow the combustion/vent path. Keep these paths separate in diagrams and reports.'],
 ['Conventional','Recognize natural-draft equipment and draft hoods where used. Appearance and approximate age do not establish safe operation.'],
 ['Induced draft','A draft inducer moves combustion gases through the heat exchanger. It is different from the circulating blower. An inducer does not make every downstream vent a positive-pressure vent.'],
 ['Condensing','A secondary heat exchanger extracts additional heat, producing condensate. Check the listed vent/intake materials, drainage, visible connections and termination.'],
 ['Efficiency','AFUE is a seasonal fuel-use measure. An 80% AFUE rating does not mean 20% of the fuel exits unburned. Do not use that explanation to justify a gas-detector test for a cracked heat exchanger.']],figtime=3257)
page('furnace_safety','Furnaces: preserve safety controls and inspection limits','S28',4279,[
 ['Ignition','Recognize standing pilot, hot-surface igniter and spark ignition. A thermocouple generates a small electrical signal from heat; it is not simply two metals touching as they warm.'],
 ['Flame sensing','An electronic flame sensor verifies flame through its designed circuit. Its principle is not identical to a thermocouple. Neither is a service adjustment for a home inspector.'],
 ['High limit','The high-limit control stops burner operation at its limit. A circulating blower may continue after the burner stops during normal shutdown. Do not bypass or intentionally overheat a unit to test it.'],
 ['Warning signs','Scorching, flame rollout, soot, damaged vents or suspected exhaust leakage call for prompt qualified evaluation. Do not fire a visibly unsafe furnace just to watch the defect.'],
 ['Heat exchanger','Limited external observation cannot prove that the entire exchanger is intact. A combustible-gas detector is not a CO analyzer and cannot by itself diagnose a crack.']],figtime=4463)
page('venting','Venting: match the appliance, connector and termination','S28',5521,[
 ['Connector','Identify the segment between appliance and vent/chimney. Look for visible slope, separation, corrosion, loose joints, support and clearance concerns.'],
 ['Different systems','B-vent, L-vent, single-wall connector, masonry chimney and listed condensing vent systems have different requirements. Do not transfer one clearance or roof-height rule to all of them.'],
 ['Concentric terminal','One exterior assembly may contain both intake and exhaust. Trace or read its identification; do not mistake it for a plumbing vent or seal an intended opening.'],
 ['Common vent','Compatibility, sizing, entry arrangement and manufacturer limitations all matter. Two appliances using the same fuel are not automatically suitable for common venting.'],
 ['Observation','Document an inaccessible chimney/flue interior. Do not remove sealed components or insert a hand into an exhaust outlet to identify the system.']],
 'COURSE: 1/4 inch per foot connector rise is a natural-draft example, not a universal condensate-vent slope. Manufacturer instructions and adopted rules must be read together; neither can simply be ignored when they appear to conflict.',5790)
page('oil_storage','Oil heat: follow the tank, fill, vent and supply line','S29',71,[
 ['Identity','Record accessible tank location, supports, fill/vent pipes, gauge, shutoffs and visible supply lines. Do not assume every abandoned pipe identifies a confirmed active underground tank.'],
 ['Condition','Observe corrosion, staining, patching, unstable supports and damaged or kinked tubing. Do not pick at rust or disturb suspect fittings to find a leak.'],
 ['Concealed storage','Fill/vent pipes or records may suggest a buried tank. State the evidence and recommend qualified tank/environmental review, including available closure records.'],
 ['Limits','A visual home inspection cannot determine the integrity of a buried tank or certify uncontaminated soil. An apparent conversion to gas does not prove proper tank closure.'],
 ['Numbers','The lecture’s 660-gallon indoor-storage figure and removal prices are historical/contextual examples. Do not treat them as current local permission or a repair estimate.']],figtime=528)
page('oil_burners','Oil burners: recognize components without servicing them','S29',768,[
 ['Combustion','A motor drives the fan and fuel pump; a nozzle atomizes fuel and electrodes provide ignition. The blast tube directs combustion toward the chamber.'],
 ['Access','Use only safe, permitted access. A sealed firebox porthole remains sealed and the inspection limitation is reported. Hot covers and moving components are not casually handled.'],
 ['Controls','Identify the primary safety control, visible service/emergency switches and shutoff locations. A failure to establish flame should result in a safety shutdown; the exact sequence is model-specific.'],
 ['Failed ignition','Do not repeatedly reset a burner: unburned fuel can accumulate. A locked-out or malfunctioning burner needs qualified service; the lecture’s “one reset” is not blanket authorization to reset an unfamiliar system.'],
 ['Condition','Report visible leakage, soot, smoke, damaged refractory or abnormal operation. Flame appearance alone does not quantify combustion efficiency.']],figtime=788)
page('oil_draft','Oil heat: keep draft control and maintenance in scope','S29',1887,[
 ['Barometric damper','Recognize the swinging draft regulator and surrounding vent connector. Soot, corrosion or other abnormal evidence deserves evaluation; do not adjust the counterweight.'],
 ['Service','The course emphasizes regular oil-burner service and combustion/smoke testing by a qualified technician. Do not adopt its suggestion that other heating systems can go ten years without maintenance.'],
 ['Switches','Identify the visible equipment disconnect and any remote emergency switch. Verify the applicable installation requirements without deliberately interrupting unsafe equipment to experiment.'],
 ['Separate appliances','Oil may fuel a furnace, boiler or water heater. Keep the heat medium, relief system and vent requirements specific to the actual appliance.'],
 ['Reporting','Record where evidence was seen, its possible consequence, service recommendation and any inaccessible chamber or flue area. Avoid asserting the hidden cause from exterior staining alone.']],figtime=2185)
page('gravity_furnaces','Older gravity furnaces: describe the system and its limits','S29',5288,[
 ['Circulation','Large supply and return ducts support natural convection, often called an octopus furnace. A later added blower or burner conversion needs identification rather than assumption.'],
 ['Condition','Inspect accessible cabinet, connections, vent connector and surrounding evidence. Approximate age alone does not demonstrate an actual heat-exchanger crack.'],
 ['Insulation','Old duct or equipment insulation may be suspect asbestos-containing material. Do not identify asbestos conclusively by sight or disturb it; recommend appropriate assessment where needed.'],
 ['Follow-up','Explain obsolescence, condition concerns and limited visibility. Qualified HVAC evaluation can address safe operation, repairs and replacement planning.'],
 ['Avoid false precision','The lecture’s replacement/abatement prices are anecdotes. A home inspection does not establish local project cost or environmental clearance.']],figtime=5320)

# Additional exam corrections are augmented by screen review before publication.
page('exam_sg008_concepts','New exam review: keep questions, answers and field limits separate','S18',4353,[
 ['Roof vocabulary','A rake is the sloping edge at a gable end. Fascia commonly follows the eave; they are not interchangeable.'],
 ['Chimney limitation','The recorded review distinguishes an inaccessible flue interior from conclusions about its condition. It does not authorize removing a chimney cap or dismantling a system.'],
 ['Electrical','Current through the body causes electrical injury; voltage and resistance affect that current. Do not turn a multiple-choice answer into a claim that voltage is irrelevant.'],
 ['Gas heat','The high-limit control stops the burner at its preset limit. The recorded correction associates yellow-tipped gas flames with inadequate combustion air; actual diagnosis requires appropriate evaluation.'],
 ['Oil heat','Keep oil and gas flame descriptions separate. A sealed porthole is a reported limitation, not a reason to break its seal. The primary control must respond to failed ignition.']],
 'EXAM: these are concept reviews, not a reconstructed answer key or invented score. Screen review records retain identifiable attempts and corrections separately. A participant’s spoken selection is not automatically the platform’s accepted answer.',4365)
