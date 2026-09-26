# Beastagotchi Pre-Implementation Discussion Queue

**Date:** 2026-09-25  
**Updated:** 2026-09-26  
**Status:** owner-requested discussion checkpoints before full architecture implementation resumes

## Current status

- **1. Correctness tranche:** complete for the bounded pre-discussion block.
- **2. Product facets / Toolbelt:** discussion complete; ideas preserved, consolidated and owner-prioritized.
- **3. Windows Beast Sandbox:** direction selected and preserved (WSL2 + guided Docker + Beast-native virtual providers + SSH physical Pi + record/replay; QEMU not required).
- **3A. “Full but not cluttered” reconciliation:** complete and preserved.
- **4. Final whole-project fresh-eyes / epiphany review:** **NEXT, but only when the owner explicitly authorizes it.**
- **5. Resume implementation:** follows the fresh-eyes review and roadmap/contract reconciliation.

## 1. Complete the already-started correctness tranche — COMPLETE

Do not leave partially-started foundation work hanging. Finish/verify the bounded correctness work already underway before reopening broad product ideation.

## 2. Beastagotchi product facets / "sides" — COMPLETE FOR THIS DISCUSSION PHASE

Explicitly step back from pages/features and identify the major user-facing facets of Beastagotchi as a whole.

Owner-started examples:
- Beast/life/progression/awards/lineage side;
- real-time logs/data/graphs/telemetry/"sensors" side;
- tools/utility/operations side.

Questions explored:
- what other distinct facets already exist implicitly?
- which deserve to become first-class product concepts?
- which are merely implementation layers and should not become user-facing silos?
- how do facets overlap without becoming hard navigation cages?
- what balance should exist between creature/life, observation, utility, creation, diagnostics, field use, connectivity, content/ecosystem, etc.?
- what genuinely useful Linux/Pi/Pwnagotchi tooling becomes appropriate because Beastagotchi sits on top of all three?

Do not turn Beastagotchi into a generic tool dump. Prefer context-aware, composable, useful capabilities integrated with canonical State, Doctor, Procedures, Surfaces and owner workflows.

Resulting records include the Toolbelt candidate ledger, accepted 1–15 priority order, singular-Doctor rule, Owner Space/managed-boundary direction, System Graph consolidation, adjacent-ecosystem directions, and the “full but not cluttered” reconciliation.

## 3. Virtual Beast/Pwnagotchi lab on Windows — DIRECTION SELECTED

Before implementation resumes, research/design a practical virtual/sandbox environment hosted on the owner's Windows laptop that approximates the reference Pwnagotchi/Beastagotchi runtime closely enough to test as much as possible without repeatedly touching the physical Pi.

Target uses:
- Pwnagotchi plugins;
- Beast Core partial/full builds;
- configuration/migrations;
- UI/graphics/Scenes/Experiences;
- cinematics/Choreography;
- Pack/extension installation;
- update/rollback/recovery;
- failure injection;
- regression tests;
- sanitized state playback/simulation;
- framebuffer/touch/display-profile simulation where possible.

Selected direction:
- WSL2 as the primary everyday Beast Sandbox;
- Docker accepted when hidden behind simple BeastLab controls for disposable/destructive tests;
- Beast-native virtual hardware providers inside WSL;
- SSH-connected physical Pi as a first-class real-hardware validation path;
- record/replay strongly selected, initially allowing manual file transfer;
- QEMU explicitly not required unless a future concrete need justifies reopening the discussion.

Be precise about fidelity limits: radio/monitor mode, exact Pi hardware, SPI TFT, GPIO/touch timing, kernel/device-tree behavior and physical thermal/performance still require real hardware.

Also connect the lab indirectly to the AI development workflow through repository branches, CI, test artifacts, sanitized logs/state bundles and other explicit bridges. Do not falsely claim direct access to the owner's laptop where none exists.

## 3A. Full-but-not-cluttered reconciliation — COMPLETE

Before the fresh-eyes pass, reconcile facets, Toolbelt ideas, Claude carryovers and Sandbox implications against the owner goals of “make Beastagotchi the best,” “think of everything,” and “full but not cluttered.”

Key result: broad capability does not require broad primary navigation. Preserve one Doctor, one System Graph, one managed mutation stack, one capability/provider lifecycle, coherent Workspaces, curated facets rather than tab cages, and shared Search/Automation/History/Support infrastructure.

See `docs/Beastagotchi_Full_Not_Cluttered_Reconciliation_2026-09-26.md`.

## 4. Final whole-project "new eyes" / epiphany review — NEXT, OWNER TRIGGER REQUIRED

**Only when the owner explicitly asks for it.**

Re-read/reassess the complete Beastagotchi project with the now-mature architecture and a deliberately broader/free-thinking perspective.

Look for:
- X + Y => Z capabilities that were not previously obvious;
- newly relevant ideas caused by later architectural decisions;
- duplicated concepts that can become one stronger system;
- Linux/Pi/Pwnagotchi facilities not yet exploited;
- fun/emotional ideas enabled by technical infrastructure;
- technical infrastructure enabled by creature/product concepts;
- data already collected that can support new experiences/tools;
- missing product facets;
- unnecessary complexity that can be removed;
- recovery/observability opportunities;
- community/SDK possibilities;
- ideas from adjacent projects/tools/ecosystems worth adapting;
- genuinely new directions even when they revise earlier assumptions.

Owner ideas are high-value input, not constraints that prohibit independent engineering/product thinking. Bring back contrary recommendations when evidence or architecture supports them and explain why.

## 5. Resume implementation

After the fresh-eyes review, reconcile resulting changes into the roadmap/contracts and continue architecture implementation in meaningful test-backed tranches.
