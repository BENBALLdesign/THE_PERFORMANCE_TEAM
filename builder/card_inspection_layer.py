"""Reviewed editorial safety emphasis and source-bound inspection sketches.

These are navigation layers over existing statements, never property findings.
The source concordance still owns all technical text and qualifications.
"""
import copy
from field_card_concordance import digest

REVISION='V2'
SAFETY_COLOR='#B3262E'
SAFETY_MEANING='Safety-related topic; assess the actual condition. An unmarked card is not a safety clearance.'
SKETCH_MEANING='Ring = detail to examine. Concept sketches, not to scale; not installation or repair details.'

# Explicit selections; neither keyword matching nor building age assigns a flag.
# Fact selectors resolve only within this card's already-reviewed concordance.
SAFETY={
 4:('Trips / access',['site_decks:grade-and-paving']),
 6:('Escape route',['site_decks:window-wells']),
 15:('Deck support',['site_decks:ledger-and-lateral-path']),
 16:('Falls',['site_decks:stairs-handrails-guards']),
 17:('Garage separation',['garage:dwelling-separation']),
 18:('Protective door / exit',['garage:passage-door','openings:doors-and-exits']),
 19:('Ignition / vehicle impact',['garage:appliance-protection']),
 20:('Door mechanism',['garage:mechanism-first']),
 21:('Entrapment protection',['garage:two-reversal-functions']),
 22:('Door test / unresolved protection',['garage:mechanism-first','garage:record-the-result']),
 23:('Electrical device protection',['devices:location-and-use','service:read-the-assembly']),
 28:('Load-path continuity',['load_paths:altered-load-paths','load_paths:follow-the-interface']),
 29:('Bearing / connection',['load_paths:follow-the-interface']),
 30:('Concealed post-tensioning',['foundation_water:respect-what-is-hidden']),
 33:('Combustion / controls',['gas_heat:warning-signs','gas_heat:normal-control-sequence']),
 34:('Fuel-gas piping / bonding',['gas:identify-the-product','gas:bonding-evidence']),
 36:('Temperature / pressure protection',['water_heat:relief-function','water_heat:distinct-devices']),
 37:('Fuel storage / exhaust',['oil_heat:storage-and-lines','oil_heat:draft-control']),
 38:('Electrical shock / fault protection',['circuits:screening-limits','devices:different-protection']),
 39:('Energized equipment',['service:before-panel-access']),
 40:('Multiple energy supplies',['devices:pv-and-generators']),
 44:('Damaged / safety glazing',['openings:read-the-glazing']),
 45:('Exit function',['openings:doors-and-exits']),
 46:('Falls',['site_decks:stairs-handrails-guards']),
 52:('Sewer-gas entry',['dwv:trap-and-vent']),
 53:('Potable-water protection',['water:backflow-protection']),
 55:('Hot-water temperature / controls',['water_heat:distribution-controls']),
 57:('Roof access',['roof_cover:form-slope-access']),
 58:('Roof load support / alterations',['roof_structure:trusses','roof_structure:ridge-and-ties']),
 59:('Roof restraint',['roof_structure:ridge-and-ties']),
 63:('Combustion exhaust path',['roof_cover:penetrations']),
 64:('Chimney support / flue',['roof_cover:chimney-parts']),
}

# Names match existing row labels. Only geometry and inspection targets are new.
SKETCHES={
 6:['Well bottom / visible outlet','Well exit opening / cover'],
 15:['Framing interface','Ledger-to-structure interface','Post-to-footing bearing'],
 16:['Handrail connections','Guard connections'],
 18:['Door / frame assembly','Hardware / operating edge'],
 20:['Spring continuity','Cable routing','Track alignment','Attachment'],
 21:['Photoeye path','Contact reversal test object'],
 28:['Beam / post contact','Post / footing contact'],
 29:['Beam / post bearing','Pocket / shim interface','Post base','Decay / alteration context'],
 36:['Actual relief device','Discharge route / outlet'],
 44:['Cracked pane','Between panes','Surface condition'],
 46:['Tread / riser junction','Handrail connection','Guard connection'],
 52:['Trap seal','Vent junction'],
 53:['Air-gap separation','Drainage vent path'],
 58:['Ridge board junction','Ridge beam / support','Truss plate / web junction'],
 59:['Rafter-tie connection','Collar-tie connection'],
}

def attach(cards,data):
    bindings={b['card_id']:b for b in data['cards']}
    records={};reverse={};sketch_records={}
    for c in cards:
        n=c['card_number'];b=bindings[c['id']]
        allowed={f for e in b['expressions'] for f in e['fact_ids']}
        if n in SAFETY:
            focus,selectors=SAFETY[n]
            ids=['SG-010:'+s for s in selectors]
            assert set(ids)<=allowed,(c['id'],ids)
            flag=dict(marked=True,label='SAFETY',focus=focus,meaning=SAFETY_MEANING,
                relationship='editorial safety relevance; not a condition finding',
                fact_ids=ids,qualification_ids=[f+':qualification' for f in ids],
                source_sha256={f:data['facts'][f]['source_sha256'] for f in ids})
            for f in ids:reverse.setdefault(f,[]).append(c['id'])
        else:
            flag=dict(marked=False,meaning='Not selected for safety emphasis; no inference of safety.')
        c['safety']=copy.deepcopy(flag);b['safety']=copy.deepcopy(flag);records[c['id']]=flag
        if n in SKETCHES:
            sketch=dict(revision=REVISION,kind='conceptual geometric inspection detail',
                targets=SKETCHES[n],scale='not to scale',meaning=SKETCH_MEANING,
                fact_ids=sorted(allowed),qualification_ids=[f+':qualification' for f in sorted(allowed)],
                property_geometry=False,installation_detail=False)
            c['inspection_sketch']=copy.deepcopy(sketch)
            b['inspection_sketch']=copy.deepcopy(sketch);sketch_records[c['id']]=sketch
    layer=dict(revision=REVISION,meaning=SAFETY_MEANING,sketch_meaning=SKETCH_MEANING,
        selection='Explicit editorial review of existing card text and linked statements plus qualifications; not a complete hazard checklist.',
        safety_color=SAFETY_COLOR,flagged_count=len(SAFETY),sketched_count=len(SKETCHES),
        safety_by_card=records,inspection_sketches=sketch_records,safety_reverse_index=reverse)
    layer['review_sha256']=digest(layer)
    data['inspection_layer']=layer
    return layer
