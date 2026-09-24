# Beastagotchi Dependency & Capability Resolver — v0.1

**Status:** approved architecture / first catalog metadata implemented  
**Date:** 2026-09-24  
**Reference build:** Raspberry Pi 4 / Jayofelony 64-bit Pwnagotchi `noai` branch  
**Jayofelony reference commit reviewed:** `93dda381ef11538e4ec03fd130abad3ceeea7a4c`

## Decision

Plugin management is expanded into a platform-wide **Dependency & Capability
Resolver**.

The user approved the Plugin & Capability Center direction, dependency/requirement
awareness, provider arbitration, remediation guidance, and the principle that
Beastagotchi should understand how Plugins, Packs, Hardware, Experiences, Apps,
Services and optional expansion modules depend on one another.

This is not permission to install everything automatically.

The governing distinction is:

- **catalog everything known**;
- **install/enable only what the active build or selected capability needs**.

## Why this belongs in Beast Core

Pwnagotchi plugins may provide real value while retaining their own upstream
implementation. Beast should normally integrate their useful state and controls
rather than cloning the plugin.

The Resolver supplies the missing layer between:

1. component inventory;
2. canonical Beast capabilities;
3. configuration;
4. dependencies;
5. hardware;
6. conflicts;
7. audited remediation.

A component can therefore answer:

- What does this provide?
- What does it require?
- What is missing?
- Is an alternate provider already available?
- What uses this component?
- What will break if it is disabled?
- Can Beast safely fix the problem?
- Does the user need to connect hardware, enter a credential, or make a choice?

## Common component model

All managed component families should converge on a common vocabulary:

- `provides` — capabilities supplied by the component;
- `requires` — mandatory requirements;
- `requires_any` — one of several providers may satisfy the requirement;
- `optional_requirements` — enrich functionality without blocking it;
- `conflicts` — components/resources that cannot safely coexist;
- `provider_group` — e.g. location, power, Internet, presentation;
- `used_by` — reverse dependency graph;
- version compatibility;
- hardware requirements;
- device-node/kernel requirements;
- package/module/executable requirements;
- service requirements;
- configuration requirements;
- secret/credential presence;
- connectivity requirements;
- permission/privilege requirements;
- storage/resource/thermal requirements;
- data-egress class;
- remediation class.

## Requirement types

The Resolver must be able to represent at least:

### Software
- Debian/OS package;
- Python distribution/module;
- executable;
- shared library;
- kernel module/driver;
- firmware;
- service/unit;
- another Plugin;
- another Beast Pack;
- Beast/Pwnagotchi/Python/component version range.

### Hardware / platform
- USB VID:PID or hardware class;
- I2C/SPI/UART/GPIO availability;
- device path such as `/dev/ttyUSB0` or `/dev/i2c-1`;
- Wi-Fi adapter role;
- Bluetooth adapter;
- GPS/GNSS provider;
- battery/UPS provider;
- display/input provider;
- SDR / Meshtastic / sensor class.

### Configuration / user action
- required config field;
- file/directory/path;
- account/API credential presence;
- paired phone;
- Internet route;
- hardware connection;
- user-selected provider.

The Resolver reports presence only for secrets. It must never reveal secret values.

## Resolution states

A requirement should resolve to a state such as:

- `satisfied`
- `optional_missing`
- `missing_installable`
- `missing_user_action`
- `provider_available_not_selected`
- `hardware_absent`
- `service_inactive`
- `configuration_missing`
- `credential_missing`
- `version_incompatible`
- `conflict`
- `unsupported`
- `unknown`

"Unknown" is preferable to inventing certainty.

## Remediation classes

A missing requirement is also classified by what Beast may safely do.

### AUTO-SAFE
A bounded, verified, reversible operation with no meaningful user choice.

### CONFIRM-TRANSACTIONAL
Beast can perform it, but only after an explicit confirmation, snapshot/plan and
rollback path.

Examples may include an approved package install, config change or service enable.

### GUIDED
A human action is required.

Examples:
- connect GPS;
- pair phone;
- attach UPS;
- enable a hardware interface;
- enter an API credential.

Beast should provide exact instructions and automatically re-check afterward.

### CHOOSE-PROVIDER
Multiple valid providers exist and Beast needs a policy or user selection.

### UNSUPPORTED / POLICY-BLOCKED
The managed path does not support or recommend the operation. Beast explains why,
but an authenticated owner may explicitly override the policy when the operation
is technically possible.

### TECHNICALLY IMPOSSIBLE
The requested action cannot presently execute as described. Owner Override does
not turn absent hardware, missing privilege, an invalid binary format or a
nonexistent source into a successful operation.

## Provider arbitration

Requirements should prefer abstract capabilities over named implementations.

Examples:

- `location.position`
- `power.battery.telemetry`
- `network.internet`
- `network.bluetooth_tether`
- `input.buttons`
- `display.primary`
- `radio.wifi.monitor`

A consumer requiring `location.position` should not care whether the provider is
USB GPS, gpsd, PwnDroid or a later Hardware Pack.

Multiple enabled providers do not create duplicate truth. The Resolver records:

- active provider;
- alternate providers;
- unavailable providers;
- reason for provider selection;
- health;
- priority/policy.

This is especially important for simultaneous power plugins and GPS providers.

## Dependency graph / Explain integration

The graph must work in both directions.

Example:

`Expedition Map -> location.position -> GPS plugin -> /dev/ttyUSB0`

If the USB receiver disappears, Beast can explain why Map is unavailable and can
offer an alternate provider if one exists.

Reverse queries are equally important:

`GPS -> used by Map, Expeditions, Capture context, Context Engine, Memories`

Before disabling GPS, Beast can therefore explain the effect.

This graph is intended to feed Beast Doctor/Explain.

## Plugin & Capability Center UX

A plugin entry should eventually show more than an enabled toggle.

Example:

**GPS**
- Running / Healthy
- Provides: Location
- Used by: Map, Expeditions, Capture Vault, Context Engine
- Provider: active
- Hardware: receiver detected
- Data egress: none
- Beast integration: full

Example:

**WiGLE**
- Installed
- Provides: external location/network export
- Internet: available
- Location: available
- API credential: missing
- Status: Needs setup
- Action: Configure credentials

Example:

**UPS-Lite**
- Enabled
- Hardware not detected
- Provides: battery telemetry
- Current provider: Waveshare UPS
- Status: Ready but inactive / hardware absent

## Jayofelony stock/default plugin compatibility class

Current Jayofelony source was reviewed at commit
`93dda381ef11538e4ec03fd130abad3ceeea7a4c`.

### Bundled default plugin source files

The current `pwnagotchi/plugins/default/` directory contains these functional
plugins:

- auto-update
- auto_backup
- bt-tether
- fix_services
- gpio_buttons
- gps
- grid
- logtail
- memtemp
- ohcapi
- pisugarx
- pwncrack
- session-stats
- switcher
- ups_lite
- webcfg
- webgpsmap
- wigle
- wittypi
- wpa-sec

It also contains `example.py`, which is treated as developer/reference material
rather than an end-user feature.

### Stock-known/configured plugin names whose implementation is not bundled in that directory

Jayofelony's current defaults/catalog also knows about:

- gps_listener
- pwndroid
- ups_hat_c

These are still part of the compatibility catalog, but Beast must not pretend a
bundled implementation exists when the source is absent from the current default
plugin directory.

### Current default enablement in Jayofelony defaults

At the reviewed commit, the defaults explicitly enable:

- auto_backup
- auto-update
- fix_services
- grid
- webcfg

Most other stock entries are disabled until hardware, credentials or user choice
make them relevant.

Beast compatibility must support the full stock-known set regardless of the
upstream default toggle.

## Initial Beast binding policy

Current v0.19 plugin catalog metadata now describes broad roles/capabilities for
the stock family.

Examples:

- GPS -> canonical location;
- memtemp -> canonical system telemetry;
- session-stats -> canonical session metrics;
- bt-tether -> managed connectivity;
- webgpsmap -> visually superseded by Beast Map/Expedition surfaces;
- auto_backup -> overlaps Beast Backup/Recovery;
- auto-update -> overlaps Beast Update Center;
- logtail -> overlaps Beast Logs/Black Box/Doctor;
- webcfg -> authentic Pwnagotchi fallback while Beast provides transactional
  configuration;
- GPIO buttons -> future input provider;
- PiSugar/UPS-Lite/UPS HAT C/WittyPi -> competing power-provider family;
- WiGLE -> external location/network-data export;
- WPA-sec/Pwncrack/OHCAPI -> external capture-processing connectors;
- Grid -> peer/publication compatibility;
- Switcher -> legacy scheduler/automation provider.

Catalog metadata does not install dependencies, select providers, send data or
change configuration.

## Software/service BOM policy

Beast should maintain a **versioned superset Bill of Materials (BOM)** for the
user's reference build.

The BOM is the answer to:

> "What software could this build ever need for the currently approved feature
> universe?"

It is **not** the install list.

Each BOM entry must carry:

- component/package/module/service name;
- source/authority;
- version/range if known;
- required by;
- optional versus mandatory;
- current installation state;
- whether it is already supplied by the Jayofelony image;
- runtime versus build/development-only;
- hardware/feature trigger;
- conflict notes;
- resource/storage impact where meaningful;
- safe install/remove method;
- rollback/removal information.

The installed set should be the graph closure of the active build's selected
features, not the entire superset.

## Why not preinstall the entire superset

Installing every known future dependency creates avoidable problems:

- larger upgrade/security surface;
- more version conflicts;
- more apt/pip ownership ambiguity;
- services that may wake up or bind ports unexpectedly;
- additional boot/RAM/CPU/storage cost;
- hardware-specific packages with no matching hardware;
- obsolete packages remaining after plans change;
- harder debugging because unused software can still alter the system;
- greater risk to the stock Pwnagotchi Python environment.

The Pi 4 has enough RAM for many packages, but RAM capacity is not the main issue.
Correctness, maintainability and clean ownership are.

## Recommended reference-build policy

For the user's own Pi 4 Beastagotchi:

1. **Inventory broadly.**
2. Keep a complete known-universe BOM.
3. Install the small common foundation once.
4. Install optional dependencies when a capability is actually selected.
5. Prefer capability bundles/profiles over one-off manual package hunting.
6. Keep inactive Packs storage-only.
7. Keep optional services disabled/stopped until the feature needs them.
8. Detect pre-existing stock-image dependencies before installing duplicates.
9. Snapshot/plan before dependency mutations.
10. Re-check health after changes and preserve rollback.
11. Record exact package/module/service provenance for reproducibility.

Future convenience action:

**PREPARE CAPABILITY**

Example:

`PREPARE: SDR / ADS-B`

Beast should show the complete plan first, including packages, services, hardware,
storage/resource effect and conflicts, and only perform approved actions.

## Current implementation boundary

Implemented now:
- stock plugin role/capability/requirement catalog metadata in
  `beastcore/plugin_integration.py`;
- provider-group, data-egress, credential and hardware-specific metadata;
- catalog explicitly reports that requirement resolution is `catalog_only`;
- dependency installation/remediation executor remains disabled.

Not implemented yet:
- live package/module/executable/service requirement resolution;
- provider selection/arbitration;
- reverse `used_by` graph;
- automatic package installation;
- schema-driven plugin config;
- credential-entry workflow;
- generalized Plugin install/update transaction.

This boundary is intentional.

## Owner sovereignty / unrestricted path

The Resolver is advisory to an authenticated owner, not a permanent policy lock.

Normal plans distinguish:
- `technical_blockers` — cannot presently execute as described;
- `policy_blockers` — managed/supported mode recommends stopping;
- `owner_override_available` — the owner may deliberately proceed outside the
  managed/support boundary when no technical blocker prevents the operation.

Beast should continue to display dependencies, conflicts, data-egress, version,
resource and recovery warnings in Owner Override mode, but policy warnings become
informational after explicit owner approval.

See `Beastagotchi_Owner_Sovereignty_Unrestricted_Mode_v0.1.md`.


## Next implementation phases

1. Define common requirement/result dataclasses and canonical capability IDs.
2. Add side-effect-free resolver probes for declared requirements only.
3. Build reverse `used_by` graph.
4. Surface resolver results in Plugin & Capability Center and Doctor.
5. Add build-specific BOM generator/export.
6. Add provider arbitration without mutating upstream plugins.
7. Add transactional remediation plans.
8. Add explicit package/service installer only after dry-run, provenance and rollback
   behavior are proven.
9. Extend the same resolver contract to Packs, Experiences, Apps and Hardware Studio.
