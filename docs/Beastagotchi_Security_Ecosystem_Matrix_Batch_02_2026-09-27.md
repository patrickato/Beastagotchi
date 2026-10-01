# Beastagotchi Security Ecosystem Matrix — Batch 02

Date: 2026-09-27
Status: pre-build security/pentest deep-dive; implementation still paused

## Locked from prior discussion

- Units 1–10 from the direct-project research pass are owner-approved.
- Broad AI / Doctor split is retained:
  - Broad AI = optional conversational assistant/orchestrator.
  - Doctor = deterministic specialist clinician/caretaker.
  - Creature = living identity/personality.
- Pwnagotchi plugin priorities currently approved as high-value candidates:
  1. `beast-bridge`
  2. `capture-ledger`
  3. `radio-vitals`
- Earlier plugin candidates 4–8 are not automatically promoted; prune/replace as stronger ideas emerge.

## Security capability labels

Every tool/integration should be classified at operation level, not by brand/tool name alone:

- **FULLY BUILDABLE** — Beast can provide a polished first-party managed experience.
- **AUTHORIZED-LAB BUILDABLE** — active behavior can be managed when the user explicitly defines owned/authorized lab scope.
- **FULL TOOL / OWNER SPACE** — Beast can install/detect/launch/import/export/help, but does not wrap sensitive operation into first-party automation.
- **HARD-BOUNDARY OPERATION** — Beast does not implement/automate the harmful operation itself.

A single tool may legitimately span more than one class.

---

# Units 11–30

## 11. Nuclei — template-driven vulnerability assessment

**Why it matters:** Nuclei is a modern template-based scanner with a large community-maintained YAML template ecosystem covering HTTP, DNS, TCP, SSL, file, JavaScript and other protocols.

**Beast fit:**
- FULLY BUILDABLE for explicit owner/authorized target assessment and non-destructive detection workflows.
- AUTHORIZED-LAB BUILDABLE for more intrusive validation against deliberate lab targets.
- FULL TOOL / OWNER SPACE for arbitrary template execution.

**Beast opportunity:** a Nuclei Provider can ingest template metadata and findings into the common Security Evidence model. The Catalog can distinguish low-risk discovery/configuration templates from intrusive/exploit-style templates instead of treating every Nuclei template equally.

**Strong idea:** Beast can display a template as a human-readable security check before execution: what it tests, protocols touched, expected impact, evidence produced, and target scope.

Source: https://github.com/projectdiscovery/nuclei

## 12. ZAP + mitmproxy — owned application/API traffic lab

**Why it matters:** OWASP ZAP provides a pluggable automation framework; mitmproxy provides interactive/scriptable HTTP(S)/WebSocket interception and replay.

**Beast fit:**
- FULLY BUILDABLE for an owner's own application/API, debugging, passive analysis and explicit test-lab traffic.
- AUTHORIZED-LAB BUILDABLE for active scanning of a scoped training/owned target.
- FULL TOOL / OWNER SPACE for unrestricted proxy features.

**Beast opportunity:** "Application Traffic Lab" where a user points their phone/browser/app at a Beast/Home Base proxy, then learns request/response structure, cookies, headers, TLS, APIs and security findings from real traffic.

Sources:
- https://www.zaproxy.org/docs/automate/automation-framework/
- https://docs.mitmproxy.org/stable/

## 13. MobSF — mobile app autopsy

**Why it matters:** MobSF performs static and dynamic Android/iOS/Windows-mobile application security analysis and exposes APIs/CLI integration.

**Beast fit:**
- FULLY BUILDABLE for owner-supplied APK/source/static analysis.
- Home Base preferred for heavy analysis/dynamic environments.

**Potential experience:**
`APK dropped into Beast Inbox -> hash/identify -> MobSF on Home Base -> permissions/components/certificates/endpoints/findings -> Search + Broad AI explanation -> optional Full Tool.`

This opens a Mobile Security facet without making the Pi do everything locally.

Source: https://github.com/MobSF/Mobile-Security-Framework-MobSF

## 14. Ghidra + Cutter/Rizin — reverse-engineering workbench

**Why it matters:** Ghidra is a full software reverse-engineering suite; Cutter provides a GUI-oriented reverse-engineering environment powered by Rizin.

**Beast fit:**
- FULLY BUILDABLE around ingestion, identification, hashing, strings, metadata, architecture detection, indexing, project handoff and learning.
- Full reverse engineering runs primarily as FULL TOOL / Home Base.

**Beast opportunity:** Firmware Autopsy graduates naturally into "Open in Ghidra" / "Open in Cutter" instead of us rebuilding a disassembler/decompiler.

Sources:
- https://github.com/NationalSecurityAgency/ghidra
- https://github.com/rizinorg/cutter

## 15. Proxmark3 + ChameleonUltra — RFID/NFC hardware family

**Why it matters:** Proxmark3 is a broad LF/HF RFID analysis platform; ChameleonUltra provides RFID/NFC read/write/emulation capabilities and documented host protocols.

**Beast fit:**
- FULLY BUILDABLE for hardware detection, firmware/version status, tag identification, signal/protocol learning, inventory and owner-tag analysis.
- AUTHORIZED-LAB BUILDABLE for emulation/testing of tags/cards the user owns or is authorized to test.
- FULL TOOL / OWNER SPACE for sensitive cloning/emulation operations.

**Beast opportunity:** these become Providers in Hardware Bench / Security Workspace rather than isolated gadgets.

Sources:
- https://github.com/RfidResearchGroup/proxmark3
- https://github.com/RfidResearchGroup/ChameleonUltra

## 16. KillerBee + Kismet Zigbee — 802.15.4/Zigbee awareness

**Why it matters:** KillerBee provides IEEE 802.15.4/Zigbee sniffing/decoding and active research primitives; Kismet can provide multi-radio datasource integration.

**Beast fit:**
- FULLY BUILDABLE for packet capture, device observation, protocol decoding and inventory.
- AUTHORIZED-LAB BUILDABLE for bounded active Zigbee research against owned test devices.
- FULL TOOL / OWNER SPACE for arbitrary injection/fuzzing.

**Beast opportunity:** Zigbee becomes another real Beast sense instead of a standalone exotic tool.

Source: https://github.com/riverloopsec/killerbee

## 17. Ubertooth — Bluetooth radio specialist

**Why it matters:** Ubertooth provides BLE sniffing and some Bluetooth Classic observation capabilities.

**Beast fit:**
- FULLY BUILDABLE for hardware onboarding, passive BLE observation/capture and packet handoff.
- FULL TOOL / OWNER SPACE for specialist Bluetooth research.

**Beast opportunity:** Device Passport should recognize an Ubertooth automatically and expose BLE abilities without the user first learning its Linux tooling.

Source: https://github.com/greatscottgadgets/ubertooth

## 18. GreatFET + Facedancer — USB Hardware Lab

**Why it matters:** GreatFET is a general USB/hardware tool; Facedancer allows Python-defined USB device emulation and USB protocol research.

**Beast fit:**
- FULLY BUILDABLE for device identification, descriptors, enumeration education, owner-device emulation and safe USB protocol analysis.
- AUTHORIZED-LAB BUILDABLE for fuzzing/test-host experimentation in an isolated lab.
- FULL TOOL / OWNER SPACE for unrestricted USB proxy/emulation behavior.

**Holy-shit combination:** Hardware Bench + Facedancer + Beast Sandbox = a guided USB protocol classroom where the user can create a harmless virtual USB device, watch enumeration happen, alter descriptors and immediately see host behavior.

Sources:
- https://github.com/greatscottgadgets/greatfet
- https://github.com/greatscottgadgets/facedancer

## 19. OpenCanary + Cowrie + T-Pot — deception ladder

**Why it matters:**
- OpenCanary is lightweight enough for a Pi.
- Cowrie emulates/proxies SSH/Telnet interactions for defensive observation.
- T-Pot is a multi-honeypot platform with much heavier storage/RAM requirements and belongs on Home Base/server-class hardware.

**Beast fit:**
- FULLY BUILDABLE as defensive Sentinel/deception features on owner networks.
- Scale by hardware: OpenCanary on Pi; richer Cowrie scenarios where appropriate; T-Pot on Home Base.

**Holy-shit combination:** Beast can have a *deception capability ladder*. A Zero 2 W can still be a tiny canary while a Home Base becomes a rich honeypot/visualization backend.

Sources:
- https://github.com/thinkst/opencanary
- https://github.com/cowrie/cowrie
- https://github.com/telekom-security/tpotce

## 20. Suricata — network security sensor

**Why it matters:** Suricata provides IDS/IPS/NSM, PCAP analysis, protocol logging and rule-based detection.

**Beast fit:**
- FULLY BUILDABLE for offline PCAP analysis and defensive monitoring on owner-controlled traffic.
- Home Base preferred for sustained high-volume inspection.

**Beast opportunity:** field captures can be queued home, analyzed by Suricata, then returned as structured incidents/findings linked to the original Beast session.

Source: https://suricata.io/features/all-features/

## 21. osquery + YARA-X + Sigma — host/security knowledge primitives

**Why they matter:**
- osquery exposes OS state as SQL-like tables.
- YARA-X provides pattern-based file/content matching.
- Sigma provides portable detection-rule semantics for log/event detections.

**Beast fit:**
- FULLY BUILDABLE for Beast self-observation, defensive inspection, local-file scanning and Home Base investigation.

**Holy-shit combination:** Doctor can use osquery-style state plus Known-Good; Search/Incident analysis can use YARA-X/Sigma-like rules; the user gets rich defensive capability without us inventing every query/detection language.

Sources:
- https://github.com/osquery/osquery
- https://github.com/VirusTotal/yara-x
- https://github.com/SigmaHQ/sigma

## 22. Velociraptor — Home Base DFIR / fleet investigation

**Why it matters:** Velociraptor is an endpoint discovery/security/forensics platform with a strong artifact/query model.

**Beast fit:**
- primarily FULL TOOL / Home Base architectural inspiration/integration.
- Potential provider/export path for advanced owner fleets rather than duplicating a DFIR platform inside Beast.

**Key lesson:** artifact-based reusable investigations are closely aligned with Doctor Probe Blocks and Security Evidence Packs.

Source: https://github.com/Velocidex/velociraptor

## 23. Juice Shop + WebGoat + CTFd — real guided cyber school

**Why they matter:** Juice Shop and WebGoat are deliberately vulnerable applications designed for training; CTFd provides a customizable CTF/challenge platform.

**Beast fit:**
- FULLY BUILDABLE when isolated as deliberate training targets.

**Holy-shit idea:** **Beast Security Range**.
The user chooses a lesson, Beast/Home Base launches an isolated vulnerable target, automatically creates a scoped assessment session, shows the lesson/hints, provides appropriate Guided tools, records evidence/progress, then destroys/resets the lab afterward.

This is where Beast can teach much more aggressive techniques safely because the target is explicitly ours and intentionally vulnerable.

Sources:
- https://github.com/juice-shop/juice-shop
- https://github.com/WebGoat/WebGoat
- https://github.com/CTFd/CTFd

## 24. Universal Tool Adapter Manifest

**Recommendation: APPROVE as platform architecture.**

Every mature external tool should be describable without bespoke UI code for basic integration. Candidate manifest fields:
- tool id/name/version/provider;
- source/license;
- install methods and supported architectures;
- board suitability (Zero 2 W/Pi4/Pi5/Home Base);
- binary/service/API detection;
- `--help`/man/info documentation methods;
- inputs/outputs and machine-readable formats;
- hardware requirements;
- privilege requirements;
- estimated resource cost;
- managed operations and their safety/context classes;
- Full Tool launch command/surface;
- parser/import adapters;
- Doctor health checks;
- update/rollback method.

This is how Beast can support hundreds of Linux/security tools without writing hundreds of completely independent integrations.

## 25. Assessment Scope Passport

**Recommendation: APPROVE.**

Security Workspace gets a first-class scope/session object defining what the user says they own/are authorized to test:
- target hosts/CIDRs/domains/APs/devices;
- lab/container/VM identifiers;
- optional notes/engagement name;
- allowed active test class;
- start/end context;
- evidence/results belonging to that session.

Tools do not each invent their own target list. Nmap/Nuclei/ZAP/Wi-Fi/BLE/etc. can consume the same scoped context where appropriate.

This is not presented as magical proof of legal authorization. It is an operational boundary and organization mechanism.

## 26. Security Evidence Bus

**Recommendation: APPROVE.**

Instead of every tool producing isolated text:

`Tool -> raw artifact + normalized Observation/Finding/Evidence -> Chronicle/Search/Doctor/AI/Report`

Examples:
- Nmap service -> Service Observation
- Nuclei match -> Security Finding
- Pwnagotchi capture -> Capture Evidence
- Suricata alert -> Incident Signal
- MobSF result -> Application Finding
- YARA-X match -> File Finding
- Kismet sighting -> Radio Observation

Always retain provenance and raw output where appropriate. Normalization never replaces the source evidence.

## 27. Gadget Dock / Hardware Capability Portal

**Recommendation: APPROVE conceptually.**

Hardware Bench should recognize security hardware families such as:
- Flipper-class devices;
- ESP32 Marauder/Bruce devices;
- Proxmark3;
- ChameleonUltra;
- Ubertooth;
- GreatFET/Cynthion-class USB tools;
- RTL-SDR;
- supported Zigbee radios;
- logic analyzers;
- Pico/ESP32 role devices.

Plugging one in should answer:
`What is it? -> Is firmware/client available? -> What can Beast do with it? -> Which Abilities become READY?`

This generalizes the strongest part of the Flipper ecosystem concept to *any* compatible hardware ecosystem.

## 28. Security Lab Capsules

**Recommendation: APPROVE concept, implementation later.**

A Capsule is a reproducible disposable training environment containing:
- target container/VM/device definition;
- network isolation;
- known scope;
- lesson/objective;
- reset/snapshot behavior;
- expected signals/findings;
- optional tools/help links;
- cleanup.

Possible targets: Juice Shop, WebGoat, DVWA, intentionally vulnerable services, owner-built Pico/ESP32/IoT training targets.

This is the safest and most educational place to push Guided security operations right up to the hard line.

## 29. Broad AI as Tool Tutor / Orchestrator

**Recommendation: APPROVE with current AI/Doctor split.**

Broad AI can converse exactly as the owner described:
- "What's monitor mode?"
- "Can my adapter do it?"
- "Show me."
- "What does this Nmap option mean?"
- "Why did that lab check fail?"
- "Open the raw packets."

The AI retrieves actual tool help/docs and Beast truth, then invokes existing Beast Actions/Tools where allowed. It does not replace Doctor and does not fabricate tool semantics.

## 30. Repo Intake / Capability Harvest Pipeline

**Recommendation: APPROVE as development ecosystem concept.**

When an owner/developer provides a GitHub repo, Beast/Studio development tooling should be able to characterize it:
- language/build system;
- license;
- releases/activity;
- architectures;
- dependencies;
- hardware interfaces;
- CLI/help/API surfaces;
- input/output formats;
- network behavior;
- secrets/config;
- resource footprint;
- candidate Providers/Actions/Full Tool handoffs;
- operation-level security boundary classification.

Output should be an integration proposal, not automatic trust/execution.

This formalizes the current "80% useful / 20% restricted" repo discussion: integrate usable portions deeply while leaving disallowed operations unwrapped.

---

# Hardware tier principle

Do not fragment Beast into different products. The same Catalog/Abilities system adapts dynamically:

- **Zero 2 W:** lightweight local Pwnagotchi/plugins/providers; external/Home Base heavy tooling.
- **Pi 4:** broader local analysis and services, still offload heavyweight RE/SIEM/mobile work.
- **Pi 5:** larger local working set; still no assumption heavy tools must run locally.
- **Home Base/PC/server:** Ghidra/Cutter, MobSF, Arkime/Zeek/Suricata at scale, T-Pot, heavy indexing, AI, larger audit jobs, lab VMs/containers.

The UI should say why a capability is Home Base preferred rather than simply hiding it.

---

# Pwnagotchi custom-plugin refinement

## Locked high-priority three

### 1. `beast-bridge`
Normalized Pwnagotchi event bridge upward to Beast.

### 2. `capture-ledger`
Durable metadata/provenance/duplicate linkage for Pwnagotchi captures.

### 3. `radio-vitals`
Lightweight radio/capture-pipeline functional health evidence.

## New stronger candidates to discuss later

### 4. `known-network-watch`
Passive owner-defined known-network fingerprint/history checks: BSSID/security/channel/capabilities drift, suspicious same-SSID variants, unusual management-frame conditions. Emits observations only; richer analysis belongs in Beast Security Workspace.

### 5. `homecoming-queue`
Pwnagotchi-native durable queue marker for owner-approved artifact/metadata handoff when a trusted Beast/Home Base connection later becomes available. No silent third-party upload; policy-controlled destinations only.

### 6. `peer-journal`
Lightweight persistent history of actual Pwnagotchi peer encounters/bonds/session facts. Useful to vanilla Pwnagotchi and can feed Beast Chronicle/Creature relationships when Beast is present.

Do not build more plugins merely to move existing Beast subsystems downward. Prefer the smallest Pwnagotchi-specific hook that remains independently useful.

---

# Strongest new cross-layer conclusions

1. **Security tooling needs one shared scope object, one evidence model and one help/discovery pattern.** That is what makes dozens/hundreds of mature tools feel like one product.
2. **External gadgets become Providers/Abilities, not isolated brands/apps.** This may be the broadest Flipper-inspired idea yet.
3. **Home Base is not just storage/update infrastructure; it is the heavy security workstation attached to a pocket Beast.**
4. **Training labs/CTFs let Beast teach genuinely advanced security practice without weakening the boundary for arbitrary third-party targets.**
5. **Repo Intake makes the open-source security world an expandable capability reservoir instead of a fixed curated list.**
6. **Broad AI becomes the natural-language tutor/orchestrator across this ecosystem; Doctor stays the evidence-based specialist.**
