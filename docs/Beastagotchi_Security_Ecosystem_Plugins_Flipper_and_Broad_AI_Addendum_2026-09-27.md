# Beastagotchi Security Ecosystem / Flipper-Inspired Catalog / Plugins / Broad AI Addendum

**Date:** 2026-09-27
**Status:** owner-approved direction; preserve for architecture refresh before implementation resumes.

## 1. Security deep-dive status

The owner strongly approved the current Security / Pentest / Pwnagotchi deep-dive direction and wants Beast to be pushed right up to the practical/safety boundary wherever a boundary exists.

Use four explicit capability bands when classifying security features:

1. **FULLY BUILDABLE / Beast-managed** — polished first-party support.
2. **AUTHORIZED-LAB BUILDABLE** — active testing features where the scope is owner-controlled / lab / CTF / explicitly authorized.
3. **FULL TOOL / OWNER SPACE** — use the mature expert tool directly; Beast may install/detect/launch/index/import/export/help where appropriate.
4. **HARD BOUNDARY** — Beast does not build polished automation for harmful operations such as indiscriminate compromise, credential theft, malware/persistence, destructive/DoS automation, stealth/evasion against third parties, or mass arbitrary targeting.

The boundary is generally operation/context based, not a blacklist of tool names.

## 2. User-provided external repos and mixed-capability tools

If the owner supplies a repository/tool that contains both ordinary/legitimate capability and functionality beyond the managed boundary:

- Beast may still catalog the project, identify capabilities, document compatibility, manage safe dependencies, expose safe outputs, and integrate clearly legitimate/authorized functionality.
- Beast may provide generic Full Tool / Owner Space launching and ordinary environment integration when appropriate.
- Beast should NOT wire hard-boundary operations into Guided workflows, one-click automation, autonomous chains, or custom wrappers that materially increase misuse capability.
- Mixed tools should be decomposed by capability instead of rejected wholesale when useful safe subsets exist.
- Importing output from a mature tool can remain separate from automating the sensitive operation that produced it.

This preserves technical truth without turning Beast's polished first-party layer into indiscriminate offensive automation.

## 3. Flipper Zero ecosystem concept worth borrowing

Flipper's app/catalog/custom-firmware ecosystem provides a useful product pattern:

- a strong base platform;
- community apps/tools;
- curated packs;
- firmware distributions that select useful additions;
- per-app metadata and compatibility;
- easy install/update/remove;
- optional hardware modules;
- customization/asset packs;
- full developer path.

Momentum explicitly pursues a feature-rich but stable/customizable model, including third-party apps and configurable menus. Unleashed exposes community plugin/base/extra packs and app sources. The official Flipper Apps Catalog supports categories, search/filter, version/changelog/repository metadata, install/update/delete, and hardware-required apps.

Beast should borrow this *ecosystem pattern*, not blindly copy Flipper code or categories.

## 4. Beast Catalog presentation model

For every major domain (security, SDR, hardware bench, maps, media, dev tools, etc.) use a hierarchy such as:

### Featured / Recommended
Curated high-value tools for the domain and current hardware.

Selection should be based on:
- maturity and maintenance;
- compatibility with current Beast hardware/OS;
- usefulness;
- upstream reputation;
- integration quality;
- resource cost;
- licensing;
- whether Guided experience exists;
- broad real-world adoption / canonical status where determinable.

Do not fake exact popularity/download rankings when no trustworthy metric exists.

### Installed / Ready
What the current Beast can use now.

### Available / Needs software / Needs hardware
Capabilities that can be obtained.

### Home Base / Full Tool
Heavy programs or GUI applications better run on another machine while remaining integrated with Beast.

### All Tools A-Z
After the curated top section, expose the complete compatible catalog alphabetically with search/filter.

This matches the owner's desired "best/top tools first, then everything else alphabetically" model without requiring dubious popularity claims.

## 5. Kali-derived Security Catalog taxonomy

Kali's current tool/metapackage taxonomy is useful as a reference universe. Beast can map/adapt categories such as:

- Information Gathering
- Vulnerability Analysis
- Web Security
- Password Auditing
- Wireless / 802.11
- Bluetooth
- RFID/NFC
- SDR
- Reverse Engineering
- Hardware Security
- Fuzzing
- Crypto / Stego
- Forensics
- Reporting
- VoIP
- Database Security
- Exploitation (primarily lab/full-tool when active exploitation is involved)
- Sniffing / Spoofing (split by safe/authorized/full-tool operation)
- Post-Exploitation (mostly lab/full-tool, not generic Beast automation)
- CTF / Labs

Kali's `kali-tools-top10` currently includes Aircrack-ng, Burp Suite, Hydra, John the Ripper, Metasploit Framework, NetExec, Nmap, Responder, sqlmap, and Wireshark. This list can inform a "Canonical / Common Security Tools" section, but Beast should not blindly expose every operation of every tool as Guided automation.

## 6. Programs are not plugins

Do not call large mature programs such as Nmap, Wireshark, Kismet, John, Ghidra, etc. "plugins" merely because Beast can integrate them.

Preferred taxonomy:

### Core subsystem
Long-lived platform capability: Doctor, Search, Security Workspace, System Graph, Task Center, etc.

### Provider / Adapter
Normalizes an external source/tool into Beast truth/events/capabilities. Examples: Kismet Provider, Nmap result adapter, Bettercap provider, gpsd provider.

### Full Tool integration
Detect/install/launch/configure/import/export/help bridge for a mature external program.

### Guided Experience
Beginner/intermediate task-oriented interface on top of a mature tool or primitive capability.

### Procedure / Procedure Pack
Reusable bounded workflow composed from existing actions/tools.

### Knowledge / Help Pack
Docs, tutorials, examples, manpages, local reference material, learning content.

### Decoder / Data Pack
Protocols, signatures, vendor databases, frequency datasets, dissectors, parsers, etc.

### Theme / Expression Pack
Creature/UI presentation assets and behavior styling.

### Plugin
A comparatively lightweight extension that hooks Beast events/capabilities/UI/Providers and adds a distinct behavior without warranting a full standalone program.

Plugins are best when they are genuinely extension logic, not wrappers around whole external applications.

## 7. Plugin re-evaluation direction

As the platform has grown, some ideas previously called plugins belong elsewhere.

Strong plugin candidates are things like:
- event-driven creature reactions;
- small data enrichers;
- alert/notification hooks;
- lightweight sensor/provider adapters;
- compact workflow helpers;
- export/import format adapters;
- specialty overlays/widgets;
- small integrations with specific services/devices.

Things that should usually NOT be plugins:
- Doctor;
- Search;
- Software Catalog;
- Security Workspace;
- Hardware Bench;
- major maps/radio workspaces;
- full Nmap/Wireshark/Kismet/Ghidra/etc. engines;
- core Provider/resource arbitration;
- Transactions/Actions/Procedures;
- primary AI routing.

These belong to core systems, Providers, Full Tool integrations, Experiences, or Procedure/Knowledge Packs.

## 8. Built-in Help / Learn integration

Beast should make the real tool's own documentation easy to access.

A generic Help Adapter may support, per tool as available:
- `--help`
- `-h`
- tool-specific `help` subcommands
- `man` pages
- `info`
- installed documentation packages
- upstream docs / README
- local offline Knowledge Catalog copy
- current web docs when permitted

The raw authoritative help should remain available exactly as supplied by the program. Beast may add:
- beginner explanation;
- examples for clearly safe/authorized workflows;
- searchable option index;
- "what does this flag mean?" explanations;
- link/handoff into the real tool.

For tools with mixed or sensitive operations, exposing their ordinary built-in documentation/full-tool environment is distinct from Beast writing new one-click harmful automation. Beast should not build Guided wrappers for hard-boundary operations.

The owner explicitly values this because users should be able to learn directly from the real program and graduate into expert use.

## 9. Internet / Search as a learning substrate

Broad Internet access and federated Search reinforce the learning model:

- tool documentation;
- manuals/manpages;
- upstream GitHub/docs;
- tutorials;
- bug/issue research;
- community references;
- authoritative security advisories.

Search results remain provenance-labeled and external instructions do not become machine authority by themselves.

## 10. Broad AI vs Doctor — architecture correction

Earlier discussion briefly leaned toward "Doctor is the AI front door." The owner clarified a better separation.

### Doctor stays Doctor
Doctor remains the deterministic specialist/caretaker/diagnostic-and-repair system already designed:
- Machine Census;
- probes;
- Known-Good / What Changed?;
- evidence and confidence;
- repair/rollback/verification;
- collective/fleet knowledge;
- presentation as an Experience.

Doctor may optionally use an AI copilot/provider internally for synthesis, but Doctor identity and function do not become dependent on a conversational model.

### Broad AI becomes the optional conversational Beast assistant
A separate optional system-wide AI surface should support the natural conversational pattern the owner described:

- "What's monitor mode?"
- "Can my adapter do it?"
- "Show me packets."
- "What does this beacon mean?"
- "I want Wireshark."
- "Why is my GPS broken?"
- "Can Beast do X?"

The broad AI can call/consult:
- Doctor;
- Search;
- Abilities;
- Software Catalog;
- Security Workspace;
- Hardware Bench;
- Actions/Transactions/Procedures;
- Home Base;
- Knowledge Catalog;
- Full Tool integrations.

The AI is therefore a natural-language orchestrator/teacher/assistant over Beast, while Doctor remains the specialist diagnostic system.

The AI provider can live on:
- Pi when an appropriate small local model exists;
- paired phone;
- Home Base / local PC / GPU machine;
- self-hosted LLM endpoint;
- optional cloud provider.

No AI provider is required for core Beast function.

## 11. "Just work" AI behavior

For users who install the AI package and do not want to configure model plumbing:

- default to **Automatic** provider selection;
- choose among permitted providers based on task/capability/resource/privacy;
- fall back gracefully to deterministic Beast/Doctor/Search results when no model is available;
- do not require the user to know which model handled a prompt;
- keep machine authority in Beast Actions/Transactions/Procedures rather than model shell access.

## 12. Flipper-style community ecosystem implications

Potential future Beast ecosystem may contain:
- Apps / Full Tools
- Plugins
- Providers
- Experiences
- Procedure Packs
- Knowledge Packs
- Data/Decoder Packs
- Theme/Expression Packs
- Security Tool Collections
- Hardware Profiles
- Bench Projects

Each should carry metadata such as:
- author/source;
- license;
- version;
- compatible boards/architectures;
- required hardware;
- required services/packages;
- dependencies/conflicts;
- capability provided;
- resource cost;
- trust/provenance;
- Guided support;
- Full Tool availability;
- Home Base compatibility;
- install/update/remove state.

This borrows the best of Flipper's app/firmware ecosystem and Kali's capability taxonomy while preserving Beast's situationally-composable architecture.

## 13. Reuse-first rule remains controlling

> Do not build something merely because we can. If a mature tool already does it well, integrate/wrap/orchestrate it. Build Beast-native code where the missing value is integration, presentation, orchestration, lifecycle, safety, discovery, learning, or Guided use.

This is especially important in security, where mature tools already contain enormous protocol and analysis expertise.
