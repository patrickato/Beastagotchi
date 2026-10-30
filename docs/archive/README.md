# Documentation Archive

This directory preserves superseded Beastagotchi documentation without allowing it
to masquerade as current project state.

## Policy

- Archive; do not silently delete useful history.
- Keep current source-of-truth documents at `docs/`.
- Historical validation remains evidence for what passed at that time only.
- If an old file is still referenced by runtime/installers/tests, do not move it
  until the reference is migrated and validation remains green.
- Git history remains the ultimate provenance record.

## Layout

- `roadmaps/` — superseded Foundation Roadmaps.
- `matrices/` — superseded Master Completion Matrices.
- `validation/` — historical source/target/physical validation and experience gates.
- `checkpoints/` — superseded within-milestone checkpoint notes.
- `superseded-specs/` — older spec revisions replaced by a newer active revision.
- `drafts/` — historical drafts.
- `continuity/` — superseded continuity/recovery audits.

For current status start at [`../README.md`](../README.md),
[`../ARCHITECTURE_CONTRACTS.md`](../ARCHITECTURE_CONTRACTS.md),
[`../adr/README.md`](../adr/README.md),
[`../Beastagotchi_Master_Completion_Matrix_v5.0.md`](../Beastagotchi_Master_Completion_Matrix_v5.0.md),
and the repository [`ROADMAP.md`](../../ROADMAP.md). The active-path
`../Beastagotchi_v019_Active_Checkpoint_Delta.md` is retained for historical
milestone provenance only; its filename does not establish current status.
