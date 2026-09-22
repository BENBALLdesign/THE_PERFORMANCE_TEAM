# Handoff 6 to Ben: Team repo committed; evidence relocation running; storage survey filed

Prepared 22 September 2026 at session close (turn cap). Owner: THE PERFORMANCE TEAM. Not a BBDF filing. Copy in `Home Inspection Training\SG-010 Handoff`.

## 1. Team repo

`C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM`, `main`, 7 commits, byte-exact blobs (`.gitattributes * -text`). Remote `origin` = `https://github.com/BENBALLdesign/THE_PERFORMANCE_TEAM.git`, **not yet created on GitHub, nothing pushed**. You: create the empty private repo under BENBALLdesign, then in the checkout `git push -u origin main`. Bug board: `docs\PINBOARD.md` (4 pins, 1 fixed). BBDF board: PIN-1014 on spec:107 (stage-door guard fires in every repo).

## 2. Evidence relocation (migration `20260922-evidence-routing`)

Tool `tools\bank_relocation.py`, spec `docs\relocations\20260922-evidence-routing.json`, plan pinned at `F:\SEED BANK\DATA_ARCHIVE\HOME_INSPECTION\_META\20260922-evidence-routing\` (50,470 files, 6.26 GB, 238 kept-in-place records). Copy: **verified complete**. Retire: **running at close** (PID started 02:39; re-hashes both sides before unlinking; first attempt stopped on a Dropbox-locked empty folder after group 1, fixed and rerun, journal makes it safe). Finish runs right after retire in the same background chain.

**Next session, first thing:**
```
cd C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM
python tools\bank_relocation.py docs\relocations\20260922-evidence-routing.json status
```
If `retirement-receipt.json` is present but `storage-completion.json` is not, run `finish`. If retire stopped, rerun `retire` (resumable). Then `docs\relocations\20260922-evidence-routing-receipt.json` appears; commit it. Expected result: installation drops from 7.06 GB to about 0.8 GB; pointers `SEED BANK LOCATION.json` in 23 folders; bank README documents the layout (`Session Evidence`, `Issues`, `Backups`, `Working Evidence`, `_META`). Then re-run `python production\sg010\publish_sg010.py verify` (passes with the receipt-removal exemption; see PINBOARD).

## 3. Still open, yours

- Step 6 registries: retire the Dropbox copies, write `REGISTRIES.json` pointer; `SG-010 Production` folder then superseded.
- Nest the installation under the checkout: rename + rewrite `original_root` in 26 pointers and `installation.json`; `publish_sg010.live_path` needs the old root mapped. Fresh session.
- Storage rulings from `__SORT__\STORAGE WEIGHT AND REDUNDANCY 2026-09-22.md`: SEED working vault re-point (1.1 TB of `BB_SEED\BB_BOOKS\library\Sources` duplicates D:, F:\IMAGES, ABSTRACTION nft), ABSTRACTION nft split (250 GB), canonical CLOUDS/IMAGES copy, DATABSTRACT stub.
- DATAbstract extraction: installation-data migration, blocked on adapters-vs-installation, naming, target repo.
- Design-Fabrication images: brief at `Dropbox\BenBallDesign\Design-Fabrication\IMAGE-CLASSIFICATION-BRIEF-2026-09-22.md`; pipeline exists (`scripts\import_photos.py`), scale it; clear the 8 uncommitted files first.

## 4. Session files

Scripts used this session are committed under `docs\separation-scripts\` (baseline, build, proof) and `docs\surveys\` (weight survey, drive index, pair verification, media match) with the survey outputs. Scratchpad is session-temp and can be deleted.
