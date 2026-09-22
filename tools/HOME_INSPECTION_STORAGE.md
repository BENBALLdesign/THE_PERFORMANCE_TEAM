# Home inspection storage

Published PDFs and their small library records stay in THE PERFORMANCE TEAM.
Bulk backups, extracted frames/OCR/audio and intermediate builds live in the
established `F:/SEED BANK/DATA_ARCHIVE/HOME_INSPECTION` domain. The bank volume is
identified by `_REGISTRY/vault.json`, not just a drive letter.

Use `home_inspection_storage.backup_root()` for preserved pre-publication sets
and `work_root(session_name)` for new extraction, staging and review payloads.
These functions refuse an unavailable or wrong bank; never fall back to a
Dropbox scratch folder. Code, small job receipts and source identities can stay
with the project. Copy only approved reading material back to the print shelf.

Migrated Dropbox folders hold `SEED BANK LOCATION.json`, a short README and an
`Open in Seed Bank.lnk` shortcut. This is an explicit pointer, not an NTFS
junction. `resolve(old_path)` follows the nearest location record and preserves
the remaining relative path. Files stored in the bank retain their bytes,
filenames and historical provenance; do not rewrite frozen manifests just to
change old absolute paths. Resolve those paths at read time.

The current library's `STORAGE LOCATIONS.json` lists the relocated roots. Its
intake receipt for S33 uses current bank locations and keeps the prior paths as
aliases. Bank-only evidence is unavailable when the volume is disconnected;
the published PDF shelf and compact library index remain locally usable.

The 21 September 2026 relocation plan and copy journal live in
`F:/SEED BANK/DATA_ARCHIVE/HOME_INSPECTION/_META/20260921-backup-routing`.
Only exact planned files may be retired after verifying their bank hashes.
Historic one-off publication scripts and frozen snapshots are provenance,
not current routing configuration. Before adapting any older recipe, use these
storage functions and a fresh publication plan; do not replay an old plan.

This routing covers the home-inspection workflow. It does not establish the
cause of a Dropbox sync problem or change unrelated BBDF backup routines.
