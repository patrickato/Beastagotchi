# Beastagotchi Recovered Conversation Continuity Addendum — 2026-09-23

**Status:** sanitized durable continuity record derived from recovered private conversation evidence.  
**Privacy rule:** this document records engineering decisions, design intent, implementation milestones and validation evidence only. Raw screenshots/transcripts remain private and are not published here.

## Why this exists

A long Beastagotchi development conversation reached the ChatGPT conversation limit before the project could be moved into a more durable long-term workspace. Cross-chat retrieval did not expose that entire conversation verbatim, so the missing section was reconstructed from repository history, Library artifacts and **93 readable screenshots supplied in seven ordered recovery batches**, plus two earlier preserved source images (the first end-of-chat screenshot and a compressed long-scroll image). The private recovery therefore currently contains **95 preserved image artifacts** for this conversation-recovery pass.

The recovery now strongly overlaps the existing repository record. The major engineering/design gaps needed to continue the project correctly are closed. Exact word-for-word chat history remains a separate archival problem.

This addendum preserves the parts of the recovered conversation that matter to future development: why several v0.19 systems were created, what rules were agreed, which alternatives were rejected or deferred, and how the implementation sequence evolved.

## Recovered development philosophy

The roadmap is a **memory and execution system, not a cage**.

Permanent development rules recovered from the conversation:

- **Never silently forget an approved idea.** It must remain implemented, active, planned, experimental, reserved, or explicitly retired with a reason.
- **Keep exploring.** Periodically stop implementation long enough to ask what the machine could become now, not only what was imagined months earlier.
- **Challenge our own designs.** If a materially better architecture, workflow, UI concept, hardware path or integration appears, redesigning previously built work is allowed.
- **Modularity by default.** Optional/exotic capabilities should increasingly live in Packs/modules instead of permanently increasing every installation's runtime burden.
- **All-in-one does not mean everything on one screen.** The TFT is the cockpit, pages/tabs expose frequent information, apps/studios provide depth, the WebUI is the workshop, and larger screens/companions take appropriate roles.
- **Real information over decoration.** Graphs, maps, animation, personality, achievements and ambient effects should use real Beast/Pi/environment state whenever possible.
- **Delight matters.** Secrets, rare events, unusual animations, collectibles, personalities, special modes and Easter eggs are part of the product, not disposable fluff.
- **Resource efficiency is architectural.** Remove duplicate polling, cache static work, suspend unused rendering/services and reduce unnecessary framebuffer writes before cutting features or degrading visuals.
- **Recovery before recklessness.** New powers should normally acquire backup, rollback, health checking and auditable mutation boundaries alongside them.
- **Design for real users.** The reference Pi remains important, but first-time setup, different displays, missing hardware, discoverability, defaults, accessibility and documentation are now first-class concerns.

The conversation also established an informal practice of **Lightbulb Reviews**: periodically examine adjacent Raspberry Pi, Pwnagotchi, embedded-device, Flipper/Bjorn/M5Stack-style, SDR/Bluetooth/GPS, home-lab dashboard, offline-AI, mapping and hardware ecosystems for ideas worth adapting. Not every idea must survive; useful outcomes include implement now, defer, place in a Pack, reject as wrong for Beast, or redesign around it.

## Recovered GitHub bootstrap / early v0.19 bridge

A seventh private screenshot batch substantially fills the earlier literal-history
bridge that had remained around repository creation and the first v0.19 work.
Sanitized chronology recovered from that batch:

- ChatGPT first gained working access to the user's GitHub installation and
  `patrickato/Beastagotchi`;
- the validated v0.18.1 source tree was populated into a proper public repository
  with normal README/roadmap/changelog/contributor/security/support material,
  CI, issue templates, ADR/collaboration material and GPL-3.0 licensing;
- issues #1-#8 were created to make the major workstreams durable outside chat;
- `v0.19-unified-experience` and Draft PR #9 began with the Presentation Broker
  control-plane for Native Pwnagotchi / Korrie Theme Manager / Beast UI ownership;
- the first visible Unified UX pass refactored Home around the Beast and revised
  Overview/System/Networks while preserving pages/tabs/swipes and real-state
  rendering;
- the user explicitly asked for periodic visual renders between physical Pi
  installs, then rejected early alternatives that still felt like variations of
  the same dashboard; this directly reinforced the later complete-Experience
  direction rather than locking one visual style too early;
- development then moved into safe Pack intake/staging, content-only activation,
  Theme/Board/Layout consumers, the Pack SDK and Depot Catalog v1 while preserving
  the ability to redesign presentation later;
- the batch reaches the Experience milestone at historical head
  `972d1b7c19450727ae969e79eaea05b8144980d9` and then the user's multi-Beast
  longevity question that triggered the roster/progression pivot already covered
  elsewhere in this addendum.

Historical repository anchors visible in the screenshots include documentation
synchronization around `59d3b2f564fc15cfb92fe1c87c406337433763f9`, Pack/Depot
progress around `94c43a1cf186280d59ac66b05156b23a216f5c82`, and the
Experience head above.

This closes the main previously noted exact-history gaps around initial GitHub
setup, first PR #9/Presentation Broker work, early Unified UX and first Packs/Depot
architecture. Additional older screenshots are now most valuable for **pre-GitHub
context, rejected alternatives, smaller idea sparks and literal-history completeness**.

## GitHub development cadence recovered

The agreed release workflow is:

main stable → milestone branch → meaningful development commits → CI → off-screen validation → physical test when warranted → milestone merge → tag/release

For v0.19 specifically:

- main remains the stable v0.18.1 baseline.
- development occurs on v0.19-unified-experience.
- coherent development blocks may be committed for CI, rollback and collaboration.
- trivial single-line churn should not be pushed simply for activity.
- not every commit becomes a package, tag or Release.
- physical Pi packages are prepared at meaningful testable milestones.
- source/CI green is not equivalent to target off-screen validation or physical TFT acceptance.

## v0.19 gate model recovered

The long conversation formalized a broad gate model covering:

1. Unified UX / visual acceptance.
2. Beast Packs / Depot.
3. Native Pwnagotchi / Korrie71 Theme Manager / Beast UI presentation ownership.
4. Update Manager / automatic maintenance.
5. Beast creature/progression system.
6. Specials, rares, secrets and achievements.
7. Expeditions / Memory.
8. Files / knowledge / diagnostics.
9. Backup / recovery / self-healing.
10. Beast Operator / local AI.
11. Plugins.
12. Performance / heat.
13. Hardware.
14. Phone / tablet / WebUI.
15. Other displays.
16. RF / Monstergotchi expansion.
17. Public release.

This gate list was explicitly a completeness/continuity device rather than a demand to finish every item in numerical order.

## Context-aware modularity

A recovered design direction connects Context Decks, Mission/Experience Packs, Beast Packs and capability autodetection.

Examples:

- connect an SDR → Spectrum/Sky-related environments become available;
- dock at home → maintenance/backups/update functions surface;
- begin an Expedition → field navigation/encounter tools become more prominent;
- connect a second Wi-Fi adapter → additional passive-observation capabilities become discoverable.

The goal is contextual capability without turning Home into a wall of permanent buttons.

The same modularity principle applies to complete identities such as WOPR, LCARS, Sonar/Submarine, Aircraft Spotter, Camping/Field, Home Base and Retro Terminal. These should be composable Experiences/Packs rather than hard-wired core bloat.

## Experience system — recovered origin and intent

The Experience milestone became a key solution to repeated UI designs feeling like rearrangements of the same dashboard.

An Experience composes:

- Theme
- Face Pack
- Animation/Motion Pack
- Board or Layout
- Context Deck
- relevant visual/behavior options

Choosing an Experience does **not** immediately modify the Pi. It loads into Beast Studio's draft/preview system against the same live state. Only the explicit APPLY TO BEAST action persists the selection.

Recovered implementation state at historical head **972d1b7c19450727ae969e79eaea05b8144980d9** included:

- declarative Face Packs;
- low-cost declarative Animation Packs;
- Beast Studio Face/Motion selectors with preview;
- local Depot browser/import/search/filter;
- Board/Layout composition;
- Mission Packs serving as Experience profiles;
- read-only downloaded content copied into editable user drafts where appropriate;
- visible warnings for missing optional components;
- hard blocking when required hardware/capabilities are absent.

The conversation explicitly reframed the visual question from “which arrangement of this dashboard?” to “which complete Beastagotchi Experience feels right?”

## Device/User → Beast Roster → Experience

A major recovered architectural pivot happened after the user asked whether multiple creatures could retain separate progression while users switch layouts/Experiences.

The previous implementation had one persistent progression profile. The approved model became:

**Device/User → Beast Roster → Experience**

Meaning:

- **Device/User** owns lifetime machine/world accomplishments.
- **Beast Roster** contains multiple persistent individual creatures.
- **Beast** owns individual progression/history/personality.
- **Experience** is the surrounding UI/presentation and does not define creature identity.
- **Theme** controls visual design.
- **Layout/Board** controls information arrangement.
- **Face/Lineage Packs** expand creature possibilities.
- **Global unlocks** determine content/creation eligibility.
- **Master Collection / Hall of Legends** records long-term aggregate completion.

Changing theme/layout/dashboard/Experience must not reset progression. Changing the active Beast changes which creature receives future progression.

Inactive Beasts are persistent resting records and should consume effectively zero runtime CPU. Only the active creature needs its live personality/progression runtime instantiated.

## Global/device versus per-Beast progression

Recovered global/device accomplishments include concepts such as:

- lifetime discovered-world archive;
- BeastDex master collection;
- Capture Vault;
- Expeditions and locations explored;
- discovered/enrolled hardware;
- global secrets/collectibles;
- Pack collection;
- very rare device-wide events;
- global achievement cabinet;
- unlocked Experiences/themes/features;
- number of Beasts raised and number reaching level 100;
- total lifetime operation;
- first discoveries for that physical device.

Per-Beast state includes:

- XP, level and evolution stage;
- personal name and lineage;
- birth/adoption time;
- runtime;
- personal Expeditions and encounters;
- personal achievements;
- witnessed rare events;
- personality history;
- cosmetics, aura, titles and evolution cosmetics;
- preferred Experience/theme;
- preferred Face/Animation set;
- personal records and last-active time.

## Beast-first versus device-first discovery

The recovered anti-farming rule distinguishes:

- **device-first discovery** — genuinely new to the Beastagotchi installation;
- **Beast-first discovery** — already known to the machine but new to the current creature.

A new Beast can still receive smaller exploration/bond credit for seeing something already known by the device. Repeated familiar observations diminish or cap so users cannot create new creatures beside the same router and farm full progression.

The Founder migration preserves the device's already-known Wi-Fi encounter set as the Founder's starting personal memory. New Beasts begin with empty personal encounter memory.

## Level 100 and longevity

Level 100 remains permanent. There is no prestige reset.

After a Beast finishes growing, the user may keep it active for records, collections, personality and rare-event history, or raise additional Beasts.

This creates long-term meta-accomplishments such as multiple level-100 creatures, multiple lineages, lineage completion, difficult collection goals and future Mythic-scale accomplishments.

## Lineages, personality and preferred Experiences

The numerical progression framework can remain common while lineages render evolution differently.

Possible lineage sources include starter content, achievements, exploration/GPS, night context, seasons, hardware, hidden conditions, Rare Moments, Legendary content and community events.

Each Beast may also have a persistent temperament seed. Real operational state stays authoritative, but creatures may differ in how safe-range conditions are expressed: curious/energetic/social, focused/calm/methodical, skittish/observant/nocturnal, etc.

Experiences remain independent objects, but a Beast may remember a preferred one. Switching may offer:

- switch Beast only; or
- switch Beast and restore that creature's preferred Experience into preview/draft.

The creature survives UI redesign; the UI survives creature switching.

## Beast Roster / Founder migration

The recovered design deliberately preserves existing user progress.

The old single progression profile becomes the **Founder Beast**. Canonical progression state keys may remain compatible and simply refer to the active Beast, minimizing breakage in existing UI consumers.

Long-term roster persistence belongs in proper structured persistence rather than proliferating unrelated JSON save files.

Historical implementation milestones recovered:

- roster/lineage persistence foundation green at **279 tests**;
- active-Beast ProgressionEngine cutover later green at **297 tests**;
- the first cutover CI run exposed an active-binding bug at the creature-switch boundary, which was corrected before continuing;
- the Founder retains a legacy profile.json rollback/compatibility mirror;
- non-Founder creatures never overwrite that mirror.

## Rare Moments, trophies and memory ownership

Rare Moment scheduling remains **device-global**. Creating ten Beasts must not create ten independent rare-event schedules.

When a Rare Moment occurs, durable history may record:

- device witnessed event;
- active Beast;
- active Experience;
- Expedition/location context where appropriate;
- timestamp;
- rarity;
- resulting unlock.

The active Beast can also retain personal witness memory/cosmetic/title evidence.

Trophy views therefore naturally split into:

- Beast-specific trophies/accomplishments; and
- a Master Collection representing everything the physical Beastagotchi has ever earned.

## Monster / lineage synthesis — recovered origin

The Monster system originated directly from the user's idea of raising multiple creatures and eventually combining mature Beasts into something meaningfully new rather than simply applying another skin.

The idea was promoted into architecture and implementation rather than left as brainstorming.

Initial rules recovered:

- many persistent Beasts can coexist;
- one creature is active at a time;
- initial synthesis requires two distinct Beast-class parents at Level 70+ / Alpha;
- parents remain intact;
- the result is a level-1 Monster with independent progression and recorded ancestry;
- first successful Monster creation unlocks monstergotchi.core;
- sex/gender is optional presentation flavor, not a core data requirement;
- different lineages may call the same mechanic breeding, fusion, synthesis, recombination, etc.;
- initially one Monster per unique parent pair prevents reroll farming.

Future additional opportunities may be earned through rare/high-level/Mythic conditions rather than unlimited rerolls.

## Deterministic heredity and curated mutation

The recovered heredity model is not a simple random 50/50 UI copy.

Potential hereditary fields include:

- face-family traits;
- eye/mouth vocabulary;
- accent geometry;
- aura style;
- motion tendencies;
- temperament biases;
- palette DNA;
- preferred information emphasis.

A deterministic inheritance seed keeps synthesized appearance reproducible across restarts.

Two complementary systems were approved:

- **procedural inheritance** — the child visibly carries aspects of both parents;
- **curated mutation** — authored rare surprises triggered by specific lineage pairs, hidden conditions, Rare Moments, seasons, achievements, high-level parents or unusual history/hardware context.

The point of mutations is occasional “what is THAT?” surprise rather than random instability.

## Monster reveal / Hall of Legends

Monster creation deserves a proper reveal/cinematic tied to real persisted synthesis state.

Possible origin-record fields include parents, generation, date, Experience, season/day phase and selected environmental context.

Hall of Legends/family-tree ideas provide long-term emotional history. Retired/legend Beasts remain preserved rather than disappearing.

Legacy traits can affect descendant cosmetics without inheriting the parent's achievement itself; the descendant receives evidence of ancestry, not unearned accomplishment.

## Generations and Monstergotchi meaning

Future concepts include:

- Beast + Beast → Generation-1 Monster;
- later Monster + Monster → Generation-2 possibilities;
- possible Beast + Monster special hybrid branches.

These were intentionally deferred until first-generation balance is understood.

This gives “Monstergotchi” a stronger meaning: an earned second chapter unlocked by the user's roster/lineage history, not merely “Beastagotchi with more software installed.”

## PeerDex / ordinary Pwnagotchi interoperability

The recovered social architecture deliberately includes ordinary Pwnagotchi units.

A local Beastagotchi can use Pwnagotchi's existing peer identity/advertisement substrate to remember a peer even if the remote unit does not run Beastagotchi.

Two interaction levels were defined:

1. **Pwnagotchi ↔ Beastagotchi**  
   Ordinary peer metadata can feed local PeerDex, memories, achievements, Expeditions, reactions and tightly capped progression.

2. **Beastagotchi ↔ Beastagotchi**  
   Compatible peers may exchange a richer privacy-safe Beast descriptor and, eventually, Lineage Capsules.

Pwnagotchi peer identity/fingerprint remains the natural “I have met this physical unit before” key. Future Beast descriptors/capsules should add their own signing/integrity layer rather than tightly coupling long-term Beast data formats to internal pwngrid details.

Current source confirms that Beast Bridge already emits richer peer_detected/peer_lost payloads and PeerDex persists/querys identity, first/last seen, local encounter count, advertised encounter count, RSSI, best RSSI, channel, version, face, counters and session-related metadata. User-facing social progression/presentation remains a later layer.

## Social progression concepts

Recovered examples:

- Stranger;
- Acquaintance;
- Familiar;
- Friend;
- Old Friend;
- Travel Companion;
- Beast Kin.

Progression must be capped:

- first encounter meaningful;
- first reunion meaningful;
- milestones meaningful;
- repeated continuous detection essentially no XP.

Retained event/achievement ideas include Old Friends, The Herd, Monster Mash, Reunion Event and Distant Kin Detected.

Future optional cooperative survey/group behavior is allowed only if explicit, visible, reversible and non-disruptive to normal Pwnagotchi behavior.

## Privacy-safe Lineage Capsules

Lineage Synthesis does not require two devices to remain physically together.

A future Lineage Capsule may contain only approved public/hereditary material such as:

- public Beast ID;
- lineage/generation/evolution stage;
- approved hereditary/visual traits;
- temperament genes;
- relevant ancestry markers;
- public lineage accomplishments;
- integrity/signature information.

It must not contain passwords, captures, Wi-Fi history, GPS history, logs, configuration secrets or owner/private operational data.

Possible transports include QR, file, local WebUI, direct Beast peer, Bluetooth and perhaps Meshtastic later.

Physical “Natural Encounter Lineage” and intentionally imported/shared lineage may be distinguished.

## Global Interaction — recovered model

Global is an **optional layer**, not a requirement for Beastagotchi.

The recovered three-ring social model is:

- **Nearby** — physical/local Pwnagotchi/Beast encounters, offline and automatic;
- **Friends** — persistent relationships requiring explicit/mutual trust;
- **Global** — opt-in Internet/community layer.

Recovered Global ideas include public Beast/Monster profiles, community Experiences/Packs, public trophies/Hall entries, opt-in friends/favorites, community challenges/events, lineage discovery, rarity statistics, Pack recommendations and coarse-region discovery where privacy permits.

A “Global Beast Pulse” could show aggregate community state without constantly moving private data.

## Global privacy and sync rules

Global remains off by default and local data remains authoritative.

Recovered implementation at the historical **288-test** gate added:

- opt-in Global profile/sync foundation;
- separate Auto Sync enablement;
- Beast Studio Global privacy panel;
- selectable roster scope;
- achievement visibility controls;
- pseudonymous public IDs;
- sanitized public snapshots;
- content-hashed change detection so revisions occur only when selected public state changes;
- no network I/O while no provider/connector is configured.

A permanent rule emerged: **EXACT PUBLIC SNAPSHOT**. Before anything can leave the machine, the user can inspect the sanitized JSON. If information is not present in that snapshot, the connector is not allowed to send it.

Explicitly excluded from the public schema include captures, SSIDs/BSSIDs/client details, GPS history, peer fingerprints, logs, credentials and private configuration.

Lineage eligibility is separate from consent to accept lineage requests. A Beast may be “Lineage Eligible” while a future setting independently says Accept Lineage Requests: Off / Friends / Anyone.

Future Global work remains connector/provider protocol, public profile CRUD/identity rotation, friends/block/report/rate limiting, directory/events/statistics and remote Lineage Capsule exchange.

## Validation anchors recovered

Historical source checkpoints visible in the recovered conversation include:

- **972d1b7c19450727ae969e79eaea05b8144980d9** — Experience/Face/Animation/Depot milestone.
- **279-test gate** — first multi-Beast/Monster persistence foundation.
- **75d8db8caf0e599c87918e8b8d7bead2571b5160** — peer/social-lineage architecture documentation checkpoint.
- **668371ba05d2384de3787bb16b19da52e1210226** — PeerDex/richer peer-data implementation sequence.
- **0eed5aee0b069ce8af3683bb9406573c233ab6ba** — Global privacy/auto-sync foundation around the 288-test gate.
- **3edc15cff7c5317fb293f861360a69d298bd7a88** — active-Beast progression/ROSTER checkpoint around the 297-test gate.
- later branch history reaches **329 tests** for roster longevity and **332 tests** for Monster reveal/preservation state.

These are historical chronology anchors, not substitutes for current branch state.

## Recovery evidence map and completeness

Private Library preservation now contains:

- Batch 01: 14 readable screenshots;
- Batch 02: 10 readable screenshots;
- Batch 03: 15 readable screenshots;
- Batch 04: 15 readable screenshots;
- Batch 05: 15 readable screenshots;
- Batch 06: 9 readable screenshots;
- two earlier preserved source images outside the ordered batches.

Total image evidence for this pass: **80 preserved images**, of which **78** are the ordered normal-resolution reconstruction set. Each ordered batch has a text index and the private Library has a master coverage map. The long-scroll source is retained for provenance but is superseded by readable normal-resolution screenshots wherever they overlap.

As of this reconciliation:

- major Beastagotchi engineering/design gaps from the inaccessible tail of the pinned conversation are closed;
- no known major subsystem, architectural decision, validation boundary, or protected-scope decision from the recovered tail is currently missing from durable project state;
- remaining older screenshots may still improve literal historical wording, reveal smaller idea sparks/rejected alternatives, or provide provenance around the earliest Unified UX, Presentation Broker, Packs/Depot and GitHub-access/setup discussions;
- those older screenshots should be treated as **archival enrichment and contradiction checking**, not as permission to regress newer code/tests or later physical decisions;
- word-for-word transcript completeness still requires a successful ChatGPT account export if one becomes available later.

## Source-of-truth rule

Use this document for recovered **why/provenance**.  
Use the current source tree + tests for what code actually does.  
Use the Master Completion Matrix for current implementation status.  
Use the Master Continuity Ledger for protected scope.  
Use the active checkpoint and ROADMAP for current execution order.

Do not treat recovered historical milestone language as permission to regress newer implementation or physical-validation decisions.
