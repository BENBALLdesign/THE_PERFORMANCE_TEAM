"""Area-based editorial layer. Sources are the reviewed SG-010 topic records."""
import copy,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=json.loads((HERE/'field-cards/cards.json').read_text())['cards']
BASE_BY_ID={c['id']:c for c in BASE}

def card(title,subtitle,kind,refs,rows,note,write,cue=''):
    return dict(title=[title,subtitle],kind=kind,refs=refs.split(),rows=[row.split('|',1) for row in rows.split(';')],note=note,write=write,cue=cue)

def inherited(id,kind):
    c=copy.deepcopy(BASE_BY_ID[id]);c.update(kind=kind,base_card=id);return c

PACKS=[
('SITE & GROUNDS','Approach, grounds and drainage',[
card('ARRIVAL','READ THE PROPERTY','check','method site_decks','SCOPE|Access, systems and prior work;AGE|Select questions, then verify;ROUTE|Accessible areas and return points;RECORD|Property, location and photo IDs','Original age does not prove the assembly.','PROPERTY / YEAR / ACCESS','Set the route before the first close look.'),
card('RUNOFF','FOLLOW THE WATER','route','site_decks roof_cover','COLLECT|Roof > gutter > downspout;DISCHARGE|Outlet > grade > receiving area;LOW POINT|Swale > depression > opening;VERIFY|Visible route > hidden limit','A buried leader does not prove an open outlet.','OUTLET / LOW POINT / PHOTO','Connect the roof discharge to the ground.'),
inherited('4B','slope'),
card('WALKING ROUTE','SURFACE + DRAINAGE','compare','site_decks','FOOTING|Settlement / trip / obstruction;WATER|Slope / ponding / foundation route','Record the location and the effect on access.','LOCATION / DIMENSION / PHOTO','One surface can carry two different concerns.'),
card('RETAINING WALL','FORM BEFORE CAUSE','check','site_decks','FORM|Material, geometry and supports;SHAPE|Lean, bow, displacement or loss;WATER|Wetting, drainage and grade;EFFECT|Building, access and adjacent land','Visible tieback ends do not prove anchorage.','WALL / WATER / MOVEMENT','Record what is visible and what is buried.'),
card('WINDOW WELL','TWO FUNCTIONS','compare','site_decks','DRAINAGE|Water / debris / visible outlet;EXIT PATH|Cover / access / dimensions','A drained well can still obstruct escape.','WELL / COVER / ROUTE / PHOTO','Check drainage and the exit path separately.'),
card('VEGETATION','LOOK AT CONTACT','check','site_decks walls','AT GRADE|Concealed wall edges and drainage;AT THE WALL|Moisture evidence and contacts;AT THE PATH|Access, trips and visibility;LIMIT|Area hidden from this inspection','Record concealment before interpreting damage.','CONTACT / HIDDEN AREA / PHOTO','Vegetation changes what you can observe.'),
card('SITE CLOSEOUT','MAP THE LIMITS','record','method site_decks','AREA|Where was access limited?;REASON|What prevented inspection?;QUESTION|What remains undetermined?;NEXT|Record, access or qualified review','Keep separate specialist services in their scope.','AREA / REASON / NEXT ACTION','Make an access limit useful to the reader.')
]),
('EXTERIOR','Walls, openings and decks',[
card('WALL ASSEMBLY','FACE + BACKING','compare','walls movement','FACING|Cladding / veneer / finish;SUPPORT|Backing / bearing / connection','A finished face does not reveal hidden layers.','FACING / SUPPORT / LIMIT','Separate what sheds water from what carries load.'),
card('ROOF TO WALL','TRACE THE JUNCTION','route','walls roof_cover','UPSLOPE|Covering > flashing overlap;ALONG WALL|Step flashing > lower end;LOWER END|Kick-out > discharge;BELOW|Stain > trim > wall evidence','Caulk alone does not establish hidden flashing.','JUNCTION / DISCHARGE / PHOTO','Follow the water to its lower termination.'),
card('VENEER','SUPPORT + EXIT','check','walls movement','OPENING|Lintel and adjacent movement;SUPPORT|Visible bearing and distress;WATER EXIT|Flashing / weeps / lower edge;CONTEXT|Backing and concealed cavity','A weep does not prove the whole cavity drains.','OPENING / SUPPORT / WEEP','Read load support and drainage together.'),
card('STUCCO / EIFS','NAME THE ASSEMBLY','check','walls','IDENTIFY|Facing, layers and known records;EDGES|Drainage and termination details;OPENINGS|Joints and adjacent water evidence;DISTRESS|Cracks, bulges and displacement','Appearance does not establish dry sheathing.','ASSEMBLY / EDGE / PHOTO','Similar finishes can conceal different layers.'),
card('TRIM + COATING','NAME WHAT FAILED','tiles','walls','FASCIA|At the eave edge;RAKE|Along the gable slope;SOFFIT|Underside of the overhang;COATING|Peeling, checking or chalking','Fresh paint and wrapped trim can hide substrate.','PART / CONDITION / PHOTO','Component and condition before the cause.'),
card('WINDOW WATER','TIE BOTH SIDES','compare','openings walls','OUTSIDE|Head / sill / joints / flashing;INSIDE|Stain / support / operation','A dry visit does not establish hidden flashing.','OPENING ID / OUTSIDE / INSIDE','Use the same opening ID for both views.'),
card('DECK SUPPORT','FOLLOW THE JOINTS','sequence','site_decks','BOARDS / FRAMING|Decay, corrosion and distortion;LEDGER / LATERAL|Substrate, flashing and connection;POSTS / FOOTINGS|Visible bearing and support','Veneer is not structural ledger support.','CONNECTION / HIDDEN FACE / PHOTO','The member and its connection both matter.'),
card('STAIRS + GUARDS','SEPARATE THE JOBS','compare','site_decks','HANDRAIL|Grasping and its connections;GUARD|Fall protection and its connections','Compare stair dimensions from safe access.\nDo not load-test suspect guards.','RISER / TREAD / CONNECTION','First and last steps can change after alterations.')
]),
('GARAGE','Garage and vehicle-entry areas',[
card('SEPARATION','FOLLOW THE BOUNDARY','check','garage','WALLS|Visible breaks and alterations;CEILING|Boundary and penetrations;PASSAGE|Door assembly and operation;OPENINGS|Pet doors and other changes','Do not certify a rated firewall by appearance.','BREACH / ALTERATION / PHOTO','Use garage/dwelling separation as the description.'),
card('PASSAGE DOOR','ASSEMBLY + ACTION','compare','garage openings','ASSEMBLY|Identify actual door and features;OPERATION|Alignment / hardware / response','Material alone does not establish protection.','DOOR / LABEL / RESPONSE','Keep the door identity with its observed behavior.'),
card('APPLIANCE','THREE PROTECTIONS','sequence','garage water_heat','IGNITION|Source elevation and listing context;IMPACT|Vehicle route and visible protection;LEAK CONTROL|Pan, drainage and visible leakage','Lecture dimensions need their actual conditions.','APPLIANCE / PROTECTION / PHOTO','One protection does not prove the other two.'),
card('OVERHEAD DOOR','MECHANISM FIRST','check','garage','SPRINGS|Visible separation or damage;CABLES|Condition and visible routing;TRACKS|Alignment and connections;ATTACHMENTS|Visible distress or looseness','Compromised mechanism: do not operate;\nrefer to a trained door technician.','COMPONENT / STOP / PHOTO','Check the mechanism before using the operator.'),
card('REVERSAL','TWO DIFFERENT TESTS','compare','garage','PHOTOEYE|Photoelectric entrapment protection;CONTACT|Contact reversal under instructions','A working photoeye does not prove reversal.\nUse operator instructions and a safe setup.','METHOD / RESULT / OMITTED','An ordinary open/close cycle proves neither test.'),
card('DOOR TEST','KEEP THE EVIDENCE','record','garage','CONDITION|Mechanism before operation;METHOD|Actual instructed test;RESPONSE|Observed result;OMITTED|Test not done and why','An unperformed test remains unverified.','DOOR ID / METHOD / RESULT','Record the check that was actually performed.'),
card('GARAGE DEVICES','READ THE APPLICATION','check','devices service','DEVICE|Actual location and intended use;PROTECTION|Observed protection and response;CONDITION|Damage, enclosure and exposure;LIMIT|What was not checked and why','A successful device test does not prove wiring.','DEVICE / RESPONSE / LIMIT','Keep operation distinct from hidden condition.'),
card('VEHICLE ENTRY','GROUND TO OPENING','route','site_decks openings garage','APPROACH|Grade > low point > threshold;OPENING|Joint > sill > adjacent finish;INSIDE|Wet area > stain > damage;RECORD|Location > condition > photo','Trace the route before assigning the water source.','THRESHOLD / WATER / PHOTO','Connect the entry surface to the interior evidence.')
]),
('BASEMENT','Basement and crawl space',[
inherited('1A','route'),
inherited('1B','evidence'),
card('CRAWL SPACE','BOUNDARY FIRST','compare','foundation_water roof_structure','VENTED|Ground cover / insulation / air paths;SEALED|Moisture and thermal boundaries','Air vents and flood openings serve different jobs.','CRAWL TYPE / ACCESS / MOISTURE','Identify the strategy before judging its parts.'),
inherited('2A','bearing'),
card('BEARING','READ THE INTERFACE','check','load_paths foundation_water','TOP|Beam/post contact and bearing;JOINT|Pocket, shim and connection;BASE|Post base and visible support;CONTEXT|Moisture, decay and alterations','An intact member can have a poor connection.','TOP / JOINT / BASE / PHOTO','Follow concentrated loads through each change.'),
card('SLAB','WHAT IS CONCEALED?','check','foundation_water movement','TYPE|Known slab and foundation context;SURFACE|Crack, offset or covered area;INTERFACE|Wall, column and floor junctions;RECORD|Construction evidence and limits','Do not drill or probe a suspected\npost-tensioned assembly to identify it.','SLAB / OFFSET / COVERED AREA','Finish alone does not reveal reinforcement.'),
card('DRAINAGE PUMP','LIQUID + OUTLET','compare','dwv foundation_water','SUMP|Groundwater collection and discharge;EJECTOR|Wastewater collection and discharge','Do not assume a shared discharge destination.\nUse only a safe available normal-control test.','BASIN / RESPONSE / DESTINATION','Identify what the pump moves and where it goes.'),
card('EARLIER SERVICE','CLUE TO RECORD','sequence','foundation_water oil_heat','VISIBLE CLUE|Old pipe, fill, vent or patched opening;HISTORY QUESTION|What system was present or removed?;RECORD NEEDED|Location, removal or other evidence','An old line does not establish a buried tank.','CLUE / RECORD NEEDED / PHOTO','Keep observed traces separate from conclusions.')
]),
('SYSTEMS','Mechanical and electrical areas',[
inherited('3B','heat'),
card('FUEL GAS','IDENTIFY THE PRODUCT','sequence','gas','RIGID PIPE|Identify material and visible condition;CSST|Distribution tubing and bonding evidence;CONNECTOR|Final appliance connection','One clamp does not prove system continuity.\nProduct identity governs the next reference.','PRODUCT / CONNECTION / PHOTO','Read markings where accessible.'),
card('WATER HEATER','IDENTITY BEFORE AGE','record','water_heat','MODEL / SERIAL|Capture the actual label;ENERGY / SIZE|Fuel, capacity and rating;DATE BASIS|Manufacturer-specific decoding;CONDITION|Leakage, corrosion and support','Manufacture and installation dates can differ.','LABEL / DATE BASIS / PHOTO','An ANSI edition is not an installation date.'),
card('RELIEF','PROTECTION + ROUTE','compare','water_heat','FUNCTION|Temperature / pressure / actual device;DISCHARGE|Visible route / obstruction / termination','A temperature-only device is not combined\ntemperature-and-pressure relief.','DEVICE / ROUTE / TERMINATION','A pan drain and relief discharge are different.'),
card('OIL SYSTEM','TANK TO BURNER','route','oil_heat','STORAGE|Tank > support > visible condition;LINES|Fill > vent > supply line;APPLIANCE|Burner > controls > vent;RECORD|Label > maintenance > access limit','Do not disturb suspect tank surfaces.\nRust alone does not prove internal failure.','TANK / LINE / CONDITION / PHOTO','Follow visible parts without performing service.'),
inherited('4A','tiles'),
card('PANEL','LABEL + VISIBLE FACT','check','service circuits','ROLE|Supply, disconnect and panel arrangement;LABEL|Equipment and component ratings;VISIBLE|Damage, openings and terminations;LIMIT|Access, hidden parts and hazards','Do not reach into energized equipment.\nA visual check does not establish torque.','PANEL / COMPONENT / PHOTO','Keep conductor size, material and use together.'),
card('MORE THAN ONE','ENERGY SOURCE','check','devices service','UTILITY|Visible supply and disconnect;PV|Accessible equipment and disconnect;GENERATOR|Supply arrangement and disconnect;RECORD|Locations and inspection limits','The main disconnect may not isolate every supply.','SOURCE / DISCONNECT / LIMIT','Recognize additional energy paths before access.')
]),
('ROOMS & STAIRS','Interior rooms, stairs and openings',[
inherited('2B','profiles'),
card('CRACK','PATTERN + CONTEXT','record','movement','GEOMETRY|Width, offset and direction;MATERIAL|What actually cracked?;CONTEXT|Opening, support and adjacent finish;HISTORY|Repairs and available observations','Width alone does not establish cause or activity.','WIDTH / OFFSET / LOCATION','Record enough for a colleague to compare.'),
card('WINDOW','PART BEFORE DEFECT','tiles','openings','FRAME|Jamb, sill and opening support;SASH|Carries the glazing;GLAZING|Glass or glazing material;SEAL / COMPOUND|Different from the glazing itself','Name the failed part and its observed effect.','OPENING / PART / PHOTO','An operating defect and a seal defect differ.'),
card('GLAZING','SORT THE SYMPTOM','sequence','openings','GLASS|Crack or visible damage;BETWEEN PANES|Fogging within the insulated unit;AT THE SURFACE|Condensation, film or compound','Appearance alone may not identify safety glazing.','GLASS / SURFACE / BETWEEN','Location within the assembly changes the question.'),
card('DOOR','WHAT DOES IT PREVENT?','compare','openings','FIT / MOVEMENT|Rubbing, alignment or restriction;FUNCTION|Locking, hardware or exit use','Do not force a stuck or damaged opening.','DOOR / RESPONSE / LIMIT','State the effect, not simply that it is bad.'),
card('STAIR ROUTE','STEP + HAND + EDGE','sequence','site_decks','STEP|Risers, treads and first/last changes;HAND|Grasping surface and connections;EDGE|Guard and its connections','Observe from safe access; do not load-test\nsuspect stair or guard components.','STEP / RAIL / GUARD / PHOTO','Treat the stair and its protection as one route.'),
card('ROOM DEVICES','OPERATE + RESTORE','check','devices','BEFORE|Record the relevant setting;CONTROL|Use the appropriate normal control;RESPONSE|State what operated or failed;AFTER|Restore the original setting','Operation does not verify every hidden connection.','DEVICE / RESPONSE / RESTORED','Record the extent of the actual check.'),
card('FINDING','MAKE IT DISCUSSABLE','sequence','method','OBSERVE|Location, component and visible condition;EXPLAIN|Concern and what remains uncertain;ACT|Defined correction, review or monitoring','Significant findings also belong in writing.','OBSERVATION / QUESTION / ACTION','Could a colleague follow your evidence?')
]),
('WET ROOMS','Kitchen, baths and laundry',[
inherited('3A','pipes'),
card('FIXTURE','THREE OBSERVATIONS','sequence','water dwv','SUPPLY|Functional response under stated conditions;DRAINAGE|Observed drainage during the test;LEAKAGE|Joints, surfaces and adjacent evidence','Functional flow is not a pressure measurement.','FIXTURE / FLOW / DRAIN / LEAK','A draining fixture does not prove concealed pipe.'),
card('WET PIPE','JOINT OR SURFACE?','compare','water','LEAKAGE CLUE|Joint, component and local wetting;CONDENSATION|Cold surface and surrounding conditions','Trace the wet surface before naming the source.','SURFACE / JOINT / CONDITIONS','Do not label every sweating pipe a failed joint.'),
card('TRAP + VENT','DIFFERENT FUNCTIONS','compare','dwv','TRAP SEAL|Limits sewer-gas entry;VENTING|Supports drainage and trap-seal function','Pipe shape may not reveal concealed venting.','TRAP / VENT / CONCEALED','Read the arrangement before naming a defect.'),
card('BACKFLOW','KEEP SUPPLY SEPARATE','compare','water dwv','SUPPLY PROTECTION|Actual air gap or device and its use;DRAINAGE VENT|Air path supporting drainage function','Venting is not potable-water backflow protection.','DEVICE / APPLICATION / PHOTO','Identify the actual function of the component.'),
card('MATERIAL','READ THE MARKING','check','water dwv','MATERIAL|Actual marking and visible evidence;FUNCTION|Supply, waste, relief or connection;JOINT|Transition, fitting and condition;CONTEXT|Exposure and installed application','Color or fitting shape alone is insufficient.','MARKING / USE / CONNECTION','PVC and CPVC are different materials.'),
card('TEMPERATURE','KEEP THE TEST CONTEXT','record','water_heat water','LOCATION|Which fixture and outlet?;CONDITION|Operating conditions during reading;VALUE / UNIT|Actual measured value and unit;CONTROL|Visible tempering or circulation','One fixture does not establish every outlet.','FIXTURE / VALUE / UNIT / TIME','Keep the reading with its location and conditions.'),
card('SLOW DRAIN','SYMPTOM TO QUESTION','sequence','dwv method','OBSERVE|Which fixture, test conditions and response?;CORRELATE|Visible joints, supports and other symptoms;REPORT|Observed concern and unresolved route','A slow drain does not locate a hidden blockage\nor prove disposal-system failure.','FIXTURE / RESPONSE / QUESTION','State what the test actually demonstrated.')
]),
('ATTIC & ROOF','Attic, roof and chimney',[
card('ACCESS','DEFINE THE VIEW','check','roof_cover roof_structure method','METHOD|How was the area observed?;EXTENT|Which planes or spaces were visible?;LIMIT|What prevented further inspection?;FOLLOW-UP|Question the unseen area leaves','Use safe access and record the actual method.','METHOD / AREA / LIMIT','The inspection method belongs with the finding.'),
card('ROOF FRAME','BOARD, BEAM OR TRUSS?','sequence','roof_structure','RIDGE BOARD|Aligns rafters;RIDGE BEAM|Carries roof load through supports;TRUSS|Chords, webs, plates and bearing','Altered trusses need appropriate design records.','MEMBER / SUPPORT / ALTERATION','Identify the system before applying a detail.'),
card('ROOF TIES','NAME THE FUNCTION','compare','roof_structure','RAFTER TIE|Resists outward thrust;COLLAR TIE|Different upper-roof connection function','Do not substitute one tie name or position\nfor the other function.','TIE / LOCATION / CONNECTION','Look at where the member connects.'),
card('ATTIC BOUNDARY','ASSEMBLY BEFORE VENT','compare','roof_structure','VENTED ATTIC|Insulation, air paths and moisture;CONDITIONED ROOF|Actual thermal and moisture boundaries','A missing vent is not a defect in every assembly.','ASSEMBLY / AIR PATH / MOISTURE','First identify what is inside the boundary.'),
card('COVER + DECK','READ BOTH SIDES','compare','roof_cover roof_structure','ABOVE|Damage, displacement, repair and debris;BELOW|Stains, sag, decay and members','Appearance alone does not prove capacity\nor remaining service life.','PLANE / ABOVE / BELOW / PHOTO','Relate the covering to the evidence below it.'),
card('FLASHING','OVERLAP TO OUTLET','route','roof_cover walls','UPSLOPE|Covering > diversion > overlap;JUNCTION|Wall > valley > chimney interface;LOWER EDGE|Flashing > gutter > outlet;BELOW|Stain > sheathing > interior evidence','Read the actual covering and flashing system.','JUNCTION / LAP / DISCHARGE','The last visible lap is not the whole assembly.'),
card('TERMINATION','WHAT DOES IT SERVE?','tiles','roof_cover roof_structure','PLUMBING VENT|Drainage air path;COMBUSTION|Appliance exhaust path;ATTIC VENT|Roof-space ventilation;EXHAUST DUCT|Room or equipment discharge','A sound-looking cap does not prove its connection.','DEVICE / FLASHING / DESTINATION','Match each terminal to the system it serves.'),
card('CHIMNEY','FOUR DIFFERENT PARTS','tiles','roof_cover','ENCLOSURE|Chase or masonry assembly;FLUE|Internal exhaust passage;CROWN|Top weather-shedding surface;RAIN CAP|Protection over the opening','Do not push a chimney to test it.\nUnseen flue condition remains unresolved.','PART / ROOF JOINT / PHOTO','Connect support, weather protection and venting.')
])]

def catalog():
    cards=[]
    for area,(short,title,items) in enumerate(PACKS,1):
        assert len(items)==8,(short,len(items))
        for slot,c in enumerate(items,1):
            c=copy.deepcopy(c)
            c.update(id=f'QC-{len(cards)+1:03d}',display_id=f'{area:02d}.{slot:02d}',area_number=area,area_short=short,area_title=title,slot=slot,card_number=len(cards)+1)
            cards.append(c)
    assert len(cards)==64
    assert sorted(c['base_card'] for c in cards if 'base_card' in c)==sorted(BASE_BY_ID)
    return cards
