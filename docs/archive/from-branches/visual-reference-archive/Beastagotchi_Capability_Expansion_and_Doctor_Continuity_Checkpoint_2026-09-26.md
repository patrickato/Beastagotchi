# Beastagotchi Doctor + Capability Expansion Continuity Checkpoint

**Date:** 2026-09-26 (late-session checkpoint)  
**Status:** durable continuity record; implementation remains paused  
**Purpose:** preserve everything important discussed from the Doctor deep-dive through the current Hardware Bench capability-expansion cluster so no ideas are lost when implementation resumes later.

---

# 1. Current project position

The Doctor deep-dive is **complete enough for this pre-building phase**.

The **Capability Expansion Pass is ACTIVE**.

The pass is explicitly asking:

> **What new things can Beastagotchi actually DO because it sits on top of Pwnagotchi + Bettercap + Linux + Raspberry Pi + Beast Core + attached hardware + local/online resources?**

Diagnostics/logging do not count as the primary answer to this pass.

Implementation remains paused until Capability Expansion, X+Y=>Z jam, AI discussion, Monster/perception/expression jam, and final reconciliation are complete.

---

# 2. Doctor — settled direction for this phase

## One Doctor

There is one Doctor, not separate Radio/Display/Storage/etc. Doctors.

Doctor is the one-stop diagnostic/repair system for:
- Pi/board/hardware;
- Linux/kernel/drivers/device tree/services/packages/filesystems/networking;
- displays/touch/SPI/I2C/GPIO/USB/Bluetooth/audio;
- Pwnagotchi/Bettercap/plugins/interfaces/capture pipeline;
- Beast Core/UI/Studio/Packs/providers/services/history;
- attached hardware and managed ecosystem.

Logs, shell commands, files, telemetry and debug output are **Doctor instruments/evidence**, not separate products.

## Doctor reasoning model

Preserve:

> **Machine Census -> symptom -> dependency path -> competing hypotheses -> targeted probes -> evidence/confidence -> repair plan -> snapshot/rollback -> repair -> functional verification -> cleanup -> learn.**

Doctor should test outcomes, not merely process/service state.

Principle:

> **Running != working.**

Examples:
- service active does not prove packet flow;
- driver loaded does not prove device function;
- GPS daemon running does not prove coordinates arrive;
- backup completion does not prove restore/readability;
- display service running does not prove pixels reach TFT.

## Probe model

- Machine Census for deep slow-changing patient inventory;
- vital signs for cheap/live facts;
- fault-family Probe Blocks such as DISPLAY-DEEP, RADIO-DEEP, STORAGE-DEEP, POWER-DEEP, etc.;
- open-ended escalation when standard probes are inconclusive.

Each probe should conceptually declare what question it answers, cost/risk, requirements, fallbacks and useful fault families.

## Known-Good / What Changed?

Doctor should heavily use healthy historical state and change history to reduce troubleshooting search space.

## Autonomy — Option C selected

Doctor is a **quiet caretaker by default**, but becomes visibly communicative when:
- owner opens Doctor;
- significant issue is detected;
- approval/input/physical action is required;
- verbose/expert mode is enabled.

Doctor investigates aggressively, repairs conservatively, and asks intelligently.

Read-only investigation/search can be broad. Mutation authority remains risk/policy/Transaction controlled.

## Live status/progress

A shared Beast live-operation status primitive is required across Doctor and other long-running work.

Use truthful progress:
- exact percentage/count only when measurable;
- otherwise live stages such as Downloading -> Verifying -> Installing -> Testing -> Cleanup;
- show current activity so the user never has to wonder whether Beast froze.

## Find it -> use it -> put it back

Owner phrase to preserve:

> **Doctor finds it -> uses it -> puts it back.**

Doctor may locate missing drivers/packages/helpers/docs/resources from local storage, Beast cache, owner library/NAS/Home Base, trusted repositories, official project/vendor sources or broader search.

Managed lifecycle:

> identify -> locate -> stage -> verify -> snapshot -> unpack/build -> install/configure -> verify actual function -> retain only required persistent artifacts -> delete ZIP/extraction/build debris -> update inventory/evidence.

Interrupted/failed operations must retain cleanup obligations; broader housekeeping catches registered leftovers without deleting unknown owner files.

## Acquisition Queue

If a resource cannot be obtained now, any subsystem (not only Doctor) may request:
- Queue for Home Base;
- Queue for next permitted Internet;
- dismiss/manual alternative.

The queue can support packages, drivers, manuals, maps, datasets, Packs, updates, models/assets, user downloads, SDR regional databases, etc.

Download != install/apply.

## Doctor knowledge/search

Doctor combines:
1. patient knowledge about this specific Beast;
2. local/offline medical library;
3. current research when permitted.

Potential corpus:
- Beast docs;
- Pwnagotchi/Jayofelony docs;
- Bettercap docs;
- Pi/Linux docs/man pages;
- plugin READMEs;
- hardware manuals/datasheets;
- owner-added TXT/Markdown/PDF/wiki material;
- previous solved Doctor cases;
- official web/GitHub/issues/community sources when online.

Internet fixes are leads, not blind root instructions.

## Collective Doctor Knowledge Network

Strong candidate preserved:

> **The fleet learns, but each Doctor still treats its own patient.**

Sanitized structured cases can contribute:
- normalized hardware/config/software profile;
- symptom/failure signature;
- probes/evidence;
- hypotheses rejected;
- repair attempted;
- artifact/source provenance;
- success/failure/rollback/partial result;
- functional verification;
- recurrence/regression/age.

No sensitive/private material by default; anything beyond baseline policy requires explicit opt-in/approval.

## Population baseline data

Important owner addition:

> **Failures teach what breaks; healthy systems teach what normal looks like.**

With owner policy, sanitized healthy baseline data may build population knowledge across board revisions, sensors, drivers, peripherals, kernels, package versions and normal behavior.

This can enable:
- healthy cohort comparison;
- rare-hardware intelligence;
- early degradation detection;
- compatibility/regression discovery;
- better similar-patient matching.

Privacy must account for combinations becoming identifying even when individual fields seem harmless.

## Source trust + empirical evidence

Do not reduce a fix to one vague trust score.

Separate dimensions include:
- provenance/author identity/integrity;
- patient hardware/software similarity;
- fleet outcomes;
- close-cohort outcomes;
- recency/current-version coverage;
- local evidence;
- recovery readiness.

Official does not automatically mean functional; unofficial does not automatically mean bad.

Possible recommendation classes:
- Verified;
- Recommended;
- Community Proven;
- Experimental;
- Unverified;
- Known Bad/Incompatible;
- Obsolete.

Doctor-verified before/after functional evidence outweighs popularity/thumbs-up.

Negative outcomes are preserved as valuable evidence rather than erased.

## Doctor presentation

Settled principle:

> **Doctor is the capability. The visual Doctor is an Experience.**

Build the complete functional Doctor independent of presentation skin.

TFT priorities:
- 480x320 clarity;
- large touch targets;
- status/current task;
- truthful live progress;
- next action/approval;
- minimal scrolling;
- low resource/thermal cost.

Creature/avatar animation is optional presentation flavor, never required for Doctor operation.

Strong visual motif to preserve:
- heart/vitals line / machine-health waveform;
- changing cadence/state/color according to health/investigation/repair/resolution;
- do not rely only on color for accessibility.

WebUI/phone may use richer layouts and animation.

Deep technical view remains available with raw commands, evidence, diffs, sources, system path, Transactions, etc.

Two Doctor UI concept images were saved in Library at:
- `/Beastagotchi/Visual References/Doctor_UI_Concept_01.png`
- `/Beastagotchi/Visual References/Doctor_UI_Concept_02.png`

---

# 3. Guided Software — cross-project platform pattern

Strong accepted direction:

> **Make complex software approachable without taking the full software away.**

For suitable tools provide:

1. **Focused/Guided** — task-oriented simple experience;
2. **Advanced Guided** — more underlying controls;
3. **Full Tool** — launch/use the complete installed program.

Guided is not restricted mode.

This started with SDR but should spider into many domains: radio, packet analysis, electronics, GPIO, maps, programming, Linux tools, measurement, etc.

---

# 4. Capability discovery / Abilities concept

Strong candidate:

> Beast should explain what the current hardware/software stack **can do now**, what it **could do with one missing piece**, and how to get there.

Possible practical Abilities states:
- READY;
- AVAILABLE;
- FULL TOOL;
- OWNER SPACE;
- NEEDS HARDWARE;
- NEEDS SOFTWARE;
- CONTEXT/LICENSING REQUIRED;
- unavailable/conflicting where applicable.

Example:

`RTL-SDR detected`
- FM Radio: Ready
- Wireless Sensors: needs rtl_433
- ADS-B: software available
- AIS: software available
- Satellite: SatDump + suitable antenna recommended
- Full SDR: Open SDR++/GQRX/etc.

As hardware/providers appear, the capability graph can change dynamically.

---

# 5. Capability Expansion Cluster 1 — RF / SDR / GPS / sensor world

Owner strongly approved this cluster with no notes.

## SDR as capability family, not one application

One RTL-SDR can provide primitive capabilities:
- tunable RF receiver;
- sample stream;
- spectrum/waterfall;
- demodulation input;
- decoder input;
- observations/events.

Focused experiences may include, subject to hardware/region/technical availability:
- AM/FM broadcast;
- Weather;
- rtl_433 sensor reception;
- ADS-B/Aviation;
- AIS/Maritime;
- amateur-radio receive/learning;
- satellite reception;
- Spectrum Lab;
- other receive-oriented domains.

Full applications remain accessible (SDR++, GQRX, GNU Radio, SDRTrunk, etc. where supported/installed).

## SDR beginner/tutor mode

Teach while doing:
- frequency;
- bandwidth;
- gain;
- squelch;
- modulation;
- sample rate;
- filters;
- waterfall/spectrum interpretation;
- frequency correction;
- antenna implications;
- receive/transmit distinction.

Pattern:

> show -> explain -> let user change -> visualize/listen -> restore recommended baseline.

## Location-aware radio profiles

GPS + local/offline/online reference data can offer relevant presets by current/selected location for broadcast/weather/aviation/maritime/amateur and other applicable domains.

## Sensor World

rtl_433 and future providers can turn RF sensors into structured Beast Providers rather than raw packet/frequency views.

Possible named/known sensors:
- weather station;
- campsite thermometer;
- freezer/greenhouse sensor;
- owner-recognized devices.

Feeds may support live UI, Expeditions, Homecoming, automation, creature reactions, trends, Search and Doctor.

## SKY / “What’s Above Me?”

Potential shared view combining real truth from:
- GPS/location;
- time;
- star/planet/Moon/Sun catalogs;
- ISS/satellite ephemerides;
- ADS-B aircraft;
- satellite passes/reception opportunities;
- optional weather-satellite context.

Real sky state can drive real creature reactions/choreography.

Celestial idea explicitly preserved:
- real star maps;
- constellations;
- Sun/Moon/planets;
- meteor/calendar events;
- ISS/satellite passes;
- Beast looking upward/reacting to actual sky;
- astronomy factual;
- astrology/zodiac only as optional cultural/theme content, never scientific telemetry.

## FIELD / “What’s Around Me?”

Potential ground-level sibling combining:
- Expedition/GPS route;
- Pwnagotchi observations;
- peers;
- Meshtastic nodes;
- Bluetooth/environmental providers;
- rtl_433 sensors;
- owner POIs;
- other mapped observations.

## GPS as shared sense

GPS should not belong to one Map app. One provider can feed:
- Pwnagotchi;
- Expeditions;
- maps;
- SDR local presets;
- SKY;
- Meshtastic;
- Homecoming;
- weather/context;
- Search;
- creature awareness.

## Tuner arbitration

“One tuner, many experiences” requires explicit resource arbitration.

If one SDR cannot simultaneously service incompatible frequency tasks, Beast should offer clear switching/ownership. Multiple tuners may allow simultaneous roles.

## Background watch jobs

Not every RF use requires a permanent foreground application. Context/policy may schedule brief sensor/weather/etc. checks where technically appropriate.

---

# 6. Walk-the-line capability rule — cross-cutting

Owner explicitly reminded that Capability Expansion must explore near managed-boundary edges rather than silently omit dual-use/advanced tools.

Preserved hierarchy:

## Beast-managed
First-party bounded supported workflows.

## Compatible
Beast can detect/configure dependencies/launch/import/export/visualize/integrate with the full external tool.

## Owner Space
Owner can install/run general Linux software outside managed Beast workflows. Beast should coexist and may expose generic hooks/state.

## Documented gap / outside managed facilitation
When Beast should not ship a purpose-built automated workflow, do not pretend the capability does not exist. Explain the class of external capability, interfaces/dependencies, and generic integration boundary where appropriate.

Core principle:

> **Explore broadly first; decide what Beast itself should manage second.**

Receive-oriented RF, packet analysis, owner-network diagnostics, full tools, education and hardware inspection can be discussed frankly.

Where transmission/licensing/authority/context materially changes risk, Beast should expose that truth rather than treating it as a generic button.

---

# 7. “Overlapping, not conflicting”

Owner phrase preserved as a possible platform principle.

One underlying capability may support many experiences without duplicating truth/configuration.

Examples:
- one RTL-SDR -> FM, sensors, ADS-B, AIS, spectrum;
- one GPS -> map, Expedition, SKY, SDR presets, Homecoming;
- one audio output -> radio + alerts + creature expression;
- one offline knowledge corpus -> Doctor + Search + tutorials + Studio;
- one Acquisition Queue -> Doctor + maps + Packs + SDR datasets + owner downloads.

If resources genuinely conflict, Beast should arbitrate/sequence/lease them explicitly.

---

# 8. Home Base / Acquisition implications

Home Base is broader than update staging.

Potential owner-policy-controlled work:
- queued uploads/downloads;
- maps/docs/manuals/wiki;
- packages/drivers/software;
- Packs/content;
- backup/NAS replication;
- exports;
- knowledge updates;
- Global Doctor sync;
- compatibility/advisory downloads;
- SDR datasets;
- future AI models/assets;
- cleanup/maintenance.

Potential product feel:

> Beast returns home and exchanges/learns/prepares heavy resources while trusted network and wall power are available.

---

# 9. Capability Expansion Cluster 2 — Hardware Bench / buses / microcontrollers

Current active cluster; preserve all ideas below.

## Hardware Bench scope

Treat Pi physical computing as one coherent workspace, not a GPIO toggle page.

Potential sources:
- GPIO;
- I2C;
- SPI;
- UART/serial;
- 1-Wire;
- PWM;
- USB serial;
- sensors;
- Pico/Pico 2;
- ESP32;
- logic analyzers;
- measurement devices;
- power/current sensing;
- future CAN/RS-485/industrial interfaces.

## Hardware onboarding

Example:

`New I2C device at 0x76`

Beast may identify possible BME280-class hardware, show temperature/humidity/pressure capabilities, available driver/profile, guided wiring/docs, raw/expert bus access, install/queue missing dependencies, then verify provider functionality.

Unknown remains unknown when identification cannot be established.

## Microcontrollers as Beast coprocessors

Pico/Pico 2/ESP32 may act as attachable physical extensions for tasks the Pi is less ideal at:
- precision timing;
- PWM;
- ADC/analog sensing;
- extra GPIO;
- sensor collection;
- LED/haptic control;
- frequency/pulse measurement;
- remote sensing;
- serial/protocol bridges;
- watchdogs;
- low-power tasks;
- logic analysis.

## Role Firmware / “role cartridges”

Strong candidate:

Plug in a supported microcontroller and optionally assign/reflash a role such as:
- Sensor Hub;
- GPIO Expander;
- LED/Haptic Controller;
- ADC Logger;
- Logic Analyzer;
- Serial Bridge;
- Power Monitor;
- Remote Environmental Node;
- Blank / Owner Firmware.

Beast may acquire verified firmware, identify chip/board, flash, verify, reboot and wait for the new Provider.

Full expert flashing/tooling remains available.

## Logic Analyzer / measurement integration

Guided Hardware experience may expose simple tasks such as:
- Watch I2C;
- inspect UART;
- observe PWM;
- decode supported protocols.

Advanced/full path may launch PulseView/sigrok or another full compatible analysis application.

## Doctor gains physical probes

Hardware Bench can make Doctor stronger.

Example diagnostic chain:
- software says I2C controller active;
- logic probe shows clocks present;
- target never ACKs;
- Doctor can distinguish likely physical wiring/power/address/device failure from software configuration.

This extends Doctor from Linux diagnosis toward actual physical-system diagnosis.

## Live pin ownership

Beast should know and display GPIO/bus ownership and conflicts.

Examples:
- GPIO occupied by audio/TFT/provider;
- SPI bus shareable via another CS;
- provider can be suspended to free pin;
- incompatible claims explained instead of silently colliding.

This is “overlapping, not conflicting” at the physical layer.

## Visual wiring

Beginner experience can display Pi header/wiring diagrams and watch for device appearance live.

Example:
- highlight 3.3V/GND/SDA/SCL;
- show sensor connection;
- wait for detection;
- acknowledge `Detected`.

Expert/raw access remains available.

## Guided Hardware / electronics learning

Extend Guided Software philosophy to physical electronics.

Potential lessons:
- LED + resistor;
- button/pull-up;
- PWM;
- I2C sensor;
- UART/SPI;
- servo;
- analog input via Pico;
- logic analyzer basics.

Pattern:

> show wiring -> explain -> detect/test -> let user change -> visualize outcome -> offer full/raw tools.

## Bench Projects

Candidate saved project bundle for owner-built hardware systems:
- expected hardware;
- wiring/pin assignments;
- microcontroller firmware role;
- Provider configuration;
- docs/tutorial;
- optional automations;
- dependency requirements.

Possible future shareable form such as a Camping Sensor Pod project.

## Remote Beast senses

Remote Pico/ESP32 nodes may extend Beast perception beyond the enclosure:
- outdoor/campsite environmental node;
- greenhouse;
- garage;
- freezer;
- workshop;
- vehicle temperature;
- other owner-built remote sensor points.

Transport may later be BLE/Wi-Fi/MQTT/Meshtastic/serial/etc.; Beast should consume a canonical Provider rather than bind creature logic directly to one transport.

This raises an important conceptual question:

> Is the Pi only the Beast's brain while remote nodes become distributed eyes/ears/senses?

Preserve for Perception/Expression jam.

## Industrial/vehicle/general interfaces

Do not artificially stop at hobby sensors.

Potential generic interfaces:
- RS-232;
- RS-485;
- Modbus;
- CAN;
- USB instrumentation;
- multimeters/scopes/environmental instruments.

Beast-managed focus can be identification, reading, visualization, owner-controlled diagnostics/configuration, education and data import/export. Full tools and Owner Space remain available.

Do not collapse generic CAN capability into a single purpose-specific “car hacking” product.

## Dynamic Abilities graph

Connecting hardware should dynamically expand what Beast can do.

Example:

Before Pico:
- analog sensing: unavailable;
- logic analyzer: unavailable;
- extra PWM: unavailable.

After Pico detection:
- analog sensing: Available;
- logic analyzer: Install Role;
- extra PWM: Available.

After flashing Sensor Hub:
- analog/environmental expansion: Ready.

---

# 10. Exact unfinished Hardware Bench questions

Owner has **not yet answered these three jam prompts** because the next message requested preservation first.

Resume with these or continue the cluster naturally:

1. **Pico/ESP32 role cartridges** — should a microcontroller be repurposable on demand (logic analyzer today, sensor hub tomorrow, LED/haptic controller later)?
2. **Bench Projects** — should Beast save complete owner-built electronics projects (hardware list, wiring, firmware, configuration, providers, tutorials), potentially shareable later?
3. **Remote senses** — if remote nodes become Beast eyes/ears/sensors, how far should the Beast identity/perception model extend beyond the Pi enclosure?

---

# 11. Other preserved adjacent ideas from this same discussion stretch

## Celestial / astronomy

Explicitly preserve:
- real star maps;
- astronomy based on actual location/time;
- optional astrology/zodiac as clearly themed/cultural content;
- Beast looking up/reacting to real sky events;
- ISS/satellite ties;
- SKY Workspace possibility.

## Search

Desired eventual federated Search spans:
- local Beast state/apps/capabilities/hardware/files;
- offline docs/manuals/wiki/PDF/TXT/datasheets;
- owner library;
- history/Expeditions/Memories/Doctor cases;
- Packs/Procedures/Tools;
- Global Doctor collective;
- online web/GitHub/docs/community sources when permitted.

## Claude

Owner instruction: use Claude aggressively as an intellectual peer/second-brain during development.

Potential roles:
- adversarial architecture review;
- alternate design;
- code review;
- failure-case generation;
- Probe/Procedure review;
- public issue/signature mining;
- test generation;
- implementation on separate branches for review.

Never blindly merge or treat another model as authority.

---

# 12. Next overall sequence

Current:

> **Capability Expansion Pass — ACTIVE**

After capability clusters are sufficiently explored:

1. Cross-layer X + Y => Z jam;
2. optional AI role/capability discussion;
3. Monster / breeding / perception / expression jam;
4. final APPROVE / MODIFY / RESERVE / REJECT reconciliation;
5. update architecture/contracts/roadmap/migration order;
6. resume implementation in meaningful test-backed tranches.

---

# 13. Exact resume point

**Do not resume full implementation.**

Resume discussion at:

> **Capability Expansion — Hardware Bench cluster**, immediately after the role-cartridge / Bench Project / remote-senses prompts, then continue scanning additional layered capabilities.

All ideas in this document are preserved for later reconciliation even where not yet final canon.
