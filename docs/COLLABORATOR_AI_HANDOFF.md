# Beastagotchi Collaborator / AI Handoff

This repository snapshot is intended to let an external developer or AI resume or review the project without reconstructing its history from private chat transcripts. The validated baseline is v0.18.1 on `main`; active development is v0.19 on `v0.19-unified-experience` in Draft PR #9.

## Read first
1. `README.md`
2. `ROADMAP.md`
3. `docs/Beastagotchi_Project_Continuity_Preservation_2026-09-23.md`
4. `docs/Beastagotchi_Design_Architecture_Bible_v1.0.md`
5. `docs/Beastagotchi_Master_Continuity_Ledger_v1.0.md`
6. `docs/Beastagotchi_Master_Completion_Matrix_v5.0.md`
7. `docs/Beastagotchi_v019_Active_Checkpoint_Delta.md`
8. `docs/UX_POLISH_MILESTONE_v0.19.md`
9. `docs/KORRIE71_THEME_MANAGER_INTEGRATION_SPEC_v0.1.md`
10. `docs/UPDATE_MANAGER_SPEC_v0.1.md`
11. `docs/KORRIE71_THEME_MANAGER_REINTEGRATION_AUDIT_2026-09-23.md`

The 2026-09-21 continuity audit is historical evidence and is superseded for current-state recovery by the 2026-09-23 preservation snapshot.

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


## Current continuation guardrails
- Keep PR #9 unmerged until the documented v0.19 gates are satisfied.
- Do not confuse source/CI green, target off-screen validation and physical TFT acceptance.
- Preserve the restored/original touch calibration; the v0.9.2 affine candidate was physically rejected.
- Do not replace the page/tab/swipe model with an app-only interface.
- Do not invent telemetry when live/persisted data is absent.
- Build substantial, test-backed blocks before asking for another physical Pi test.
