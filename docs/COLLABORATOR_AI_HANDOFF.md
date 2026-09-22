# Beastagotchi Collaborator / AI Handoff

This repository snapshot is intended to let an external developer or AI review the project without reconstructing its history from chat transcripts.

## Read first
1. `README.md`
2. `docs/Beastagotchi_Design_Architecture_Bible_v1.0.md`
3. `docs/Beastagotchi_Project_Continuity_Audit_v1.0.md`
4. `docs/Beastagotchi_Master_Completion_Matrix_v4.6.md`
5. `docs/Beastagotchi_Foundation_Roadmap_v2.9.md`
6. `docs/BEASTAGOTCHI_MASTER_README_DRAFT.md`
7. `docs/UX_POLISH_MILESTONE_v0.19.md`
8. `docs/KORRIE71_THEME_MANAGER_INTEGRATION_SPEC_v0.1.md`
9. `docs/UPDATE_MANAGER_SPEC_v0.1.md`

## Architecture
- `beastcore/`: trusted state/data/action platform.
- `beastui/`: touchscreen/rendering client.
- `beaststudio/`: web customization/operator surface.
- `pwnagotchi_plugin/`: narrow Pwnagotchi event bridge.
- `docs/`: decisions, specs, roadmaps and validation history.
- `tests/`: historical regression suite.
- `tools/`: diagnostics/render/validation helpers.

## Review questions
External reviewers are especially invited to critique:
- UI/UX hierarchy and touch ergonomics.
- rendering architecture and responsive strategy.
- privilege/action boundaries.
- update/rollback design.
- Theme Manager coexistence/merge strategy.
- plugin compatibility and configuration safety.
- performance/thermal behavior on Pi 4.
- code organization, duplicated historical code and migration path to v1.0.
- test gaps, packaging and CI.

Please distinguish architectural critique from personal preferences and cite files/functions when possible.
