# Beastagotchi Repository Hygiene

**Status:** living repository-maintenance policy.  
**Goal:** keep the active tree readable without deleting historical evidence or breaking runtime/install/test references.

## Rules

1. Current source-of-truth documents stay prominent in root or `docs/`.
2. Clearly superseded roadmaps, matrices, checkpoints, validation reports, drafts and specifications move under `docs/archive/`.
3. History is archived rather than silently deleted.
4. Do not move a file merely because its version number is old. If runtime, installers, tests or active documentation depend on its exact path, migrate references first and let CI prove the change.
5. Identical blobs are **candidates** for consolidation, not automatic deletions. Different filenames may still carry milestone/provenance meaning.
6. Fix stale links, version numbers, test counts and source-of-truth references when discovered.
7. Generated/private recovery material does not belong in the public repo unless it is deliberately sanitized into engineering documentation.
8. Repository cleanup must preserve the separation between source/CI evidence, target off-screen evidence and physical acceptance.

## Completed cleanup — 2026-09-23

- 55 clearly superseded/history documents moved from the active docs root into organized `docs/archive/` areas.
- Archive categories include roadmaps, matrices, validation, checkpoints, superseded specs, drafts and continuity history.
- docs index/repository map updated to explain the active-vs-historical model.
- installer/test references exposed by the archive move were corrected.
- the cleanup returned to a green 332-test + compile + shell-syntax source gate.
- a frozen pre-cleanup preservation branch remains available separately.

## Current active source-of-truth set

Use these before historical snapshots:

- `README.md`
- `ROADMAP.md`
- `docs/README.md`
- `docs/Beastagotchi_Design_Architecture_Bible_v1.0.md`
- `docs/Beastagotchi_Master_Continuity_Ledger_v1.0.md`
- `docs/Beastagotchi_Master_Completion_Matrix_v5.0.md`
- `docs/Beastagotchi_v019_Active_Checkpoint_Delta.md`
- `docs/Beastagotchi_Project_Continuity_Preservation_2026-09-23.md`
- `docs/Beastagotchi_Recovered_Conversation_Continuity_Addendum_2026-09-23.md`
- `docs/Beastagotchi_Preservation_Recovery_Workflow.md`
- `docs/Beastagotchi_Development_Release_Workflow.md`
- `docs/REPOSITORY_MAP.md`

## Open hygiene candidates

These are intentionally **not** removed yet.

### Canonical data-key version family

Multiple canonical-data-key revisions remain in active documentation along with the JSON key inventory.

Action:
- identify the current authoritative schema/revision;
- audit runtime/tests/install/docs references;
- move superseded revisions to archive only after references are migrated.

### Touch calibration naming collision

`config/touch_experimental_rejected_v092.json` and
`config/touch_recommended_v092.json` currently resolve to identical blob content.

This is especially sensitive because physical testing later established that the restored/original calibration is production-authoritative and the v0.9.2 affine candidate is rejected.

Action:
- inspect file intent/history and all consumers before renaming/removing either file;
- ensure no filename implies a rejected profile is recommended for production;
- add explicit comments/docs or migrate names only with a safe compatibility path.

### Render-validation duplicate

`tools/render_v017_validation.py` and `tools/render_v018_validation.py`
currently resolve to the same Git blob.

Action:
- determine whether v0.18 intentionally reused the v0.17 renderer as a historical alias;
- if no active reference requires both names, retain one active implementation and archive/document the alias.

### Target-validation duplicate aliases

The following pairs currently resolve to identical blobs:

- `validate_v06.sh` / `validate_v061.sh`
- `validate_v08.sh` / `validate_v081.sh`

Action:
- determine whether the later names represent historical checkpoint aliases;
- avoid deleting until install/docs/test references are audited;
- prefer a documented compatibility shim or archive path over silent disappearance.

### Legacy milestone validation tools

Many `validate_v*.sh` and `tools/render_v*_validation.py` files are milestone-specific historical tools.

Action:
- classify each as currently required, useful compatibility tooling, or historical-only;
- historical-only tools may move to a documented archive/tooling-history area after reference audit;
- keep the current validation entry points obvious.

## Routine checkpoint behavior

Every preservation checkpoint should also ask:

- Are current docs pointing at the latest matrix/checkpoint?
- Are historical reports crowding the active docs root?
- Are test counts/version labels stale?
- Did a newer spec supersede an older active-path copy?
- Are there byte-identical duplicates that can be consolidated safely?
- Are archived paths referenced by installers/tests?
- Did private recovery material accidentally enter the public tree?
- Is the repo still clear about what is current, historical, source-tested, target-tested and physically accepted?

If archival status is uncertain, **flag it instead of deleting it**.
