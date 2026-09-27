# Beastagotchi Current Discussion Queue — 2026-09-27 Security Deep-Dive

**Status:** canonical current discussion order. Implementation remains paused.

## Completed before the security addendum

1. Doctor deep-dive / jam.
2. Capability Expansion Pass.
3. Cross-layer X+Y=>Z jam.
4. AI role/capability discussion.
5. Monster / breeding / perception / expression jam.
6. First APPROVE / MODIFY / RESERVE / REJECT reconciliation.

## Important correction

The first reconciliation is now **provisional**, not final-final. The owner intentionally reopened pre-build design for one additional major domain: Security / Pentest / Pwnagotchi capability expansion.

This is not a random rewind. The security pass is an explicit inserted stage before architecture contracts and implementation order are frozen.

## Current stage — Security / Pentest / Pwnagotchi Deep-Dive

Completed/current discussion batches include:

- Wi-Fi / Pwnagotchi / Bettercap capability deep-dive.
- Managed vs Authorized-Lab vs Full Tool / Owner Space vs Hard-Boundary classification.
- Capture Intelligence / Handshake Inspector / PMKID awareness / provenance / deduplication / quality verification.
- Radio qualification, multi-radio roles, channel coverage and Security Doctor integration.
- Authorized assessment sessions, network topology, safe discovery, remediation and retest concepts.
- Kismet / Wireshark / Nmap / Kali-space integration direction.
- Security Software Catalog and Flipper-style curated collections.
- Mature-tool reuse rather than cloning.
- Broad AI separated from Doctor; Doctor remains specialist/deterministic clinician.
- Pwnagotchi custom-plugin role clarification.
- Current direct-example research: Bjorn, P4wnP1 A.L.O.A., Bruce, ESP32 Marauder, OpenCanary, Lynis, Zeek, Arkime, RaspAP, Cockpit, Node-RED, Home Assistant patterns, Binwalk and current Pwnagotchi plugin ecosystems.

## Current immediate sub-pass

1. Direct real-world projects/repos we can borrow from, integrate, or use as architectural precedent.
2. Identify "holy shit / genius" combinations that become possible when Beast Core, Pwnagotchi, Doctor, Home Base, Security Workspace, Hardware Bench, Search, AI, Chronicle, Providers and external tools are composed.
3. Re-evaluate Pwnagotchi `custom-plugins` specifically and propose new plugin candidates that remain useful to vanilla Pwnagotchi while becoming richer under Beastagotchi.
4. Clarify Broad AI vs Doctor ownership before freezing the AI architecture.

## Still to do before implementation resumes

1. Finish the Security Ecosystem Matrix category-by-category.
2. Classify major tools/repos as:
   - FULLY BUILDABLE;
   - AUTHORIZED-LAB BUILDABLE;
   - FULL TOOL / OWNER SPACE;
   - HARD-BOUNDARY OPERATIONS.
3. Record board suitability: Zero 2 W / Pi 4 / Pi 5 / Home Base.
4. Reconcile security additions back into the earlier APPROVE / MODIFY / RESERVE / REJECT record.
5. Rewrite architecture contracts, capability/tool ledgers, roadmap and migration/build order.
6. Resume implementation in meaningful, test-backed tranches.

## Standing product direction

- Keep Pwnagotchi/Bettercap real and visible; do not sanitize away the security identity.
- Beginner -> Guided -> Advanced Guided -> Full Tool -> Owner Space.
- Do not rebuild mature tools merely because we can.
- Internet/Search/Knowledge should help users understand and reach authoritative tool documentation.
- Security tooling should be easy to discover and learn, without removing the real expert path.
- Pwnagotchi `custom-plugins` remain a genuine plugin layer; larger Beast systems and third-party applications are not mislabeled as plugins.
- Preserve owner sovereignty and ordinary Linux access.
