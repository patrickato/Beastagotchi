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


## Repository continuity preservation sync — 2026-09-23

A cross-source recovery pass reconciled the accessible Beastagotchi/Monstergotchi
conversation context, Library artifacts and the live repository. The durable
summary is now committed as:

`docs/Beastagotchi_Project_Continuity_Preservation_2026-09-23.md`

Synchronization corrections made alongside this checkpoint include:
- top-level README/documentation indexes now point to Completion Matrix v5.0;
- stale 195/253-test entry-point references were replaced by the preserved
  332-test v0.19 source gate;
- already-implemented Face/Animation Pack, Depot browser, Experience composition
  and Global public-preview items are no longer described as future work;
- PeerDex persistence is acknowledged as implemented while bridge/UI integration
  remains pending;
- the older 2026-09-21 continuity audit is retained as historical evidence rather
  than treated as the current project state.

This is documentation/preservation synchronization only. It does not constitute a
new physical TFT, target-runtime or presentation-owner validation.

## Pinned-chat recovery reconciliation — 2026-09-23

A six-batch private screenshot recovery reconstructed the inaccessible tail of the
final pinned Beastagotchi development conversation far enough to strongly overlap
the repository's existing v0.19 history.

Sanitized durable decisions are preserved in:

`docs/Beastagotchi_Recovered_Conversation_Continuity_Addendum_2026-09-23.md`

Newly reinforced continuity includes:
- roadmap-as-memory/execution-system development philosophy;
- Lightbulb Reviews and proactive adjacent-ecosystem exploration;
- context-aware Pack/Experience/hardware composition;
- the Experience-system design rationale;
- Device/User → Beast Roster → Experience separation;
- device-global versus per-Beast progression and Rare Moment ownership;
- Beast-first versus device-first discovery/anti-farming behavior;
- origin of the multi-Beast/Monster/Monstergotchi lineage architecture;
- deterministic heredity + curated mutation direction;
- privacy-safe Lineage Capsules;
- ordinary Pwnagotchi peer interoperability and PeerDex/social progression;
- Nearby / Friends / Global separation;
- exact PUBLIC SNAPSHOT Global privacy rule.

Current source also confirms that Beast Bridge emits richer peer callback payloads
and PeerDex persists/querys the richer identity/encounter metadata. The remaining
social-layer gap is user-facing progression/presentation and the richer
Beast-to-Beast descriptor/capsule layer.

This reconciliation is documentation/provenance work only. It does not add a new
target-runtime or physical TFT acceptance result and does not change the rule
that PR #9 remains unmerged until the visible/physical v0.19 gates are complete.



## Recovery consolidation status — 2026-09-23 evening

The private pinned-chat recovery now contains six ordered readable screenshot
batches totaling **78 screenshots**, plus two earlier source images, for **80
preserved image artifacts** in this recovery pass.

The recovery has reached strong chronological overlap with the current repository
record. Major engineering/design gaps required for safe continuation are considered
closed. Further older screenshots remain valuable for literal-history enrichment,
smaller idea recovery and contradiction checks, but are no longer prerequisites
for reconstructing current v0.19 architecture or next-work order.

Public GitHub continues to contain only sanitized engineering/provenance material;
raw screenshots/transcript-like evidence remains private in the Beastagotchi
Preservation Library.

This is preservation/documentation work only. The current implementation source
gate remains the previously established **332 tests + Python compile + shell
syntax**; no new target/off-screen or physical TFT validation is implied.


## Unified UX operational-surface milestone — 2026-09-23 evening

The next visible v0.19 cleanup block is now source-green.

Implemented:
- Operations Center changed from four equal diagnostic cards to an attention-first
  live-platform hierarchy;
- operational list overlays use a three-row rhythm that leaves room for
  **50px-high bottom navigation controls**, meeting the reference resistive-touch
  minimum instead of the previous 36px visible buttons;
- platform overlay paging/swipe logic now follows the same three-row page size;
- empty operational surfaces explain that unavailable state remains unavailable
  rather than filling the screen with demo values;
- the captured-state gallery tool now renders Control Center, Apps and the major
  operational overlays from the same captured real state used for page renders;
- regression coverage now checks operational-surface rendering and platform
  navigation target geometry.

Current source/CI gate after this block: **343 tests passed + Python compile +
shell syntax** in GitHub Actions run #124.

This is still source/CI validation only. No new target/off-screen Pi run, physical
TFT readability/touch acceptance, or sustained thermal validation is claimed.

The next visible UX step is to use an actual captured Beast state with the expanded
gallery, review clipping/hierarchy/theme regressions off-screen, and only then
prepare a bounded Pi validation package when the visible delta is large enough.


## Pinned-chat recovery batch 07 — GitHub/bootstrap bridge

A new private recovery batch adds **15 screenshots**, bringing the ordered set to
**93 screenshots across seven batches**, plus two earlier source images for
**95 preserved image artifacts** total.

This batch substantially closes the previously noted literal-history gap around:
- initial working GitHub access and repository population from the v0.18.1 baseline;
- creation of the durable issue/CI/documentation structure;
- first v0.19 Draft PR #9 / Presentation Broker control-plane work;
- early Unified UX and the user's request for periodic renders between Pi installs;
- explicit rejection of early visual alternatives that still felt like variants
  of one dashboard;
- safe Pack intake/staging and content-only activation;
- Theme/Board/Layout Pack consumers, Pack SDK and Depot Catalog v1;
- the Experience milestone at historical head
  `972d1b7c19450727ae969e79eaea05b8144980d9`;
- the transition into the multi-Beast longevity question already preserved in the
  later roster/lineage recovery.

The final portion overlaps strongly with the previously recovered Experience /
multi-Beast material. Further screenshot recovery should preferentially move
**earlier than the first GitHub-connection point** if the goal is to uncover new
context rather than duplicate later history.

This is preservation/provenance only. It does not alter current implementation
status or physical validation.


## Pinned-chat recovery batch 08 — true beginning

Fifteen additional private screenshots recover the beginning of the pinned
conversation and bring the ordered set to **108 screenshots across eight batches**,
plus two earlier source images for **110 preserved image artifacts** total.

Recovered origin context includes:
- v0.18.1 target/off-screen validation and historical 195-test source gate;
- Korrie71 UI criticism leading directly to the v0.19 UX/Visual Cohesion gate;
- first Theme Manager coexistence and Presentation Broker reasoning;
- first Update Manager architecture;
- GitHub migration / collaborator handoff decision;
- physical visual-review cadence;
- Unified Experience Architecture framing;
- stable core + Beast Packs/Depot ecosystem;
- TFT cockpit / WebUI workshop split;
- per-module resource attribution and optimize-before-throttle policy;
- GPLv3/free-open licensing intent.

Batch 08 meets Batch 07 at repository creation. Batches 08→01 now cover the
supplied pinned conversation from its beginning through its end with no known
major chronological gap. This is preservation/provenance only and does not alter
source, target/off-screen or physical validation status.


## Theme Manager 3.0 reintegration checkpoint

Fresh source-level review of current `Korrie71/pwnagotchi-theme-manager` 3.0 identified
several useful reintegration targets without changing Beast's architecture:

- install-first Gallery/Depot workflow with preview/filter/phone handoff;
- compact Doctor/Explain diagnostics;
- structural theme metadata;
- existing pwngrid peer transport as a candidate for a tiny privacy-safe Beast
  descriptor rather than inventing a second nearby-presence protocol;
- Wardrive route-summary presentation as an Expedition UX reference;
- PWA installability for local WebUI/companion use;
- changed-row framebuffer writes and lazy live-token providers;
- clean unload/live install as compatibility evidence for future presentation handoff.

Implemented now:
- bounded read-only `ThemeManagerProbe` in `beastcore/theme_manager_interop.py`;
- Theme Manager version/capability evidence is surfaced through plugin canonical state;
- PresentationBroker consumes that evidence while keeping physical execution locked;
- explicit managed release/acquire support is **not** assumed merely because clean
  unload/live-install behavior exists.

Code-bearing checkpoint:
`574c7e48144cb2cc088a2260ed57d80015b617d4`

Source gate:
- **343 tests passed**
- Python compile passed
- shell syntax passed
- GitHub Actions `35952293274`

No new target/off-screen or physical TFT validation is claimed.

Development priority remains user-visible v0.19 UX/gallery -> bounded physical TFT
acceptance before real Presentation Broker ownership switching. Safe interop work such
as token registry/semantic-layer metadata may proceed in bounded blocks without
displacing that visible milestone.

## Canonical Template Token milestone

The first neutral Korrie-derived interoperability contract is now implemented
without changing physical presentation behavior.

Implemented:
- new `beastcore/template_tokens.py` allow-listed Template Token Registry;
- tokens resolve only from canonical Beast Core `StateRegistry` state;
- no duplicate hardware/network polling and no background token loop;
- source/quality/timestamp/error truth preserved with each resolved value;
- unknown or unavailable data renders explicitly as `--` rather than invented
  telemetry;
- formatting, aliases, privacy class, publication-policy metadata and update
  class are declarative;
- bounded template rendering (1024 input characters / 64 substitutions by
  default);
- bounded read-only `GET /template-tokens` Local API exposure;
- regression coverage for canonical resolution, truthful unavailability,
  aliases, metadata, rendering bounds and API exposure;
- specification added at
  `docs/Beastagotchi_Template_Token_Registry_v0.19.md`.

Initial tokens cover system/thermal/resource truth, Wi-Fi counts, radio channel,
captures, GPS fix/satellites, UPS battery estimate, dock/context, active Beast
identity/progression, Expedition summary and PeerDex count.

This creates the shared substrate for Beast UI/Studio/Boards/Packs and a future
allow-listed Theme Manager `STAT_SOURCE` adapter. The Theme Manager bridge itself
is **not enabled** here and physical Presentation Broker execution remains locked.

Source/CI gate:
- **348 tests passed in 6.34s**
- Python compile passed
- shell syntax passed
- sanitized real-state UX gallery render/upload passed
- GitHub Actions run `35953678888`

This is source/CI evidence only. It does not change target/off-screen or physical
TFT acceptance status.

The user-visible v0.19 physical acceptance gate remains the priority before real
Native <-> Theme Manager <-> Beast ownership switching. This token work was chosen
because it improves the long-term shared architecture without perturbing the
screen that still needs human physical acceptance.

## Plugin / Dependency / Capability catalog milestone — 2026-09-24

The user's stock-plugin thought experiment was promoted into a durable platform
architecture rather than left as a future "plugin menu" idea.

Reviewed upstream reference:
- `jayofelony/pwnagotchi`
- branch `noai`
- commit `93dda381ef11538e4ec03fd130abad3ceeea7a4c`

Current upstream facts preserved:
- 20 functional plugin source files are bundled under
  `pwnagotchi/plugins/default/`;
- `example.py` is developer/reference material;
- `gps_listener`, `pwndroid` and `ups_hat_c` remain stock-known/configured
  names but are not bundled in that directory at the reviewed commit;
- the upstream defaults currently enable auto_backup, auto-update, fix_services,
  grid and webcfg while most hardware/credential-specific plugins remain opt-in.

Approved architecture:
- Plugin Manager evolves into a Plugin & Capability Center;
- all managed component classes converge on PROVIDES / REQUIRES / OPTIONAL /
  CONFLICTS / USED BY vocabulary;
- abstract capabilities are preferred over named providers;
- overlapping providers are cataloged/arbitrated instead of creating duplicate
  canonical truth;
- missing requirements are classified into automatic-safe, confirmed
  transactional, guided, provider-choice or unsupported remediation;
- data-egress and credential-presence metadata are first-class;
- the same resolver model extends to Packs, Hardware, Experiences, Apps and
  Services;
- Beast Doctor/Explain will consume the dependency graph.

Reference-build package policy:
- maintain a complete versioned **superset BOM** for the user's Pi 4 build;
- do not bulk-install that superset;
- actual installed/runtime software remains the dependency closure of selected
  capabilities/hardware;
- optional services remain inactive when their feature is not selected.

Implemented in this block:
- expanded `PluginIntegrationEngine` metadata for the Jayofelony stock-known
  plugin family;
- role, canonical namespaces, provides, requires, provider group, data-egress,
  credential-required and hardware-specific fields;
- explicit `catalog_only` requirements state;
- dependency/remediation executor remains disabled;
- new automated tests prevent catalog metadata from being mistaken for provider
  selection or dependency mutation.

New specifications:
- `docs/Beastagotchi_Dependency_Capability_Resolver_v0.1.md`
- `docs/Beastagotchi_Reference_Build_BOM_Strategy_v0.1.md`

Source/CI evidence for the code-bearing checkpoint:
- **351 tests passed in 7.17s**
- Python compile passed
- shell syntax passed
- sanitized real-state UX gallery render/upload passed
- GitHub Actions run `35957950912`

This is source/CI validation only. No packages/services were installed on the
physical Pi, no plugin configuration was changed and no new physical TFT
acceptance is claimed.

The physical v0.19 UX gate remains ahead of any dependency installer. Safe next
work may continue with side-effect-free requirement modeling/probes, semantic
render metadata and Doctor/Explain, but package/service mutation requires a later
explicit transactional executor.

