"""Prepare cumulative SG-010 data from the frozen SG-009 baseline. Prepares data only; never publishes."""
from prepare import *
import content_s33
REVIEWED={
 'S33':'full speech reviewed; incorporated by content_s33',
 'S34':'full speech reviewed; incorporated by content_s34',
 'S35':'full speech reviewed; incorporated by content_scope',
 'S36':'opening outline and screens reviewed; incorporated by content_scope',
 'S37':'result screen visually verified; incorporated by content_assessment',
 'S38':'full meaningful speech reviewed; incorporated by content_s38',
 'S39':'repaired recording; speech and screens reviewed through fireplace screen 13/15 (end of file); incorporated by content_s39'}
ORDER=['method','foundation_water','load_paths','movement','roof_structure','walls','openings','site_decks','garage','roof_cover','water','dwv','water_heat','gas','service','circuits','devices','gas_heat','furnace_service','oil_heat','hydronic_electric','cooling','heatpumps','insulation','appliances','life_safety','interior_routes','scope']
VERSIONS={'APP-A':'1.8','APP-B':'1.7','APP-C':'1.9','APP-D':'1.3','APP-E':'1.4','APP-F':'1.3','APP-G':'1.3','APP-H':'1.2'}
def main():
 old=read(WORK/'baseline/SG-009-L1/study-guide.json')
 d=json.loads(json.dumps(old,ensure_ascii=False).replace('../SG-009/',''))
 compact=read(WORK/'baseline/SG-009/study-guide.json')['pages']
 walk=read(WORK/'baseline/SG-009-W1/study-guide.json')['pages']
 apps={a['id']:read(WORK/'baseline/SG-009'/a['path'].replace('.html','.json')) for a in old['appendices']}
 content_s33.apply(d,compact,apps,walk)
 for module in ['content_s34','content_scope','content_assessment','content_s38','content_s39','content_coverage']:
  if (HERE/(module+'.py')).exists():__import__(module).apply(d,compact,apps,walk)
 # Modules insert topics beside related ones; keep every L1 section contiguous (stable, first-appearance order).
 sections=list(dict.fromkeys(p['section'] for p in d['pages']))
 d['pages'].sort(key=lambda p:sections.index(p['section']))
 d['hierarchy']['domains']=[dict(first_topic=next(p['id'] for p in d['pages'] if p['section']==s),title=s) for s in sections]
 # Historical source and attempt records retain their original attribution.
 sources=read(WORK/'baseline/SG-009/intake-sources.json')+[read(HERE/'data/recording-20260921-020522-source.json')]
 sources+=read(BUILDER/'incoming-inventory.json')['new_sources']
 for source in sources:
  if source.get('id') in REVIEWED:source['status']=REVIEWED[source['id']]
 catalog_path=REG/'recordings-catalog.json'
 if catalog_path.exists():
  catalog=read(catalog_path);locations={r['source_sha256']:r for r in catalog['records']}
  for source in sources:
   location=locations.get(source['source_sha256'])
   if location:
    source.setdefault('prior_source_path',source.get('source_path',''))
    source['source_path']=location['canonical_path'];source['archive_recording_id']=location['recording_id'];source['source_location_catalog']=str(catalog_path)
 d.update(edition='SG-010-L1',edition_family='SG-010',date='21 September 2026',edition_date='2026-09-21',title='Home Inspection Study Guide - The long cut',companion='SG-010',presentation_revision=REV,edition_change='SG-010 cumulative incorporation and scope/organization review',prior_edition_metadata={'edition':'SG-009','issue':'S32-C1-2026-09-21','preserved':True},sources=sources,source_coverage=f"S01-S{len(sources):02}; recorded lessons, references and assessment evidence remain separately identified.")
 d['reference_pages']=apps['APP-D']['pages'];d['exam_pages']=apps['APP-G']['pages']
 apps['APP-D']['terms'].sort(key=lambda x:x['term'].casefold())
 apps['APP-E']['sources']=sources
 apps['APP-E']['coverage_note']='Cumulative source register for SG-010. S32 is a short reference bookmark; S33-S35 extend lessons and recorded reviews; S36-S37 record an initial practice assessment and result; S38 adds hydronic, steam, electric heat and cooling lessons; S39 is the repaired interior recording (floors, openings, stairs, fireplaces) and ends at fireplace screen 13/15. Course completion and practice scores remain distinct.'
 for aid,a in apps.items():
  a.update(version=VERSIONS[aid],edition='SG-010',date='2026-09-21',presentation_revision=REV)
  if 'issued_with' in a:a['issued_with']='SG-010'
  if 'history' in a and isinstance(a['history'],list):a['history'].append(dict(version=VERSIONS[aid],date='2026-09-21',edition='SG-010',change='Cumulative final-course incorporation and reference review; stable item IDs retained.'))
  save(OUT/f'Appendices/{aid}-v{VERSIONS[aid]}.json',a)
 d['appendices']=[dict(id=aid,version=VERSIONS[aid],title=a['title'],path=f'Appendices/{aid}-v{VERSIONS[aid]}.html',pdf=f'Appendices/{aid}-v{VERSIONS[aid]}.pdf') for aid,a in apps.items()]
 # Physical route order: systems before rooms; scope and follow-through close the set.
 assert set(ORDER)=={p['id'] for p in compact},({p['id'] for p in compact}^set(ORDER))
 compact.sort(key=lambda p:ORDER.index(p['id']))
 for p in compact:
  p['title']=str(compact.index(p)+1).zfill(2)+'  '+p['title'].split('  ',1)[-1]
 for fn,value in [('study-guide-L1.json',d),('compact-editorial.json',dict(pages=compact)),('walking-editorial.json',dict(pages=walk)),('intake-sources.json',sources)]:save(OUT/fn,value)
 save(HERE/'editorial-review.json',dict(edition='SG-010',status='staged; publication verification pending',parent='S32-C1-2026-09-21',new_topics=[p['id'] for p in d['pages'] if p['id'] not in {q['id'] for q in old['pages']}],versions=VERSIONS,compact_charts=len(compact),L1_topics=len(d['pages']),glossary_terms=len(apps['APP-D']['terms']),source_count=len(sources),reviewed_S33_corrections=content_s33.CORRECTIONS))
 print('Prepared',len(d['pages']),'topics;',len(compact),'compact charts;',len(sources),'sources')
if __name__=='__main__':main()
