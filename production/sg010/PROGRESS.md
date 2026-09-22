# SG-010 production progress

Performance Team work. Not BBDF. Read with `../SG-010 Handoff/SG-010 - FRESH SESSION HANDOFF.md`.
Python: `C:\Users\benja\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -B`.

## How to rebuild (from this folder)

1. `prepare_content.py`: frozen SG-009 baseline + content modules S33-S39 + coverage, written to Seed Bank `output`. Data only.
2. `render_sg010.py appendices terms l1 compact_appendices compact walking`: renders into Seed Bank `output`. Never publishes.
   Always rerun all render stages after step 1, because prepare resets the appendix page indexes.

## Done (2026-09-21)

- **Step 1, S39 review:** `content_s39.py` covers Units 3-6: floors, glazing, egress, doors, stairs, fireplaces. The recording ends at fireplace screen 13/15 and the Unit 6 exam is missing; this is stated in N14, APP-G and D1-T12. Unit results: 8/9, 6/8, 4/4.
- **Step 2, prep and scope:**
  - This folder is self-contained for content. It has its own `prepare.py` and copies of all content modules.
  - Glossary near-duplicates are merged into card-bound baseline terms (`merge_term`).
  - APP-E coverage note and S33-S39 source statuses are updated.
  - Compact charts are in physical-route order (ORDER in prepare_content).
  - `content_coverage.py` maps all 19 NHIE families, using the official outline labels (content_scope had D2 labels swapped). Open gaps are listed rather than hidden: EVSE, indoor-air management (partial), countertops/cabinets, smart home, sprinklers, smart-tech limits, service-life table, and fireplace screens 14-15.
- **Renders, all in Seed Bank `output`:**

  | Item | Result |
  |---|---|
  | Long appendices A1.8/B1.7/C1.9/D1.3/E1.4/F1.3/G1.3/H1.2 | 86 pages. APP-B shows scope coverage; APP-H references render as a table (was str(dict)) |
  | APP-D term locator | 107 terms located. Writes `navigation.json` glossary_pages here |
  | L1 | 139 topics, 127 pages. Cover counts from data; sections from data; index with L1 / D locators |
  | Compact SG-010 | 28 charts, 32 pages (16 sheets). Two-column cover routes; finder of 43 entries routed by chart id; shelf lengths from data |
  | Compact appendices | Carried forward from the SG-009 compact JSON (`compact_sg010.py`); 18 pages; no SG-009 or "experimental" labels |
  | W1 | 8 pages. New: W / L / C path tags per step, plus the one-time COMBUSTION = energy route naming note (SG-009 W1 had none) |

- Pages spot-checked by eye: L1 cover, safety glazing, subject index; compact cover, chart 27, finder; W1 pp. 1 and 6; compact APP-D notes and APP-E.

## Remaining (handoff items)

- Semantic colour/pattern/area cues, safety crosses and MD crab on the new pages (`paint.py`, `mark_maryland.py`, `tools/home_inspection_page_frame.py`). None has been applied to SG-010 renders yet.
- Contents (`sg009-location-contents/contents.py`) and full navigation / FIND A SUBJECT, adapted to the new ranges.
- 64 cards (5x7 + Letter): update bindings for S33-S39 facts, with previous-to-current aliases. `field_cards_64` has import-time side effects.
- Walker: crosswalk and prompt updates; keep P1 frame and evidence; combined packet.
- Library builder parameterization; Start Here PDF; new shelf manifest; archive the previous CURRENT set to bank history; publish after full visual QA.
- Recording archive: finish the plan review (S06-S12 old prefixes, S13/S14 labels, S31/S32 punctuation), apply, then build the ledger PDF.
- W1 footer reads "W1 | COMPACT", inherited from the shared SG-009 frame; left unchanged on purpose.
- No new external references were added for S39; its numbers are attributed as course / Code Check values.

## Walker SG-010 staged update (2026-09-21, handoff item 8)

- Builder `walker_sg010.py` (this folder). Stage only: writes to Seed Bank `sg010-20260921\walker-sg010\` (`baseline`, `output`, `qa`). Property Reviews and CURRENT are untouched.
- Staged `output\505 WALKER - COMBINED PROPERTY REVIEW.pdf`: 20 pages, P1 frame, SHA-256 `146a80815f4b9829b4bd40f2d98373e1297825b8ea3998a6ee4a0dbf83f82fb3`. The 18-page baseline `612e244f...` is retained as pages 1-4 and 7-20.
  - New p5 is SG-010 routes: the retained evidence windows and 12 card routes to compact chart / L1 pages.
  - New p6 has 10 conditional prompts from S33/S34/S38/S39. They cite only retained findings F01-F06 and add 0 observed conditions.
  - Card footers and the p4 basis line were changed SG-009 -> SG-010 (and S31 -> S39) as width-neutral swaps. All footers are regenerated n/20.
  - Body pixels are unchanged on all 18 retained pages at 72 dpi (asserted).
- `output\concordance-SG010-crosswalk.json` has topic routes old->new (only cooling 24->25 and heat pumps 25->26 moved), 222 fact aliases (1 with revised wording; 12 were not in the prior crosswalk), prompts and APP-C v1.9 mention IDs. `output\change-manifest.json` has the page map, text edits and body checks.
- Deliberately unchanged:
  - The p13 Visual R2 subtitle "...existing property cards and SG-009." (historical statement).
  - Standalone 5x7, Letter, findings, imagery and outline PDFs.
  - QC and N numbers on the cards.
- Open: the standalone card and findings PDFs still read SG-009. Recheck QC bindings after the 64-card update (item 7). Publishing still needs the release pass (manifest, combined-packet.json, README, backup). Fireplace prompts rest on S39 screens 1-13.

## 64 general field cards (2026-09-21, staged only)

- Driver: `cards_sg010.py` (fails closed on a stale lock; `--establish` = explicit re-review). Review lock: `field-card-review-lock.json`. Alias map: `field-card-fact-aliases-SG009-to-SG010.json` (also copied to the output folder).
- Basis: the published SG-009 deck (baseline cards.json/concordance, including E1 QC-033 and the S32 QC-047 note). Card wording, IDs QC-001..064 and area groups are unchanged. Import side effects are patched out: no Dropbox mkdir, and nothing goes to CURRENT/Editions.
- Output: `WORK/field-cards-64-sg010/painted/` holds the 5x7 PDF (64 pp) and the Letter PDF (32 pp), with the SG-009 C1 paint layer (area colour, hatch, dots). Unpainted versions and all data are in `WORK/field-cards-64-sg010/`. The change report is `sg010-card-update.json`. QA PNGs are in `qa/`.
- Alias map: all 110 SG-009 card facts resolve (0 stranded; 109 unchanged, and dwv:before-and-during-flow has revised text). Cooling/heat-pump facts moved p24→25 and p25→26. All 104 SG-009 fact IDs cited by W1/Walker resolve to SG-010. There are 24 new SG-010 facts with no predecessor.
- Bindings added on 22 cards: 001, 006, 008, 018, 023, 025, 027, 033, 044-048, 050, 053, 054, 056, 057, 060, 063, 064, plus 049 (revised dwv row). All 64 source lines were rebuilt with SG-010 page ranges. Safety: 44-46 extended; 47 newly flagged (alarms); E1 33/42 carried. MD crab on 33/34 only.
- Open: no card covers hydronic/steam/electric heat or fireplace operation directly. The terms Hartford Loop, Low-water cutoff and MCA / maximum OCP are not card-bound. Physical print test not done. Publishing still needs Ben's go.

## Post-render layers (2026-09-21, staged only)

New scripts here, adapted from SG-009 `sg009-location-contents/contents.py`, `sg009-color-language/paint.py`, the cross in `sg010/edition_inspection_layer.py` and `sg010/mark_maryland.py`. None of the old freeze, package or publish steps were carried over. Run them in this order: `contents_sg010.py`, then `paint_sg010.py`. Both read the unlayered renders in Seed Bank `output` and write to `output/layered/`. Unlayered renders are unchanged.

- **Contents** (`contents_sg010.py`):
  - Compact p.1 becomes a location table: 28 charts with house icon, area label, SG page and L1 entry page.
  - L1 pp. 2-7 become six location-contents leaves, built from the L1 outline and `page-index-L1.json`. They list 139 topics and group rows, repeat the area key on each leaf, and link to exact pages.
  - Each page is drawn with the SG-010 header and footer, including the live vector brand from `card_brand.mark`.
  - Every other page is byte-checked unchanged.
  - Locations for new topics: interior glazing/doors/stairs/floors → Rooms / stairs; fireplaces → Rooms + chimney (masonry) or Rooms + systems (factory/gas); hydronic, steam and electric heat → Systems + rooms; insulation → Attic + lowest; kitchen/bath → Wet rooms; alarms → Rooms + wet; scope/report → Throughout.
  - Outputs: `layered/contents-locations-SG-010.json` and `contents-layout.json`.
- **Paint** (`paint_sg010.py`), applied to the 3 guides and the current 8 long + 8 compact appendices:
  - Area colours on table fills, left-edge area tabs and topic bars.
  - Hatch tags on limit/qualification lines and dot tags on source pointers.
  - A legend on each page (skipped on L1 p.103, where it would collide).
  - Red safety crosses, guides only: 58 in L1 from `LONG_FLAGS` (SG-009 set plus S33-S39 labels; all found), and 15 in compact from a narrow tile-title vocabulary.
  - Blue crabs on explicit MD/jurisdiction words: collision-checked, at most 3 per page, one per column list.
  - Report: `layered/layers-report.json`.
- **QA:** images are in Seed Bank `sg010-20260921/qa-layers/`. Checked by eye: compact p.1, p.30 in colour and grayscale; L1 pp. 4, 7, 8, 114; APP-H compact p.1. Two defects were found and fixed: crosses sat in the wrong column, and the legend overlapped.
- **Not done / open:**
  - The field cards were left alone (another agent owns them).
  - The SG-009 inspection-layer sketch bands were not carried.
  - `tools/home_inspection_page_frame.py` was not applied. It frames property packets, and the guides already carry the SG-010 frame.
  - The compact cross vocabulary misses the "Doors" tile on p.30 (a trapping lock is a safety concern). Review the list.
  - W1 has no crosses.

## 2026-09-21 Handoff 2 Part A done (steps 1-7)

1. **Section order.** `prepare_content.py` now stably groups L1 pages by section in first-appearance order after the modules run and rebuilds `hierarchy.domains` from data. 14 sections, all contiguous (Scope pp. 10-12, Method 13-40, Roof structure/insulation 41-43, ... Interior evidence, Interior/appliances/life safety, Reporting). L1 stays 139 topics / 127 pp; page numbers shifted, so everything downstream was rebuilt.
2. **Paint.** `COMPACT_SAFE_TILES={('interior_routes','Doors')}` adds the Doors cross on compact p.30 (16 compact crosses, was 15). APP-H compact is now a per-row crab document (`MD_ROW_DOCS`): every row or card whose first words name a jurisdiction gets a gutter crab (12, was 5); other documents keep the 3-per-page cap. Checked by eye: compact p.30, APP-H compact pp. 1-3, L1 contents leaf 2.
3. **Full rebuild** (prepare, 6 render stages, contents, paint, cards, Walker). Cards: lock still valid (bindings unchanged), 22 changed cards, 24 new facts, 0 stranded; card source lines cite compact pages, which did not move. Walker: 20 pp, SHA-256 `0c70daf3d66fa7c06babe114bd3415cace7def10c2bdf9915574c02a68982e1c`, 10 prompts, 0 observed conditions; crosswalk pins match the rebuilt L1 JSON and page index; p.5 checked by eye.
4. **Re-hash.** `rehash_recordings.py`: independent full SHA-256 of all 89 canonical files in `F:\SEED BANK\RECORDINGS` against `recordings-catalog.json`: 89 OK, 0 mismatch, 0 missing (80.55 GB, 35.5 min). Receipt: Seed Bank `sg010-20260921\recordings-rehash-receipt.json`.
5. **Navigation** (`navigation_sg010.py`, output Seed Bank `sg010-20260921\navigation\`): `navigation.json` with 368 entries (139 subjects, 107 definitions, 14 numbered notes, 64 cards, 8+8 appendices, 21 sources, 6 property, 1 illustration), 62 subject aliases (31 new for S33-S39 subjects: boiler, radiators, steam heat, smoke alarm, tempered glass, egress window, radon, ...), term pages re-located from the layered APP-D and asserted equal to the render stage. PDF layer: 43 links on the compact finder (p.32) and 312 on the L1 subject index (pp. 123-127); the contents-layer links (compact p.1: 28; L1 leaves 2-7: 159) are verified, not re-linked; every link target equals its printed number. APP-D long cut gets 107 term + 14 note bookmarks. `FIND A SUBJECT.html` (shelf) and `navigation.html` (edition) rebuilt with computed printed routes.
6. **Library.** `BB_CODE\tools\home_inspection_library.py` is parameterized (`build(..., edition=, glossary=, current=)` and CLI `--edition/--glossary/--current`; facts verify against the guide named in their own ID prefix, so SG-009 property facts still check against the frozen SG-009 guide; the Start Here row is optional and recorded when absent). Defaults unchanged: the frozen S32-C1 package still verifies `current`. That edit is an uncommitted working-tree change in BB_CODE (no BBDF filing). `library_sg010.py` builds Seed Bank `sg010-20260921\library\SG-010-2026-09-21`: 1145 records, 5550 relations, 49 PDFs, 107 definitions; verify = current; lookups QC-033 / P505-09 / AFCI / Hartford Loop / SG-010-L1:steam_systems resolve; 0 unavailable routes. `Library/CURRENT.json` untouched.
7. **Weil-McLain.** `references_sg010.py` appends the EG Series 7 manual to `references/reference-receipt.json` (SHA-256 `84bd732df4228e4c8862638fdeece1f3aa0aa056dd81361aacc821621ce88778`, 92 pp, 14,423,473 bytes, URL = `content_s38.BOILER`) and verifies hash + page count of all 7 entries. It also names the seven shelf files (`Source PDFs/<APP-E id> - <title>.pdf`).

**Staged shelf** (`shelf_sg010.py`, Seed Bank `sg010-20260921\stage\`): a CURRENT EDITION-shaped tree with 49 PDFs / 884 pp / 89.7 MB (3 guides, 8+8 appendices, 2 card PDFs, 21 sources of which 14 carried byte-exact from SG-009 and re-verified, 6 property incl. the 20-page Walker packet, 1 diagram), `_Maintenance/manifest.json` + `issue.json` (issue id `SG-010-2026-09-21`, parent `S32-C1-2026-09-21`; no Start Here row yet), and the staged edition data folders the library indexes. Run order: `navigation_sg010.py` -> `shelf_sg010.py` -> `library_sg010.py`.

- Open after Part A: the five standalone Walker PDFs on the staged shelf still read SG-009 (Part B step 8); Start Here absent; the issue id `SG-010-2026-09-21` is the agent's choice; the 31 new subject aliases are editorial; W1 has no links or crosses; no physical print test.

## 2026-09-21 Recording archive applied (catalog + ledger)

- Plan review (`.scratch/sg010/archive_plan_review.py`, pre-review copy `archive-plan.pre-review.json`): S06-S12 evidence resolved to current Team evidence folders; S13/S14 historical caches unavailable (provenance only) with SG-009 `Evidence/S13|S14` listed separately as selected published evidence, not the full cache; S31/S32 resolved via Seed Bank pointers; S31/S32 filenames repunctuated. Every evidence entry keeps `historical_path`. Reviewed plan sha256 609db101...
- Applied `tools/recording_archive.py` (added a retry for Dropbox transient lock on the catalog replace; tests 4/4 pass). 89 records archived and verified in F:\SEED BANK\RECORDINGS; journal/receipt in `_catalog/migrations/2026-09-21`. No media remains in Sound Recordings.
- Ledger: `RECORDING ARCHIVE - LEDGER.pdf` (24 pp, visually reviewed) + `recordings-catalog.json/.csv` + `recording-aliases.csv` + README in Sound Recordings and bank. Builder `archive_ledger.py --publish` now copies the reviewed PDF (hash-checked) instead of rebuilding. Lookup pointers: `Library/RECORDINGS - LOOKUP.md`, `Property Reviews/505 Walker Ave/RECORDING - LOOKUP.md`.

## 2026-09-21 Handoff 3 Part B done (steps 8-10): SG-010 PUBLISHED

8. **Start Here and shelf.** `walker_labels_sg010.py` relabeled the standalone Walker PDFs in place (5x7 cards 12 swaps, Letter sheets 12, Findings p.4 "SG-009 through S31" -> "SG-010 through S39"; width-neutral, body pixels asserted unchanged at 72 dpi); the image sequence keeps its Visual R2 historical sentence and the outline has no edition text, so both carried byte-exact. `directory_sg010.py` builds the 3-page `00 - START HERE.pdf` from the manifest rows (65 GoToR links, all 49 PDFs linked, every target page validated); `shelf_sg010.py` now adds the `directory` row, README and process docs. Two Start Here layout collisions were found on screen and fixed before publication.
9. **Visual verification.** `qa_sg010.py` rendered all 421 reading pages onto 97 contact sheets (colour, 10 grayscale, 22 changed cards at 110 dpi) in Seed Bank `qa-final/`. Five parallel reviewers plus a full-resolution re-check of every flagged spot: no clipping, overlap, off-page table, missing frame, wrong numbering or garbled glyph. Cosmetic items recorded, not fixed, in `qa-final/visual-review.json` (L1 p.39 missing continuation tab; renderer pagination orphans in APP-D long p.18 and APP-G long pp.3/14/19; two inline crab placements; small compact p.19 diagram; card area bands close in grayscale). No physical print test.
10. **Archive and publish.** `publish_sg010.py stage / plan / publish (finish)`: 294 writes, 24 removals, all 43 replaced and 24 removed SG-009 files archived byte-exact and hash-verified to Seed Bank `Backups/Current Set History/before-SG-010-2026-09-21` (46 MB) before any write. Published: CURRENT EDITION (50 PDFs / 49 + Start Here, 884 + 3 pp), `Study Guide Editions/SG-010` (edition data, both appendix cuts with html/json, cards folder, Presentation Source/SG-010-2026-09-21 with scripts and reports), `SG-010-L1`, `SG-010-W1`, root registries (STUDY-GUIDE-EDITIONS current_edition SG-010; APPENDIX-VERSIONS current A1.8-C1 ... H1.2-C1 / long A1.8 ... H1.2 with history + presentation_revisions rows), TRAINING-DOCUMENT-MAP register (now lists SG-009 and SG-010 families), root shelf PDFs (STUDY GUIDE.pdf, WALKING CUT - W1.pdf, APP-A..H aliases), index/STUDY GUIDE html, PENDING RECORDINGS (published through S39), Property Reviews (20-page combined packet, three relabeled standalones, SG-010 crosswalk, combined-packet.json, manifest, README, change record), Library (package `SG-010-2026-09-21` rebuilt against the published tree with no overlay, verify current, 1145 records / 5550 relations / 50 PDFs / 107 definitions; `CURRENT.json` moved after verification; README, Packets pointer, COURSE STATUS, FINAL READINESS, practice-exam record updated). Frozen standalone reading set in Seed Bank `Issues/SG-010-2026-09-21` (98 MB) with the issue record and small Data in Dropbox `Study Guide Editions/SG-010 Issues/SG-010-2026-09-21`. Receipt: `CURRENT EDITION/_Maintenance/publication-receipt.json`. `SG-010 - HANDOFF STATE.json` updated (archive applied, plan hash 609db101... verified, re-hash 89/89).

- Decisions carried as the agent's (confirm or rename later): issue id `SG-010-2026-09-21`, parent `S32-C1-2026-09-21`; 31 new subject aliases; APP-H per-row crab rule; Walker combined packet on the shelf; new card bindings and the QC-047 flag unreviewed by Ben.
- `BB_CODE/tools/home_inspection_*` remains untracked/uncommitted (left as-is; not a BBDF filing).
- Next: separate THE PERFORMANCE TEAM into its own repository with THE SEED process at `C:\Users\benja\Dropbox\BB_SEED`.

## 2026-09-22 Presentation revision P1 published (SG-010-P1-2026-09-22)

Ben rulings (session, 2026-09-22): keep issue id; accept the 22 rebound cards + QC-047 flag and the 31 aliases (`field-card-acceptance.json`); fix the cosmetic items now; retune the area tones; do not commit the BB_CODE tools, record them for the future Team repository (`THE PERFORMANCE TEAM/CODE CARRY`); stop after the fix and hand off.

- `palette_sg010.py`: the eight C1 hues re-tuned in lightness to a 14-luma ladder (min step 13.7); navy labels on the two light bands; card header ink unchanged. Consumed by `paint_sg010.py`, the card paint layer (`cards_sg010.py`), `navigation_sg010.py` and `visual-language.json` (`area_palette`, `grayscale_rule`).
- `render_sg010.py`: local `add_pages` (no empty "Source notes:" label; short tables < 170 pt kept whole; source line kept with its table), short register tables kept with their heading, near-square compact figure cap 125 pt. Page counts unchanged (APP-D 20, APP-G 19, compact 32, L1 127). A first attempt with a 420 pt keep threshold grew APP-D/APP-G to 23/26 pages and was discarded.
- `paint_sg010.py`: continuation pages inherit the continuing topic's area tab; appendices place the crab gutter-first.
- `shelf_sg010.py` / `publish_sg010.py`: revision-aware (PARENT = SG-010-2026-09-21; live rows carried; registry rows updated in place; APPENDIX-VERSIONS history hashes updated, presentation_revisions row added; Walker packet untouched).
- Full chain re-run (render -> contents -> paint -> cards -> navigation -> shelf -> library -> qa), targeted re-proof of every changed element, then stage / plan / publish: 154 writes, 1 removal, first issue archived byte-exact to `before-SG-010-P1-2026-09-22` and frozen in Seed Bank `Issues/SG-010-2026-09-21`; P1 frozen in `Issues/SG-010-P1-2026-09-22`; Library `SG-010-P1-2026-09-22` current. Open: APP-G long p.19 orphan row (long-table widow control).
