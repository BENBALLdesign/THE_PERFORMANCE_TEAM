# Storage weight and redundancy, 22 September 2026

Metadata index of D:, F: and the heavy Dropbox roots (stat only; 468k files), then duplicate candidates by name and size (files of 64 KB and up), with two sample files per pair hash-verified. Index and pairs: session scratchpad `drive-index.json`; verified samples all IDENTICAL for the fourteen largest pairs. Not a full hash of every file; treat the byte totals as name+size estimates.

## Weight

| Root | Size | Files | Heaviest parts |
| --- | --- | --- | --- |
| `C:\Users\benja\Dropbox\BB_SEED` | 1.25 TB | 289k | `BB_BOOKS\library` 1.24 TB (PNG 1.24 TB / 275k files); `BB_BOOKS\reference` 5.8 GB (sqlite); `_runtime\gpu` 2.6 GB (DLLs); `work` 0.75 GB |
| `C:\Users\benja\Dropbox\ABSTRACTION nft` | 271 GB | 65k | `CODE STRUCTURE\GEN-dataPROT` 98 GB (cloud CSVs ~1.2 GB each); `__~CURRENT~OUTPUT~__keep_clean` 88 GB; `SOURCE-IMAGES` 53 GB; `FRAKT launch\hres` 13 GB; `Dataset-Warehouse` 7 GB / 38k files; a `.venv` inside `GEN-ABSTractors` |
| `C:\Users\benja\Dropbox\THE PERFORMANCE TEAM` | 7.06 GB | 55k | session evidence + intake audio 5.9 GB (being moved to the bank now), older editions 1.0 GB |
| `C:\Users\benja\Dropbox\DATABSTRACT` | 95 KB | 8 | `FLEET_STATISTICS_DATAPATHS` only; no git |
| `D:` (932 GB, 263 GB free) | 718 GB | 41k | `Strange Attractors\Vault` 142 GB; `CLOUDS` 81 GB; `OUTPUT for filing` 120 GB; `SignalBOOST\CLOUDS` 74 GB; `DAM` 131 GB; `URSMonthly` 41 GB; `SoundSignals` ~90 GB |
| `F:` (4.6 TB, 3.3 TB free) | 1.38 TB | 82k | `SEED BANK\CLOUDS` 541 GB; `IMAGES\dataBLOCKS` 302 GB; `IMAGES\burnout~` 201 GB; `IMAGES\ColorTHIEF~` 91 GB; `SEED BANK\RECORDINGS` 81 GB; `SEED BANK\GENERATED` 57 GB; `IMAGES\~SOUNDsIgnALs~~` 51 GB; `SEED BANK\IMAGE_ARCHIVE` 29 GB; `MINTS` 15 GB; `SEED BANK\DATA_ARCHIVE` 8 GB |

## Redundancy (hash-verified samples)

The single big fact: **`BB_SEED\BB_BOOKS\library\Sources` is a Dropbox copy of the local drives.** About 1.1 TB of the 1.24 TB duplicates material that already exists on D:, F: or in `ABSTRACTION nft`.

| Duplicate pair | Est. size | Files |
| --- | ---: | ---: |
| `BB_SEED\BB_BOOKS\library\Sources\IMAGES\*` = `F:\IMAGES\*` (burnout~, dataBLOCKS, ColorTHIEF~, ~SOUNDsIgnALs~~) | 531 GB | 18,978 |
| `...\Sources\IMAGES\Strange Attractors` = `D:\Strange Attractors` | 142 GB | 14,801 |
| `...\Sources\IMAGES\DAM` = `D:\DAM` | 132 GB | 5,129 |
| `...\Sources\IMAGES\Unfiled` etc. = `D:\OUTPUT for filing` | 126 GB | 4,353 |
| `...\Sources\IMAGES\SoundSignals` = `D:\SoundSignals` | 117 GB | 14,234 |
| `...\Sources\IMAGES\dataBLOCKS` = `ABSTRACTION nft\CODE STRUCTURE\SOURCE-IMAGES` (which itself = `F:\IMAGES\dataBLOCKS`, 53 GB) | 102 GB | 3,717 |
| `D:\SignalBOOST\CLOUDS` = `ABSTRACTION nft\CODE STRUCTURE\GEN-dataPROT\...\clouds` | 74 GB | 209 |
| `D:\CLOUDS` = `F:\SEED BANK\CLOUDS\F-DATA` | 70 GB | 57 |
| `...\Sources\IMAGES\URSMonthly` = `D:\URSMonthly` | 41 GB | 1,475 |
| `F:\IMAGES\~SOUNDsIgnALs~~` = `F:\SEED BANK\IMAGE_ARCHIVE\~SOUNDsIgnALs~~` (same drive) | 29 GB | 2,771 |
| `...\Sources\MINTS` = `F:\MINTS` = `ABSTRACTION nft\FRAKT launch\hres` (three copies) | 15 GB | 1,593 |

Team side: 0.9 GB of `Study Guide Editions\SG-008\Presentation History` duplicates the bank's `Backups\Current Set History\20260920-040130`; small.

## What this means

- THE SEED registers Dropbox `BB_SEED` as its *working* vault and `F:\SEED BANK` as the archive vault (`BB_BOOKS\registry\vaults.json`). The library import copied every source master into Dropbox. Per THE SEED's own boundary (`GIT-SEPARATION.md`: "Artwork, CLOUD data and frame masters remain in their external vaults and are referenced by installation records"), those masters belong in `F:\SEED BANK\IMAGE_ARCHIVE` / `CLOUDS`, referenced by the library, not copied into `BB_BOOKS`.
- `ABSTRACTION nft` (271 GB in Dropbox) is mostly generated output, cloud data and source images that also exist on D: or F:. Code (`GEN-ABSTractors`, `PY Toolbox`, `ImageGenerationCode`) is a few GB; that is what a repo would keep.
- D: and F: overlap each other only twice (CLOUDS 70 GB; ~SOUNDsIgnALs~~ 29 GB inside F:). D: is otherwise the working masters, F: the archive plus `IMAGES`.

## Decisions for Ben (nothing moved outside THE PERFORMANCE TEAM)

1. BB_SEED: re-point `BB_BOOKS\library\Sources` at the bank (`IMAGE_ARCHIVE`, `CLOUDS`, `MINTS`) and retire the Dropbox copies. That is a SEED-side migration: its library records hold source paths and digests; it needs the same plan/copy-verify/retire discipline as the Team's `bank_relocation.py`, plus a vault-registry change. Roughly 1.1 TB leaves Dropbox.
2. ABSTRACTION nft: split code (repo) from outputs (bank `GENERATED`), sources (bank `IMAGE_ARCHIVE`, already there for dataBLOCKS) and clouds (bank `CLOUDS`); the Dropbox folder keeps the small working set. Roughly 250 GB leaves Dropbox.
3. D: vs F:: decide which copy of `CLOUDS` is canonical (F-DATA in the bank already has 70 GB of D:\CLOUDS) and whether `F:\IMAGES` is the master or `SEED BANK\IMAGE_ARCHIVE` is; today both exist and the bank archive is the smaller, partial one.
4. DATABSTRACT (Dropbox): 8 files, unrelated to the DATAbstract storefront checkout at `Dropbox\BenBallDesign\DATAbstract`; fold into that or delete.
