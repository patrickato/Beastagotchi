# Beastagotchi Security Direct Examples + AI/Doctor + Pwnagotchi Plugin Addendum

Date: 2026-09-27
Status: discussion/architecture preservation; implementation still paused

## 1. Broad AI vs Doctor — corrected split

Doctor remains the specialist diagnostic/repair clinician and factual authority around evidence, probes, confidence, Known-Good, transactions, rollback, verification and fleet medical knowledge.

Broad AI becomes a separate optional conversational assistant/orchestrator. It may use an interchangeable local/phone/Home Base/self-hosted/cloud model and can call Doctor, Search, Abilities, Software Catalog, Security Workspace, managed Actions and Full Tool handoffs.

Creature remains a third distinct identity/presentation system.

Target mental model:

- Doctor = specialist clinician.
- Broad AI = optional conversational assistant / general interpreter / orchestrator.
- Creature = living identity/personality.

Doctor works fully with AI disabled. Broad AI may consult Doctor but does not replace Doctor's deterministic evidence or authority. On weak boards such as Pi Zero 2 W, Broad AI can remain entirely external while the local Beast/Pwnagotchi/Doctor stack stays functional.

## 2. Direct real-world projects to study/use/integrate

### Bjorn
Pi + e-paper + web UI + target discovery + vulnerability/action-module architecture. Mixed capability: useful architecture/data/UI/module ideas can be studied independently of offensive functions that Beast should not wrap.
Potential takeaways: action-module manifests, autonomous-but-visible task state, e-paper summary + rich web UI, target knowledge graph, extensible module catalog.
Source: https://github.com/infinition/Bjorn

### P4wnP1 A.L.O.A.
Raspberry Pi Zero-family USB gadget framework. Provides runtime USB gadget composition such as Ethernet, serial, storage and HID plus templates and web/CLI control.
Potential Beast direction: USB Gadget Workspace / USB Role Provider for recovery console, direct device link, serial, file transfer, virtual NIC, provisioning and authorized lab automation. Treat sensitive HID/offensive payload behavior separately from neutral USB-gadget primitives.
Source: https://github.com/RoganDawes/P4wnP1_aloa

### ESP32 Marauder / Bruce
Portable ESP32/M5Stack security firmware ecosystems with Wi-Fi/Bluetooth and broader hardware capabilities.
Potential Beast direction: external coprocessor/remote-sense Providers. Detect supported ESP32/M5Stack hardware, identify firmware, ingest passive observations/PCAP/logs, and later support role-cartridge style provisioning where appropriate. Do not clone mature firmware unnecessarily.
Sources:
- https://github.com/justcallmekoko/ESP32Marauder
- https://github.com/BruceDevices/firmware

### Kismet
Multi-source radio observation architecture spanning Wi-Fi and other radio/sensor data sources.
Potential Beast direction: Kismet Provider feeding structured observations, devices, alerts and radio metadata into Search, Chronicle, maps, Security Workspace, Doctor and creature perception.
Source: https://www.kismetwireless.net/docs/readme/datasources/datasources/

### Zeek
Passive network traffic analyzer that turns PCAP/live traffic into structured connection/protocol/security logs.
Potential Beast direction: Home Base analysis provider. Beast field captures or authorized LAN captures can become structured searchable facts instead of opaque PCAP blobs.
Source: https://docs.zeek.org/

### Arkime
Indexed searchable full-packet-capture / session system with PCAP export.
Potential Beast direction: Home Base "Security Time Machine" for long-lived searchable packet/session history linked to Beast sessions, incidents and Chronicle.
Source: https://arkime.com/

### OpenCanary
Low-resource ARM64-capable multi-protocol honeypot/decoy.
Potential Beast direction: Sentinel Mode. When on an owner/trusted network Beast can become a defensive canary and feed events to notifications, Chronicle, Doctor context and creature expression.
Source: https://github.com/thinkst/opencanary

### Lynis
Agentless Linux/Unix security audit/hardening tool.
Potential Beast direction: Doctor Security Check / Security Posture Pack for the Beast itself; parse results, explain findings, track drift and re-test after remediation.
Source: https://github.com/CISOfy/lynis

### RaspAP
Full-featured Raspberry Pi/Debian Wi-Fi router/AP web stack.
Potential Beast direction: learn from and/or integrate network-role management for isolated Security Lab networks, temporary AP/router roles, VPN/tether paths and second-radio scenarios while respecting Pwnagotchi radio ownership.
Source: https://github.com/RaspAP/raspap-webgui

### Cockpit
Web Linux administration built on normal system APIs/commands and coexists with CLI workflows.
Potential Beast direction: architectural precedent for Guided UI + real Linux underneath; optionally a Full Tool handoff for system administration rather than duplicating everything in Beast.
Source: https://cockpit-project.org/

### Node-RED
Browser flow editor with community nodes, palette management, projects and Git-backed flows.
Potential Beast direction: Advanced Automation Full Tool. Beast keeps its deterministic managed Signals/Events/Actions builder, while expert users can optionally wire Beast nodes into Node-RED. Candidate custom nodes: Pwnagotchi Event, Doctor Finding, Radio Observation, Hardware Sensor, Beast Action, Notification, Task/Transaction state.
Source: https://nodered.org/

### Home Assistant architecture
Strong precedent for integration/provider/entity/event/action registries.
Potential Beast lesson: external tools/devices become standardized entities/providers rather than each inventing their own subsystem. Useful validation of Beast's Provider/Signal/Event/Action direction.
Source: https://developers.home-assistant.io/docs/architecture/core/

### Binwalk
Firmware-analysis tool that identifies/extracts embedded data and supports entropy analysis.
Potential Beast direction: Firmware Autopsy flow through Inbox + Hardware Bench + Search + optional Home Base reverse-engineering tools.
Source: https://github.com/ReFirmLabs/binwalk

## 3. "Holy shit" combinations to preserve

### Security Time Machine
Pwnagotchi/Bettercap/Kismet capture events + Chronicle + trusted timestamps + GPS/context + Home Base Zeek/Arkime + Search + Broad AI. User asks: "What happened around the time my Wi-Fi went weird last night?" and Beast can correlate radio events, packet/session evidence, known-device changes and system events.

### USB Shape-Shifter / Recovery Cable
Borrow neutral P4wnP1 USB gadget primitives. A supported Beast could dynamically become USB Ethernet + serial + storage or other safe roles, creating a one-cable recovery/provisioning/direct-management path even when Wi-Fi/networking is broken.

### Security Sensor Mesh
Main Beast + external ESP32/M5Stack/Marauder-class devices + future Pico/ESP32 role cartridges + phone + Home Base. Remote nodes become specialized passive senses whose data is normalized through Beast Providers. One handheld Beast can therefore gain physically distributed radio/environment/security awareness.

### Sentinel Homecoming
Field Pwnagotchi returns to Home Base, syncs permitted observations/updates, then optionally changes roles: field hunter/observer -> trusted-network Sentinel using OpenCanary/network monitoring. Same hardware has a meaningful "away" and "home" security personality.

### Self-Auditing Beast
Doctor + Lynis + Known-Good + What Changed? + package inventory + secrets/permissions + update history. Doctor can answer "Did I make this Beast less secure since last week?" using actual deltas rather than generic hardening advice.

### Firmware Autopsy Bench
Owner drops firmware into Inbox -> identify/hash -> Binwalk/strings/entropy -> extract filesystem where appropriate -> Search/index -> optional Home Base Ghidra/Cutter -> link findings back to Hardware Bench device passport. This turns Beast into an approachable hardware/firmware learning console.

### Advanced Flow Forge
Managed Beast Automation remains simple. Node-RED is optional Full Tool for people who want arbitrary visual chaining. Beast can ship a small set of clean nodes/adapters rather than inventing a giant proprietary flow language.

## 4. Pwnagotchi custom-plugins — what should remain a real Pwnagotchi plugin

Jayofelony's current plugin system already provides plugin lifecycle/event hooks and a custom-plugin repository/install model. That makes `custom-plugins` an appropriate place for lightweight behavior tightly coupled to Pwnagotchi events, while large Beast systems remain outside it.

### High-value plugin candidates

1. `beast-bridge`
   - highest-priority candidate.
   - subscribes to Pwnagotchi lifecycle/events and emits normalized structured local events to Beast over a stable local transport.
   - allows Pwnagotchi to remain protected/independently usable while Beast receives handshakes, epochs, AP observations, deauth/association events, peer state and UI/session context.
   - no remote dependency required.

2. `capture-ledger`
   - on capture/handshake, create sidecar metadata: timestamp, interface/radio identity, channel, AP/client identifiers, session id, optional location source/freshness, file hash and duplicate relationship.
   - feeds Beast Capture Intelligence but remains useful to vanilla Pwnagotchi users.

3. `radio-vitals`
   - lightweight monitoring of monitor-interface existence, current channel/hop behavior, packet reception activity, radio resets/failures and basic capture-pipeline health.
   - tiny standalone UI/status possible; richer Doctor interpretation when Beast exists.

4. `plugin-sentry`
   - Pwnagotchi-specific plugin health/status surface: enabled/loaded state, configuration problems, recent plugin exceptions/failures and optional timing/resource hints where technically feasible.
   - complements but does not replace Beast Doctor.

5. `session-stamp-plus`
   - assigns durable session/expedition context to epochs/captures and records concise session facts for later Homecoming/Chronicle.
   - useful even without Beast through JSON/CSV sidecars.

6. `incident-watch`
   - passive event detector for notable local radio conditions such as unusual deauthentication bursts or owner-defined known-network drift indicators.
   - emits events; does not become an offensive automation system.

7. `profile-switcher`
   - named Pwnagotchi plugin/config profiles such as Field, Home, Debug, Low-Power, Display-Test.
   - applies bounded known settings and provides restore/rollback metadata.

8. `queue-status`
   - minimal Pwnagotchi-side indicator for pending Beast/Home Base work such as knowledge/maps/packages/owner-approved artifact sync, without automatically exfiltrating captures or secrets.

## 5. Things that should NOT become Pwnagotchi custom-plugins

Keep these at Beast/platform level:
- Doctor itself;
- Broad AI;
- Search/Knowledge Broker;
- Software/Security Catalog;
- Security Workspace;
- Hardware Bench;
- secrets store;
- maps/location substrate;
- generic automation engine;
- full Linux applications such as Nmap, Wireshark, Kismet, Zeek, Arkime;
- Home Base orchestration;
- System Graph / Transactions / Procedures.

A Pwnagotchi plugin may bridge into these systems, but should not contain them.

## 6. Existing plugin ecosystem lessons

Current Pwnagotchi repositories demonstrate useful patterns:
- default/example plugin hooks include load/UI and radio/Pwnagotchi events;
- GPS uses handshake events to append context;
- current defaults include `custom_plugin_repos` and install support;
- community plugins already add Bluetooth tethering with discovery/setup UX, GPS/map/status features, battery support and session statistics.

Beast should therefore add manifests/schema/provenance/health around the existing model rather than invent a totally separate "Pwnagotchi plugin" mechanism.

## 7. Plugin manifest idea

Without forcing plugin authors to rewrite immediately, Beast can optionally maintain a sidecar manifest/catalog record describing:
- id/name/version/source/license;
- compatible Pwnagotchi/Jayofelony versions;
- required packages/hardware/secrets;
- config keys/types/defaults;
- UI surfaces;
- event hooks used;
- network access / third-party data sharing;
- resource expectations;
- trust/provenance/test status;
- install/update/rollback method.

This would make "have all plugins available and toggle them from the UI" much safer and easier without modifying each plugin's core logic.
