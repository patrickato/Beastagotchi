# Beastagotchi v0.19 Unified Experience — Active Checkpoint Delta

## Branch / PR
- Branch: `v0.19-unified-experience`
- Draft PR: #9
- Base: validated v0.18.1 mainline
- CI status at this checkpoint: green

## What is now implemented

### Product/UX foundation
- Shared v0.19 design tokens for spacing, touch sizing, radii, motion and 480×320 reference geometry.
- Primary page/tab/swipe model is centralized and remains first-class.
- Shared visual component primitives for cards, labels/values, status badges, progress bars, dividers and section titles.
- Header/footer navigation now gives stronger page identity and explicit previous/next destinations.
- The app/studio layer remains deeper than the primary pages; it does not replace them.

### Primary page redesign
- Home/Beast identity emphasis:
  - creature remains the visual anchor
  - level, evolution stage, growth and aura remain visible
  - operational telemetry is summarized rather than rendered as equal-weight diagnostic boxes
  - session/lifetime exploration context remains present
- Overview:
  - prioritizes whole-device state and attention items
  - reduces equal-weight tile clutter
  - preserves dense diagnostic detail in Operations rather than forcing it onto the main page
- System:
  - clearer device-health/resource-mode hierarchy
  - power/dock/link/capability summary retained
  - CPU and temperature history remain truthfully separated by scale
- Networks:
  - fewer/taller rows for physical TFT legibility
  - real RSSI remains the source for strength rails
  - complete catalog remains available through deeper detail/search surfaces

### Presentation ownership groundwork
- Presentation Broker state/control-plane exists for:
  - native Pwnagotchi
  - Korrie71 Theme Manager
  - Beast UI
- Executor remains disabled.
- No physical framebuffer/touch handoff is active yet.
- Legacy Theme Manager conflict detection remains visible.
- Real release/acquire adapters require validated ownership semantics before activation.

### Visual validation
- v0.19 Home smoke rendering exists across multiple theme families.
- Captured-state UX gallery renderer added at:
  `tools/render_v019_ux_gallery.py`
- Gallery accepts a real captured Beast state JSON and does not invent missing telemetry.
- 800×480 output in this gallery remains explicitly compatibility-scaled, not a native-responsive claim.

## Deliberately NOT done yet
- Do not enable real Presentation Broker handoff on the Pi yet.
- Do not merge PR #9 to main yet.
- Do not claim final v0.19 UX completion.
- Do not claim full native multi-resolution support.
- Do not replace the page/tab model with an app-only interface.
- Do not discard progression, achievements, rares, secrets, cinematics, Expeditions or other continuity-ledger items.

## Next implementation block
1. Bring remaining high-frequency primary pages toward the same hierarchy/interaction grammar.
2. Continue Control Center / overlays cleanup where the 480×320 interface is still visually dense.
3. Produce an off-screen v0.19 comparison gallery from captured Pi state.
4. Review gallery for clipping, hierarchy and theme-specific regressions.
5. Prepare a bounded Pi install/visual-validation package.
6. Perform physical TFT review for:
   - readability
   - touch confidence
   - navigation clarity
   - visual polish
   - perceived clutter
   - heat / CPU impact
7. Use physical feedback before broadening the redesign further.

## Continuity rule
The Master Continuity Ledger and latest Master Completion Matrix remain authoritative. Ideas may be deferred, reorganized or redesigned, but must not silently disappear.


## 2026-09-23 Pack / Depot / documentation synchronization

Since the earlier checkpoint, v0.19 also implements:

- verified Pack intake/staging and transactional managed-registry installation;
- scoped safe content-only activation;
- enabled Theme Pack discovery in Beast UI and Studio;
- read-only Board Pack destinations in the Beast launcher;
- Layout Pack templates importable into editable personal Boards;
- safe update-source checking and Pack update orchestration;
- Beast Pack SDK examples;
- bounded Depot Catalog v1 parser with source trust kept separate from catalog
  discoverability;
- explicit content-activation capability reporting without changing the legacy
  generic Pack activation contract.

Current source gate at this checkpoint: **253 tests passing** plus Python compile
and shell syntax.

The public roadmap and detailed status matrix are now synchronized to:
- `ROADMAP.md`
- `docs/Beastagotchi_Master_Completion_Matrix_v5.0.md`
- `docs/Beastagotchi_Development_Release_Workflow.md`

GitHub cadence is now explicit: development commits stay on the active milestone
branch for CI/rollback; `main`, tags and Releases move only at meaningful
validated milestone gates.


## Experience composition milestone

v0.19 now also has:
- declarative no-code Face Packs;
- declarative low-cost Animation Packs;
- Beast Studio Face/Motion selectors;
- persistent local Depot catalog import/search/filter browser;
- Mission Pack Experience profiles that can compose Theme + Face + Motion +
  Board/Layout + Context Deck into a Studio draft;
- exact preview before persistence;
- explicit APPLY TO BEAST remains the only preference mutation gate.

Experience loading itself does not write preferences. Downloaded Board/Layout
content is copied into the draft so Pack-owned source remains read-only.


## Multi-Beast / Monster lineage milestone

The first persistence foundation for the new roster architecture is now green at
**279 automated tests**.

Implemented:
- additive SQLite Beast/Monster roster tables;
- independent progress records;
- active/resting state;
- non-destructive Founder migration from the existing profile JSON;
- persistent ancestry;
- level-70+ two-parent v1 Lineage Synthesis;
- preserved parents;
- level-1 Monster offspring;
- deterministic inheritance seed;
- global `monstergotchi.core` unlock on first successful Monster synthesis.

The live ProgressionEngine has deliberately not been cut over yet. That remains
the next migration gate so current v0.19 behavior is not risked before the roster
storage path is proven lossless.


## Active-Beast progression + Roster control milestone

v0.19 now binds the live ProgressionEngine to the active persistent roster
creature rather than the old single JSON save slot.

Validated behavior:
- existing legacy profile migrates into the Founder Beast;
- existing progression state keys remain compatible with current UI consumers;
- each Beast/Monster persists XP/history independently;
- switching active creature redirects subsequent progression without overwriting
  resting creatures;
- restarting Core reloads the currently active creature;
- Founder progression maintains the old profile JSON as a rollback-compatibility
  mirror;
- non-Founder creatures never overwrite that legacy Founder mirror;
- Beast Studio now includes a Roster surface with active/resting status,
  level/stage/lineage/generation, achievement count, ancestry hint and
  lineage-eligibility visibility;
- active-creature switching is an audited Action Broker mutation;
- switching does not silently change the current Experience.

The first cutover CI run exposed an active-binding bug at the mutation boundary.
That defect was fixed before promotion. The current full source gate is
**297 tests passing**, Python compile green and shell syntax green.


## Roster longevity milestone

The multi-creature progression branch now also has:
- per-creature preferred Experience/presentation memory;
- deterministic Monster heritage generation;
- explicit previewed/audited Lineage Synthesis in Studio;
- Monster-specific fallback evolution stages;
- per-creature milestone/Expedition/Rare/personality memory;
- Hall of Legends induction independent of active/resting state;
- ancestry graph and Studio ancestry viewer.

Current full gate: **329 tests passing**, Python compile green, shell syntax green.


## Monster reveal milestone

Lineage Synthesis now has a user-visible TFT ceremony tied to the actual persisted
Monster result. The first Monster separately identifies the Monstergotchi unlock;
later Monsters receive normal synthesis reveals. Mutation metadata and inherited
traits are presented from real synthesis state, not generated UI demo data.

Rare Moments retain final-layer visual priority and the reveal adds no permanent
background workload.

Current full source gate: **332 tests passing**, Python compile green, shell
syntax green.
