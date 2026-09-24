# Beastagotchi Roadmap

This is the public orientation layer. The current detailed checklist is
`docs/Beastagotchi_Master_Completion_Matrix_v5.0.md`. The continuity ledger
remains the anti-forgetting authority.

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
Development lives on `v0.19-unified-experience` in Draft PR #9. The current
preserved source gate is **351 passing tests** plus Python compile/shell validation.

v0.19 is deliberately doing two jobs at once:

1. make Beastagotchi feel polished, coherent and pleasant rather than merely
   feature-rich; and
2. convert optional features/content into safe modular packages so growth does
   not make every installation permanently larger/hotter/more complex.

## v0.19 execution order

### Gate 1 — Unified UX / visual acceptance
Recent progress:
- Operations Center has moved from an equal-weight tile wall to an attention-first live-platform summary;
- platform list overlays now use 50px bottom navigation targets and a calmer three-row 480×320 rhythm;
- operational empty states explicitly preserve unavailable truth instead of synthesizing demo state;
- the captured-real-state gallery now includes Control Center, Apps, Operations, Notifications, Diagnostics, Services, Hardware, Storage, Incidents and Connectivity in addition to the primary page set.

Still to finish:
- finish hierarchy/interaction cleanup across the high-frequency page carousel;
- preserve Home/Beast + page/tab/swipe identity;
- reduce remaining box-grid/clutter patterns and improve type/touch hierarchy;
- finish shared dialogs/toasts/loading/error states beyond the newly normalized platform browsers;
- deepen structural theme differences rather than palette-only variation;
- generate and review the next real captured-state comparison gallery;
- perform another physical Pi/TFT visual + touch + heat review;
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
- stock plugin capability/requirement/provider/egress metadata is now cataloged in PluginIntegrationEngine;
- requirement execution is explicitly disabled: this milestone is catalog-only;
- reference architecture and BOM policy are documented.

Next:
- side-effect-free requirement probes for declared requirements only;
- reverse dependency / `used_by` graph;
- provider arbitration;
- Plugin & Capability Center requirement/status presentation;
- Beast Doctor/Explain integration;
- build-specific BOM generator/export;
- transactional dependency remediation only after dry-run/provenance/rollback are proven.

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
- later evaluate additional generations and privacy-safe cross-device Lineage Capsules.

### Gate 7A — Peer encounters / Beast social layer

Direction:
- reuse Pwnagotchi's existing pwngrid peer identity/encounter substrate;
- ordinary Pwnagotchi peers can count locally even when they do not run Beastagotchi;
- Beast-to-Beast features add a separate privacy-safe capability layer;
- first-meeting/reunion/friend/bond events feed progression with anti-farming limits;
- future Lineage Capsules allow cross-device ancestry without sharing captures,
  secrets, logs or location history;
- no cloud service is required.

Current foundation:
- Beast Bridge emits richer peer_detected/peer_lost payloads from Pwnagotchi peer objects;
- persistent PeerDex storage/query implementation accepts ordinary Pwnagotchi peer identities and retains encounter/RSSI/channel/version/face/counter/session metadata;
- user-facing social progression/presentation and the richer Beast-to-Beast descriptor layer remain incomplete.

Next:
- canonical peer events through Beast Bridge;
- Beast UI peer presentation and achievements;
- public Beast peer descriptor/privacy schema;
- explicit opt-in Lineage Capsule exchange;
- remote-lineage synthesis only after local roster/synthesis is mature.

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
