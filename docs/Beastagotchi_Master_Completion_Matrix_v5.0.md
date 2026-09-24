# Beastagotchi Master Completion Matrix v5.0

**Status date:** 2026-09-23  
**Stable baseline:** v0.18.1 on `main`  
**Active development:** `v0.19-unified-experience`, Draft PR #9  
**Current v0.19 source gate:** **348 automated tests passing** + Python compile + shell syntax

This is the current implementation checklist and anti-forgetting execution
matrix. It supersedes v4.7 for status tracking but does not delete any earlier
approved scope.

## Legend

- [x] implemented in the current codebase and covered by source/CI validation
  unless a physical qualifier says otherwise;
- [~] partial/in-progress;
- [ ] planned/not implemented;
- **PHYSICAL** means source support exists but target-hardware validation remains;
- **RESERVED** means explicitly approved long-term scope, not abandoned.

---

## 1. Protected Pwnagotchi foundation / canonical data

- [x] keep Pwnagotchi/Bettercap as protected independent engines
- [x] Beast Core daemon separate from Pwnagotchi process
- [x] Beast Bridge callback/event path rather than HTML scraping as primary path
- [x] canonical state/event/history model
- [x] SQLite durable history/state
- [x] Bettercap current-session Wi-Fi state
- [x] `.apcache` fallback/encounter history path
- [x] AP/client/channel/encryption/vendor/handshake data normalization
- [x] CPU/load/RAM/temp/uptime/throttle telemetry
- [x] GPS/gpsd telemetry and debounced fix state
- [x] services/storage/USB/capability discovery
- [x] live-data-first UI contract; no demo telemetry substituted for missing data
- [x] critical Pwnagotchi/Bettercap/read-only-root failures affect overall health
- [x] semantic STARTING/DEGRADED/CRITICAL startup readiness
- [ ] broader adapter SDK for third-party live data providers

## 2. Physical display / touch / presentation substrate

- [x] ILI9486 480×320 framebuffer path validated on target Pi
- [x] ADS7846/XPT2046 single-touch input validated
- [x] production touch affine calibration retained
- [x] tap/swipe/long-press input handling
- [x] large touch targets / edge-aware hit zones
- [x] reversible framebuffer ownership
- [x] native RGB565 framebuffer writer
- [x] framebuffer diff/write optimization
- [x] native Pwnagotchi RAW/Dark/Light/Chroma bridge
- [x] logical 480×320 canvas separated from physical output
- [x] aspect-preserving transform + reverse touch mapping
- [x] 640×480 / 800×480 compatibility output proofs
- [x] first native-responsive Dashboard/Board renderer
- [ ] migrate remaining legacy pages to native-responsive layouts
- [ ] production support for common 5-inch HDMI/DSI target
- [ ] production external-display Command Center runtime
- [ ] repeated physical multi-owner presentation-switch test

## 3. Main page / tab / swipe experience

- [x] page/tab/swipe concept explicitly permanent
- [x] Home/Beast remains primary landing page
- [x] main carousel is curated, not a cap on total apps/features
- [x] Home/Beast shows creature + level/growth/evolution/aura context
- [x] Recon page family
- [x] Networks page family
- [x] Spectrum page family
- [x] Captures page family
- [x] Map/field page foundations
- [x] System page family
- [x] Overview whole-device summary
- [x] Dashboard/Boards as live instrument pages
- [~] v0.19 hierarchy/typography/navigation redesign across high-frequency pages
- [~] consistent first-time-user interaction grammar
- [~] consistent empty/loading/error/no-capability states
  - operational platform browsers now have truthful no-data messaging and a calmer three-row layout
- [~] consistent dialogs/confirmations/toasts
  - platform browser bottom navigation is now standardized at 50px-high touch targets
- [ ] v0.19 physical TFT visual acceptance
- [ ] final production visual language acceptance

## 4. Beast UI visual system / themes

- [x] shared design tokens: canvas, spacing, touch, radii, motion, hierarchy
- [x] shared card/status/progress/divider primitives
- [x] structural Theme model separate from data/layout
- [x] Classic
- [x] Matrix
- [x] Starcore
- [x] Black Ice
- [x] Hunter
- [x] Minimal
- [x] native Pwnagotchi theme profiles
- [~] additional theme families already represented in current source/design work
- [~] make major themes structurally distinct rather than palette/effect variants
- [x] exact/off-screen gallery tooling
- [x] captured-state gallery path that does not invent missing telemetry
- [x] captured-state gallery includes Control Center/Apps and major operational overlays
- [ ] final visual regression acceptance gallery
- [ ] physical theme-family readability/heat comparison

### Retained visual identities — RESERVED
- [ ] Synthwave
- [ ] Amber Tactical
- [ ] Ghost Minimal
- [ ] Cyberpunk
- [ ] Stealth / Red Alert
- [ ] Forest
- [ ] Vaporwave
- [ ] Space
- [ ] Holographic
- [ ] Golden
- [ ] Samurai
- [ ] WOPR / NORAD
- [ ] Steampunk
- [ ] Blueprint
- [ ] Terminal+
- [ ] Biohazard
- [ ] Glitch
- [ ] Comic
- [ ] seasonal/user theme families
- [ ] sonar/submarine presentation
- [ ] Mission Control presentation
- [ ] Oscilloscope Lab presentation

## 5. Renderers / visualization / Studio customization

- [x] renderer choice separated from theme
- [x] line/area/multiline graph foundations
- [x] bars/stacked-bars/histogram foundations
- [x] heatmap/waterfall/waveform families
- [x] radial/donut/radar/polar/signal families
- [x] timeline/numeric/microtrend families
- [x] Theme Library / Theme Studio foundations
- [x] Visualizer Studio
- [x] Beast Studio exact preview path
- [x] live Dashboard composer
- [x] 12×8 spatial Board geometry
- [x] drag/resize/overlap/hide instruments in Studio
- [x] custom Boards
- [x] Context Decks
- [x] palette overrides
- [x] named Studio variants
- [x] Correlation Lab
- [ ] full per-widget renderer eligibility/editor polish
- [ ] full Spatial Studio beyond current Board composer
- [ ] theme scheduling/randomization
- [ ] context-driven automatic layout switching

## 6. Beast personality / progression / creature experience

- [x] finite level model 1–100
- [x] persistent progression profile
- [x] evolution stages
- [x] XP/growth tied to real activity
- [x] session aura foundation
- [x] canonical personality state derived from real operational conditions
- [x] energy/curiosity/focus/confidence/stress model
- [x] Face Engine prefers canonical Beast state with Pwnagotchi fallback
- [~] mature animation/personality state-machine presentation
- [~] richer growth/evolution ceremony/presentation
- [ ] full user-facing progression history
- [ ] Beast customization/personality controls

## 6A. Multi-Beast roster / lineages / Monsters

- [x] architecture changed from one permanent save slot toward global + per-creature progression
- [x] additive SQLite roster schema
- [x] independent Beast identity/progression records
- [x] active/resting Beast state
- [x] legacy single `profile.json` migration into a non-destructive Founder Beast record
- [x] independent XP/level persistence proven for multiple Beasts
- [x] active Beast switching persistence foundation
- [x] ancestry storage
- [x] Monster synthesis transaction foundation
- [x] first Monster globally unlocks `monstergotchi.core`
- [x] parents are preserved and never reset/consumed
- [x] v1 synthesis requires two distinct level-70+ Beast-class parents
- [x] v1 prevents repeated reroll synthesis from the same unordered parent pair
- [x] deterministic inheritance seed + parent lineage/preference snapshot recorded
- [x] core synthesis is sex/gender agnostic; lineage Packs may present optional identity/family terminology
- [x] live ProgressionEngine cut over from legacy single profile to active roster Beast
- [x] canonical active-Beast/progression roster summary state
- [x] Beast Studio Roster UI / audited active-creature switcher
- [x] per-Beast preferred presentation memory (Experience/Theme/Face/Motion/Board/Deck + validated Studio configuration)
- [x] Roster supports Wake Only versus Wake + Load Preferred into Studio draft
- [x] preferred presentation restore remains preview-only until explicit APPLY TO BEAST
- [x] global/device achievement layer separated from per-Beast achievements
- [x] Beast-first versus device-first discovery accounting with capped familiar-world XP
- [x] low-volume per-Beast memory timeline for evolution/achievement/Rare/Expedition/lineage milestones
- [x] per-Beast Expedition participation join records with throttled persistence
- [x] stable personality-state transition history (10s debounce; no high-rate telemetry duplication)
- [x] deterministic hybrid visual/behavior heritage trait generator
- [~] mutation framework + generic rare mutation vocabulary; curated lineage-pair/archetype rules pending
- [x] Monster-specific fallback evolution vocabulary (Origin → Awakened → Morph → Adapted → Chimera → Ascendant → Prime → Mythic → Monstergotchi)
- [x] Beast Studio non-mutating synthesis plan + explicit audited Monster creation
- [x] procedural Monster synthesis reveal ceremony with first-Monstergotchi-unlock distinction
- [ ] optional richer authored Monster reveal assets / lineage-specific ceremonies
- [x] Hall of Legends foundation with explicit level-100 induction independent of active/resting state
- [x] ancestry/family-tree data graph + Beast Studio textual viewer foundation
- [ ] dedicated visual ancestry/family-tree renderer
- [ ] additional synthesis slots earned through high-level/rare milestones
- [ ] evaluate later-generation Monster×Monster / Monster×Beast rules
- [ ] privacy-safe cross-device Lineage Capsule exchange for optional community ancestry
- [ ] physical roster/switch/synthesis usability validation

## 6B. Peer encounters / Beast social layer

- [x] architecture recognizes existing Pwnagotchi pwngrid peer layer as reusable substrate
- [x] compatibility decision: ordinary Pwnagotchi peers count as Beastagotchi encounters even when remote device has no Beastagotchi
- [x] two-tier interaction model defined: Pwnagotchi-compatible encounter vs Beast-to-Beast encounter
- [x] privacy-safe cross-device Lineage Capsule concept protected
- [ ] Beast Bridge canonical peer_detected / peer_lost events
- [x] persistent PeerDex / social encounter table keyed by pwngrid fingerprint (storage/query foundation; bridge/UI integration still pending)
- [ ] first-meeting / reunion / recurring-friend achievement families
- [ ] capped/diminishing social XP to prevent proximity farming
- [ ] peer encounters attached to Expeditions / Memory Vault
- [ ] Beast UI nearby-peer / old-friend presentation
- [ ] Beast peer-extension public descriptor schema
- [ ] explicit opt-in Beast-to-Beast descriptor exchange
- [ ] Lineage Capsule export/import
- [ ] automatic nearby Lineage Capsule exchange after explicit user approval
- [ ] local Beast + remote lineage synthesis path
- [ ] later peer group/party/cooperative survey concepts
- [ ] later Meshtastic/LoRa peer-presence transport

## 6C. Global Interaction / public profile sync

- [x] Global Interaction architecture: optional and offline-independent
- [x] separate local pwngrid identity from opt-in public Beast identity
- [x] automatic sanitized public-profile mirror concept
- [x] Global publishing disabled by default
- [x] auto-sync independently disabled by default
- [x] active/all/selected roster publication scopes
- [x] granular publication categories for names/lineage/level/stage/synthesis eligibility/Monsters/ancestry/Experiences/roster totals
- [x] achievements publication modes: none / selected / all
- [x] pseudonymous public creature IDs instead of raw internal Beast IDs
- [x] change-hashed local revision queue; unchanged/private-only changes do not create duplicate public revisions
- [x] current sync foundation performs no network I/O until a connector is configured
- [x] Beast Studio Global privacy/settings UI
- [x] exact public-profile preview: "this is exactly what others will see"
- [ ] connector/provider interface
- [ ] remote profile create/update/delete
- [ ] public identity rotation/revocation UI
- [ ] community directory/feed
- [ ] friend/follow/block/report/rate-limit controls
- [ ] global achievement rarity/statistics
- [ ] community challenges/events
- [ ] remote Lineage Capsule exchange
- [ ] explicit privacy/security review before any public backend deployment

## 7. Achievements / secrets / rares / delight systems

- [x] achievement/award foundation
- [x] progress/rarity concepts
- [x] achievement explorer foundations
- [x] Rare Moment scheduling/witnessing foundation
- [x] rare-event acknowledgement path
- [x] fade/drift/cross/orbit/ghost/storm/apparition/cinematic mechanism foundations
- [x] seasonal/day-phase/moon context foundations
- [ ] hundreds-scale long-tail achievement catalog
- [ ] trophy cabinet / collections presentation
- [ ] hidden achievements
- [ ] Easter eggs / secret interactions
- [ ] codes/ciphers
- [ ] Cipher Console / puzzles
- [ ] rare/epic/legendary discovery tiers
- [ ] 5–60 second Rare Cinematics library
- [ ] weather-driven presentation where a real data source exists
- [ ] richer celestial/seasonal presentation
- [ ] optional sound/haptics/LED reward reactions

## 8. Expeditions / encounters / memory

- [x] Expedition foundation
- [x] trip/session metrics
- [x] distance/AP encounter tracking
- [x] BeastDex network encounter concept/foundation
- [x] Capture Vault
- [x] persistent encounter/history storage
- [ ] Expedition archive browser polish
- [ ] visual Expedition replay
- [ ] Memory Vault / scrapbook
- [ ] trophy/record integration
- [ ] peer-Beast encounter records
- [ ] unified long-term exploration timeline

## 9. Search / files / offline knowledge

- [x] Universal Search foundation
- [x] Field Library foundation
- [x] text/Markdown/config/HTML indexing
- [x] EPUB extraction
- [~] PDF extraction when PyMuPDF/pypdf available
- [x] FTS5-ranked search with fallback
- [x] safe authenticated Beast Studio import/open
- [x] incident → offline runbook link
- [ ] native Kiwix/ZIM reader
- [ ] polished on-device search input suitable for touch targets
- [ ] broader file manager/portal UX
- [ ] QR import/share workflows
- [ ] built-in offline manual integrated into Library

## 10. Operations / services / observability

- [x] whole-device Overview
- [x] Operations Center
- [x] service/dependency topology
- [x] Task Center / durable jobs
- [x] Black Box incidents
- [x] incident state/event snapshots
- [x] allow-listed audited service restart
- [x] Plugin catalog reconciliation
- [x] Connectivity Center with route vs Internet truth
- [x] container capability discovery
- [x] display/DRM capability inventory
- [x] local AI/model/voice capability discovery
- [x] privacy-sanitized Support Bundles
- [x] Support Bundles exposed via Action Broker/Task/Studio
- [x] per-process CPU/RSS resource visibility
- [x] Beast UI render/compose/write-cost visibility
- [x] Pi clock/throttle/resource-governor visibility
- [~] bounded persistent logging/export policy
- [ ] target validation of journald/export retention vs SD write wear
- [ ] Boot POST / self-explaining startup diagnostic UX
- [ ] richer explain-error/remediation UX

## 11. Recovery / backups / rollback

- [x] recovery backup creation
- [x] online SQLite-safe snapshot
- [x] backup SHA-256
- [x] archive boundary/link safety verification
- [x] manifest verification
- [x] embedded SQLite quick_check
- [x] isolated restore staging
- [x] dry-run restore plan
- [x] config snapshots for transactional plugin changes
- [x] Support Bundle independent of WebUI
- [ ] live restore apply
- [ ] rescue backup before restore
- [ ] service quiesce ordering
- [ ] post-restore health verification
- [ ] automatic restore rollback
- [ ] full Recovery Center wizard
- [ ] bounded self-healing actions

## 12. Beast Operator / AI / automation

- [x] structured tool registry
- [x] Observer/Operator/Maintainer/Administrator tiers
- [x] real time-limited owner-authorized privilege sessions
- [x] session expiry/revocation/audit
- [x] no implicit generic shell primitive
- [x] structured read/search/library/incident/job tools
- [x] structured backup/plugin/container/support/recovery actions
- [ ] local inference backend
- [ ] owner-approved controlled shell/admin tool with explicit session boundary
- [ ] push-to-talk offline voice backend
- [ ] AI-assisted diagnostics/remediation UX
- [ ] local model resource/thermal policy

## 13. Plugins / Pwnagotchi configuration

- [x] plugin inventory/categorization foundation
- [x] plugin enable/disable through audited action path
- [x] config snapshot before mutation
- [x] TOML/config validation foundation
- [x] restart + post-change health observation
- [x] automatic rollback on failed plugin transaction
- [x] Plugin Manager in Beast UI/Studio
- [x] legacy display-owner conflict awareness
- [x] Jayofelony stock/stock-known plugin compatibility class cataloged
- [x] stock plugin role / provides / requires / provider-group / data-egress / credential / hardware metadata foundation
- [x] dependency metadata remains catalog-only; automatic requirements executor explicitly disabled
- [x] shared Dependency & Capability Resolver architecture approved across Plugins/Packs/Hardware/Experiences/Apps/Services
- [x] reference-build superset BOM policy: catalog broadly, install only selected-feature dependency closure
- [~] plugin compatibility/dependency metadata coverage
- [ ] side-effect-free declared-requirement probes (package/module/executable/service/hardware/config/credential/version)
- [ ] reverse dependency / `used_by` graph
- [ ] provider arbitration for overlapping location/power/network/presentation providers
- [ ] Plugin & Capability Center requirement/remediation UX
- [ ] Beast Doctor/Explain integration with dependency graph
- [ ] build-specific BOM generator/export: full / installed / missing / unused / conflicts
- [ ] transactional dependency remediation with dry-run/provenance/rollback
- [ ] generalized plugin install/update path
- [ ] schema-driven config editor for plugin options
- [ ] broader Beast adapter library for useful plugin data
- [ ] trusted-plugin quick-install catalog
- [ ] broken/experimental plugin sandbox/workbench

## 14. Presentation Broker / Korrie71 Theme Manager coexistence

- [x] presentation-owner architecture defined
- [x] owners modeled: Native / Theme Manager / Beast UI
- [x] transactional broker state machine
- [x] persistence/rollback tests using fake adapters
- [x] existing Theme Manager/Fancygotchi conflict detection
- [x] bounded read-only Theme Manager source capability probe (version/interoperability evidence; no import/execute)
- [x] canonical plugin/presentation state exposes Theme Manager capability evidence without enabling physical handoff
- [x] canonical live Template Token Registry backed only by Beast Core state; bounded Local API exposure + privacy/publication metadata
- [ ] allow-listed Theme Manager `STAT_SOURCE` adapter using canonical Beast tokens
- [ ] Visual Asset Interop v1 mapping for compatible palette/mood/face/effect/structure metadata
- [ ] real native Pwnagotchi release/acquire adapter
- [ ] real Korrie71 Theme Manager release/acquire adapter
- [ ] real Beast UI release/acquire adapter
- [ ] persistent user-facing owner selector
- [ ] health probation + automatic rollback during real handoff
- [ ] physical repeated owner-switch validation
- [ ] determine/document which non-owning WebUI/data services remain active
- [ ] direct collaborative compatibility/merge contract with Korrie71 project

## 15. Beast Packs / modular downloadable ecosystem

- [x] Pack manifest schema
- [x] Pack registry: builtin/installed/staged
- [x] capability/dependency/conflict visibility
- [x] resource/thermal metadata
- [x] archive intake safety limits
- [x] traversal/link/device rejection
- [x] SHA-256 verified staging
- [x] transactional registry install
- [x] Pack history/rollback foundations
- [x] content-only activation tier
- [x] code/executable/service/permission blockers for content-only Packs
- [x] Theme Pack discovery
- [x] Board Pack read-only launcher destinations
- [x] Layout Pack template import
- [x] Beast Pack SDK documentation/examples
- [x] Depot Catalog v1 parser
- [x] Depot catalog kept separate from source trust
- [x] Face Pack consumer — declarative glyph/vector profiles, selectable in Beast Studio
- [x] Animation Pack consumer — bounded declarative face motion/orbit profiles
- [ ] Audio Pack consumer
- [ ] Data Pack consumer
- [ ] Map Pack consumer
- [~] Depot browser/search/filter UI — persistent local catalog import/browser complete; remote refresh/acquire pending
- [ ] Pack remove/uninstall UX
- [ ] Pack update UX with compatibility comparison
- [ ] code-bearing App Pack activation adapter
- [ ] Renderer Pack activation adapter
- [ ] Integration Pack activation adapter
- [ ] Hardware Pack activation adapter
- [ ] Developer/experimental Pack isolation model
- [ ] optional signature scheme beyond SHA-256 where practical

## 16. Update Manager / automatic maintenance

- [x] update policy store
- [x] manual / notify / auto-stage / auto-install policy vocabulary
- [x] trusted GitHub-source policy
- [x] bounded GitHub Release metadata checker
- [x] verified update staging
- [x] Pack update orchestration
- [x] safe eligible-Pack auto-install path
- [x] update transactions/history foundation
- [ ] full Beastagotchi self-update adapter
- [ ] Pwnagotchi update adapter
- [ ] Theme Manager update adapter
- [ ] docked/online maintenance-window policy
- [ ] compatibility fingerprint before component upgrade
- [ ] backup + probation + rollback for component upgrades
- [ ] user-facing update notification/history polish
- [ ] safe reboot/restart orchestration after multi-component update

## 17. Mission Packs / profiles / automation

- [x] declarative Mission Pack model
- [x] capability requirements
- [x] preferred deck/theme/layout metadata
- [x] checklist/doc/app suggestions
- [x] safe structured-action concept
- [x] Field Survey / Road Trip / Lab Diagnostics / Home Base examples
- [~] Mission Pack downloadable integration — enabled Mission Packs are discovered as namespaced read-only profiles; transactional Apply pending
- [~] Mission/Experience UI — Beast Studio previews composed Theme/Face/Animation/Board/Deck selections; Apply pending
- [ ] rules/profile automation engine
- [ ] mission/session results/replay
- [ ] share/export user Missions

## 18. Performance / thermal / power

- [x] Resource Governor foundation
- [x] per-process CPU/RSS visibility
- [x] UI compose/render/framebuffer-write measurements
- [x] CPU temp/load/RAM/clock/throttle visibility
- [x] resource/thermal class metadata for Packs
- [x] inactive Pack principle: storage only, no background runtime
- [~] eliminate duplicate collectors/polling/render work
- [~] non-owner renderer suspension policy
- [ ] sustained enclosure heat profile on target Pi 4
- [ ] thermal budget by major optional module
- [ ] fan/cooling hardware integration
- [ ] battery/power telemetry integration for supported hardware
- [ ] learned runtime estimate
- [ ] dock/Home Base power policy

## 19. Hardware Studio / accessory enrollment

- [x] generic capability discovery foundations
- [x] Bluetooth adapter presence state
- [x] USB/storage/display capability visibility
- [~] hardware inventory surfaces
- [ ] Hardware Studio role enrollment
- [ ] second Wi-Fi adapter role assignment
- [ ] Alfa AWUS036ACM enrollment path
- [ ] fan/cooling enrollment
- [ ] UPS/battery enrollment
- [ ] RGB/LED/haptic/speaker roles
- [ ] RTC / physical buttons / rotary/input accessories
- [ ] NFC/camera/environment/IMU/proximity roles
- [ ] Beast Bus JSON/MQTT/serial accessory protocol
- [ ] distributed Pi Zero/ESP32 sensor enrollment

## 20. Phone / tablet / WebUI companion

- [x] Beast Studio local WebUI foundation
- [x] deep configuration intentionally favors WebUI
- [x] connectivity architecture documented
- [ ] responsive local companion/PWA shell
- [ ] phone/tablet settings surface
- [ ] phone/tablet logs/incidents/backups/files surface
- [ ] phone/tablet live Beast/status view
- [ ] local Wi-Fi/Ethernet discovery flow
- [ ] USB/RNDIS workflow where supported
- [ ] appropriate Bluetooth/BLE companion functions
- [ ] notification/export/share workflows
- [ ] no-cloud normal-use path validation

## 21. Multi-display / desktop / containers

- [x] compatibility transforms for 640×480 and 800×480
- [x] native-responsive Board renderer
- [x] external display discovery
- [x] Command Center app capability discovery
- [x] Docker/Podman capability discovery
- [x] Beast-enrolled container mutation boundary
- [ ] native-responsive remaining pages
- [ ] large-screen Command Center runtime
- [ ] optional lightweight Desktop Mode
- [ ] container app lifecycle UI
- [ ] per-container resource/thermal policy
- [ ] curated container app templates

## 22. Optional RF / field expansion universe — RESERVED / planned

- [ ] second-radio passive/management architecture
- [ ] SCOUT passive survey mode
- [ ] Kismet integration
- [ ] Bluetooth encounter persistence/scanning module
- [ ] SPECTRUM SDR mode
- [ ] RTL-SDR spectrum/waterfall
- [ ] lawful broadcast receive
- [ ] ADS-B SKY mode / aircraft radar
- [ ] rtl_433 compatible unencrypted sensor views
- [ ] Meshtastic/LoRa MESH mode
- [ ] offline map engine
- [ ] GPS route overlays
- [ ] unified RF Universe map/timeline
- [ ] FIELD sensor mode
- [ ] Monster View dense tricorder screen
- [ ] peer Beast/Monstergotchi networking
- [ ] Home Assistant/MQTT/NAS integrations
- [ ] explicitly authorized LAB-mode tooling under separate safety boundary

## 23. Reliability / plug-and-play / public project

- [x] GitHub repository established
- [x] CI test workflow
- [x] Design & Architecture Bible
- [x] Roadmaps / completion matrices / continuity ledger
- [x] screenshots/renders stored in repo
- [x] Beast Pack SDK docs/examples
- [x] current repository license is GPL-3.0
- [ ] finalize contributor/copyright policy for collaboration/merging
- [ ] supported-hardware matrix
- [ ] one-command public installer
- [ ] upgrader
- [ ] uninstaller
- [ ] migration framework
- [ ] clean-machine preflight
- [ ] release checksums/signing policy
- [ ] concise Quick Start
- [ ] full user manual
- [ ] troubleshooting/runbooks
- [ ] contributor guide
- [ ] issue/bug-report templates with support bundle instructions
- [ ] public beta gate
- [ ] v1.0 release gate

## 24. Required physical validation gates

- [x] original TFT/framebuffer validation
- [x] original touch validation
- [x] production touch calibration selection
- [x] v0.18.1 off-screen/target baseline validation
- [ ] v0.19 current visual/interaction physical review
- [ ] Theme Manager ↔ Native ↔ Beast real ownership-switch test
- [ ] v0.19 sustained thermal/load test
- [ ] second-display target test
- [ ] public clean-install test on a second machine
- [ ] friend/community tester install test
- [ ] regression test after installer/upgrader exists

## 25. Explicitly retained “do not forget” ideas — RESERVED

- [ ] recent-SSID Matrix ambient mode
- [ ] theme-reactive sound
- [ ] UI-linked LEDs
- [ ] dock transition scenes
- [ ] peer-Beast encounter scenes
- [ ] procedural theme randomizer
- [ ] theme scheduling
- [ ] per-session mood/theme history
- [ ] visual Expedition replay
- [ ] local file portal
- [ ] QR workflows
- [ ] Boot POST
- [ ] explain-error UX
- [ ] built-in offline manual
- [ ] disaster-recovery/self-healing
- [ ] update regression/rollback visualization

---

## Current next work

1. Keep PR #9 unmerged.
2. Finish the remaining high-frequency v0.19 hierarchy/interaction cleanup; the
   first Control Center/operational-overlay cleanup block is now source-green.
3. Generate and review another captured-real-state v0.19 visual acceptance gallery
   using the expanded page + interaction + operational-surface renderer;
   fix clipping, hierarchy and theme-specific regressions off-screen first.
4. Reconcile the PeerDex bridge/event integration and user-facing social state
   without overstating the already-implemented persistence foundation.
5. Package a bounded Pi validation build only after the visible UX delta is
   substantial enough to justify physical testing.
6. Perform physical 480×320 readability/touch/navigation/thermal acceptance.
7. After that gate, implement and repeatedly validate real Native ↔ Theme Manager ↔
   Beast presentation-owner adapters with probation/rollback.
8. Continue the remaining Pack, Update, responsive-display, recovery, hardware,
   companion and experience-depth work from this matrix.

Preservation snapshot: `Beastagotchi_Project_Continuity_Preservation_2026-09-23.md`.

No unchecked item above is considered dropped unless a later documented decision
explicitly retires it with a reason.
