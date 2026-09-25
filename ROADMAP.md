# Beastagotchi Roadmap

This is the public orientation layer. The current detailed checklist is
`docs/Beastagotchi_Master_Completion_Matrix_v5.0.md`. The continuity ledger
remains the anti-forgetting authority.

For a concise current **finished vs remaining gate view**, see
`docs/Beastagotchi_Current_Gate_Status_2026-09-24.md`.

The current post-preservation architecture decisions are recorded in
`docs/Beastagotchi_Maturity_Architecture_Review_2026-09-24.md`. This review is
an active design authority for contract consolidation, Scene/Visual Runtime work,
Experience compilation and incremental monolith decomposition; it does not erase
the continuity ledger or completion matrix.

The open-ecosystem expansion direction is preserved in
`docs/Beastagotchi_External_Software_Integration_Strategy_2026-09-24.md` and
`docs/Beastagotchi_Lightbulb_Review_Capability_Platform_2026-09-24.md`. External
packages/services are treated as capability providers behind Beast contracts,
not as reasons to duplicate mature Linux/Pi software or bloat every install.

Cohesion/help/recovery/BenchLink decisions are preserved in
`docs/Beastagotchi_Cohesion_Guidance_Backup_BenchLink_2026-09-24.md`, including
spoiler-safe Choreography integration, Doctor + Runbook Registry + optional AI
Guide, contextual “Explain This” help, tiered backup/recovery, Exact Remote
Mirror, a future local BenchLink/AI tool bridge and Cohesion Graph/Lint.

Adaptive hardware/display scaling, semantic deep links, one unified Doctor with
modular probes, Rollback/Known-Good Snapshots and independent Recovery Vaults
are preserved in
`docs/Beastagotchi_Adaptive_Platform_DeepLinks_Unified_Doctor_RecoveryVault_2026-09-24.md`.
The first capability-first `PlatformProfile` is implemented in Core and exposed
at `/platform-profile`; board names refine defaults but do not define the product
boundary.

Experience DNA is implemented in `beastcore/experience_dna.py` with 16 broad visual families, independent layout/density/motion/creature/Doctor/mystery axes, adaptive platform variants, and Studio schema exposure. See `docs/Beastagotchi_Experience_DNA_Abundant_Taxonomy_2026-09-24.md` and `docs/Beastagotchi_Experience_Prototype_Briefs_v0.19_2026-09-24.md`.

PwnDoctor cross-pollination and the on-demand Doctor Knowledge/Skill Cache direction are preserved in
`docs/Beastagotchi_Doctor_Knowledge_Runtime_CrossPollination_2026-09-24.md`.
The Doctor should remain a small trusted kernel that resolves versioned condition/runbook/probe knowledge on demand; downloaded knowledge does not automatically gain Action authority.

## Release state

### Stable baseline — v0.18.1 on `main`
v0.18.1 is the current stable baseline. Its source gate passed 194/194 tests,
Python compile, shell syntax and the 32-frame validation gallery. It includes
owner-authorized Operator sessions, verified recovery staging + dry-run restore
planning, Mission Packs, canonical Beast personality state and the first
native-responsive Dashboard/Board renderer.

480×320 remains the physically validated reference display. Larger legacy pages
are not yet claimed as native-responsive.

### Active development — v0.19 Unified Experience
Development lives on `v0.19-unified-experience` in Draft PR #9. The last green
pre-reconstruction checkpoint passed **415 tests** plus Python compile/shell
validation. Gate 1 has since been intentionally reopened for visual reconstruction
and contract consolidation, so the active head must return to a new green source
gate before any physical acceptance claim.

v0.19 is deliberately doing two jobs at once:

1. make Beastagotchi feel polished, coherent and pleasant rather than merely
   feature-rich; and
2. convert optional features/content into safe modular packages so growth does
   not make every installation permanently larger/hotter/more complex.

## v0.19 execution order

### Gate 1 — Unified UX / visual acceptance

**Current status: ACTIVE — VISUAL RECONSTRUCTION.** The previous generated gallery
was explicitly rejected off-screen as too flat/card-like and too far from the
intended Beastagotchi visual language. Physical acceptance is therefore deferred
until the real generated renderer earns off-screen acceptance again.

Recent progress:
- Operations Center has moved from an equal-weight tile wall to an attention-first live-platform summary;
- platform list overlays now use 50px bottom navigation targets and a calmer three-row 480×320 rhythm;
- operational empty states explicitly preserve unavailable truth instead of synthesizing demo state;
- the captured-real-state gallery now includes Control Center, Apps, Operations, Notifications, Diagnostics, Services, Hardware, Storage, Incidents and Connectivity in addition to the primary page set.
- a bounded physical-acceptance harness now exists with automatic rollback reuse, framebuffer captures, 1 Hz runtime/Core sampling, touch evidence and a timestamped support bundle.
- the commit-pinned Pi artifact now carries a verified one-command staging wrapper + quickstart; staging verifies SHA/source provenance, preserves Beast Core config, backs up the existing Beast SQLite DB, installs Core/UI, starts Core only and leaves TFT ownership untouched until an explicit acceptance start.
- physical evidence now records the staged source commit / CI-tested commit / source archive SHA so the real TFT session is traceable back to the exact GitHub artifact;
- a layered Scene compositor proof has begun so creature/environment art, ambient motion and live HUD information can coexist without forcing every Experience into a card-grid composition;
- the maturity architecture review preserves the direction toward versioned Signal, Action, Capability, Scene and Experience contracts rather than continuing one-off UI growth;
- Signal v1 metadata is now implemented over the existing canonical StateRegistry/Telemetry Catalog, and a read-only Integration Catalog now inventories optional Linux/Pi provider backends without auto-installing them.
- Home flagship scenes now publish semantic Scene layers with per-layer render-cost metadata; SceneRuntime also tracks canonical signal changes and resolves dirty semantic layers/bounds without treating ambient decoration as telemetry.
- the deterministic Home motion proof now renders multi-frame Classic/Cyberpunk/Black-Ice/WOPR evidence from captured state and records Scene/compositor-cache metadata frame by frame;
- a real composition defect was fixed in the concept-creature path: compact concept rasters were previously passed through Pillow `thumbnail()` and therefore never enlarged to their assigned scene region. Flagship creatures now scale aspect-preservingly into the scene with edge feathering, so the Beast actually owns visual space instead of reading as a pasted icon.

Still to finish:
- return the active reconstruction head to a fully green source/CI gate;
- continue stabilizing/caching the layered Scene compositor and improve source-art fidelity now that the creature-scale composition bug is fixed; regenerate real-state visual evidence after each bounded flagship-scene step;
- obtain off-screen owner acceptance of the actual generated Home/major-scene language before staging it physically;
- define the bounded Scene/semantic-layer contract needed for visual depth and future Studio editing without turning Gate 1 into a platform rewrite;
- finish hierarchy/interaction cleanup across the high-frequency page carousel;
- preserve Home/Beast + page/tab/swipe identity;
- reduce remaining box-grid/clutter patterns and improve type/touch hierarchy;
- finish shared dialogs/toasts/loading/error states beyond the newly normalized platform browsers;
- deepen structural theme differences rather than palette-only variation;
- generate and review the next real captured-state comparison gallery;
- execute the now-implemented bounded `beast-v019-accept` Pi/TFT session covering visual/touch/heat plus real framebuffer-write evidence;
- include Capsule Share QR/phone scanning in that same physical session rather than creating a separate micro-test;
- use that review before declaring the v0.19 visual language accepted.

### Gate 2 — Beast Packs / Depot
Already implemented:
- manifest registry, intake, SHA-256 verified staging and transactional registry install;
- safe content-only enable/disable;
- Theme Pack runtime discovery;
- Board Pack read-only launcher destinations;
- Layout Pack templates importable as editable personal Boards;
- Beast Pack SDK examples;
- bounded Depot Catalog v1 parser with trust kept separate from discoverability.

Also implemented since the original Gate 2 plan:
- Face Pack consumer;
- Animation Pack consumer;
- local Depot browser/import/search/filter;
- Experience draft/preview composition.

Next:
- audio/data/map asset consumers;
- downloadable metadata/cache UX;
- compatibility/version presentation;
- remove/update flows and clearer rollback history;
- dedicated adapters for code-bearing app/renderer/integration/hardware Packs.

### Cross-cutting — Plugin & Capability Center / Dependency Resolver

Approved direction:
- treat Jayofelony stock/stock-known plugins as a first-class Pwnagotchi compatibility class;
- keep upstream plugins doing their native job while Beast normalizes useful data/actions instead of cloning every plugin;
- model `PROVIDES / REQUIRES / OPTIONAL / CONFLICTS / USED BY` across Plugins, Packs, Hardware, Experiences, Apps and Services;
- prefer abstract capabilities such as `location.position`, `power.battery.telemetry` and `network.internet` over hard dependencies on one implementation;
- arbitrate overlapping providers so several enabled GPS/power plugins do not create duplicate canonical truth;
- distinguish safe automatic remediation, confirmed transactional remediation, guided user action, provider choice and unsupported blockers;
- expose data-egress/credential/hardware requirements without ever exposing secret values;
- maintain a complete versioned **superset BOM** for the user's Pi 4 reference build while installing/running only the dependency closure needed by selected features.

Implemented foundation:
- transactional plugin toggle + config snapshot/health rollback already exists;
- Pack dependency/capability/conflict vocabulary already exists;
- stock plugin capability/requirement/provider/egress metadata is cataloged;
- shared read-only DependencyCapabilityResolver is used by Plugins and Beast Packs;
- bounded declared-requirement probes cover canonical capabilities, services,
  packages, executables, Python modules, paths, config presence and credential
  presence without installing/changing anything;
- provider index + reverse `used_by` graph exist;
- available providers are distinct from active/selected components;
- active dependency health is distinct from whole-catalog readiness;
- technical-vs-policy blockers use Owner Sovereignty semantics;
- sensitive plugin configuration exposes only presence, never credential values;
- `GET /dependencies` and platform-bundle summaries expose read-only graph health;
- read-only provider arbitration now distinguishes active native/preferred/selected
  providers, alternates, available-but-unselected providers and choice-required
  states without mutating upstream components;
- configured-but-disabled plugins can remain valid alternates;
- deterministic recommendation/fallback chains and human-readable reasons exist;
- owner preference is modeled as a future explicit input, not silently invented;
- automatic failover/provider mutation remain explicitly disabled;
- reference architecture, arbitration policy and BOM policy are documented.

Implemented beyond the initial resolver:
- persistent owner provider-preference store with atomic/private persistence;
- audited provider preference set/clear actions gated by an owner-authorized
  Operator session;
- preferences change policy only and never silently enable/switch providers;
- provider candidates now expose evidence health/confidence and canonical
  freshness where real StateRegistry metadata exists;
- first Beast Doctor/Explain layer answers why a provider is active, alternates,
  downstream `USED BY` impact and preference problems;
- read-only `/doctor`, `/explain` and `/provider-preferences` APIs plus
  structured Operator tools;
- Doctor/provider-policy state is included in sanitized support evidence.

Next:
- Plugin & Capability Center / Beast Studio presentation for provider policy,
  Doctor explanations and `USED BY`;
- provider-specific runtime health adapters beyond generic readiness evidence;
- causal-chain explanations across missing requirements, not only provider choice;
- context-aware Field/Dock/Home/Battery policy inputs;
- known-good build fingerprint + "what changed?" comparison;
- pre-action blast-radius simulation;
- anti-flap hysteresis/minimum dwell/cooldown;
- transactional TEST FAILOVER after handoff primitives exist;
- build-specific BOM generator/export;
- common resolver adoption by Experiences/Apps/Hardware Studio;
- generalized version-range resolution and guided configuration;
- transactional dependency remediation only after dry-run/provenance/rollback are proven.

### Cross-cutting — Extension Ecosystem / Beast Capsules

Approved direction:
- distinguish four user-facing extension classes:
  - Pwnagotchi Plugin;
  - Beast Pack;
  - Beast App;
  - Companion Expansion;
- use adapters as the translation pattern between existing plugin/service/hardware
  sources and canonical Beast state/events;
- keep Pwnagotchi plugins thin when their real job is callbacks/lifecycle access;
  progression, trophies, lineage and Beast UI remain canonical Beast concerns;
- let Pack manifests declare content roles/signals/transports instead of creating
  a new technical pack type for every idea;
- treat Companion Expansion as one user-facing install whose internal pieces may
  include Pwnagotchi plugin + Beast Pack/App/adapter;
- plugins/extensions contribute truthful normalized signals; the canonical
  Achievement Engine decides unlocks;
- build a transport-neutral Beast Capsule layer so the same portable object can
  move by QR, file, USB/SD, NFC, Bluetooth/local direct transfer, phone/WebUI or
  Beast-to-Beast transport;
- make offline exchange a first-class ecosystem goal, not merely "works without
  Internet."

Implemented foundation:
- Pack manifests now support `extension_class`, `content_roles`,
  `signals_provides`, `signals_consumes`, `offline_transports`,
  `capsule_types` and Companion component declarations;
- `beastcore/capsules.py` provides bounded BC1 canonical JSON + SHA-256
  integrity + zlib/base64url encoding;
- bounded QR-ready BCQ1 multi-frame text framing/reassembly with per-frame CRC,
  mixed-session detection and complete Capsule verification;
- Lineage Capsule export from the persistent Beast roster using a separate
  offline Capsule namespace and pseudonymous creature IDs;
- Lineage export omits local IDs, raw identity/preferences/counters, captures,
  network history, credentials, exact location and logs;
- achievement IDs are opt-in; achievement count may be shared without the IDs;
- read-only `/capsule/export` and `/capsule/types` endpoints;
- import remains preview-only/non-mutating;
- checksum/integrity is explicitly not presented as sender authenticity;
- no QR-rendering/camera dependency was added to the base image.

Implemented visual transport step:
- optional lightweight QR renderer adapter in Beast UI using `qrcode` when
  available;
- real Capsule Share Beast App overlay fetching a fresh Lineage Capsule from Core;
- 48px+ manual frame controls and horizontal swipe navigation;
- explicit unsigned/integrity-only + privacy messaging;
- machine-readable QR transport is rendered above theme scanlines/effects;
- CI gallery includes a clearly labeled non-importable preview derived only from
  the sanitized real-device fixture;
- representative off-screen 480×320 density gate requires >=3 px/module;
- manual off-screen artifact inspection decoded the generated PNG back to its
  exact BCQ1 frame;
- `qrcode` remains development/CI + candidate optional runtime dependency; it
  is not silently installed into the protected Pwnagotchi environment.

Next:
- Beast-owned optional Python runtime path is now implemented for the QR renderer:
  `prepare-qr` installs the CI-tested qrcode 8.2 wheel into
  `/opt/beast-python/site-packages` with SHA-256 provenance and `remove-qr`
  removes it without modifying Pwnagotchi site-packages;
- physically validate TFT/phone-camera scanning before choosing animation timing;
- automatic frame cycling + receiver/missing-frame UX after physical evidence;
- Studio Capsule Workshop exact-share preview is implemented with explicit
  name/appearance/achievement-ID controls, exact envelope JSON and local QR frame
  rendering; no import/publication/roster mutation occurs;
- extend that Workshop with file export and later scan/import preview while
  keeping receive non-mutating;
- signed Capsule identity/authenticity design;
- Beast Card/PeerDex Capsule;
- Challenge Capsule;
- remote-lineage storage distinct from locally owned Beasts;
- only later confirmed lineage import/synthesis semantics;
- Plugin Profiler for callback/runtime/error attribution;
- generic plugin-card generation from capability/config/action declarations;
- Companion Expansion install orchestration only after each internal component's
  transaction boundary is explicit.

### Cross-cutting — Owner Sovereignty / Unrestricted Mode

Approved direction:
- Beastagotchi is an owner-controlled open platform, not a locked appliance;
- safe defaults, compatibility checks, snapshots, rollback and trusted sources are the managed path, not permanent ownership restrictions;
- plans distinguish technical blockers from Beast policy/support blockers;
- policy blockers are explicitly owner-overridable when the requested action is technically possible;
- persistent Expert Mode plus per-action "Proceed unsupported anyway" are retained UX requirements;
- unsupported/custom systems remain usable and are labeled accurately rather than punished or feature-locked;
- SSH/root/manual administration remains the ultimate escape hatch;
- owner override remains locally authorized and must not become an unauthenticated remote bypass;
- exact manual instructions should be provided when Beast cannot safely perform a self-disabling action from its own running control plane;
- warnings about dependency, conflict, egress, resource/thermal impact and rollback remain visible even when the owner proceeds.

Implemented foundation:
- Owner Sovereignty / Unrestricted Mode specification;
- PluginBroker planning distinguishes `technical_blockers` and `policy_blockers`;
- persistent Expert Mode state exists and changing it requires an active
  owner-authorized administrator session;
- explicit per-action plugin policy override is supported only while Expert Mode
  is active; technical blockers remain absolute;
- plugin override retains transactional snapshot/verification/restart/health/
  rollback behavior;
- successful overrides persist customized/support-state evidence and durable
  audit events;
- read-only owner-mode status is available through Core/API/structured Operator
  tools;
- sanitized Support Bundles report Expert/customized state.

Next:
- dedicated Beast Studio/TFT Expert Mode control + obvious indicator;
- policy-vs-technical blocker semantics now extend into the common Dependency &
  Capability Resolver;
- reverse `used_by` impact in override confirmations;
- unsupported plugin/source import;
- exact manual/root escape-hatch instructions for self-disabling operations;
- verified return-to-managed-baseline workflow;
- direct owner administration surface only after local-auth/audit/recovery boundaries are explicit.

### Gate 3 — Presentation ownership / Theme Manager coexistence

A fresh review of the substantially expanded Theme Manager is captured in
`docs/KORRIE71_THEME_MANAGER_REINTEGRATION_AUDIT_2026-09-23.md`. It adds
candidate work around dirty-region display writes, canonical live tokens,
declarative visual effects/scenes, timed physical preview/revert, semantic render
layers, a Theme Manager asset bridge and a neutral presentation-engine adapter.
Those are design targets until individually implemented/tested.

Implemented now:
- bounded read-only Theme Manager source capability probe;
- version/capability evidence exposed through canonical plugin/presentation state;
- clean unload/live-install compatibility evidence kept distinct from a real managed handoff API;
- physical presentation executor remains locked.

Next:
- keep Gate 1 visual acceptance ahead of a new backend detour;
- canonical live-token foundation is implemented; add semantic render-layer metadata in a bounded block;
- add Beast-native Doctor/Explain and improve Depot human workflow using the 3.0 audit;
- validate stock/Jayofelony release/acquire semantics;
- validate Korrie71 Theme Manager release/acquire semantics;
- implement real Presentation Broker adapters;
- persistent owner selection: Native / Theme Manager / Beast;
- transactional handoff with health observation and rollback;
- keep non-owning WebUI/API/data functions alive where compatible;
- physically validate repeated switching without framebuffer/touch races.

### Gate 4 — Update Center
Already implemented:
- trusted-source metadata checks;
- SHA-256 verified download staging;
- Pack transaction history;
- policy intent: manual / notify / auto-stage / auto-install;
- safe Pack auto-install boundary for verified eligible Packs.

Next:
- full compatibility fingerprinting;
- user-facing update history/status;
- maintenance-window/docked/Internet-online policy;
- component-specific adapters for Beastagotchi, Pwnagotchi and Theme Manager;
- backup/health probation/rollback before any broader unattended component update;
- never turn a Depot listing into automatic trust.

### Gate 5 — Performance / thermal / hardware
- continue per-process and per-render cost attribution;
- remove duplicate polling/render loops before degrading the experience;
- suspend inactive optional services/content;
- validate sustained Pi 4 heat/load on the target enclosure;
- Hardware Studio / accessory role enrollment;
- second Wi-Fi role UX;
- cooling/fan, battery/power and dock telemetry/control where hardware exists;
- Bluetooth/SDR/Meshtastic/etc remain capability-driven optional modules.

### Gate 6 — Responsive displays / companion surfaces
- migrate legacy pages to native responsive composition;
- common 5-inch HDMI/DSI-class target;
- external Command Center;
- responsive Beast Studio / local companion PWA;
- phone/tablet settings, logs, files, backups and control;
- local Wi-Fi/Ethernet/USB and appropriate Bluetooth/BLE connectivity paths.

### Gate 7 — Beast Roster / Lineages / Monstergotchi

Implemented foundation:
- persistent multi-Beast SQLite roster;
- Founder migration path for the existing single progression profile;
- independent XP/levels and active/resting state;
- ancestry and Monster synthesis records;
- Alpha/level-70 v1 synthesis gate for both parents;
- parents preserved after synthesis;
- first Monster unlocks the future `monstergotchi.core` layer.

Implemented after the foundation:
- live progression is bound to the active roster creature with Founder legacy rollback mirroring;
- Beast Studio Roster shows persistent creatures and provides audited active-creature switching;
- global versus per-Beast achievement/collection split;
- Beast-first versus device-first encounter rewards with anti-farming cap;
- per-Beast preferred presentation memory + preview restore;
- deterministic inheritance foundation;
- per-Beast milestone/Expedition/Rare/personality memory timeline;
- procedural Monster synthesis reveal ceremony;
- Hall of Legends + ancestry graph/Studio viewer foundation.

Next:
- curated lineage-pair mutation rules;
- lineage-specific/authored Monster reveal variants;
- dedicated visual ancestry renderer;
- later evaluate additional generations;
- Lineage Capsule **export/transport foundation is implemented**; remote-lineage
  storage/import/synthesis remains future work.

### Gate 7A — Peer encounters / Beast social layer

Direction:
- reuse Pwnagotchi's existing pwngrid peer identity/encounter substrate;
- ordinary Pwnagotchi peers can count locally even when they do not run Beastagotchi;
- Beast-to-Beast features add a separate privacy-safe capability layer;
- first-meeting/reunion/friend/bond events feed progression with anti-farming limits;
- Lineage Capsules now have a privacy-curated offline export/transport foundation
  without captures, secrets, logs, location history or local roster IDs;
- no cloud service is required.

Current foundation:
- Beast Bridge emits richer peer_detected/peer_lost payloads from Pwnagotchi peer objects;
- persistent PeerDex storage/query implementation accepts ordinary Pwnagotchi peer identities and retains encounter/RSSI/channel/version/face/counter/session metadata;
- user-facing social progression/presentation and the richer Beast-to-Beast descriptor layer remain incomplete.

Next:
- canonical peer events through Beast Bridge;
- Beast UI peer presentation and achievements;
- public Beast peer descriptor/privacy schema;
- actual QR rendering/scanning + explicit opt-in Lineage Capsule receive flow;
- Beast Card / PeerDex Capsule enrichment;
- remote-lineage storage and synthesis only after import/authenticity semantics
  are mature.

### Gate 7B — Global Interaction

Implemented local/privacy foundation:
- Global is optional and off by default;
- auto-sync is separately opt-in;
- sanitized public snapshots can track selected roster/progression changes;
- achievements can be none/selected/all;
- public creature IDs are pseudonymous;
- snapshots are content-hashed and queued only when public data changes;
- no network I/O occurs until a future connector is configured.

Also implemented:
- Global settings/privacy UI with exact public-profile preview.

Next:
- provider/connector contract;
- public profile create/update/delete and identity rotation;
- directory/friends/community events/rarity statistics;
- remote Lineage Capsules with block/report/rate-limit protections.

### Gate 8 — Experience depth
- richer progression/evolution/personality presentation;
- achievements/awards/rarity/trophy cabinet;
- secrets/codes/ciphers/Cipher Console;
- Rare Moments and 5–60 second Rare Cinematics;
- seasonal/day-phase/weather/celestial presentation from real context;
- Expedition archive/replay and Memory Vault/scrapbook;
- peer-Beast encounters and other retained delight systems.

### Gate 9 — Recovery / self-maintenance
- Recovery Vault provider model so rescue copies can leave a failing source SD for USB, BenchLink, NAS/SFTP, another trusted Beast or optional encrypted remote storage;
- Rollback/Known-Good Snapshots for fast pre-change recovery, distinct from disaster backups;
- unified Doctor architecture: one user-facing Doctor, modular background/on-demand probes, shared severity/evidence/runbook/recovery model;
- semantic Beast Links/deep links so Doctor/help/runbooks can navigate users directly to exact settings, evidence, backups, capabilities and actions across TFT/WebUI/phone;
- tiered backup model: transaction snapshot → Critical State → Rebuild Bundle → bare-metal/full-system backup → Emergency Rescue;
- Doctor-integrated backup freshness and storage-risk response, with small critical rescue before stressing suspected failing media;
- verified Runbook Registry + contextual assistance path for diagnosis/recovery;
- future BenchLink for local laptop/device diagnostics, Exact Remote Mirror and explicit support/recovery operations;
- live restore transaction with rescue backup;
- service quiesce/apply/verify/rollback;
- self-healing actions with explicit limits;
- Kiwix/ZIM reader;
- offline runbook UX;
- bounded persistent log/export policy validated for SD-card wear.

### Gate 10 — Public beta / v1.0
- supported-hardware matrix;
- installer/upgrader/uninstaller + migration framework;
- clean-machine preflight;
- screenshots/video/quick-start/manual/troubleshooting;
- Pack author/contributor documentation;
- stable release packaging and checksums;
- physical regression matrix;
- tagged public beta followed by v1.0.

## Permanent protected scope

The following are not removed just because they are not in the current sprint:
pages/tabs/swipes; Beast/Home creature identity; levels/growth/evolution;
achievements/awards/secrets/rares/legendaries/ciphers; Expeditions/replay/Memory
Vault; Theme/Visualizer/Spatial Studios; files/logs/backups/incidents; phone and
tablet surfaces; multi-display support; second Wi-Fi/Bluetooth/GPS/SDR/ADS-B/
Meshtastic/sensors; offline maps/RF Universe; dock/Home Base; peer Beasts/Beast
Bus; optional local AI/voice; containers; WOPR/NORAD, sonar, Mission Control,
Oscilloscope and other retained visual/app concepts.

## GitHub development cadence

Normal development:
`main` (stable) → milestone branch → bounded development commits + CI → physical
gate where required → merge/tag/release.

Development commits are allowed on the active branch because they provide
rollback points and CI. They are **not** treated as releases. `main`, tags and
GitHub Releases are updated only for meaningful validated milestones.

## Sources of truth

- Detailed status: `docs/Beastagotchi_Master_Completion_Matrix_v5.0.md`
- Anti-forgetting scope: `docs/Beastagotchi_Master_Continuity_Ledger_v1.0.md`
- Architecture: `docs/Beastagotchi_Design_Architecture_Bible_v1.0.md`
- Active checkpoint: `docs/Beastagotchi_v019_Active_Checkpoint_Delta.md`
- UX gate: `docs/UX_POLISH_MILESTONE_v0.19.md`
- Development/release workflow: `docs/Beastagotchi_Development_Release_Workflow.md`
- Recovered design/provenance: `docs/Beastagotchi_Recovered_Conversation_Continuity_Addendum_2026-09-23.md`


## Preservation checkpoint — 2026-09-23

The recovered cross-chat/Library/repository state is preserved in `docs/Beastagotchi_Project_Continuity_Preservation_2026-09-23.md`. That document records current branch/SHA provenance, superseded physical decisions, validation boundaries and recovered historical artifacts. Raw private chats are not required to reconstruct the engineering state.


## Development method recovered from continuity work

The roadmap is intentionally a **memory/execution system, not a rigid cage**.
Approved ideas must not silently disappear. Beastagotchi should periodically
perform Lightbulb Reviews, challenge its own designs when better paths appear,
prefer modular Packs for optional/exotic capabilities, keep real information
ahead of decoration, preserve delight/rarity/personality systems, optimize
duplicate work before degrading features, and pair new powers with recovery and
rollback.

The detailed recovered rationale is preserved in
`docs/Beastagotchi_Recovered_Conversation_Continuity_Addendum_2026-09-23.md`.

- Experience DNA expansion: prototype **Atlas -> Forge -> Observatory -> Habitat -> Monolith** as deliberately different whole-product experience families; legacy theme identities remain presets/references rather than the main taxonomy.

### 2026-09-24 Experience-DNA visual proof update

- the first five non-legacy Home proofs are now implemented and CI-rendered from the same sanitized real target state: **Atlas, Forge, Observatory, Habitat, Monolith**;
- a side-by-side comparison artifact confirms meaningful structural diversity before palette customization;
- Atlas remains the most card-adjacent and should integrate its edge instruments more organically;
- Forge needs richer physical/material depth, not additional telemetry density;
- Observatory currently has the strongest information hierarchy and should be extended into Spectrum/measurement pages next;
- Habitat requires substantially richer creature/environment art and choreography while protecting creature-first hierarchy;
- Monolith requires premium typography/transitions and restraint; do not fill its negative space with more widgets;
- next architecture proof: extend **Atlas** and **Observatory** beyond Home, then Habitat, to prove Experience DNA changes whole-product page language rather than only the landing screen.
- Cross-page Experience proof is now implemented: **Atlas Recon** retains field-survey language and **Observatory Spectrum** retains scientific measurement language from the same canonical state.
- `beastui/experience_registry.py` centralizes currently implemented Experience/page renderers; Studio schema exposes coverage and `/api/experience-preview` provides paired live previews.
- next diversification proof: translate **Habitat** into progression/memory/Expedition surfaces before broad production integration.
- production TFT ownership should wait for an Experience Compiler/resolution path and owner off-screen acceptance; do not hard-wire prototypes directly into live navigation yet.
- All five first non-legacy Experience prototypes now have cross-page proof: Atlas Home/Recon, Forge Home/System, Observatory Home/Spectrum, Habitat Home/Beast, Monolith Home/Overview. Preserve their distinct product grammars as additional pages are added.
