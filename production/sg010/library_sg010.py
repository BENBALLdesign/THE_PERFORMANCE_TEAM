"""SG-010 library package (Part A step 6): fresh records and relations from the staged SG-010 owners.

Wraps the parameterized BB_CODE/tools/home_inspection_library.py: the staged tree (shelf_sg010.STAGE) overlays
THE PERFORMANCE TEAM, the SG-010 edition data and APP-D v1.3 are selected explicitly. Frozen published packages
under Library/ are never touched; Library/CURRENT.json is not moved until Part B QA.
"""
from prepare import *
sys.path.insert(0,str(REPO/'tools'))
import home_inspection_library as lib
from shelf_sg010 import STAGE
PKG=WORK/'library'/REV
def main():
    assert (STAGE/'Home Inspection Training/CURRENT EDITION/_Maintenance/manifest.json').exists(),'run shelf_sg010.py first'
    if PKG.exists():shutil.rmtree(PKG)  # a staged package, rebuilt from its owners each run; published packages live in Library/
    result=lib.build(BASE,PKG,overlay=STAGE,edition='SG-010',glossary='APP-D-v1.3.json')
    status=lib.verify(PKG,BASE,STAGE)
    assert status['status']=='current',status
    lookups={}
    for q,expect in [('QC-033','QC-033'),('P505-09','P505-09'),('AFCI','APP-D:term:afci'),('Hartford Loop','APP-D:term:hartford-loop'),('SG-010-L1:steam_systems','SG-010-L1:steam_systems')]:
        r=lib.lookup(PKG,q,limit=1)['results']
        lookups[q]=r[0]['record']['id'] if r else None
        if expect:assert lookups[q]==expect,(q,lookups[q])
    assert lib.lookup(PKG,'zzzz_nonexistent_term_019724')['results']==[]
    rows=[json.loads(l) for l in (PKG/'records.jsonl').read_text(encoding='utf8').splitlines()]
    unavailable=[r['id'] for r in rows for x in r['routes'] if x.get('availability')=='unavailable in current reading set']
    kinds={k:sum(r['kind']==k for r in rows) for k in sorted({r['kind'] for r in rows})}
    report=dict(package=str(PKG),result=result,verify=status,kinds=kinds,lookups=lookups,routes_unavailable=sorted(set(unavailable)),
                current_pointer='not set; Library/CURRENT.json unchanged until Part B QA',frozen_packages='untouched')
    save(WORK/'library'/'staged-build-report.json',report);print(json.dumps(report,indent=1))
if __name__=='__main__':main()
