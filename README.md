# THE PERFORMANCE TEAM

Home-inspection study-guide production (the SG editions, appendices, field cards and the 505 Walker property review), the published-source library, the recording archive tools and the portable extraction skills. This repository is the code, contracts and registries. It is a sibling of [THE_SEED](https://github.com/BENBALLdesign/THE_SEED) under **BENBALLdesign**, built with THE SEED's git/installation split, and it does not depend on BBDF or on BB_CODE.

## Layout

| Folder | Role | Git |
| --- | --- | --- |
| `production/sg010` | The SG-010 pipeline: prepare, render, contents, paint, cards, Walker, references, navigation, shelf, library, QA, publish. `PROGRESS.md` and `NEXT SESSION BRIEF.md` are the run record | tracked |
| `builder` | The builder modules the production scripts import (renderers, edition, glossary, field-card bindings and concordance, Maryland marker), plus `property-505-r2` (atlas brand, marker) and `sg009-color-language/paint.py` | tracked |
| `tools` | `team_paths.py` (where everything is), `home_inspection_storage.py` (Seed Bank routing), `home_inspection_library.py` (build, verify, lookup), `home_inspection_page_frame.py`, `recording_archive.py` | tracked |
| `registries` | `STUDY-GUIDE-EDITIONS.json`, `APPENDIX-VERSIONS.json`, `recordings-catalog.json` (+ csv, aliases), `Library/CURRENT.json` | tracked |
| `assets/brand` | Print tokens (`palette`, `typography`, `spacing`) and the canonical logo the renderers read | tracked |
| `skills/portable-v1.2` | Recording and audio extraction skills; no machine paths | tracked |
| `tests` | Resolver and archive-boundary checks; run without an installation | tracked |
| `docs` | Separation records: build receipt, baseline summary, proof, carry manifest, handoff | tracked |
| Installation (`installation.json`) | The Dropbox folder `THE PERFORMANCE TEAM`: `CURRENT EDITION`, `Study Guide Editions`, `Library/<issue>` packages, `Property Reviews`, the published `TRAINING-DOCUMENT-MAP` | local, ignored |
| Seed Bank (`F:\SEED BANK`) | Recordings, working evidence, backups, frozen issues, QA proofs | external, pointed to |

## Set up a checkout

1. Python 3.12+; `pip install -r requirements.txt`.
2. Copy `installation.example.json` to `installation.json` and set `installation_root` (the Dropbox installation) and `seed_bank`. `pymupdf_path` is only for an environment that has PyMuPDF on a side path instead of installed.
3. `python -B -m pytest` runs the tests. They need no installation.
4. Run the pipeline from `production/sg010` in the order `NEXT SESSION BRIEF.md` gives, with `python -X utf8 -B <script>`. Bulk output goes to the Seed Bank work folder; the scripts fail closed when the bank is absent and never back up into Dropbox.

`python tools/team_paths.py` prints what the checkout resolves.

## Boundary

Git holds no PDFs, images, media, evidence, installation records or credentials (`.gitignore` is an allow-list). Published reading material stays in the installation and is hash-listed by the manifests and registries that are tracked. See [SEPARATION.md](SEPARATION.md) for the verified boundary and what is still open.
