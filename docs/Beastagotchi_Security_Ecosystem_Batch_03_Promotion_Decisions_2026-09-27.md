# Beastagotchi Security Ecosystem — Batch 03 Promotion Decisions

Date: 2026-09-27
Status: owner delegated final selection; security brainstorm is being closed before architecture freeze

## Decision principle

Do not turn every interesting security tool into release scope. Promote durable Beast primitives and major capability families; keep heavyweight/specialist integrations as post-release modules unless they are required for the core architecture.

## Promote into Beast architecture / capability model

### 31. Software X-Ray / SBOM
Belongs. Use mature SBOM/inventory tools as providers rather than inventing package truth. Supports Doctor, What Changed?, support bundles, plugin/repo intake, Home Base analysis, and supply-chain visibility.

### 32. Artifact Trust / Provenance
Strongly belongs. Verification metadata for downloads, packs, plugins, binaries, model assets, updates, and future Beast releases should be first-class. Download complete != trusted artifact.

### 33. Secret Leak Guard
Belongs. Integrate with the existing Secrets policy and support/export/repo workflows. Scan owner-selected bundles/files before sharing or publishing. Findings are advisory and reviewable.

### 36. Logic Analyzer Lab
Belongs in Hardware Bench as a major post-release capability family. Reuse sigrok/PulseView-class tooling and protocol decoders rather than reimplementing analyzers.

### 37. MCU/Firmware Debug & Recovery Bench
Belongs in Hardware Bench. Chip identification, read/backup/hash/compare, JTAG/SWD/flash tooling, and controlled owner-device flashing fit the platform. Writes must be explicit high-risk Transactions with backup/recovery context.

### 39. Digital Forensics Workspace
Belongs primarily as a Home Base capability family. Beast can own intake, hashing, provenance, evidence metadata, timeline links, Search, and handoff while heavy analysis lives off-Pi.

### 43. Bettercap Caplets -> Beast Procedures
Strong architecture fit. Where appropriate, known caplets can be cataloged, explained, parameterized, risk-classified, and wrapped into the same Procedure/Transaction model. Unknown/sensitive caplets are never silently trusted.

### 44. Bettercap Structured Provider
Release-relevant foundation. Pwnagotchi Truth Cockpit, Doctor, radio-vitals, Capture Intelligence, and Security Workspace should consume Bettercap structured state/events/APIs wherever possible instead of parsing console text.

### 45. Security Capability Packs
Strongly belongs. Packs organize optional capability families without turning Jayofelony into a Franken-Kali image. Candidate packs include Wireless Analysis, Web/App Lab, Firmware/RE, Hardware Debug, Forensics, Defensive Sentinel, CAN/Industrial, Mobile Analysis, and Security Range.

## Approve as optional integrations, mostly post-release

### 34. Code Audit Workbench
Useful for Studio, Repo Intake, plugins, scripts, and Home Base. Integrate mature static-analysis tooling; do not treat findings as deterministic truth.

### 35. TLS / Service Security Inspector
Useful Guided authorized-service workflow. Strong post-release Security Workspace integration.

### 38. CAN / Automotive / Industrial Bus Lab
Belongs in Hardware Bench long-term, especially passive capture/decoding and owned bench work. Active transmission remains scoped owner-controlled lab behavior.

### 40. Greenbone/OpenVAS Provider
Useful heavy Home Base vulnerability-management option. Not required for core Beast or release.

### 41. Wazuh Provider
Optional future ecosystem integration for larger owner fleets. Not a Beast dependency.

## Reserve

### 42. Threat Intelligence Platforms
MISP/OpenCTI-class integrations remain reserved until Beast has a concrete owner-facing need. Do not make Beast imitate an enterprise threat-intelligence platform.

## Release boundary

For the upcoming release, only the *foundation* needed to support the security ecosystem should affect architecture/build order:

- structured Bettercap/Pwnagotchi truth contracts;
- the approved Pwnagotchi plugin trio: beast-bridge, capture-ledger, radio-vitals;
- shared Security Scope model;
- shared Security Evidence/Observation/Finding model;
- Tool/Provider manifest metadata and Help/Learn hooks;
- Full Tool / Authorized Lab / Beast-managed / Owner Space classification;
- artifact provenance/trust fields in acquisition/catalog contracts;
- Secrets/redaction contract compatibility;
- Security Capability Pack contract shape.

The heavy integrations themselves do NOT block release.

## Explicit post-release defer

The next planned physical/hardware-hacking/security-crossover research batch is intentionally deferred until post-release development. Preserve the topic, do not continue expanding pre-release scope.

## AI / Doctor / Creature split remains approved

- Broad AI = optional conversational assistant/orchestrator.
- Doctor = deterministic specialist clinician/caretaker with optional AI consultation.
- Creature = living identity/personality/perception/expression system.

Do not collapse these into one subsystem.
