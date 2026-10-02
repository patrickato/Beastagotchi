# Beastagotchi v0.19 Preservation Checkpoint — 2026-09-23

This is a **sanitized engineering checkpoint**. Private conversation captures, raw transcripts, credentials, exact location history, and unrelated personal material are intentionally excluded.

## Durable decisions recovered

- The roadmap is a memory/execution system rather than a rigid checklist. Approved ideas remain implemented, active, planned, experimental, reserved, or explicitly retired with a reason.
- Periodic **Lightbulb Reviews** should inspect adjacent Raspberry Pi, Pwnagotchi, embedded, RF, offline-AI and UI ecosystems for useful concepts.
- Prefer modular Packs/modules for optional and exotic capabilities rather than permanently loading everything into core.
- “All-in-one” means discoverable, coherent, integrated and reachable—not everything on one screen.
- Prefer real machine/environment state over decorative or invented telemetry.
- Optimize duplicate polling/work and suspend unused rendering/services before degrading visuals under resource pressure.
- Recovery is part of feature design: new powers should gain backup, rollback and health-checking alongside them.
- Design for first-time and non-reference-hardware users while retaining the Pi 4 reference implementation.

## v0.19 continuity

The active branch is `v0.19-unified-experience`; unfinished work is not to be merged into `main` merely for preservation.

Recovered implementation direction includes unified UX; Beast Packs/Depot; Presentation Broker transitions; update discovery/staging/orchestration; roster/progression/memories/heritage/reveal; Experiences and mission experiences; resource governance; plugin operations; knowledge/diagnostics; rare events/achievements; and Expeditions.

A key progression rule is the split between global/device accomplishments and per-creature accomplishments. Device-first discoveries should not be repeatedly farmable for full XP. New creatures can still earn smaller personal “new to me” credit. On migration, the Founder inherits the device’s already-known Wi-Fi encounter set; later creatures begin with empty personal encounter memory.

Presentation ownership remains transactional and single-owner:

`Native Pwnagotchi -> Korrie Theme Manager -> Beast UI`

Context Decks + Mission/Experience Packs + hardware autodetection remain a major architectural direction so relevant capability can surface when SDR, second Wi-Fi, dock/home-base, Expedition or other context becomes available without bloating the permanent Home screen.

## Validation evidence policy

Keep three categories distinct:

1. **Source/CI validation** — automated unit/integration/static checks and CI.
2. **Target off-screen validation** — validation in the target software/hardware environment without claiming physical UX approval.
3. **Physical validation** — real-device touchscreen/display/readability/thermal/interaction testing.

Passing source/CI does not constitute physical validation.

## Repository-hygiene audit

The repository already has useful archive structure under `docs/archive/` for roadmaps, matrices, validation reports, superseded specs, drafts, continuity records and v0.19 checkpoints. Preserve useful history there instead of deleting it.

Ambiguous items flagged for deliberate review rather than silent removal:

- `docs/Beastagotchi_Canonical_Data_Keys_v2.json` through `v6.json` coexist with `docs/beastagotchi_v1_canonical_data_keys.json`; establish the authoritative current schema before archiving older variants and repairing references.
- `config/touch_experimental_rejected_v092.json` and `config/touch_recommended_v092.json` currently have identical blob content; verify intent before deduplicating.
- `tools/render_v017_validation.py` and `tools/render_v018_validation.py` currently have identical blob content; determine whether v018 is an intentional alias or obsolete duplicate.
- `validate_v06.sh` / `validate_v061.sh` and `validate_v08.sh` / `validate_v081.sh` are duplicate blobs. Preserve historical meaning, but audit references before consolidating active copies.
- Legacy `validate_v*.sh` and `render_v*_validation.py` scripts may now be historical tooling. Determine live references/usage before moving them to archive.

Current source-of-truth material should remain prominent: `ROADMAP.md`, Architecture Bible, current Master Completion Matrix, Master Continuity Ledger, active v0.19 checkpoint, development workflow, repository map and docs index.

## Privacy / preservation boundary

Raw private chat material is preserved outside the public repository. Only sanitized engineering decisions, implementation status, validation evidence and continuity changes belong here.

A literal word-for-word backup of complete ChatGPT conversations still requires ChatGPT account data export; screenshot recovery and continuity summaries are not a substitute for that export.
