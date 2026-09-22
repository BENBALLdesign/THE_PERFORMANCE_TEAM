# Ben to Ben: where everything is and what to do next

22 September 2026, end of the separation session. Not a BBDF filing. Copies: Team `__SORT__`, `Home Inspection Training\SG-010 Handoff`, and the repo at `docs\HANDOFF-7-BEN-TO-BEN.md`.

## Where things live

| Thing | Path |
| --- | --- |
| Team repo (code, registries, receipts) | `C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM`, `main`, pushed to `https://github.com/BENBALLdesign/THE_PERFORMANCE_TEAM` (head `df3b5ca`) |
| Installation (reading material only, 0.8 GB) | `C:\Users\benja\Dropbox\THE PERFORMANCE TEAM`, named by the repo's ignored `installation.json`; `REGISTRIES.json` at its root points to the repo |
| Seed Bank domain | `F:\SEED BANK\DATA_ARCHIVE\HOME_INSPECTION` (`README.md` there documents `Backups`, `Issues`, `Session Evidence`, `Working Evidence`, `_META`) |
| Recordings | `F:\SEED BANK\RECORDINGS`, catalog `registries\recordings-catalog.json` |
| Published shelf | `THE PERFORMANCE TEAM\Home Inspection Training\CURRENT EDITION` (SG-010-P1-2026-09-22, 50 PDFs, 887 pp; core print set 295 pp) |
| Library | `Home Inspection Training\Library\SG-010-P1-2026-09-22`, verified `current` |
| Python to use | `C:\Users\benja\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -B` (system Python 3.14 runs the tests) |
| Bug board | repo `docs\PINBOARD.md` (5 pins, 3 fixed); BBDF PIN-1014 on spec:107 |
| Site image brief | `C:\Users\benja\Dropbox\BenBallDesign\Design-Fabrication\IMAGE-CLASSIFICATION-BRIEF-2026-09-22.md` |
| Storage survey | Team `__SORT__\STORAGE WEIGHT AND REDUNDANCY 2026-09-22.md` (also `docs\surveys` in the repo) |

## What is done

Separation steps 1-5 and half of 6: baseline hashed, checkout built and BBDF cut, proof run byte-identical, first commits pushed, registries retired from the installation. Evidence relocation `20260922-evidence-routing` complete: 50,232 files / 6.26 GB into the bank, 23 pointers, library `current`. Publish verify passes (with the known receipt-assertion exemption, pinned).

## Do next, in order

1. **Nest the installation** (fresh session started outside the installation folder, Dropbox idle):
   ```
   cd C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM
   python docs\separation-scripts\step6_registries_and_nest.py
   git add installation.example.json production\sg010\publish_sg010.py docs\SEPARATION-STEP6-RECEIPT.json
   git commit -m "Nest the installation under the checkout"
   git push
   ```
   Renames `THE PERFORMANCE TEAM` into `THE_PERFORMANCE_TEAM\THE PERFORMANCE TEAM`, rewrites 26 pointers, updates `installation.json`. If rename is denied again, close anything with a window or terminal inside the folder, wait for Dropbox to go idle, retry. Do not use the Dropbox web UI to move it (pointers would not be rewritten).
2. **Retire `Home Inspection Training\SG-010 Production`** in the installation: it is superseded by `production\sg010` in the repo (its copies read the old registry paths). Move it to the bank under `Working Evidence\sg010-production-dropbox-copy-20260922` with `tools\bank_relocation.py` (write a one-group spec), or delete after confirming `git ls-files production/sg010` covers it.
3. **Print test**: 295-page core set duplex (148 sheets) plus one card format (5x7 64 sheets or Letter 32). Check the grayscale band separation on paper; record the result in `production\sg010\PROGRESS.md`.
4. **Your reviews still open on SG-010**: 22 rebound cards and the QC-047 safety flag; practice-exam source match.
5. **Fix if you want it**: `publish_sg010.verify` receipt-removal assertion, one line (`docs\PINBOARD.md` row 1).

## Rulings only you can make (each unblocks a queued piece of work)

- **Storage**: re-point THE SEED's working vault so `BB_SEED\BB_BOOKS\library\Sources` (1.1 TB, duplicates D:, F:\IMAGES, ABSTRACTION nft) lives in the bank; split `ABSTRACTION nft` (271 GB) into code / outputs / sources / clouds; pick the canonical `CLOUDS` and `IMAGES` copy between D: and F:; fold or delete Dropbox `DATABSTRACT` (8 files).
- **DATAbstract extraction**: adapters/exports vs its own installation; `DATAbstract` vs `DATABSTRACT` naming; storefront repo or a second app. Then commit the storefront's 102 changed files in four commits (ignore rules first, scripts after checking `probe-metaplex.mjs` / `ingest-held.mjs` for keys, ledger, docs + package).
- **Website images**: category vocabulary; `tier` vs `hero`; held originals in git or bank; which Product Photos are portfolio; Fractals/NFT on the page or not; client name and address exposure; a spec number for the site. First clear the half-finished `stained-oak-library` promote (8 uncommitted files).

## Rules that held this session

No BBDF filing, rows, rooms or personas for Team work. Stage git by explicit path (the BBDF stage-door hook fires in every repo). Every bug found goes on a board. Nothing bulk is written into Dropbox; the bank is checked by vault id before any bulk write.
