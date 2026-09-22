"""Shared paths for SG-010 production (Performance Team). Bulk work stays in the Seed Bank."""
from pathlib import Path
import json,shutil,sys,hashlib,copy
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]   # THE_PERFORMANCE_TEAM checkout root (HERE=production/sg010; parents[0]=production; parents[1]=root)
BUILDER=REPO/'builder'
sys.path.insert(0,str(REPO/'tools'))
import team_paths
import home_inspection_storage as storage
WORK=storage.work_root('sg010-20260921')
OUT=WORK/'output'
BASE=team_paths.installation()   # the Dropbox installation: published reading material, never code
TEAM=BASE
REG=team_paths.REGISTRIES   # tracked registries live in the checkout
LIBRARY_CURRENT=REG/'Library/CURRENT.json'
LIB=BASE/'Home Inspection Training/Study Guide Editions'
OLD=WORK/'baseline/SG-009'
REV='SG-010-P1-2026-09-22'   # presentation revision P1 of SG-010 (first issue: SG-010-2026-09-21)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def merge_term(apps,term,definition,topic,source_pointer,refs):
 """Fold a later review into an existing (card-bound) glossary term instead of adding a near-duplicate."""
 t=next(x for x in apps['APP-D']['terms'] if x['term']==term)
 t['definition']=t['definition'].rstrip()+' '+definition
 t.setdefault('related_topics',[])
 if topic!=t.get('topic') and topic not in t['related_topics']:t['related_topics'].append(topic)
 t['source_pointer']+=' / '+source_pointer
 t['source_refs']=list(t.get('source_refs',[]))+list(refs)
