# Separation from BBDF and the installation

THE PERFORMANCE TEAM was carved out of the BBDF tree on 22 September 2026 following THE SEED's pattern (`BB_SEED/BB_CODE/docs/GIT-SEPARATION.md`, `SIBLING-CHECKOUTS.md`, `CLEAN-BRANCHES.md`): git owns code, contracts, tests and small registries; the installation keeps published reading material; bulk media and history stay in the Seed Bank behind small JSON pointers; a new intent is a new checkout, never a branch switch inside a populated folder.

## Rulings (Ben, 2026-09-22)

- Checkout `C:\Users\benja\Dropbox\THE_PERFORMANCE_TEAM`; remote `BENBALLdesign/THE_PERFORMANCE_TEAM`, sibling of THE_SEED.
- Registries move to the checkout; the installation points to them.
- The Builder Snapshot is not tracked. The live production scripts and `builder/` are the code; the snapshot stays in the installation and the Seed Bank as history.
- The BB_CODE tools recorded in CODE CARRY are absorbed here. BB_CODE keeps nothing of the Team's.

## What was cut

Every BBDF dependency the scripts had, recorded patch by patch in `docs/SEPARATION-BUILD.json`:

- `bbdf_core.paths` (design-system palette and logo) in five modules: replaced by `tools/team_paths.py` reading vendored copies under `assets/brand` (hashes of the originals recorded).
- Hard-coded `BEN_BALL\BB_CODE`, `.scratch\sg010`, `.scratch\property-505-r2`, `.scratch\sg009-color-language`, `.scratch\sg009\field-cards` and `.scratch\recording-20260921-020522` paths: the modules and data now live in `builder/` and `production/sg010/data/`.
- Hard-coded installation and Seed Bank paths: `installation.json` (ignored) names them; `team_paths.installation()` and `seed_bank()` resolve them. The Seed Bank vault check is unchanged.
- The PyMuPDF side path: `pymupdf` is a requirement; `team_paths.ensure_pymupdf()` bridges an environment that still uses the side path.
- Registry readers (`prepare_content`, `rehash_recordings`, `publish_sg010`, `home_inspection_storage`, `home_inspection_library`, `recording_archive`): read and write `registries/` in the checkout. `publish_sg010` stages registry writes under `_registries` and maps plans pinned before the separation to the new location.

Not carried: `edition_inspection_layer`, `mark_maryland` and `card_inspection_drawings` (listed in the carry manifest, imported by nothing, and they create folders at import time).

## Verified on 22 September 2026

- Baseline: every file in the installation hashed before any move (54,577 files, 7,059,001,813 bytes, 0 errors). Full record `F:\SEED BANK\DATA_ARCHIVE\HOME_INSPECTION\_META\20260922-separation\baseline.json`; summary `docs/SEPARATION-BASELINE.json`.
- Tests: 9 checks pass under the codex Python 3.12 runtime and 17 under system Python 3.14 with pytest (tests plus the portable skill's runtime tests), with no `installation.json`.
- Import smoke: all 25 production modules import from the checkout; no tracked module names `bbdf_core`, `BB_CODE` or a user path (a test enforces this).
- Proof run from the checkout against the installation (`docs/SEPARATION-PROOF.json`): `shelf_sg010` rebuilt the staged shelf with all 49 file rows and the Start Here directory byte-identical to the published `CURRENT EDITION` manifest; `library_sg010` rebuilt the staged package with `records.jsonl`, `relations.jsonl` and `files.jsonl` byte-identical to the published `Library/SG-010-P1-2026-09-22` and verified `current`; `qa_sg010`, pointed at a separate proof folder, produced 97 contact sheets byte-identical to Part B's. The Part B QA record `qa-final/visual-review.json` was not touched.
- `home_inspection_library.py verify` from the checkout: the published package is `current`, nothing changed.
- `publish_sg010.py verify` from the checkout passes every check (154 plan writes, 50 PDFs, registries, library, frozen package, bank issue) once the plan's removal of `publication-receipt.json` is exempted. That assertion fails identically from the original location: `finish()` writes a new receipt at the path the plan removed, so `verify` can only pass before the receipt exists. Pre-existing; not changed here.
- Git dry run under the allow-list `.gitignore`: 109 files, about 2.3 MB, no PDFs, images, media or installation records.

## Still open

- **Step 5, first commit and remote.** Not done: the repository has no `.git` yet, by design, so Ben reviews first. `gh` is not installed on this machine; create the remote on GitHub or install `gh`. Publication review per GIT-SEPARATION before pushing.
- **Step 6, registries.** The registries are copied here and every checkout reader uses the copies, but the installation originals (`STUDY-GUIDE-EDITIONS.json`, `APPENDIX-VERSIONS.json`, `Sound Recordings/recordings-catalog.*`, `recording-aliases.csv`, `Home Inspection Training/Library/CURRENT.json`) are still in place, byte-identical. Retiring them means deleting those files and leaving a `REGISTRIES.json` pointer at the installation root; the Dropbox `SG-010 Production` scripts then read the old paths and must be treated as superseded by this checkout. Do this after the first commit.
- `TRAINING-DOCUMENT-MAP.md/.html` stay in the installation: they are generated reading material with links relative to it, written by `publish_sg010.document_map`.
- Other small records under `Home Inspection Training/Library` (`COURSE STATUS.json`, `FINAL READINESS.json`, `SG-010 CONTINUATION.json`, `STORAGE LOCATIONS.json`, `Intake`, `Packets`) remain installation records; the handoff did not list them as registries.
- `prepare_content.py` records the catalog path it read into the prepared data (`source_location_catalog`). A future re-render will therefore carry the checkout path where SG-010 carried the Dropbox path. Content is unchanged.
- The published manifest's `registry` field still names the installation-root path of `STUDY-GUIDE-EDITIONS.json`; the hash it pins is what `verify` checks, and it matches the checkout copy.
- No physical print test has been performed; the open content items in `production/sg010/PROGRESS.md` are unchanged by the separation.
