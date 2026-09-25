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
12. `docs/Beastagotchi_Dependency_Capability_Resolver_v0.1.md`
13. `docs/Beastagotchi_Reference_Build_BOM_Strategy_v0.1.md`
14. `docs/Beastagotchi_Owner_Sovereignty_Unrestricted_Mode_v0.1.md`
15. `docs/Beastagotchi_Provider_Arbitration_v0.1.md`
16. `docs/Beastagotchi_Doctor_Explain_v0.1.md`
17. `docs/Beastagotchi_Plugin_Extension_Architecture_v0.1.md`
18. `docs/Beastagotchi_Beast_Capsules_Offline_Ecosystem_v0.1.md`
19. `docs/Beastagotchi_Doctor_Knowledge_Runtime_CrossPollination_2026-09-24.md`
20. `docs/Beastagotchi_Adaptive_Platform_DeepLinks_Unified_Doctor_RecoveryVault_2026-09-24.md`
21. `docs/Beastagotchi_Experience_DNA_Abundant_Taxonomy_2026-09-24.md`
22. `docs/Beastagotchi_Experience_Prototype_Briefs_v0.19_2026-09-24.md`

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
- extension ecosystem boundaries: Pwnagotchi Plugin vs Beast Pack vs Beast App vs Companion Expansion.
- Beast Capsule/offline transport design, QR framing, signed identity, PeerDex/Challenge/Trophy Capsule opportunities and remote-lineage trust semantics.
- dependency/capability graph design, provider arbitration and how to keep a maximal known-universe BOM without a kitchen-sink runtime.
- provider arbitration, common resolver adoption by Experiences/Apps/Hardware Studio, and generated BOM/Doctor UX now that the shared read-only graph exists.
- Beast Doctor causal-chain explanation, known-good fingerprints, blast-radius previews and how to keep explanations truthful instead of inventing confidence.
- Doctor Knowledge Resolver/Skill Cache design: condition/runbook/probe packs may be resolved on demand, but downloaded knowledge must not inherit mutation authority; evaluate shared condition-pack interop with the standalone PwnDoctor research branch.
- owner sovereignty / Expert Mode design: preserve owner freedom without turning local policy override into unauthenticated remote privilege.
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
- Cataloging the full software/service universe is approved; bulk-installing/enabling that universe is not. Optional dependencies remain feature/hardware driven.
- A Beast policy blocker is not ownership authority: technically possible unsupported operations need an explicit owner override/manual escape path; technical impossibility remains distinct.
- The shared DependencyCapabilityResolver is read-only and already used by Plugins + Packs. Do not add package/service mutation to it; remediation execution belongs to separately planned/audited transactions.
- Secret-bearing plugin config may expose presence only; do not surface credential values into canonical state, dependency evidence, logs or support bundles.
- Provider arbitration is read-only: native-first defaults, owner preference modeling, recommendations and fallback chains must not be confused with an enabled handoff/failover executor.
- Persistent provider preferences are owner policy only; setting one must not silently enable/switch a provider. Preserve the Explain-before-act path and keep automatic failover disabled until provider handoffs have probation/rollback evidence.
- Capsule integrity is not authentication. Current BC1 SHA-256/CRC checks detect corruption but do not prove sender identity; remote lineage/trophy trust must wait for explicit signature semantics.
- Do not move Beast progression/UI/lineage logic into Pwnagotchi plugins merely because plugin hooks exist. Keep plugins thin and canonical Beast concerns in Beast Core/Packs/Apps.
- Offline/sneakernet exchange is protected scope; do not make cloud/network access a prerequisite for Capsule sharing.

## Experience-DNA visual direction

Do not collapse future visual work back into the old Classic/Cyberpunk/Black-Ice/WOPR/LCARS/Hunter loop.

Those identities remain useful presets/references only. The top-level architecture now uses Experience DNA with broad visual/layout/density/motion/creature/utility/input/Doctor/mystery axes.

First prototype order: Atlas, Forge, Observatory, Habitat, Monolith.

Each must differ in grayscale silhouette, content hierarchy, creature presence, motion language and Doctor relationship before palette is considered.