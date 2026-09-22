"""SG-010 scope audit, run last: every NHIE task family mapped to guide topics, with gaps left visible.

Labels follow the official NHIE content outline (references/nhie-outline.txt). Exam weighting is a
coverage check only; it is not field risk. A listed gap means no guide topic covers that knowledge item.
"""
from prepare import *

FAMILIES=[
 ('D1-T1','Site: vegetation, grade, drainage, retaining walls, paving, pool barriers','exterior_site grading_vegetation retaining_wall_types retaining_wall_drainage walks_patios seasonal_and_pool_scope site_access_limits',[]),
 ('D1-T2','Exterior: cladding and trim, doors and windows, decks/stairs/railings, vehicle doors','exterior_scope siding_assembly siding_wood siding_panels_shingles siding_metal_vinyl siding_older_materials siding_stucco siding_eifs siding_masonry_checks siding_veneer_details siding_kickout_path siding_coatings siding_report trim_parts trim_condition trim_video_clues window_parts window_glazing window_operation_detail window_energy window_waterpath door_operation openings_report safety_glazing egress_openings steps_stoops rails_guards porch_supports deck_condition deck_connections balcony_connections window_wells garage_doors garage_appliances site_exterior_report',[]),
 ('D1-T3','Roof: coverings, drainage, flashings, skylights and penetrations','roof_forms roof_cover_condition roof_flashing roof_penetrations chimney_parts roof_drainage',[]),
 ('D1-T4','Structure: foundation, floor, walls, roof and ceiling structure','foundation_types movement moisture drainage crawl_access crawl_openings supports notches_and_holes engineered_and_connections slab_evidence post_tension wall_systems stud_cuts special_walls masonry_systems masonry_distress floor_terms floor_layers cantilevers_openings access_and_services roof_frame roof_ties roof_trusses roof_deck manufactured_structure',[]),
 ('D1-T5','Electrical: service, panels, wiring methods, devices, alternative energy, EV service equipment','electric_service electric_panels electric_conductors electric_multiwire electric_wiring_methods electric_legacy electric_devices electric_alternative',['F. Electric vehicle service equipment: glossary term only (EVSE / EV-ready); no guide topic']),
 ('D1-T6','Cooling: equipment and distribution','cooling_scope cooling_types ductless_cooling heatpump_modes heatpump_inspection geothermal cooling_water_air',[]),
 ('D1-T7','Heating: equipment, distribution and vent systems','heating_controls combustion_air furnace_types furnace_safety venting furnace_access furnace_airflow temperature_rise furnace_vent_details heat_exchanger_limits furnace_accessories oil_storage oil_burners oil_draft gravity_furnaces hydronic_systems steam_systems electric_heat_delivery',[]),
 ('D1-T8','Insulation, moisture management and ventilation of attics, crawl spaces and foundations','insulation_materials air_vapor_thermal ventilation_exhaust attic_environment crawl_moisture crawl_openings',[]),
 ('D1-T9','Mechanical exhaust and indoor air management','ventilation_exhaust kitchen_appliances bath_laundry furnace_airflow furnace_accessories',['B. Indoor air management (air cleaners, humidifiers, dehumidifiers): partial, through furnace accessories only']),
 ('D1-T10','Plumbing: supply, fixtures, DWV, water heating, fuel storage and distribution, pumps','water_supply plumbing_materials backflow_dwv plumbing_fixture_checks dwv_traps_vents drainage_pumps water_heater_identity water_heater_relief water_heater_installation water_heater_variants gas_piping oil_storage kitchen_waste bath_laundry',[]),
 ('D1-T11','Interior: surfaces, doors, windows, stairs, countertops and cabinets, kitchen appliances, smart home','interior_facings interior_moisture floor_finishes interior_doors safety_glazing interior_stairs window_operation_detail kitchen_appliances kitchen_waste',['C. Installed countertops and cabinets: W1 route reminder only; no guide topic','E. Smart home technology: no guide topic']),
 ('D1-T12','Fireplaces, fuel-burning appliances, chimneys and vents: solid fuel and gas/liquid fuel','fireplace_masonry fireplace_factory_gas chimney_parts venting furnace_vent_details combustion_air',['S39 ends at fireplace screen 13/15: screens 14-15 and the Unit 6 exam were not captured']),
 ('D1-T13','Life safety: egress, fire separation, smoke and CO alarms, fire sprinklers','egress_openings interior_life_safety garage_separation garage_appliances safety_glazing interior_stairs rails_guards',['4. Fire suppression / sprinkler systems: mentioned as an access limit only; no guide topic']),
 ('D2-T1','Inform the client what was inspected, methods used, and describe systems by characteristics','inspection_method reporting report_workflow',[]),
 ('D2-T2','Describe limitations: what was not inspected and why','site_access_limits access_and_services heat_exchanger_limits report_workflow reporting',['3. Limitations from smart and emerging technology: no guide topic']),
 ('D2-T3','Describe systems and components not functioning properly or defective','reporting report_workflow movement moisture',['1. Expected service life: guide deliberately separates condition from age estimates (roof_cover_condition); no service-life reference table']),
 ('D2-T4','Describe systems and components needing further evaluation or action','report_workflow special_service_boundaries reporting',[]),
 ('D3-T1','Pre-inspection agreement: scope, limitations, terms, privacy, timing','professional_scope special_service_boundaries',[]),
 ('D3-T2','Quality, integrity and objectivity: legal concepts, conflicts, financial protection, client interest','professional_scope report_workflow',[])]

def apply(d,compact,apps,walk):
    topics={p['id'] for p in d['pages']}
    families=[]
    for id,label,ids,gaps in FAMILIES:
        keys=ids.split();missing=[k for k in keys if k not in topics];assert not missing,(id,missing)
        status='reviewed against the NHIE outline for SG-010; '+('gaps listed' if gaps else 'no knowledge-item gap found')+'; publication QA pending'
        families.append(dict(id=id,task_family=label,topic_ids=keys,gaps=gaps,status=status,weight_is_not_field_risk=True))
    unmapped=sorted(topics-{k for f in families for k in f['topic_ids']})
    coverage=read(OUT/'scope-coverage.json')
    coverage.update(families=families,status='SG-010 coverage review complete; listed gaps remain open',unmapped_topics=unmapped,reviewed_on='2026-09-21',labels='Official NHIE content outline task families')
    save(OUT/'scope-coverage.json',coverage);apps['APP-B']['scope_coverage']=families
