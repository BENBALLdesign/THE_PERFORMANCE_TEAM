from pathlib import Path
import json,shutil,sys,hashlib,copy
HERE=Path(__file__).resolve().parent
REPO=HERE.parent   # THE_PERFORMANCE_TEAM checkout root (HERE=builder)
sys.path.insert(0,str(REPO/'tools'))
import home_inspection_storage as storage
WORK=storage.work_root('sg010-20260921')
OUT=WORK/'output'
import team_paths
BASE=team_paths.installation()
TEAM=BASE
LIB=BASE/'Home Inspection Training/Study Guide Editions'
OLD=WORK/'baseline/SG-009'
REV='SG-010-2026-09-21'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
