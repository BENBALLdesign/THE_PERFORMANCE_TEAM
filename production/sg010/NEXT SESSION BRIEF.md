# SG-010: final integration and publish (brief for a fresh session)

Performance Team work, not BBDF. Do not file handoffs, rows or specs. Do not message anyone, convene a room, or use the BEN_BALL sort/queues. Bulk data (staging, QA images, backups) stays in the Seed Bank, `F:\SEED BANK`. Fail closed if it is unavailable, and never back up into Dropbox. The user has authorized local compilation, verification and publication within THE PERFORMANCE TEAM and the Seed Bank. No physical print test has been done; never claim one.

**Read first:** `PROGRESS.md` in this folder (every section), then `../SG-010 Handoff/SG-010 - FRESH SESSION HANDOFF.md` (binding decisions, build hazards 5/9/10, verification and finish criteria).

**Runtimes:**
- Python: `C:\Users\benja\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -B`
- Poppler: `C:\Users\benja\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin`

**Pipeline** (run from this folder, in this order; every later stage depends on the earlier ones):
1. `prepare_content.py`
2. `render_sg010.py appendices terms l1 compact_appendices compact walking`
3. `contents_sg010.py`
4. `paint_sg010.py` (writes to `output/layered`)
5. `cards_sg010.py` (review lock; use `--establish` only after reviewing the changed bindings)
6. `walker_sg010.py`
7. `references_sg010.py` (verifies the 7 new reference PDFs against their receipt)
8. `navigation_sg010.py` (links, bookmarks, navigation.json, FIND A SUBJECT; output Seed Bank `navigation\`)
9. `shelf_sg010.py` (staged CURRENT EDITION-shaped tree + manifest; output Seed Bank `stage\`)
10. `library_sg010.py` (staged library package; output Seed Bank `library\SG-010-2026-09-21`)
Independent: `rehash_recordings.py` (35 min; reads 80 GB).

Seed Bank work folder: `F:\SEED BANK\DATA_ARCHIVE\HOME_INSPECTION\Working Evidence\sg010-20260921`.

## Part A: done (2026-09-21, handoff 2 session)

All seven steps are complete; see `PROGRESS.md` "Handoff 2 Part A done" for what each produced and where. Summary: L1 sections contiguous; Doors cross and per-row APP-H crabs; full rebuild incl. cards (0 stranded) and Walker (20 pp, `0c70daf3…`, 0 observed conditions); 89/89 recordings re-hashed OK; navigation with verified links and 121 bookmarks; parameterized library built and verified against the staged shelf; Weil-McLain receipt entry. The staged shelf (`stage\`) already holds the 49-PDF reading set and its manifest; only the Start Here PDF, the Walker standalone labels and publication remain.

## Part B: done (2026-09-21, handoff 3 session)

Steps 8-10 are complete; presentation revision SG-010-P1-2026-09-22 is the published issue (first issue SG-010-2026-09-21 archived); see `PROGRESS.md` "Handoff 3 Part B done". New scripts: `walker_labels_sg010.py`, `directory_sg010.py`, `qa_sg010.py`, `publish_sg010.py` (stage / plan / publish / finish / verify). The items below are the original brief, kept for the record.

8. **Start Here and shelf.** Build a Start Here PDF and finish the shelf manifest, following the SG-009 CURRENT EDITION structure and `_Maintenance/manifest.json`.
   - Start from the staged tree in Seed Bank `stage\Home Inspection Training\CURRENT EDITION` (`shelf_sg010.py`); add the `directory` row (Start Here) and the final `validation`, `registry` and `issue_path` fields at publish.
   - Update the Walker standalone labels (the five standalone PDFs on the staged shelf still read SG-009), then re-run `shelf_sg010.py` and `library_sg010.py`.
   - The issue id `SG-010-2026-09-21` (= `REV`) and parent `S32-C1-2026-09-21` are the agent's choice; confirm or rename before publishing.
   - At publish, update `combined-packet.json`, the manifest and the README in Property Reviews.
9. **Verification.** Verify fully per the handoff and look at the rendered pages. Include long tables, every changed card type, 5x7 legibility and grayscale.
10. **Archive and publish.**
    - Archive the previous CURRENT EDITION set into the established Seed Bank history.
    - Publish SG-010 to CURRENT EDITION and to `Study Guide Editions/SG-010`, `SG-010-L1` and `SG-010-W1`. Leave SG-009 and older issues untouched. The staged edition data folders under `stage\Home Inspection Training\Study Guide Editions\` are the library's owners; publish them with the PDFs.
    - Library: rebuild the package against the published tree (no overlay), copy it to `Library/<issue>`, then and only then move `Library/CURRENT.json`.
    - Update the root registries (`STUDY-GUIDE-EDITIONS.json`, `APPENDIX-VERSIONS.json`, `TRAINING-DOCUMENT-MAP`) and the root shelf PDFs.
    - Regenerate hashes and registries against the delivered bytes.
    - Update `SG-010 - HANDOFF STATE.json`: the archive is applied, the plan hash is `609db10181199be47a62673f325fba81a1a5b53e150a7fa52c110a9590e45591`, and the independent re-hash (89/89 OK) is at Seed Bank `sg010-20260921\recordings-rehash-receipt.json`.
    - `BB_CODE\tools\home_inspection_library.py` carries an uncommitted parameterization (defaults unchanged; frozen S32-C1 still verifies current). Commit it with the publish or leave it; do not file it under BBDF.

## Known open items (report them; don't hide them)

- No field card covers hydronic, steam or electric heat, or fireplace operation.
- The NHIE gaps listed in APP-B.
- S39 is missing fireplace screens 14-15 and the Unit 6 exam.
- The S13/S14 caches are provenance only.

## After SG-010

Separate THE PERFORMANCE TEAM out as its own repository using THE SEED process, at `C:\Users\benja\Dropbox\BB_SEED`.
