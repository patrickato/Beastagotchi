# Beastagotchi Security Ecosystem Batch 02 — Promotion Decisions

Date: 2026-09-27
Status: approved design-selection record; implementation remains paused until security deep-dive reconciliation completes.

## Promoted into the Beast architecture/capability plan

The following Batch 02 ideas are promoted because they either provide a durable platform primitive or unlock a major capability family.

### Security capability providers / full-tool integrations

11. Nuclei integration — promote as a vulnerability-check provider for scoped/authorized assessments. Guided mode should explain template purpose, expected traffic, intrusiveness and evidence. Raw/full Nuclei remains available.

12. ZAP + mitmproxy — promote as Application Traffic Lab / Web Security providers. Guided traffic inspection and owner/lab testing; full tools preserved.

13. MobSF — promote as Home Base mobile-app analysis provider. Pi handles intake/hash/context; heavy analysis happens remotely/Home Base.

14. Ghidra + Cutter/Rizin — promote as reverse-engineering Full Tool providers, preferably Home Base. Beast handles artifact intake, indexing, metadata and handoff.

15. Proxmark3 + ChameleonUltra — promote as RFID/NFC hardware family under Hardware Bench/Security. Guided owner/lab workflows plus Full Tool.

16. KillerBee + Kismet — promote as Zigbee/802.15.4 capability family. Passive observation first; active research confined to authorized-lab/full-tool paths.

17. Ubertooth — promote as specialist Bluetooth hardware Provider.

18. GreatFET + Facedancer — promote as USB Hardware Lab capability family. Strong educational/lab value, especially USB enumeration/emulation and hardware learning.

19. OpenCanary/Cowrie/T-Pot deception ladder — promote as defensive Sentinel family, scaled by hardware. OpenCanary suitable for small boards; heavier platforms Home Base/server only.

20. Suricata — promote as Home Base/offline-PCAP IDS/NSM provider feeding normalized findings back to Beast.

21. osquery + YARA-X + Sigma — promote as defensive inspection/detection building blocks. Use mature query/rule languages rather than inventing Beast-specific replacements.

23. Security Range — promote. Use intentionally vulnerable labs such as Juice Shop/WebGoat/CTF-style targets in isolated environments for Guided learning and practice.

### Core platform primitives — high priority

24. Universal Tool Adapter Manifest — PROMOTE HIGH PRIORITY. Each external tool should have structured metadata for detection, installation, help invocation, inputs/outputs, hardware/resource requirements, permissions, launch path, supported architecture, and Guided/Lab/Full Tool boundary.

25. Assessment Scope Passport — PROMOTE HIGH PRIORITY. A single session scope object should define authorized hosts/APs/devices/lab targets and be reusable across tools.

26. Security Evidence Bus — PROMOTE HIGH PRIORITY. Preserve raw evidence while also normalizing observations/findings/events into shared Beast types for Search, Chronicle, Doctor, AI and Reporting.

27. Gadget Dock / Hardware Capability Portal — PROMOTE HIGH PRIORITY. Attached security/hardware devices should be identified, qualified and translated into Abilities.

28. Security Lab Capsules — PROMOTE HIGH PRIORITY. Reusable isolated training/lab packages containing target, isolation, objective, reset/snapshot, help material and cleanup.

29. Broad AI as Tool Tutor — PROMOTE. Broad AI remains distinct from Doctor and Creature. It retrieves real documentation/context and orchestrates allowable Beast actions; Doctor remains specialist diagnostic authority.

30. Repo Intake / Capability Harvest Pipeline — PROMOTE HIGH PRIORITY. Existing repositories should be systematically evaluated for reusable safe capabilities, providers, parsers, help systems, hardware support, licensing, Home Base roles and boundary-sensitive functionality.

## Reserved / optional rather than architecture obligations

22. Velociraptor — RESERVE as Home Base/DFIR inspiration and optional Full Tool integration. Its artifact concept is worth studying, but Beast should not attempt to become a full endpoint-DFIR platform by default.

## Pwnagotchi custom-plugin decisions

Approved high-priority custom-plugin candidates remain:

1. `beast-bridge`
2. `capture-ledger`
3. `radio-vitals`

Additional plugin ideas remain candidates only and should not be promoted automatically. Any new Pwnagotchi plugin must justify why the behavior belongs inside the Pwnagotchi event/plugin runtime instead of Beast Core.

## Architectural consequence

Security is not a pile of programs. The target model is:

**one Scope -> many mature Tools -> one Evidence model -> one Search/History -> one Help/Learn system -> optional Broad AI -> Doctor when something is broken.**

The Pi remains usable on Zero 2 W / Pi 4 / Pi 5 by moving heavy analysis to Home Base or another provider when needed.
