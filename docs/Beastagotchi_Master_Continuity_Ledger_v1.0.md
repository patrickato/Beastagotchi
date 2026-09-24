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

Current implementation:
- PluginBroker plans expose `technical_blockers`, `policy_blockers`,
  `owner_override_available`, `owner_override_executed` and
  `managed_allowed`;
- persistent Expert Mode is stored privately and can be changed only through an
  active owner-authorized administrator session or by the owner manually outside
  Beast;
- an explicit plugin `owner_override=true` may bypass policy blockers only while
  Expert Mode is enabled;
- technical blockers remain non-overridable;
- successful plugin overrides keep normal snapshot/verification/restart/health/
  rollback behavior and mark the device customized for later diagnostics;
- owner-mode status is exposed read-only through Core/API/structured tools;
- Support Bundles carry sanitized managed/expert/customized state;
- actual arbitrary plugin/package/service/script execution remains future work,
  so this milestone does not convert Expert Mode into a generic command runner.

Canonical specification:
`Beastagotchi_Owner_Sovereignty_Unrestricted_Mode_v0.1.md`.

## Shared dependency/capability resolver implementation — 2026-09-24

The previously approved Dependency & Capability Resolver is now a real shared
read-only service rather than plugin-only catalog metadata.

Implemented:
- new `beastcore/dependency_resolver.py` with common `RequirementResult` and
  `DependencyCapabilityResolver`;
- Beast Core shares one resolver instance across PluginIntegrationEngine and
  PackRegistryEngine;
- bounded, non-mutating probes for:
  - canonical/abstract capabilities;
  - service state from Beast's existing canonical service inventory;
  - Debian package presence through `dpkg-query -W`;
  - executable presence;
  - Python module presence without importing/executing it;
  - filesystem/device path presence;
  - configuration presence;
  - credential presence only;
- no resolver path installs/removes software, starts/stops services, mutates
  configuration, selects providers or sends data;
- native capability providers are inferred from existing canonical Beast state,
  avoiding new background polling;
- enabled/available component providers are indexed and reverse `used_by`
  relationships are produced;
- provider **availability** is distinct from active **selection**, which lets an
  installed-but-disabled dependency Pack satisfy availability without pretending
  it is currently active;
- active selected-component blocker totals are distinct from whole-catalog
  readiness, so disabled optional hardware plugins do not make the running Beast
  look unhealthy;
- mandatory missing prerequisites become technical blockers when evidence is
  factual; unknown/unproven requirements remain policy blockers rather than
  invented facts;
- known absent hardware classes are technical blockers;
- resolver owner-override availability follows the same policy-vs-technical
  semantics as Expert Mode;
- Pwnagotchi plugin config inspection now records sensitive-field
  `present=true/false` while continuing to omit the secret value itself;
- credential-required stock plugins consume only that presence evidence;
- Plugin and Pack catalog rows now carry requirement result/evidence,
  technical/policy blockers and reverse usage;
- read-only `GET /dependencies` and platform-bundle summaries expose graph
  health to future Studio/Doctor surfaces.

This remains an observation/planning layer. Provider arbitration, dependency
installation and remediation execution are deliberately disabled.

The next dependency-system priorities are provider arbitration policy,
Plugin & Capability Center/Doctor presentation, generated BOM exports, wider
adoption by Experiences/Apps/Hardware Studio, generalized version resolution and
only later transactional remediation.

## Capability provider arbitration + Lightbulb review — 2026-09-24

Provider arbitration has advanced from a roadmap item into a bounded read-only
policy engine.

Implemented:
- new `beastcore/provider_arbitration.py` /
  `CapabilityProviderArbitrator`;
- every dependency graph now carries provider decisions;
- decision states distinguish:
  - active native/canonical provider;
  - active explicit preference when a future preference is supplied;
  - one unambiguous selected provider;
  - fallback when a preferred provider is unavailable;
  - choice required;
  - ready but unselected;
  - unavailable;
- canonical/native state wins by default when already live, preventing a
  compatibility plugin from silently displacing Beast's existing normalized
  truth;
- multiple selected non-native providers do not get silently collapsed into one;
  Beast reports a choice requirement and a deterministic recommendation;
- configured-but-disabled plugins can remain available alternates;
- decisions include reasons, candidates, alternates and an ordered fallback
  chain;
- explicit owner preference is modeled but no provider-preference writer exists
  yet;
- provider selection mutation and automatic failover remain disabled;
- `GET /dependencies` and the platform bundle expose provider decision/summary
  information for future Studio/Doctor presentation.

Durable design ideas recovered/added during this block:

- **context-aware provider profiles**: Field/Dock/Home/Battery-critical contexts
  may prefer different location/network/power providers while keeping decisions
  visible and owner-overridable;
- **graceful degradation**: losing an optional capability should degrade only the
  dependent feature instead of collapsing the whole Expedition/Experience;
- **hot-plug arrival UX**: new compatible hardware can be recognized as a new
  provider and offered as keep-current / switch / fallback without reboot;
- **failover rehearsal**: TEST FAILOVER can temporarily hand over, verify
  canonical telemetry, restore and report before automatic failover is trusted;
- **provider confidence**: future consumers may request any/high-confidence/
  low-power/local-only providers instead of a Boolean capability;
- **capability leasing**: scarce/exclusive resources such as framebuffer, SDR,
  camera, microphone or radio modes can have explicit owner/lease/waiting state;
- **dependency/update impact simulation**: USED BY can answer what becomes
  degraded before removing/updating a provider;
- **known-good build fingerprint**: BOM + dependency graph + provider choices +
  customization state can support Doctor's "what changed since known-good?"
  comparison.

Canonical specification:
`docs/Beastagotchi_Provider_Arbitration_v0.1.md`.

The project must retain the conversational/lightbulb side of development: new
architecture work should continue to ask what additional user-facing capability
the same underlying data or mechanism can unlock, rather than treating roadmap
implementation as a silent checklist exercise.

## Provider preferences + health/confidence + Beast Doctor — 2026-09-24

The read-only provider arbitration milestone was extended into a first genuinely
user-explainable provider-management layer.

Implemented:

- persistent `ProviderPreferenceManager` at
  `/var/lib/beastagotchi/provider-preferences.json`;
- atomic private `0600` writes;
- persistent capability -> provider owner preference plus set timestamp/actor;
- canonical `providers.preferences` state;
- audited Action Broker operations:
  - `provider.preference_set`
  - `provider.preference_clear`;
- an active owner-authorized Operator session is required to mutate preference
  policy;
- saving/clearing a preference does **not** enable a plugin, start a service,
  switch hardware ownership or perform failover;
- a temporarily unavailable/unknown provider preference may remain dormant
  instead of being silently erased;
- provider candidates now expose initial evidence health/confidence:
  - live canonical state can carry high confidence and measured freshness;
  - requirements-ready component providers are `ready_unverified` or
    `standby_ready`;
  - blocked/uncertain providers remain explicitly weaker evidence;
- confidence describes **evidence quality**, not vendor/device quality.

The first `BeastDoctor` implementation now consumes provider/dependency state
rather than creating duplicate pollers.

Doctor can explain:
- why a capability's provider is active;
- current provider health/confidence/freshness;
- owner preference and preference mismatch;
- alternates and fallback chain;
- Plugin/Pack reverse `USED BY` relationships;
- downstream components that may degrade if the active provider disappears;
- whether automatic failover exists (currently false);
- bounded evidence-based recommendations.

New read-only surfaces:
- `GET /doctor`
- `GET /explain?capability=...`
- `GET /explain?provider=...`
- `GET /provider-preferences`
- structured Operator tools `doctor.explain` and `provider.preferences`.

Structured mutation tools:
- `provider.preference_set`
- `provider.preference_clear`.

A low-frequency Doctor Core loop publishes bounded canonical summary state.
Sanitized Support Bundles preserve non-secret provider-policy and Doctor status.

Durable product rule:

> **Explain before act.**

Before Beast offers an important provider/component mutation, the desired flow is:
Explain -> Plan -> Preview impact -> Snapshot -> Execute -> Observe probation ->
Rollback/Accept -> Record.

This principle should later be shared by Plugin disable/remove, Pack removal/update,
service changes, hardware role reassignment, Presentation Broker handoff and
dependency remediation.

Additional Lightbulb directions retained from this block:
- causal-chain troubleshooting such as
  `Expedition route missing -> location unavailable -> preferred PwnDroid not
  ready -> phone link absent`;
- a known-good machine fingerprint combining BOM, providers, versions, hardware,
  plugins/Packs and customization state;
- "what changed since known-good?" Doctor comparison;
- pre-action blast-radius simulation showing what loses capability and what has a
  replacement provider;
- field-TFT Doctor condensed to OK / ATTENTION / DEGRADED / ACTION REQUIRED with
  one-tap causal explanation;
- browser workshop graph for full dependency/provider exploration;
- recovery recommendations ranked by reversibility rather than by aggression.

Canonical specs:
- `docs/Beastagotchi_Provider_Arbitration_v0.1.md`
- `docs/Beastagotchi_Doctor_Explain_v0.1.md`

Automatic failover remains deliberately disabled. Provider switching/handoff has
not been physically or transactionally validated merely because policy and
explanation now exist.

## Extension ecosystem / Beast Capsules / offline exchange — 2026-09-24

The plugin discussion was expanded into a durable extension model rather than
treating every new feature as another Pwnagotchi plugin.

Approved extension classes:

1. **Pwnagotchi Plugin** — code that genuinely needs Pwnagotchi lifecycle,
   callbacks or Bettercap/Pwnagotchi hooks.
2. **Beast Pack** — modular content/data/presentation/rules/assets.
3. **Beast App** — deeper interactive Beast-native functionality.
4. **Companion Expansion** — one user-facing feature whose internal pieces may
   legitimately span Pwnagotchi plugin + Beast Pack/App/adapter layers.

Adapters remain the preferred bridge for useful existing plugins/services/hardware
that only need normalization into canonical Beast state/events.

Durable rules:
- Pwnagotchi plugins should normally act as sensors/actuators rather than recreate
  Beast progression/UI/lineage systems;
- plugins/extensions contribute truthful normalized signals/events;
- the canonical Achievement/Trophy Engine decides unlocks instead of accepting
  arbitrary "grant trophy X" commands from a plugin;
- Pack manifests use broad technical types plus `content_roles` rather than
  creating a new pack type for every concept;
- manifests may declare signals provided/consumed, offline transports, Capsule
  types and Companion component membership;
- generic Beast-native plugin cards should eventually be synthesizable from
  capabilities/config/actions/health metadata;
- a future Plugin Profiler should measure callback/error/staleness/resource cost
  rather than enforcing arbitrary plugin-count limits.

### Beast Capsule decision

Beastagotchi now explicitly targets an **offline/sneakernet ecosystem**, not just
offline operation.

A Beast Capsule is a transport-neutral portable object. The same logical Capsule
may later move through:
- QR;
- animated/multi-frame QR;
- local file;
- USB/SD;
- NFC;
- Bluetooth/local direct transfer;
- Beast-to-Beast transport;
- local phone/WebUI.

Implemented foundation:
- `beastcore/capsules.py`;
- BC1 canonical JSON + bounded SHA-256 integrity + zlib/base64url encoding;
- BCQ1 bounded multi-frame QR-ready text framing/reassembly;
- per-frame CRC, missing-frame/mixed-session/conflicting-duplicate checks;
- complete Capsule integrity verification after reassembly;
- Lineage Capsule export from the persistent Beast roster;
- separate local Capsule namespace, intentionally distinct from Global/public
  profile identity;
- stable pseudonymous portable creature and local-parent IDs;
- privacy-curated payload that excludes raw roster IDs, raw identity/preferences,
  counters, captures, Wi-Fi/network history, credentials, exact location and logs;
- achievement IDs are opt-in while achievement count may be shared;
- Local API read-only `/capsule/export` and `/capsule/types` endpoints;
- Capsule import remains non-mutating/preview-only;
- current digest is integrity only and must never be described as authenticated
  sender identity;
- actual QR image rendering/camera scanning is not bundled yet, avoiding a new
  base-image dependency before physical benchmarking.

Pack manifests now understand:
- `extension_class = pack | companion`;
- `content_roles`;
- `signals_provides`;
- `signals_consumes`;
- `offline_transports`;
- `capsule_types`;
- Companion Pwnagotchi plugin / Beast App / Beast Pack membership metadata.

Protected future Capsule families:
- Beast Card / PeerDex Capsule;
- Challenge Capsule;
- signed Achievement/Trophy proof Capsule;
- selected Configuration Capsule;
- Pack Reference Capsule;
- signed Lineage Capsule v2.

Protected Lightbulb directions:
- physical QR/NFC relics/cards/tokens;
- witnessed/social achievements through offline exchange;
- Capsule Inbox/Outbox and Capsule Workshop;
- animated QR progress/missing-frame UI;
- air-gapped challenge/response exchange;
- signed device/creature identity only after backup/rotation/recovery semantics are
  designed;
- large Pack payloads should use QR only for identity/digest/reference while
  USB/SD/file carries bulk bytes.

Cross-device Lineage import is **not** considered complete merely because export
exists. Remote-lineage storage, authenticity, duplicate/replay handling, owner
confirmation and synthesis semantics remain separate gates.

Canonical documents:
- `docs/Beastagotchi_Plugin_Extension_Architecture_v0.1.md`
- `docs/Beastagotchi_Beast_Capsules_Offline_Ecosystem_v0.1.md`
- `docs/Beastagotchi_Beast_Packs_Depot_Spec_v0.1.md`
- `docs/Beastagotchi_Secrets_Achievements_Seasonal_Spec_v0.9.md`

## Capsule Share visible transport / QR compositor protection — 2026-09-24

The first user-visible Beast Capsule transport surface is implemented.

New pieces:
- optional `beastui/qr_render.py` adapter using Python `qrcode` when present;
- `qrcode>=8.0` in CI/development dependencies, deliberately not yet forced
  into the target Pwnagotchi virtualenv;
- Beast UI local API client for real Lineage Capsule export;
- **Capsules** Identity app;
- asynchronous Capsule Share overlay with real QR, manual frame navigation and
  explicit privacy/authenticity labels;
- honest unavailable state when Core/renderer is missing;
- no decorative fake QR fallback.

A regression test exposed that the global theme scanline layer could paint over
the QR after the transport surface had rendered. This was treated as a real
compositor defect. Capsule transport now renders above normal theme
scanlines/effects, while Monster/Rare overlays retain higher intentional
precedence.

The CI real-state gallery now contains a clearly labeled
`GALLERY PREVIEW · NOT IMPORTABLE` Capsule screen. Its data is derived only from
the sanitized real-device fixture; it does not impersonate a local roster record.

Source/off-screen gate:
- 394 tests green at run `35974384239` (#302);
- compile/shell/gallery green;
- artifact `10796753380`;
- digest
  `sha256:fa9efe68f4a5bf6f30b53675f8ce700e8da9694f4f52195a2feb7a66779d9f57`;
- representative QR density >=3 px/module;
- rendered 480×320 gallery PNG manually decoded back to the exact BCQ1 frame.

Durable dependency decision:
QR rendering should be represented as an optional Beast capability/runtime
dependency rather than casually dumping another package into Pwnagotchi's
protected environment. The packaging boundary should be resolved before the
physical test package.

Durable visual decision:
machine-readable transport is a protected render layer. Theme decoration may
frame it but must never cross/corrupt its modules or quiet zone.

Physical acceptance still pending:
- actual ILI9486 panel;
- camera/phone scan reliability;
- display brightness/contrast;
- repeated frame scans;
- best automatic-frame interval;
- thermal/render cost on target.

The Capsule Share screen should be included in the next substantial physical
v0.19 acceptance package.

## Bounded physical acceptance as a product gate — 2026-09-24

Durable decision:
physical v0.19 acceptance should happen as one substantial, reversible session,
not as a sequence of repeated tiny install/check/reinstall loops.

The session now has first-class tooling:
- `beast-v019-accept start`
- `beast-v019-accept sample`
- `beast-v019-accept capture`
- `beast-v019-accept finish observe|pass|rollback`

The acceptance package is not a replacement for the Presentation Broker. It is
a validation harness that deliberately reuses the established display-handoff
scripts and automatic rollback timer.

Objective machine evidence and subjective physical acceptance remain separate.
The machine can measure render/write timing, dirty-row efficiency, CPU,
temperature, governor state, touch-event evidence and service health. It cannot
decide whether the actual TFT is readable, touch feels good, a phone reliably
scans the QR, glare is acceptable, animation looks smooth, or the product feels
polished.

Privacy rule:
physical acceptance/support archives must minimize unrelated telemetry. Raw
Pwnagotchi configuration, whole canonical state, full platform bundle and raw
Pwnagotchi journal are not required for this gate and should not be collected by
default. Framebuffer captures remain potentially sensitive because they preserve
whatever the user was actually viewing.

Durable dependency rule:
the optional QR renderer should ultimately live in a Beast-owned dependency
boundary rather than casually modifying Pwnagotchi's protected Python
environment.

Next physical gate:
deploy the current v0.19 branch to the reference Pi, run one bounded acceptance
session, use the TFT normally during a 60-second objective sample, exercise
Capsule Share with a real phone camera, then return the generated evidence
archive plus the user's physical impressions for review.

This physical session still does not authorize promotion of Draft PR #9 to
`main`; real Presentation Broker multi-owner switching and remaining release
gates remain separate.

## Beast-owned optional Python runtime boundary — 2026-09-24

Durable dependency decision:
optional Beast Python packages should have a Beast-owned import/install boundary,
not be casually added to Pwnagotchi's protected `/opt/.pwn` site-packages.

The first implemented path is:

`/opt/beast-python/site-packages`

Beast UI/Studio include it in PYTHONPATH after the project source directory.

The normal installer creates the directory but does not fetch optional packages.
For the Capsule QR physical gate, explicit owner action is available:

- `beast-v019-accept prepare-qr`
- `beast-v019-accept remove-qr`

The current preparation path pins the CI-tested `qrcode==8.2`, downloads the
wheel first, records its SHA-256, installs it with `pip --target` into the
Beast-owned directory and writes dependency provenance. Removal targets only the
Beast-owned qrcode files/metadata/console entry.

This is a concrete first implementation, not yet a generalized automatic package
manager. Future Dependency & Capability Resolver remediation should inherit the
same principles:
- explicit ownership boundary;
- declared capability need;
- dry-run/plan where practical;
- provenance;
- target isolation;
- reversible removal;
- no silent pollution of upstream runtimes.

Durable packaging decision:
the physical v0.19 gate should use a commit-pinned CI source artifact. GitHub
Actions now emits `v019-pi-acceptance-source` containing a PR/source-head archive,
portable archive SHA-256, `SOURCE_COMMIT_SHA.txt` and `CI_TESTED_SHA.txt`. PR CI
may test a synthetic merge commit, so source and tested SHAs are deliberately
recorded separately rather than conflated.

Source validation at the first complete implementation:
- commit `a8318ca810406290f4b4cfdb73d946345abc2350`;
- run `35977711327` (#349);
- 399 tests;
- compile/shell/gallery green;
- Pi source artifact id `10798463813`.

The next work item is real target execution, not more abstract preparation of
this same gate.

## Studio Capsule Workshop exact-share contract — 2026-09-24

Durable product rule:
Capsule sharing should expose the **exact payload before transport**, not merely a
friendly summary. The owner must be able to see what the QR actually represents.

The first Beast Studio Capsule Workshop now implements that rule for Lineage
Capsules:
- choose a persistent roster creature;
- explicitly choose whether to include name, curated appearance and achievement
  IDs;
- render the exact Capsule envelope JSON;
- render the exact BCQ1 frame locally;
- navigate frames manually;
- keep integrity/authenticity wording explicit;
- keep the privacy exclusions visible.

Durable security rule:
the Workshop remains paired-token protected and local-first. QR generation uses
the Beast-owned renderer path and never sends Capsule material to an external QR
service/CDN.

Durable mutation rule:
the current Workshop is **export/exact-preview only**. Building or viewing a
Capsule must not create a creature, alter ancestry, award progression, publish
Global data, or silently import remote lineage.

Source gate for this implementation:
- commit 9ce74f318e7830c5134d9aa94dda10a9a4c81dca;
- Actions run 35979568253 (#367);
- 406 tests + compile + shell + gallery + Pi source artifact green.

Receive/import remains a later separately designed gate.

## Pi staging artifact / physical provenance chain — 2026-09-24

Durable release/testing rule:
**software staging and display ownership are separate decisions**.

The v0.19 Pi artifact now contains a self-contained staging path that verifies and
installs the exact tested source without claiming the TFT.

The staging wrapper:
- verifies archive SHA-256 and commit/root provenance;
- preserves an existing Beast Core config;
- makes a private SQLite backup of the local Beast database before the new Core
  starts;
- reuses normal installers;
- starts Beast Core only;
- optionally prepares the Beast-owned QR dependency;
- finishes with a target preflight;
- leaves Beast UI stopped and Pwnagotchi display ownership untouched.

A separate explicit:
`beast-v019-accept start`
remains required to begin the bounded TFT handoff.

Durable evidence rule:
physical acceptance evidence must identify the exact staged source commit, the CI
commit that tested it and the source archive digest. The acceptance harness now
imports this staging provenance and includes it in both JSON and text reports.

Durable recovery rule:
the pre-stage Beast DB backup is evidence/recovery material, not an automatic
schema rollback. Automatic database rollback across unknown future migrations
must not be invented casually.

Final code-bearing gate for this block:
- source `89e88277c351c1b60f1af3e01a3002d84d46ed63`;
- run `35981407684` (#384);
- 415 tests;
- compile/shell/gallery/Pi artifact green;
- independently verified artifact id `10800377275`;
- source checksum/root/staging-script syntax all verified.

Lightbulb implication:
this source->artifact->staging->physical-evidence provenance chain should become
the model for future beta/release validation too. Later Doctor/"known-good"
fingerprints can reference the same deployment identity instead of inventing a
parallel provenance system.

