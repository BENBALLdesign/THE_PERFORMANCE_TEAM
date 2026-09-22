"""Step 2 + 3 of the THE PERFORMANCE TEAM separation: populate the checkout and cut the BBDF dependencies.

Copies are recorded with origin path and hash; every patch is an exact, single-occurrence text replacement
that fails closed. Line endings are preserved byte-for-byte on files that are not patched, and patched files
keep their original newline style. Nothing in the installation, BB_CODE or the Seed Bank is modified.
"""
import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

CO = Path(r'C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM')
TEAM = Path(r'C:\Users\benja\Dropbox\THE PERFORMANCE TEAM')
CODE = Path(r'C:\Users\benja\Dropbox\BEN_BALL\BB_CODE')
DESIGN = Path(r'C:\Users\benja\Dropbox\BEN_BALL\BB_DESIGN\03_Marketing\BBDF_DESIGN_SYSTEM')
PROD = TEAM / 'Home Inspection Training/SG-010 Production'
CARRY = TEAM / 'CODE CARRY/bb_code'
SC = CODE / '.scratch'

assert not (CO / '.git').exists(), 'checkout already has a git history'
receipt = []
patches_applied = []


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def copy(src, dst):
    src = Path(src)
    dst = CO / dst
    assert src.is_file(), src
    if dst.exists():
        assert sha(dst) == sha(src), ('exists and differs', dst)   # pristine copy from an earlier attempt: reuse
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    receipt.append(dict(file=dst.relative_to(CO).as_posix(), origin=str(src), origin_sha256=sha(src), bytes=src.stat().st_size))


def patch(rel, pairs):
    p = CO / rel
    with p.open('r', encoding='utf-8', newline='') as f:
        s = f.read()
    crlf = '\r\n' in s
    for a, b in pairs:
        if crlf:
            a = a.replace('\n', '\r\n')
            b = b.replace('\n', '\r\n')
        n = s.count(a)
        assert n == 1, (rel, n, a[:80])
        s = s.replace(a, b)
    with p.open('w', encoding='utf-8', newline='') as f:
        f.write(s)
    row = next(x for x in receipt if x['file'] == rel)
    row.update(patched=True, patches=len(pairs), sha256=sha(p))
    patches_applied.append(dict(file=rel, replacements=[dict(before=a, after=b) for a, b in pairs]))


# ---------------------------------------------------------------- copies
# Production scripts and their small data (the live pipeline).
for p in sorted(PROD.iterdir()):
    if p.is_file() and p.suffix in ('.py', '.json', '.md'):
        copy(p, 'production/sg010/' + p.name)
copy(SC / 'recording-20260921-020522/source.json', 'production/sg010/data/recording-20260921-020522-source.json')

# Builder package: only the modules the production scripts import (statically or through cards_sg010.load),
# plus the small data files they read. The rest of .scratch/sg010 is history (Builder Snapshot, Seed Bank).
BUILDER_MODULES = ['additional_topics', 'build', 'card_brand', 'card_inspection_layer', 'content_s33', 'content_s38',
                   'design_language', 'edition', 'editorial', 'field_card_bindings', 'field_card_concordance',
                   'field_cards_64', 'field_cards_64_content', 'field_cards_layer2', 'glossary', 'housing',
                   'maryland_marker', 'navigation', 'prepare', 'setup', 'supplements', 'timeline', 'verified_scores',
                   'walking']
for m in BUILDER_MODULES:
    copy(SC / 'sg010' / (m + '.py'), 'builder/' + m + '.py')
for d in ['housing-data.json', 'navigation.json', 'incoming-inventory.json']:
    copy(SC / 'sg010' / d, 'builder/' + d)
copy(SC / 'property-505-r2/atlas_brand.py', 'builder/property-505-r2/atlas_brand.py')
copy(SC / 'property-505-r2/maryland_marker.py', 'builder/property-505-r2/maryland_marker.py')
copy(SC / 'property-505-r2/assets/BENBALL_A_CANONICAL.svg', 'builder/property-505-r2/assets/BENBALL_A_CANONICAL.svg')
copy(SC / 'sg009-color-language/paint.py', 'builder/sg009-color-language/paint.py')
copy(SC / 'sg009/field-cards/cards.json', 'builder/data/sg009/field-cards/cards.json')

# Tools and their test (CODE CARRY, byte-identical to the untracked BB_CODE originals).
for p in sorted((CARRY / 'tools').iterdir()):
    copy(p, 'tools/' + p.name)
copy(CARRY / 'tests/test_recording_archive.py', 'tests/test_recording_archive.py')

# Brand assets the renderers read (vendored from the design system; hashes recorded).
for t in ['palette.json', 'typography.json', 'spacing.json']:
    copy(DESIGN / 'tokens' / t, 'assets/brand/tokens/' + t)
copy(DESIGN / 'logos/BENBALL_A_CANONICAL.svg', 'assets/brand/logos/BENBALL_A_CANONICAL.svg')

# Registries (Ben ruling 2026-09-22: move to the checkout; the installation will point here).
for r in ['STUDY-GUIDE-EDITIONS.json', 'APPENDIX-VERSIONS.json']:
    copy(TEAM / r, 'registries/' + r)
for r in ['recordings-catalog.json', 'recordings-catalog.csv', 'recording-aliases.csv']:
    copy(TEAM / 'Sound Recordings' / r, 'registries/' + r)
copy(TEAM / 'Home Inspection Training/Library/CURRENT.json', 'registries/Library/CURRENT.json')

# Extraction skills (portable, no machine paths).
SK = TEAM / 'Sound Recordings/skills/portable-v1.2'
for p in sorted(SK.rglob('*')):
    rel = p.relative_to(SK)
    if p.is_file() and 'tmp' not in rel.parts and '__pycache__' not in rel.parts and rel.name != 'local-settings.json':
        copy(p, 'skills/portable-v1.2/' + rel.as_posix())

# Provenance documents.
copy(TEAM / 'CODE CARRY/CARRY MANIFEST.json', 'docs/CARRY-MANIFEST.json')
copy(TEAM / 'CODE CARRY/README.md', 'docs/CODE-CARRY-README.md')
copy(TEAM / '__SORT__/SG-010 - HANDOFF 4 - TO BEN - PERFORMANCE TEAM SEPARATION.md', 'docs/HANDOFF-4-SEPARATION.md')

# ---------------------------------------------------------------- patches (step 3: cut the BBDF dependencies)
patch('production/sg010/prepare.py', [
    ("REPO=Path('C:/Users/benja/Dropbox/BEN_BALL/BB_CODE')\nBUILDER=REPO/'.scratch/sg010'\nsys.path.insert(0,str(REPO/'tools'))\nimport home_inspection_storage as storage\n",
     "REPO=HERE.parents[2]   # THE_PERFORMANCE_TEAM checkout root (production/sg010 -> production -> root)\nBUILDER=REPO/'builder'\nsys.path.insert(0,str(REPO/'tools'))\nimport team_paths\nimport home_inspection_storage as storage\n"),
    ("BASE=Path('C:/Users/benja/Dropbox/THE PERFORMANCE TEAM')\nTEAM=BASE\n",
     "BASE=team_paths.installation()   # the Dropbox installation: published reading material, never code\nTEAM=BASE\nREG=team_paths.REGISTRIES   # tracked registries live in the checkout\nLIBRARY_CURRENT=REG/'Library/CURRENT.json'\n"),
])
patch('builder/prepare.py', [
    ("BASE=Path('C:/Users/benja/Dropbox/THE PERFORMANCE TEAM')\n", "import team_paths\nBASE=team_paths.installation()\n"),
])
patch('builder/design_language.py', [
    ('"""Experimental SG-010 presentation: live BBDF tokens, distinct chart forms."""',
     '"""Experimental SG-010 presentation: vendored brand tokens (assets/brand), distinct chart forms."""'),
    ("ROOT=Path(__file__).resolve().parents[2]\nsys.path.insert(0,str(ROOT))\nfrom bbdf_core import paths\n",
     "ROOT=Path(__file__).resolve().parents[1]\nsys.path.insert(0,str(ROOT/'tools'))\nimport team_paths\n"),
    ("_assets=paths.resolve('bb_design','03_Marketing/BBDF_DESIGN_SYSTEM')\n",
     "_assets=team_paths.brand()   # vendored print tokens and canonical logo\n"),
])
patch('builder/card_brand.py', [
    ("from bbdf_core.paths import resolve\n\nLOGO = resolve('bb_design', '03_Marketing/BBDF_DESIGN_SYSTEM/logos/BENBALL_A_CANONICAL.svg')\n",
     "import sys\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))\nimport team_paths\n\nLOGO = team_paths.brand('logos/BENBALL_A_CANONICAL.svg')\n"),
])
patch('builder/field_cards_layer2.py', [
    ("sys.path.insert(0,str(HERE.parents[1]))\nfrom bbdf_core.paths import resolve\nTOKENS=resolve('bb_design','03_Marketing/BBDF_DESIGN_SYSTEM/tokens/palette.json')\n",
     "sys.path.insert(0,str(HERE.parent/'tools'))\nimport team_paths\nTOKENS=team_paths.brand('tokens/palette.json')\n"),
])
patch('builder/field_card_concordance.py', [
    ("LIBRARY=Path('C:/Users/benja/Dropbox/THE PERFORMANCE TEAM/Home Inspection Training/Study Guide Editions')\n",
     "import sys;sys.path.insert(0,str(HERE.parent/'tools'))\nimport team_paths\nLIBRARY=team_paths.installation()/'Home Inspection Training/Study Guide Editions'\n"),
])
patch('builder/sg009-color-language/paint.py', [
    ("HERE=Path(__file__).resolve().parent;TEAM=Path('C:/Users/benja/Dropbox/THE PERFORMANCE TEAM')\n",
     "HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[1]/'tools'));import team_paths;TEAM=team_paths.installation()\n"),
])
patch('tools/home_inspection_storage.py', [
    ("BANK = Path('F:/SEED BANK')\n", "import team_paths\n\nBANK = team_paths.seed_bank()\n"),
    ("    mirror = Path('C:/Users/benja/Dropbox/THE PERFORMANCE TEAM/Sound Recordings/recordings-catalog.json')\n",
     "    mirror = team_paths.registry('recordings-catalog.json')\n"),
])
patch('tools/home_inspection_page_frame.py', [
    ("CODE = Path(__file__).resolve().parents[1]\nsys.path.insert(0, str(CODE))\nfrom bbdf_core import paths\nTOKENS = paths.resolve('bb_design', '03_Marketing/BBDF_DESIGN_SYSTEM/tokens')\n",
     "sys.path.insert(0, str(Path(__file__).resolve().parent))\nimport team_paths\nTOKENS = team_paths.brand('tokens')\n"),
])
patch('tools/recording_archive.py', [
    ("MEDIA=Path('C:/Users/benja/Dropbox/THE PERFORMANCE TEAM/Sound Recordings')\nCATALOG='recordings-catalog.json'\n",
     "import sys;sys.path.insert(0,str(Path(__file__).resolve().parent))\nimport team_paths\n_installation=team_paths.installation(strict=False)\nMEDIA=(_installation/'Sound Recordings') if _installation else None   # None until installation.json names the installation\nCATALOG='recordings-catalog.json'\nMIRROR=team_paths.registry(CATALOG)   # the small tracked catalog copy; the bank copy stays authoritative for media\n"),
    ("save(bank/CATALOG,catalog);save(MEDIA/CATALOG,catalog)", "save(bank/CATALOG,catalog);save(MIRROR,catalog)"),
    ("confined(src,[MEDIA,bank])", "confined(src,[r for r in (MEDIA,bank) if r])"),
    ("confined(p,[MEDIA,bank])", "confined(p,[r for r in (MEDIA,bank) if r])"),
])
patch('tests/test_recording_archive.py', [
    ("self.patch2=patch.object(ra,'MEDIA',self.media);self.patch2.start()\n",
     "self.patch2=patch.object(ra,'MEDIA',self.media);self.patch2.start()\n        self.patch3=patch.object(ra,'MIRROR',self.root/'registries/recordings-catalog.json');self.patch3.start()\n"),
    ("def tearDown(self):self.patch1.stop();self.patch2.stop();self.tmp.cleanup()",
     "def tearDown(self):self.patch1.stop();self.patch2.stop();self.patch3.stop();self.tmp.cleanup()"),
])
patch('tools/home_inspection_library.py', [
    ("from collections import Counter\n", "from collections import Counter\n\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nimport team_paths\n"),
    ("def recording(query, team='C:/Users/benja/Dropbox/THE PERFORMANCE TEAM', limit=8):\n    \"\"\"Find originals through the mutable archive catalog without editing editions.\"\"\"\n    catalog_path=Path(team)/'Sound Recordings/recordings-catalog.json'\n",
     "def recording(query, team=None, limit=8):\n    \"\"\"Find originals through the mutable archive catalog without editing editions.\n\n    The catalog is a tracked registry of the checkout; team is accepted for call compatibility only.\n    \"\"\"\n    catalog_path=team_paths.registry('recordings-catalog.json')\n"),
    ("p=sub.add_parser('recording');p.add_argument('query');p.add_argument('--team',default='C:/Users/benja/Dropbox/THE PERFORMANCE TEAM');",
     "p=sub.add_parser('recording');p.add_argument('query');p.add_argument('--team',default=None);"),
])
patch('production/sg010/contents_sg010.py', [
    ("from bbdf_core import paths\n", "import team_paths\n"),
    ("_pal=json.loads((paths.resolve('bb_design','03_Marketing/BBDF_DESIGN_SYSTEM/tokens')/'palette.json').read_text(encoding='utf-8-sig'))['color']",
     "_pal=json.loads(team_paths.brand('tokens/palette.json').read_text(encoding='utf-8-sig'))['color']"),
])
patch('production/sg010/walker_sg010.py', [
    ("CODE = Path('C:/Users/benja/Dropbox/BEN_BALL/BB_CODE')\nsys.path[:0] = [str(CODE/'tools'), 'C:/Users/benja/.cache/home-inspection-pdf-tools',\n                str(CODE/'.scratch/property-505-r2')]\nimport pymupdf as fitz\n",
     "CODE = Path(__file__).resolve().parents[2]   # THE_PERFORMANCE_TEAM checkout root\nsys.path[:0] = [str(CODE/'tools'), str(CODE/'builder/property-505-r2')]\nimport team_paths\nteam_paths.ensure_pymupdf()\nimport home_inspection_storage as storage\nimport pymupdf as fitz\n"),
    ("PROP = Path('C:/Users/benja/Dropbox/THE PERFORMANCE TEAM/Property Reviews/505 Walker Ave')\nSG = Path('F:/SEED BANK/DATA_ARCHIVE/HOME_INSPECTION/Working Evidence/sg010-20260921')\n",
     "PROP = team_paths.installation()/'Property Reviews/505 Walker Ave'\nSG = storage.work_root('sg010-20260921')\n"),
])
patch('production/sg010/qa_sg010.py', [
    ("sys.path.insert(0,'C:/Users/benja/.cache/home-inspection-pdf-tools')\nimport pymupdf as fitz\n",
     "team_paths.ensure_pymupdf()\nimport pymupdf as fitz\n"),
])
patch('production/sg010/cards_sg010.py', [
    ("[(\"HERE/'field-cards/cards.json'\",\"HERE.parent/'sg009'/'field-cards/cards.json'\")]",
     "[(\"HERE/'field-cards/cards.json'\",\"HERE/'data/sg009/field-cards/cards.json'\")]"),
    ("(\"BASE=HERE/'field-cards'\",\"BASE=HERE.parent/'sg009'/'field-cards'\"),",
     "(\"BASE=HERE/'field-cards'\",\"BASE=HERE/'data/sg009/field-cards'\"),"),
    ("\"Builder modules live in BB_CODE/.scratch/sg010; the SG-010 driver is SG-010 Production/cards_sg010.py.\"",
     "\"Builder modules live in the THE_PERFORMANCE_TEAM checkout (builder/); the SG-010 driver is production/sg010/cards_sg010.py.\""),
    ("spec=importlib.util.spec_from_file_location('paint_sg009',REPO/'.scratch/sg009-color-language/paint.py')",
     "spec=importlib.util.spec_from_file_location('paint_sg009',BUILDER/'sg009-color-language/paint.py')"),
])
patch('production/sg010/prepare_content.py', [
    ("[read(REPO/'.scratch/recording-20260921-020522/source.json')]", "[read(HERE/'data/recording-20260921-020522-source.json')]"),
    (" catalog_path=BASE/'Sound Recordings/recordings-catalog.json'\n", " catalog_path=REG/'recordings-catalog.json'\n"),
])
patch('production/sg010/rehash_recordings.py', [
    ("CATALOG=BASE/'Sound Recordings/recordings-catalog.json'\n", "CATALOG=REG/'recordings-catalog.json'\n"),
])
patch('production/sg010/publish_sg010.py', [
    ("def staged(p):\n    q=PUB/Path(p).relative_to(TEAM);q.parent.mkdir(parents=True,exist_ok=True);return q\n",
     "REGDIR='_registries'   # staging folder for files whose live home is the checkout's registries/, not the installation\n"
     "ROOT_REGISTRIES={'STUDY-GUIDE-EDITIONS.json','APPENDIX-VERSIONS.json'}\n"
     "def staged(p):\n"
     "    p=Path(p)\n"
     "    q=PUB/REGDIR/p.relative_to(REG) if p.is_relative_to(REG) else PUB/p.relative_to(TEAM)\n"
     "    q.parent.mkdir(parents=True,exist_ok=True);return q\n"
     "def target_of(p):\n"
     "    \"\"\"Live path of a staged file: registries live in the checkout, everything else in the installation.\"\"\"\n"
     "    rel=Path(p).relative_to(PUB)\n"
     "    return REG.joinpath(*rel.parts[1:]) if rel.parts[0]==REGDIR else TEAM/rel\n"
     "def confine(t):\n"
     "    t=Path(t);return inside(t,REG) if t.resolve().is_relative_to(REG.resolve()) else inside(t,TEAM)\n"
     "def backup_rel(t):\n"
     "    t=Path(t);return Path(REGDIR)/t.relative_to(REG) if t.is_relative_to(REG) else t.relative_to(TEAM)\n"
     "def live_path(t):\n"
     "    \"\"\"Plans pinned before the separation name the registries at the installation root; they now live in the checkout.\"\"\"\n"
     "    t=Path(t)\n"
     "    if t.parent==TEAM and t.name in ROOT_REGISTRIES:return REG/t.name\n"
     "    if t==LIBRARY/'CURRENT.json':return LIBRARY_CURRENT\n"
     "    return t\n"),
    ("reg=read(TEAM/'STUDY-GUIDE-EDITIONS.json');reg.update(current_edition=", "reg=read(REG/'STUDY-GUIDE-EDITIONS.json');reg.update(current_edition="),
    ("stage_json(TEAM/'STUDY-GUIDE-EDITIONS.json',reg);", "stage_json(REG/'STUDY-GUIDE-EDITIONS.json',reg);"),
    ("ar=read(TEAM/'APPENDIX-VERSIONS.json');", "ar=read(REG/'APPENDIX-VERSIONS.json');"),
    ("stage_json(TEAM/'APPENDIX-VERSIONS.json',ar);", "stage_json(REG/'APPENDIX-VERSIONS.json',ar);"),
    ("registry=staged(TEAM/'STUDY-GUIDE-EDITIONS.json')\n    m.update(registry=str(TEAM/'STUDY-GUIDE-EDITIONS.json'),",
     "registry=staged(REG/'STUDY-GUIDE-EDITIONS.json')\n    m.update(registry=str(REG/'STUDY-GUIDE-EDITIONS.json'),"),
    ("assert sha(CURRENT/live['directory']['file'])==live['directory']['sha256'] and sha(TEAM/'STUDY-GUIDE-EDITIONS.json')==live['registry_sha256']",
     "assert sha(CURRENT/live['directory']['file'])==live['directory']['sha256'] and sha(REG/'STUDY-GUIDE-EDITIONS.json')==live['registry_sha256']"),
    ("t=TEAM/p.relative_to(PUB);inside(t,TEAM);before=", "t=target_of(p);confine(t);before="),
    ("keep={str(TEAM/p.relative_to(PUB)) for p in PUB.rglob('*') if p.is_file()}", "keep={str(target_of(p)) for p in PUB.rglob('*') if p.is_file()}"),
    ("s=inside(r['source'],PUB);t=inside(r['target'],TEAM);", "s=inside(r['source'],PUB);t=confine(r['target']);"),
    ("p=Path(r['target']);b=backup/p.relative_to(TEAM);cp(p,b)", "p=Path(r['target']);b=backup/backup_rel(p);cp(p,b)"),
    ("p=inside(r['target'],TEAM);assert (sha(p) if p.exists() else None)==r['before_sha256'];p.parent.mkdir",
     "p=confine(r['target']);assert (sha(p) if p.exists() else None)==r['before_sha256'];p.parent.mkdir"),
    ("plan=read(PLAN);assert read(LIBRARY/'CURRENT.json')['issue']==PARENT,'CURRENT.json already moved'",
     "plan=read(PLAN);assert read(LIBRARY_CURRENT)['issue']==PARENT,'CURRENT.json already moved'"),
    ("save(LIBRARY/'CURRENT.json',dict(issue=REV,", "save(LIBRARY_CURRENT,dict(issue=REV,"),
    ("for fn in ['STUDY-GUIDE-EDITIONS.json','APPENDIX-VERSIONS.json','TRAINING-DOCUMENT-MAP.md']:cp(TEAM/fn,data/fn)\n",
     "for fn in ['STUDY-GUIDE-EDITIONS.json','APPENDIX-VERSIONS.json']:cp(REG/fn,data/fn)\n    cp(TEAM/'TRAINING-DOCUMENT-MAP.md',data/'TRAINING-DOCUMENT-MAP.md')\n"),
    ("cp(LIBRARY/'CURRENT.json',data/'Library/CURRENT.json')", "cp(LIBRARY_CURRENT,data/'Library/CURRENT.json')"),
    ("for r in plan['writes']:assert sha(Path(r['target']))==r['sha256'],r['target']",
     "for r in plan['writes']:assert sha(live_path(r['target']))==r['sha256'],r['target']"),
    ("m=read(CURRENT/'_Maintenance/manifest.json');assert m['published'] and sha(TEAM/'STUDY-GUIDE-EDITIONS.json')==m['registry_sha256']",
     "m=read(CURRENT/'_Maintenance/manifest.json');assert m['published'] and sha(REG/'STUDY-GUIDE-EDITIONS.json')==m['registry_sha256']"),
    ("reg=read(TEAM/'STUDY-GUIDE-EDITIONS.json');assert reg['current_edition']=='SG-010'",
     "reg=read(REG/'STUDY-GUIDE-EDITIONS.json');assert reg['current_edition']=='SG-010'"),
    ("if r['before_sha256'] is not None:assert sha(b/Path(r['target']).relative_to(TEAM))==r['before_sha256']",
     "if r['before_sha256'] is not None:assert sha(b/backup_rel(r['target']))==r['before_sha256']"),
    ("package=LIBRARY/REV;cur=read(LIBRARY/'CURRENT.json');", "package=LIBRARY/REV;cur=read(LIBRARY_CURRENT);"),
])

# ---------------------------------------------------------------- receipt
dropped = dict(
    builder_snapshot='Home Inspection Training/SG-010 Handoff/Builder Snapshot: not tracked (Ben ruling 2026-09-22); the live production scripts and builder/ are the code, the snapshot stays in the installation and the Seed Bank',
    scratch_modules_not_imported=['edition_inspection_layer', 'mark_maryland', 'card_inspection_drawings'],
    scratch_reason='listed in CARRY MANIFEST as builder modules but not imported by any production script (static import or cards_sg010.load); both create folders at import time',
)
doc = dict(schema='performance-team-separation-build/1',
           built_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
           checkout=str(CO), installation=str(TEAM), bb_code=str(CODE), design_system=str(DESIGN),
           purpose='Steps 2-3 of the separation (handoff 4): copy code, contracts, registries and brand assets into the checkout and cut every BBDF dependency; installation, BB_CODE and Seed Bank untouched.',
           files=len(receipt), patched=sum(1 for r in receipt if r.get('patched')), copies=receipt, patches=patches_applied, dropped=dropped)
out = CO / 'docs/SEPARATION-BUILD.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('BUILT', doc['files'], 'files,', doc['patched'], 'patched ->', out)
