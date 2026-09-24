# Beastagotchi Master Continuity Ledger v1.0

**Status:** Authoritative anti-forgetting index.  
**Rule:** useful ideas are never silently removed. They become **implemented**, **partial**, **planned**, **reserved**, **experimental**, or **retired with an explicit reason**.

This file complements, rather than replaces, the Design & Architecture Bible, Foundation Roadmaps, Master Completion Matrices, physical validation reports, and subsystem specifications already in this repository.

## Product identity that must survive every milestone

Beastagotchi is a modular Raspberry Pi field-computer environment built around a protected Pwnagotchi/Bettercap engine. It should simultaneously feel like a living digital creature, cyberdeck/field terminal, real-time RF/system monitor, modular app platform, configurable instrument panel, persistent exploration/progression system, and self-explaining/self-maintaining device.

The project must remain live-data-first, offline-capable, touch-friendly, extensible, reversible, highly customizable, and usable without SSH for normal operation.

## Main page / tab experience — retained

The **pages/tabs/swipe carousel concept is permanent**. The main carousel is curated for frequent field use; it is not an architectural limit on the number of apps or tools.

The primary landing experience remains a **Beast/Home page** centered on the creature and its live state, including identity, face/animal presentation, level, XP/growth, evolution stage, mood/personality, session aura and meaningful status. Supporting pages expose different live information sets rather than turning the home page into a dense dashboard.

Current/reference page families include Home/Beast, Recon, Networks, Spectrum, Captures, Map, System and related high-frequency pages. Detailed tools may open as apps/studios/decks rather than consuming permanent carousel slots. Stored files, Field Library content, Capture Vault, Memory/Expedition records, logs, backups and support artifacts must remain reachable from the Beast experience even when deep editing is better suited to the WebUI.

## Progression, secrets, specials and delight — retained

The following are explicit product commitments, not disposable extras:

- finite level progression (1–100) and meaningful evolution stages;
- persistent XP/progression tied to real activity rather than fake/demo counters;
- Beast personality driven by real operational context;
- session aura and context-reactive presentation;
- achievements/awards with rarity, progress and discovery presentation;
- rare, epic/legendary-style moments and scarce witnessed events;
- secrets, hidden interactions, codes, ciphers and future Cipher Console/puzzle systems;
- seasonal, calendar, day-phase, weather/celestial/moon context where real data is available;
- Rare Moments with omens, witnessing rules and dedicated cinematic presentation;
- 5–60 second rare cinematics and multiple presentation families;
- trophy cabinet / collections / BeastDex-style records;
- long-tail achievement families and hidden awards;
- Expedition/session records, visual replay and scrapbook/Memory Vault concepts;
- peer-Beast encounters, special discoveries and future distributed-world events;
- theme-reactive sound, optional haptics/LED reactions and other sensory rewards;
- Easter eggs that can be discovered without compromising reliability or truthful telemetry.

Canonical detailed references include `Beastagotchi_Secrets_Achievements_Seasonal_Spec_v0.9.md`, `SPOILERS_SECRETS_AND_ACHIEVEMENTS.md`, `Beastagotchi_Rare_Cinematic_Pipeline_v0.9.1.md`, `Beastagotchi_Adaptive_Behavior_Progression_Spec_v0.1.md`, and `Beastagotchi_Expeditions_Spec_v0.11.md`.

## Multi-Beast roster / lineage / Monster system — retained

Progression is no longer intended to be one replaceable character skin around a
single save slot. The approved direction is a persistent **Beast Roster**:
multiple individual Beasts may coexist at independent levels 1–100, retain
their own progression/history while resting, and be switched without losing
state.

The legacy single progression profile becomes the user's **Founder Beast**
through a lossless migration path.

Global/device progression and per-Beast progression are separate layers. Global
records include the world/encounter archive, Capture Vault, device-wide Rare
Moment schedule, shared collections/unlocks and meta-completion. Individual
creatures own their XP/level/evolution, personal achievements, personality
history, witnessed events, records, cosmetics and preferred Experiences.

High-level Beast pairs may perform **Lineage Synthesis**. Core does not require
male/female identity; animal-style Packs may call it breeding while robot,
alien, abstract or AI lineages may present it as fusion/synthesis/recombination.
Parents persist unchanged. The result is a new Monster with independent
progression and recorded ancestry. Creating the first Monster is the approved
unlock event for the future Monstergotchi layer.

Retained extensions include deterministic inherited traits, rare curated
mutations, Monster-specific evolution, Hall of Legends, ancestry/family-tree
views, later-generation synthesis if playtesting supports it, and a future
privacy-safe cross-device Lineage Capsule concept for optional community
ancestry without sharing captures, logs, secrets or location history.

## Peer encounters / social lineage — retained

Beastagotchi must preserve interoperability with ordinary Pwnagotchi peers.
Existing pwngrid peer advertisements/fingerprints are treated as the low-level
encounter substrate. A remote Pwnagotchi does **not** need Beastagotchi installed
for the local Beastagotchi to notice it, record the encounter, react socially or
award bounded local progression/achievements.

Richer two-way Beast features require both peers to implement the compatible
Beast peer extension. Approved direction includes persistent PeerDex/friend
history, reunion/bond milestones, Expedition-linked encounters, privacy-safe
public Beast descriptors and future Lineage Capsules.

Cross-device lineage must not expose captures, Wi-Fi history, credentials,
private logs, precise location history or owner secrets. QR/file/local-network/
Bluetooth/Meshtastic transports may be explored. No cloud account is required.

## Structural customization — retained

Data, widgets, renderers, layouts, themes, face packs and Beast personality remain separate layers. Themes are structural identities, not simple recolors. Layouts remain independently selectable/editable. Visualizer Studio, Theme Studio, Spatial Studio/custom Boards, Context Decks and user-authored combinations remain part of the planned platform.

Reserved visual/theme identities include Classic, Matrix, Starcore, Black Ice, Hunter, Minimal, Synthwave, Amber Tactical, Ghost Minimal, Cyberpunk, Stealth/Red Alert, Forest, Vaporwave, Space, Holographic, Golden, Samurai, WOPR/NORAD, Steampunk, Blueprint, Terminal+, Biohazard, Glitch, Comic, seasonal/user packs, sonar/submarine, Mission Control, Oscilloscope Lab and other retained identities documented elsewhere.

## Beast Packs / downloadable ecosystem — new explicit direction

The base installation should stay comparatively small and stable while optional content and capabilities can be installed as versioned **Beast Packs**. Candidate pack types include themes, face/animation/audio packs, dashboards/layouts, apps, hardware adapters, Mission Packs, offline map/data bundles, optional renderers and experimental capabilities.

A future Beast Depot/Library should support install, update, disable, remove, compatibility checks, dependencies, resource/thermal metadata, signatures/checksums where practical, and rollback. Downloaded-but-inactive content should consume storage, not continuous CPU/GPU/thermal budget.

## Presentation ownership — retained and expanded

Stock/native Pwnagotchi, Korrie71 Theme Manager and Beast UI must be able to coexist without racing for the framebuffer/touch device. A Presentation Broker should provide an exclusive persistent owner lease and transactional handoff. Initial presentation owners:

- `native` — stock/Jayofelony Pwnagotchi presentation;
- `theme_manager` — Korrie71 Theme Manager presentation + touch;
- `beast` — Beastagotchi presentation + touch.

The selected owner keeps control until another presentation explicitly requests it. Failed acquisition should roll back to the previous healthy owner. Non-owning systems may remain alive for WebUI/API/data functions when compatible.

## WebUI / companion experience — retained and expanded

The physical display is the **cockpit**; the responsive local WebUI is the **workshop**. Deep configuration should favor phone/tablet/desktop WebUI while essential field operation remains available on-device.

Native Pwnagotchi capabilities should not disappear simply because Beastagotchi is installed. Beast should preserve, expose, link to or safely adapt useful native Pwnagotchi settings/interfaces. Phone/tablet connectivity architecture must account for local Wi-Fi, Ethernet/dock, USB/RNDIS where supported, and Bluetooth/BLE capabilities where technically appropriate. A local-first PWA-style Beast companion is approved direction; no cloud account is required for normal use.

## Multi-display / screen strategy — retained

480×320 ILI9486 is the physically validated reference/minimum target, not the only final target. The platform should prudently support other common screens when doing so can be accomplished cleanly through responsive layout/display transforms rather than per-screen forks. Targets include 640×480/800×480 compatibility, common 5-inch HDMI/DSI-class displays, larger HDMI/DRM displays/Command Center, and responsive browser surfaces on phones/tablets/desktops.

No resolution is declared production-supported until it has appropriate automated and, where practical, physical validation.

## Reliability records must exist independently of WebUI

The WebUI is a view/controller, never the sole storage location for critical records. Important state must remain on persistent storage so it survives browser loss, UI crashes and reboots.

Existing durable paths include:

- `/var/lib/beastagotchi/beast.db` — canonical Beast database/state history;
- `/var/lib/beastagotchi/backups/` — verified recovery backups;
- `/var/lib/beastagotchi/config-snapshots/` — configuration snapshots;
- `/var/lib/beastagotchi/restore-staging/` — staged restore inspection/apply preparation;
- `/var/lib/beastagotchi/support/` — privacy-sanitized support bundles;
- `/var/lib/beastagotchi/library/` — offline Field Library;
- `/var/lib/beastagotchi/missions/` — Mission Pack state;
- `/var/lib/beastagotchi/ui/` — persistent UI preferences/runtime records;
- durable Black Box incidents/jobs/actions in the Beast database.

Service logs should remain accessible through the underlying system journal and Beast UI/WebUI. A bounded persistent log/export policy should ensure troubleshooting evidence can be recovered locally without creating uncontrolled SD-card write amplification.

## Thermal/resource efficiency — retained and elevated

Heat is a first-class engineering constraint. Optimization order is: eliminate duplicate work, share telemetry, suspend non-owning render engines, make collectors event-driven/adaptive, cache static layers, reduce framebuffer writes, stop unused optional services, profile expensive modules, and only then use graceful degradation during genuine pressure.

Resource Governor is protection, not an excuse for an inefficient normal state. Future module/package metadata should expose expected background/resource/thermal class where useful.

## Plug-and-play / documentation — retained and elevated

The final public experience should approach plug-and-play within the limits of Raspberry Pi/Pwnagotchi hardware variation: clear supported-hardware matrix, installer/upgrader/uninstaller, preflight checks, automatic capability discovery, safe defaults, rollback, diagnostics, screenshots, concise quick-start, detailed manuals, troubleshooting/runbooks, contributor docs and explicit validation status.

## Expansion universe — retained

Still approved/reserved: BEAST/SCOUT/SPECTRUM/SKY/MESH/FIELD/SYSTEM/LAB modes; RF Universe; Kismet/passive survey; Bluetooth encounter persistence; RTL-SDR spectrum/waterfall and lawful decoders; ADS-B aircraft radar; rtl_433-compatible unencrypted sensor views; Meshtastic/LoRa; offline maps; Home Base/dock mode; peer Beast networking; distributed Pi/ESP32 sensors; Beast Bus; hardware enrollment; RGB/haptics/speaker/fan/RTC/physical controls/NFC; camera/environment/IMU/proximity; MQTT/Home Assistant/NAS integration; optional local AI/voice; Container Center; external-display Command Center; Desktop Mode; Monster View; dynamic world animation; theme scheduling/randomization; local file portal; QR workflows; Boot POST; explain-error UX; built-in offline manual; disaster recovery/self-healing; update regression/rollback; and other items retained in the Master Completion Matrices and Roadmaps.

## Change-control rule

Every substantial milestone must update this ledger or the current Master Completion Matrix when it:

1. implements a retained idea;
2. changes an architectural commitment;
3. defers an item;
4. retires an item (with explicit reason); or
5. adds a new approved idea.

No item is considered gone simply because it is not mentioned in a milestone summary.


## Repository preservation source

The 2026-09-23 cross-source recovery and reconciliation is preserved in
`Beastagotchi_Project_Continuity_Preservation_2026-09-23.md`. It records the
current branch/PR checkpoint, physical decisions that supersede older theoretical
recommendations, recovered validation state, Library artifact provenance and
working continuation rules.

Raw private chat transcripts are not required as a source of truth. When a
conversation produces a durable architectural decision, physical-hardware truth,
scope commitment or validation result, that decision should be promoted into the
repository before the chat becomes the only surviving record.

## Recovered permanent development method — 2026-09-23

The pinned-chat recovery made several project-process commitments explicit enough
to preserve here because they affect every future milestone:

- the roadmap is a **memory and execution system, not a cage**;
- approved ideas never silently disappear: they remain implemented, active,
  planned, experimental, reserved, or explicitly retired with a reason;
- periodically perform **Lightbulb Reviews** of adjacent Raspberry Pi,
  Pwnagotchi, embedded-device, RF, mapping, offline-AI and interaction ecosystems
  for ideas worth adapting;
- proactively propose useful connections the user may not know to ask for;
- challenge our own design when a materially better architecture/workflow/UI or
  integration appears, even when that requires redesign;
- use **modularity by default** so optional/exotic capabilities increasingly
  become Packs/modules instead of permanent base-image load;
- “all-in-one” means discoverable, coherent, integrated and reachable, **not**
  every control on one screen;
- prefer real Beast/Pi/environment information over decorative fake telemetry;
- keep delight—secrets, rares, unusual animation, collectibles, personality and
  special modes—as real product scope;
- optimize duplicate polling/rendering/services before cutting features or
  degrading visuals;
- pair new powers with recovery, rollback and health-checking;
- continue evolving from a one-reference-device project into something usable
  by first-time/community users without weakening the Pi 4 reference target.

The sanitized recovered chronology and design provenance are retained in
`Beastagotchi_Recovered_Conversation_Continuity_Addendum_2026-09-23.md`.

## Plugin / Dependency / Capability direction — approved 2026-09-24

The user explicitly approved the Plugin & Capability Center direction developed
from the Jayofelony stock-plugin review and approved extending it into a shared
Dependency & Capability Resolver.

Durable decisions:

- stock/Jayofelony plugins remain upstream plugins where practical; Beast should
  integrate useful state/actions rather than clone every plugin;
- plugins become first-class capability providers with explicit `PROVIDES`,
  `REQUIRES`, optional requirements, conflicts, provider groups and reverse
  `USED BY` relationships;
- the same dependency vocabulary should extend across Plugins, Beast Packs,
  Hardware, Experiences, Apps and Services;
- abstract capability requirements are preferred over named implementations
  (for example `location.position` rather than forcing one GPS provider);
- multiple enabled providers must not create duplicate canonical truth; Beast
  should select/record an active provider and retain alternates;
- missing requirements must be classified into safe automatic remediation,
  confirmed transactional remediation, guided human action, provider choice or
  unsupported/incompatible state;
- required secrets are represented only as presence/missing state; secret values
  must never be exposed by the dependency graph;
- data-egress class is part of plugin/component metadata;
- disabling a provider should be able to explain downstream impact through a
  reverse dependency graph;
- Beast Doctor/Explain should use the graph to answer both "why is this not
  working?" and "what will this change affect?";
- Plugin Manager should mature into a Plugin & Capability Center rather than a
  binary toggle list.

For the user's Pi 4 reference build, a second explicit decision was made:

- maintain a complete, versioned **superset software/service BOM** for the known
  approved feature universe;
- do **not** interpret that catalog as a request to preinstall/enable everything;
- the actual runtime/install set should be the dependency closure of selected
  capabilities/hardware;
- optional services should remain stopped/disabled when their capability is not
  active;
- future "Prepare Capability" workflows should show the full dry-run plan before
  any package/service/config mutation.

This preserves the information advantage of a maximal build without creating a
kitchen-sink runtime.

Current implementation boundary:
- PluginIntegrationEngine now carries initial stock plugin
  role/provides/requires/provider/egress/credential/hardware metadata;
- requirement resolution is explicitly marked catalog-only;
- no dependency installer or provider selector was enabled by this decision.

Current specifications:
- `Beastagotchi_Dependency_Capability_Resolver_v0.1.md`
- `Beastagotchi_Reference_Build_BOM_Strategy_v0.1.md`

## Owner sovereignty / unrestricted administration — approved 2026-09-24

The user explicitly approved a permanent owner-control principle:

Beastagotchi must not become a locked appliance that permanently prevents the
authenticated owner from modifying their own Pi.

Durable rules:

- managed/supported behavior is the default, not the only possible behavior;
- Beast should warn, explain, snapshot, offer rollback and identify unsupported
  combinations, but a Beast policy preference is not equivalent to ownership
  authority over the machine;
- technically possible policy-blocked actions should have an eventual owner
  override path;
- plans distinguish `policy_blockers` from `technical_blockers`;
- per-action "Proceed unsupported anyway" and a persistent Expert Mode are
  retained UX requirements;
- arbitrary/custom plugins, repositories, packages, services, hardware,
  configuration and scripts remain legitimate owner modifications;
- unsupported/custom operation may be marked accurately for diagnostics/support,
  but must not trigger artificial punishment or unrelated feature locks;
- SSH/root/console remains the ultimate escape hatch;
- when Beast cannot safely disable/remove part of its own active control plane,
  it should explain why and provide an exact maintenance/manual path rather than
  pretending the owner is forbidden from doing so;
- Owner Override is a locally authorized administrative capability. It must not
  become an unauthenticated remote policy bypass;
- warnings about data egress, dependencies, conflicts, resource/thermal impact
  and loss of rollback/support remain visible after override;
- owner freedom does not purport to override third-party licenses, service terms
  or applicable law.

Legal posture:
- the repository remains GPLv3;
- GPLv3 sections 15/16 already provide the project's baseline "as-is" warranty
  disclaimer and limitation of liability to the extent permitted by law;
- project documentation may state that unsupported/custom modifications are
  undertaken at the user's risk, but should not claim that UI wording can
  guarantee zero liability in every jurisdiction.

Current code foundation:
- PluginBroker plans now expose `technical_blockers`, `policy_blockers`,
  `owner_override_available`, `owner_override_executed` and
  `managed_allowed`;
- current execution remains conservative; actual override execution is not yet
  enabled.

Canonical specification:
`Beastagotchi_Owner_Sovereignty_Unrestricted_Mode_v0.1.md`.

