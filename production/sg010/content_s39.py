"""S39 review: recovered interior Units 3-6 (floors, openings, stairs, fireplaces).

The repaired recording (R49353ce5bfa0, parent R4f902a2e300b) ends at course screen
'Inspecting Fireplaces (13/15)'. Screens 14-15 and the Unit 6 exam are not in evidence.
Course statements and lecture shortcuts stay qualified; they are not adopted as universal rules.
"""
from prepare import *

FRAMES=WORK/'intake/S39/Visual/R49353ce5bfa0/frames'
LIMIT='Recording ends at course screen Inspecting Fireplaces 13/15; screens 14-15 and the Unit 6 exam are not in evidence.'

def refs(t,label):return [dict(source='S39',seconds=t,label=label)]
def topic(id,title,rows,t,label,headers=('Identify / check','Evidence to record','Interpretation / limit'),text=None):
    blocks=[dict(kind='table',headers=list(headers),rows=rows,widths=[106,210,188])]
    if text:blocks.append(dict(kind='text',text=text))
    return dict(id=id,title=title,section='Interior evidence',blocks=blocks,refs=refs(t,label))

NEW=[
 topic('floor_finishes','Floor finishes: identify the layer before judging it',[
  ['Solid / engineered wood','Record strip, plank or parquet; visible cupping, crowning, buckling, gaps, stains, soft areas and finish wear. Compare with the structure below where accessible.','Moisture, humidity and tight installation are candidate causes. Sanding limits depend on actual wear-layer thickness, which is rarely visible from above.'],
  ['Laminate / floating floor','Identify a click or glued floating assembly over foam or cork; record peaking, open joints, swelling at edges and bounce.','A photographic wood-grain surface is not wood. Swelling records water exposure; it does not locate the source.'],
  ['Tile / stone / terrazzo','Walk the surface for loose or hollow tiles; record cracked tiles, failed grout and staining, especially at wet fixtures.','Cracks can follow a flexible substrate or movement below. Do not tap or lift tile to prove a concealed cause.'],
  ['Resilient sheet / tile','Record lifting, tears, telegraphed seams, ridges, crackling underfoot and discoloration.','Older resilient tile and backing can contain asbestos; treat as suspect and leave undisturbed (special_service_boundaries).'],
  ['Carpet / coverings','Record trip hazards, stains, odor, blocked registers or convectors and what the covering hides.','Carpet quality is outside most inspection scopes. Wood in a closet does not establish the finish under adjacent carpet.'],
  ['Wet areas / recent work','Check floors at tubs, toilets, showers, sinks, laundry and exterior doors; press gently with a foot for softness and compare below.','New carpet, flooring or built-ins can conceal earlier damage. Record the limit; do not remove coverings.']],180,'Floor finish lesson screens (Unit 3)',
  text='S39 COURSE: examples such as 3/4 in. hardwood sanded several times, 3/8 in. once, and softwood kept above 5/8 in. are course figures, not a field test. Unit 3 exam answers retained: a mid-room low area points to support below; squeaks point to the subfloor-joist connection; hardwood in a closet supports no conclusion about the carpeted room.'),
 topic('safety_glazing','Safety glazing: location decides the question, the mark answers it',[
  ['Material','Identify tempered, laminated, wired or ordinary annealed glass where the mark or construction shows it.','Tempered breaks into small pieces; laminated is held by an interlayer. Traditional wired glass cuts badly and is not safety glazing without a qualifying mark.'],
  ['Permanent mark','Look for a permanent identifying mark in a corner of each individual pane in a hazardous location; photograph it.','Each tempered pane in an assembly needs its own mark. Simulated divided light is one pane; true divided light is several. No visible mark means unverified, not proven annealed.'],
  ['Doors / sidelights','Glass in doors, and in fixed panels near a door where the course diagram applies (24 in. arc; lower edge near the walking surface).','Use the adopted code for exact dimensions and exceptions. Small leaded panes that a 3 in. sphere cannot pass are a course exception.'],
  ['Large panels / wet areas','Large low panes near walking surfaces; glass at tubs, showers and enclosures, including every pane of a frameless enclosure.','The course gives four criteria that must all apply for large panels, and 60 in. for wet areas. Glass block is a lecture exemption; confirm in the governing code.'],
  ['Stairs / guards','Glass within 36 in. horizontally of stairs, landings and ramps; glass in any railing or guard assembly.','A qualifying protective bar is a course alternative. Guard glass is a fall-protection question as well as a breakage question.'],
  ['Report','Name the opening, pane, mark observed or not, and why the location matters. Recommend evaluation or replacement where the hazard is plausible.','Older installations predate current rules. State the safety concern without calling it a code violation. Do not impact-test glass.']],901,'Safety glazing lecture',
  text='LOCAL MD-28: Hazardous-location dimensions and exceptions come from the adopted code edition. Lecture statements that tempered glass is five times stronger and that laminated windshields are "not safety glass" are not adopted; laminated glass can qualify as safety glazing when marked.'),
 topic('egress_openings','Emergency escape: operate the whole route, not just the window',[
  ['Where it applies','Identify sleeping rooms and basements. The course applies one escape opening per basement plus one in each basement sleeping room.','Room labels in listings are not proof of use. Record the room as observed; applicability depends on the adopted code and actual use.'],
  ['Clear opening','Operate the window fully. Compare net clear opening, sill height and area with the course values: 20 in. wide, 24 in. high, sill no higher than 44 in., 5.0 sq ft at grade and 5.7 sq ft above.','Sash size is not clear opening. Awning, hopper and casement stops can reduce the opening. Measure where taken and record it; do not guess.'],
  ['Wells / ladders','Record well depth, projection, ladder or steps, drainage and debris. Course diagram: ladder may encroach 6 in.; needed when the well is deeper than 44 in.','Ledges that cannot be gripped may not function as a ladder. Refer to the governing dimensions rather than a photo judgment.'],
  ['Covers / bars / locks','Operate release hardware on bars, grilles and well covers from inside. Record keys, tools, padlocks, fixed bars or secondary sash locks needing a tool.','Release must not need a key, tool or special knowledge. A fixed grate or bar at a required opening is a safety concern; a deep open well is a separate fall concern.'],
  ['Leave it as found','Some bar releases need two people to relatch. Plan the test so the house is left as secure as found.','Do not leave a vacant house unsecured to finish a test; record what was not operated and why.']],1740,'Egress, window wells and security bars',
  text='LOCAL MD-31: Current escape-opening values describe new work. For an existing house, report an impaired or undersized escape route as a safety concern without claiming a retrofit requirement. The lecture claim that every well cover must rest by gravity alone is narrowed to the release requirement.'),
 topic('interior_doors','Interior doors: operate each accessible door and read its hardware',[
  ['Door type','Identify flush (hollow or solid core), panel, louvered, bifold, bypass and pocket doors; note glazing.','Hollow-core doors are interior doors. At the garage separation, apply garage_separation rather than an interior-door standard.'],
  ['Operation / fit','Operate each accessible door: rubbing, sticking, gaps, swing, latching when pushed closed without holding the knob.','Moisture swelling, loose hinges and framing movement are candidate causes. Relate repeated misfit to floor and wall evidence.'],
  ['Hardware','Record missing hinge pins, loose or missing screws, loose knobs, misaligned strikes and missing floor guides on bypass doors.','Heavy or tall doors depend on hinge fastening into framing. Record the condition; do not repair it during the inspection.'],
  ['Locks / orientation','Check privacy locks lock from the room side with an emergency release. Record reversed knobs and keyed or double-cylinder locks on exit paths.','A lock that holds an occupant in a room, or needs a key to exit, is a safety concern regardless of cause.'],
  ['Damage / modification','Look at both faces and behind doors: holes, delamination, cut-down hollow-core doors, split jambs, missing stops and wall damage.','Cosmetic damage is minor; a split jamb or cut-down door affects function. Always look behind doors for concealed panels or equipment.'],
  ['Clearance / air','Note undercut or clearance where rooms lack a return-air path.','The course 3/4 in. undercut is an example. Airflow adequacy is a heating/cooling question, not a door defect.']],3000,'Interior doors lecture',
  text='S39 COURSE: most standards require a representative number of doors and windows; the course and lecture recommend operating all accessible units. Record the method actually used. Lecture repair tips (long hinge screws, glued strike-hole plugs) are homeowner information, not inspection actions.'),
 topic('interior_stairs','Interior stairs, guards and balconies: uniformity, grip and fall',[
  ['Geometry / uniformity','Walk the stair; look for a different first or last riser after flooring changes, worn or loose treads, open risers and winders.','Course values (7-3/4 in. rise, 10 in. run, 3/8 in. variation) change with edition and local amendment. A variation between risers is the usual hazard.'],
  ['Handrail','Record presence, continuity from top to bottom riser, returns or newel ends, graspable profile and height (course 34-38 in.).','A flat 2x cap or board on edge is not graspable. A rail that stops short or ends in a hook is a catch hazard. Handrail and guard are different functions.'],
  ['Guard / balusters','Record guards at open sides and balconies where the drop exceeds 30 in.; missing, loose or climbable members; openings (course 4 in.; 4-3/8 in. on stair open sides).','Older wide baluster spacing is common and rarely rebuilt. Report it as a hazard for small children and note temporary protection; avoid a blanket replace order.'],
  ['Headroom / width / landings','Observe low headroom at the nosing line, narrow width, a door swinging over the top tread and missing landings.','Course: 6 ft 8 in. headroom measured from the nosing line, 36 in. width, landing where a door swings over the stair. Low basement and attic stairs are common and usually not fixable.'],
  ['Winders / spiral','Record pie-shaped treads with little usable depth and spiral stair dimensions.','Course: 6 in. minimum at the narrow end and 10 in. at the walkline 12 in. out. Spiral stairs have their own dimensional set and may not count as a required exit route.'],
  ['Lighting / balcony support','Record lighting and switches at both ends where six or more risers; shake-test only a sound-looking guard gently; observe balcony bounce and support.','A cantilevered interior balcony is an accepted method (Unit 5 exam). Report shaking, sagging, tilting or loose guards; do not load-test a suspect assembly.']],4080,'Interior stair and railing lecture',
  text='LOCAL MD-29: Dimensions come from the adopted code; record measured values rather than pass/fail labels. The lecture suggestion to measure discreetly so a client will not expect measurement is not adopted: state in the report what was measured and what was observed only.'),
 topic('fireplace_masonry','Masonry fireplace: hearth, firebox, damper, flue',[
  ['Front / facing','Record soot staining above the opening, cracked or loose facing, charred trim and a loose mantel.','Smoke staining suggests spillage. Candidate causes: draft, flue size or height, deposits and house depressurization from exhaust equipment.'],
  ['Hearth / extension','Record hearth extension depth and width, cracks, and support of a raised hearth.','Course: 16 in. out and 8 in. each side for openings under 6 sq ft; 20 in. and 12 in. for larger. Older fireplaces are often shallower: describe the risk of sparks and rolling logs.'],
  ['Combustible clearance','Record wood trim and mantel distance from the opening.','Course: 6 in. at the sides; 12 in. for a mantel projecting more than 1-1/2 in. Repeated heating lowers the ignition temperature of nearby wood.'],
  ['Firebox / damper','Identify firebrick or metal lining; record cracked brick, open joints, rust and a damper that does not open fully or close. Note a top-sealing retrofit damper.','A missing damper is reported. A metal firebox in masonry needs its designed gap. Ash or a burning fire limits the view.'],
  ['Flue / chimney','Look up past the damper with light and mirror; record liner type, cracks, offsets, deposits and obstructions.','Course: clean at more than 1/8 in. of deposits; one flue per fireplace. When the flue is not visible, say so and recommend a qualified chimney evaluation.'],
  ['Top of chimney','Record cap, spark arrestor, crown and scorch marks on nearby roofing (chimney_parts).','A missing cap on an older chimney is a recommendation, not a missing required part. Removing a cap to view the flue is outside the inspection.']],6180,'Masonry fireplace lecture and screens',
  text='S39 COURSE: the course states flue liners have been required since about 1950. Build year is only a lookup cue; record the liner actually observed. The inspector does not light or extinguish fires. If a fire is burning, record the limited inspection.'),
 topic('fireplace_factory_gas','Factory-built, gas and vent-free units: read the label before the flame',[
  ['Factory-built ("zero clearance")','Identify the listed metal unit and its vent; record label, cracked refractory panels, rust, open vent joints and missing standoffs.','"Zero clearance" means combustibles may meet the cabinet only as the listing allows. Clipped standoffs or missing air spaces violate the instructions.'],
  ['Vent type','Distinguish B-vent to a chase, direct-vent concentric pipe with sealed glass, and outside combustion-air ducts.','Follow the manufacturer label for termination and air-inlet position. Course: B-vent needs 1 in. clearance and fire blocking at each floor; seeing down to the firebox from the attic is a deficiency.'],
  ['Gas logs in a vented firebox','Identify the pan burner and ember media; confirm the damper is removed or held open.','Decorative vented gas logs need an open flue. Carbon monoxide produces no smoke to warn the occupant.'],
  ['Vent-free units','Identify vent-free burners, the oxygen depletion sensor and the metal rating plate. Compare the rating plate with the log set installed.','A vented log set installed in a vent-free firebox is a serious combustion hazard. Local rules on vent-free units vary; confirm them.'],
  ['Operation','Operate only by normal controls within scope: ignition, flame, glass and venting. Record a switch that turns on a fireplace.','Brief fogging of the glass at start-up is condensation. Glass is specialty ceramic; cleaning follows the manufacturer. Do not operate a unit with a damaged vent or odor.'],
  ['Inserts / other units','Record inserts, coal grates, decorative or roughed-in fireplaces, pellet or multi-fuel appliances and the data plate.','Insert flue connections are concealed: recommend specialist removal and evaluation. Never call a fireplace operational without seeing inside. Look up unfamiliar appliances by the data plate.']],6600,'Gas, factory-built and vent-free fireplace lecture',
  text='S39 COURSE: EPA-certified wood stoves use catalytic or non-catalytic secondary combustion; NFPA 211 is the referenced chimney and solid-fuel standard. The course figure of about 20 years of life for factory-built units is not adopted as a life expectancy. '+LIMIT)]

COMPACT=dict(id='interior_routes',title='28  Interior glazing, escape, stairs and hearths',route='Mark > operate > walk > fall edge > heat source',topics=[p['id'] for p in NEW],rows=[
 ['Safety glazing','Hazardous location first; then a permanent mark on each pane.','No mark means unverified. Older glass is a safety concern, not a code finding.'],
 ['Escape opening','Operate fully; clear opening, sill, well, ladder, bars and covers release without key or tool.','Compare with the course values; for an existing house, report an impaired route as a safety concern.'],
 ['Doors','Operate each accessible door; hinges, latch, lock orientation, damage behind the door.','A lock that traps or needs a key to exit is a safety concern.'],
 ['Stairs / guards','Uniform risers, graspable continuous rail, guard at the open side, headroom, winders, light.','Record measured values; older balusters: note temporary protection rather than a blanket replacement.'],
 ['Floors','Name the finish layer; soft, lifted or stained areas at wet fixtures; what coverings hide.','Suspect older resilient tile stays undisturbed.'],
 ['Masonry hearth','Facing, hearth extension, clearances, firebox, damper, visible flue.','Flue not visible: say so and refer. Do not light fires.'],
 ['Gas / factory-built','Label, vent type, damper held open for gas logs, vent-free rating plate, insert referral.','Match the log set to the firebox listing. Record normal-control operation only.']],discuss='Which of these would injure someone before anyone knew it was there?',note='S39 / N14. Recording ends at fireplace screen 13/15; dimensions are course values under the adopted code.',figure=None)

QUALIFICATIONS=[
 ['Safety glazing','Laminated glass can be safety glazing when marked; tempered strength multiples and glass-block exemption are lecture claims to check against the adopted code.','S39 00:15-00:26'],
 ['Egress covers','Release without key, tool or special knowledge is the requirement; "gravity only" and a universal well-cover mandate are not adopted.','S39 00:32-00:35'],
 ['Measurement practice','State what was measured. Do not hide measurement from the client to manage expectations.','S39 01:15-01:16'],
 ['Handrail / guard','A handrail on each side is not implied by fall height; the open side needs a guard where the drop exceeds the threshold.','S39 01:08-01:09'],
 ['Field repairs','Hinge-screw and strike-plug repairs described in the lecture are not inspection actions.','S39 00:52-01:08'],
 ['Egress by spiral stair','The lecture relays an appraiser comment that a spiral stair cannot be a required exit route; verify locally before reporting it.','S39 01:34'],
 ['Fireplace life / liners','A 20-year factory-built life and a 1950 liner date are course figures; they are not an age test for an individual unit.','S39 screens 116, 103'],
 ['Evidence limit','The recording ends at Inspecting Fireplaces 13/15; screens 14-15 and the Unit 6 exam were not captured.','S39 end of file']]

RESULTS=[('Interior Unit 3',276,600.033,8,9,89),('Interior Unit 4',882,3912.8,6,8,75),('Interior Unit 5',1374,6031.3,4,4,100)]

def apply(d,compact,apps,walk):
    i=next(i for i,p in enumerate(d['pages']) if p['id']=='interior_moisture')+1
    d['pages'][i:i]=copy.deepcopy(NEW)
    topics={p['id']:p for p in d['pages']}
    for tid,text in [
     ('window_glazing','S39: hazardous-location glazing and marks are covered in safety_glazing. Keep glazing defects (this topic) separate from the location question.'),
     ('window_wells','S39: the full escape route, including bars, covers and release hardware, is covered in egress_openings.'),
     ('rails_guards','S39: interior stairs, winders, headroom and balcony guards are covered in interior_stairs; the same handrail/guard distinction applies.'),
     ('chimney_parts','S39: fireplace-side evidence (hearth, firebox, damper, gas and vent-free units) is covered in fireplace_masonry and fireplace_factory_gas.'),
     ('floor_terms','S39: finish-layer identification and wet-area floor evidence are covered in floor_finishes.')]:
        if tid in topics:topics[tid]['blocks'].append(dict(kind='text',text=text))
    compact.append(copy.deepcopy(COMPACT))
    for p in compact:
        if p['id'] in ('movement','openings','site_decks'):p['note']=p.get('note','')+' S39: interior floors, glazing marks, escape openings, doors and stairs: see "Interior glazing, escape, stairs and hearths".'
    for term,exp,definition,tid in [
     ('Safety glazing','Tempered or qualifying laminated glass','Glazing that meets impact-safety criteria and carries a permanent mark on each pane. Required in hazardous locations defined by the adopted code; ordinary wired glass does not qualify.','safety_glazing'),
     ('Emergency escape and rescue opening','Required escape window or door','An operable opening from a sleeping room or basement sized, positioned and released without keys, tools or special knowledge. Values depend on the adopted code.','egress_openings'),
     ('Winder / walkline','Turning tread / measuring line','A tapered tread in a turning stair. Its depth is measured along a walkline a set distance from the narrow side; the narrow end also has a minimum.','interior_stairs'),
     ('Nosing line','Stair headroom reference','A sloped line connecting tread nosings. Stair headroom is measured vertically from this line, not from the tread surface.','interior_stairs'),
     ('Hearth extension','Noncombustible floor in front of the firebox','The noncombustible extension beyond the fireplace opening, sized from the opening area, that protects the floor from sparks and embers.','fireplace_masonry'),
     ('Smoke chamber / smoke shelf','Transition from firebox to flue','The sloped chamber above the damper that guides smoke into the flue; the shelf at its base deflects downdrafts. Neither is present in most factory-built units.','fireplace_masonry'),
     ('Factory-built fireplace','Listed metal fireplace and vent system','Often called zero-clearance. Combustibles may meet the unit only as its listing allows; standoffs, air spaces and vent parts are part of the listing.','fireplace_factory_gas'),
     ('Vented gas logs / vent-free unit','Different gas fireplace appliances','Vented decorative logs need an open flue and a damper held open. A vent-free unit discharges to the room and carries an oxygen depletion sensor; its rating plate identifies it.','fireplace_factory_gas'),
     ('Floating floor','Finish not fastened to the subfloor','Laminate or engineered planks joined to each other over an underlayment. Movement and water swelling show at joints and edges.','floor_finishes')]:
        apps['APP-D']['terms'].append(dict(term=term,expansion=exp,definition=definition,topic=tid,source_pointer=topics[tid]['title'],source_refs=topics[tid]['refs']))
    apps['APP-D']['notes'].append(['N14','Interior openings, stairs and fireplaces','Location decides whether a glazing, escape or stair value applies; the adopted code supplies the number. Record the mark, measurement or operation actually observed. '+LIMIT])
    apps['APP-G']['pages'].append(dict(id='S39_course_qualifications',title='S39: interior lessons and lecture qualifications',blocks=[dict(kind='table',headers=['Topic','Retained qualification','Locator'],rows=QUALIFICATIONS,widths=[106,287,111])],refs=refs(6000,'Recovered interior lessons')))
    (OUT/'Evidence/S39').mkdir(parents=True,exist_ok=True)
    for unit,frame,seconds,correct,total,score in RESULTS:
        src=FRAMES/f'frame-{frame:07}.jpg';dst=OUT/f'Evidence/S39/S39-F{frame:04}.jpg';shutil.copy2(src,dst)
        apps['APP-G']['recorded_results'].append(dict(source='S39',frame=frame,seconds=seconds,timestamp=f'{int(seconds//3600):02}:{int(seconds%3600//60):02}:{seconds%60:06.3f}',asset=f'Evidence/S39/S39-F{frame:04}.jpg',frame_sha256=sha(dst),label=f'{unit} result',interpretation='Reviewed screen context; course statements retain editorial qualifications',unit=unit,score=score,correct=correct,total=total,review='Visually confirmed result screen from the repaired S39 recording; not a question-by-question audit.'))
    for name,note,tid in [
     ('Safety-glazing mark','Name the opening and pane, the mark observed or not, and why the location matters.','safety_glazing'),
     ('Escape route release','Record clear-opening observation, sill, well, and whether bars or covers released from inside without a key or tool.','egress_openings'),
     ('Stair rail and guard','Keep handrail graspability, guard at the open side, baluster spacing and riser uniformity as separate statements.','interior_stairs'),
     ('Fireplace limits','Record flue visibility, damper operation, hearth extension and the gas-log or vent-free identification; refer where not visible.','fireplace_masonry')]:
        n=len(apps['APP-C']['items'])+1;apps['APP-C']['items'].append(dict(id=f'M{n:04}',added='2026-09-21',mention=name,note=note,source='S39 / '+tid,links=[dict(label='SG-010-L1 topic',url='../../SG-010-L1/STUDY GUIDE.html#'+tid)],status='Prompt; requires actual property evidence',checklist_status='Not a property finding'))
    apps['APP-F']['modules'].append(['Interior openings / stairs / hearth','T001 / T002 / T003 / T009','Applies in every era; older stairs, glazing and fireplaces often predate current values. Record marks and measurements taken; do not light fires or remove caps, inserts or coverings.'])
    room=next(p for p in walk if p['id']=='rooms')
    room['refs']=list(dict.fromkeys(room['refs']+['interior_routes']))
    room['note']=room.get('note','')+' S39: check glass marks in hazardous locations, operate escape windows and bar releases, walk every stair for uniform risers and a graspable rail, and read the fireplace label before any flame.'
    coverage=read(OUT/'scope-coverage.json')
    for r in coverage['families']:
        add={'D1-T11':['floor_finishes','interior_doors','interior_stairs'],'D1-T12':['fireplace_masonry','fireplace_factory_gas'],'D1-T13':['safety_glazing','egress_openings','interior_stairs']}.get(r['id'])
        if add:
            r['topic_ids']=list(dict.fromkeys(r['topic_ids']+add))
            r['status']='S39 recovered-recording review incorporated; fireplace screens 14-15 not captured; publication QA pending' if r['id']=='D1-T12' else 'S39 recovered-recording review incorporated; publication QA pending'
    save(OUT/'scope-coverage.json',coverage);apps['APP-B']['scope_coverage']=coverage['families']
