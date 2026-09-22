# Handoff 4 to Ben: SG-010 closed; next, THE PERFORMANCE TEAM as its own repository

Prepared 22 September 2026 by the SG-010 Part B session. Owner: THE PERFORMANCE TEAM. Not a BBDF filing; no row, queue, room or message was used. Placed in `BEN_BALL\__SORT__` at your request; a copy sits in `Home Inspection Training\SG-010 Handoff`.

## 1. Where SG-010 stands

- **Published issue:** `SG-010-P1-2026-09-22` (presentation revision P1 of the cumulative SG-010 edition through S39). First issue `SG-010-2026-09-21` is archived byte-exact in the Seed Bank (`Backups\Current Set History\before-SG-010-P1-2026-09-22` and `Issues\SG-010-2026-09-21`). SG-009 / S32-C1 is archived under `before-SG-010-2026-09-21`.
- **Shelf:** `Home Inspection Training\CURRENT EDITION`: 50 PDFs (compact 32 pp, L1 127 pp, W1 8 pp, 8 + 8 appendix cuts, 64 cards + 32 Letter sheets, 505 Walker packet 20 pp + five standalones, 21 source PDFs, CC-S32-01, `00 - START HERE.pdf`). Receipt: `_Maintenance\publication-receipt.json`.
- **Library:** `Library\SG-010-P1-2026-09-22` (verify current), `Library\CURRENT.json` points to it. Frozen SG-009 and first-issue packages untouched.
- **Your rulings recorded** (`Study Guide Editions\SG-010\field-card-acceptance.json`, README, HANDOFF STATE): issue id kept; 22 rebound cards + QC-047 flag accepted; 31 subject aliases accepted as retrieval routes; P1 fixes applied (grayscale retune, pagination control, continuation tabs, gutter crabs, compact p.19 figure).
- **Still open, stated not hidden:** no physical print test; practice-exam source unmatched (S37 result clip staged separately); S39 fireplace screens 14-15 and Unit 6 exam missing; no card for hydronic/steam/electric heat or fireplace operation; NHIE gaps in APP-B; H14 unavailable.
- **BB_CODE tools:** not committed in BB_CODE. Recorded byte-exact in `THE PERFORMANCE TEAM\CODE CARRY` (`CARRY MANIFEST.json`: origins, hashes, git status) for the future Team repository commit.

## 2. What you asked for next

Separate THE PERFORMANCE TEAM into its own repository using THE SEED process (`C:\Users\benja\Dropbox\BB_SEED` is the worked example: `README.md`, `BB_CODE\docs\GIT-SEPARATION.md`, `SIBLING-CHECKOUTS.md`, `CLEAN-BRANCHES.md`, `HANDOFF-PROCESS.md`).

## 3. Proposed approach (for your ruling before anyone starts)

**Pattern from THE SEED:** git owns code, contracts, tests and small registries; installation records and published reading material stay local and ignored; bulk media stays in an external vault referenced by small JSON pointers; a new intent is a new checkout, never a branch switch inside a populated folder.

**Applied to the Team:**

| Layer | What | Where it lives | Git |
|---|---|---|---|
| Code | `SG-010 Production` scripts (pipeline, publish, QA), `CODE CARRY\bb_code` (library, storage, page frame, recording archive tools + tests), extraction skills in `Sound Recordings\skills\portable-v1.2`, Builder Snapshot as reference modules | new repo | tracked |
| Contracts and registries | `STUDY-GUIDE-EDITIONS.json`, `APPENDIX-VERSIONS.json`, `TRAINING-DOCUMENT-MAP.*`, shelf manifest and issue records, `Library\CURRENT.json`, recordings catalog + aliases, storage location pointers | new repo | tracked |
| Published reading material | `CURRENT EDITION`, `Study Guide Editions\*`, `Library\<issue>` packages, `Property Reviews` PDFs | Dropbox installation | ignored (hash-listed by the manifests that are tracked) |
| Bulk and history | recordings, extraction evidence, backups, frozen issue copies, QA proofs | `F:\SEED BANK` | external, referenced by `SEED BANK LOCATION.json` pointers |

**Sequence (proposed):**
1. Freeze a baseline: hash every file under THE PERFORMANCE TEAM (small JSON), so the split can be verified as lossless.
2. New checkout folder (not `git init` inside the live Dropbox tree): e.g. `C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM` or a path you name. Copy code + registries in; write `.gitignore` for PDFs, evidence, `Library\<issue>\owners`, caches. Requirements file from the codex runtime (`reportlab pypdf pdfplumber pymupdf pillow numpy lxml`).
3. Cut the BBDF dependencies: `bbdf_core.paths` (logo `BENBALL_A_CANONICAL.svg`, `palette.json`) becomes a vendored asset or a local resolver; `BB_CODE\.scratch\sg010` modules become a tracked `builder\` package; the PyMuPDF side-path (`C:\Users\benja\.cache\home-inspection-pdf-tools`) becomes a requirement.
4. Prove it: from the new checkout run `shelf_sg010 -> library_sg010 -> qa_sg010` against the installation and confirm the library verifies `current` with identical hashes; run the recording-archive tests.
5. First commit; remote under **BENBALLdesign** as a sibling of THE_SEED (name your call: `THE_PERFORMANCE_TEAM`). Publication review per GIT-SEPARATION: no PDFs, media, credentials or installation records in the payload.
6. Only then: the live Dropbox folder keeps the installation role; code edits happen in the checkout. Record the boundary in a `SEPARATION.md` like THE SEED's.

**Decisions you own:** checkout path and remote name; whether registries stay in Dropbox and are mirrored, or move to the checkout and are pointed to; whether the Builder Snapshot is tracked as history or dropped in favour of the live production scripts; whether the Team repo absorbs the BB_CODE tools (recommended, that is what CODE CARRY is for) or BB_CODE keeps them.

**Estimate:** one session for steps 1-4, a second for 5-6 with your review between them.

## 4. Size facts for the split

THE PERFORMANCE TEAM is 6.7 GB in Dropbox, almost all under `Home Inspection Training` (dated session evidence and intake folders, edition PDFs, frozen issue pointers); `Property Reviews` 23 MB, `ADMINISTRATION` 11 MB, `Sound Recordings` 2 MB (media already in the bank), registries and `CODE CARRY` under 200 KB. The git payload is therefore a few MB of code and JSON; everything else is installation or vault.

## 5. Pointers

- Production: `Home Inspection Training\SG-010 Production` (`PROGRESS.md`, `NEXT SESSION BRIEF.md`, `publish_sg010.py`).
- State: `Home Inspection Training\SG-010 Handoff\SG-010 - HANDOFF STATE.json`.
- Carry set: `THE PERFORMANCE TEAM\CODE CARRY\CARRY MANIFEST.json`.
- Seed Bank domain: `F:\SEED BANK\DATA_ARCHIVE\HOME_INSPECTION` (Backups, Issues, Working Evidence) and `F:\SEED BANK\RECORDINGS`.
