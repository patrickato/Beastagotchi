# Beastagotchi Security Ecosystem Matrix — Batch 03

Date: 2026-09-27
Status: discussion candidates; not all promoted yet.

## Units 31–45

31. Software X-Ray / SBOM — Syft + Trivy/Grype-class tooling. Generate package/software inventories and SBOMs for Beast itself, repositories, filesystems, archives and containers. Feed Doctor, Software Catalog, update impact, vulnerability correlation and support bundles. Heavy scans may run on Home Base.

32. Artifact Trust / Provenance — Sigstore/Cosign-style signature and attestation verification. Beast should verify signed downloads/artifacts where upstream provides signatures or attestations, record provenance, and expose verification status in Software Catalog / Acquisition Queue / Doctor evidence.

33. Secret Leak Guard — Gitleaks/Trivy secret scanning. Scan owner-selected repositories/files or Beast-generated support/export bundles for accidentally exposed credentials/tokens. Integrate with Secrets policy; never silently upload findings. Useful before sharing logs, support bundles or publishing plugins.

34. Code Audit Workbench — Semgrep and language-specific linters/static analyzers. Apply to Beast code, plugins, owner scripts, downloaded repos and Studio workspaces. Findings are advisory evidence, not automatic truth. Strong fit for Repo Intake pipeline.

35. TLS / Service Security Inspector — testssl.sh and similar mature TLS scanners. Guided owner/lab workflow for HTTPS, MQTT, mail/STARTTLS and other TLS-enabled services; machine-readable results normalized into Security Findings with remediation and re-test.

36. Logic Analyzer Lab — sigrok/PulseView/libsigrokdecode. Hardware Bench should detect supported low-cost logic analyzers and provide Guided captures/decoding for UART, I2C, SPI and other protocols, then hand off to full PulseView/sigrok tools. Strong educational and Doctor-hardware value.

37. MCU / Firmware Debug & Recovery Bench — OpenOCD + flashrom where hardware/platform permits. Guided chip identification, adapter detection, read/backup/verify workflows, configuration help and recovery planning. Writes/flashes are explicit high-risk Transactions with strong warnings and backups; Full Tool remains available.

38. CAN / Automotive / Industrial Bus Lab — Linux SocketCAN + can-utils. Passive capture, decode, log, replay in controlled benches, interface qualification and protocol learning. Active generation/testing belongs only in owner-controlled bench/lab contexts. Integrates with Hardware Bench and Evidence Bus.

39. Digital Forensics Workspace — The Sleuth Kit/Autopsy + Volatility 3 + Timesketch. Beast handles evidence intake, hashing, metadata, timelines and handoff; Home Base runs heavier disk/memory/timeline analysis. Preserve originals and provenance; do not claim legal chain-of-custody certification.

40. Vulnerability Management Provider — Greenbone/OpenVAS on Home Base. Assessment Scope Passport feeds authorized targets; Greenbone performs heavy vulnerability management; findings return to Beast Evidence Bus, remediation, Chronicle and re-test. Not suitable as a default Pi workload.

41. Home Base Security Operations Provider — Wazuh-class optional integration. Useful for owners who want file-integrity, inventory, event and endpoint telemetry across Home Base / lab systems. Not part of core Beast; optional provider consuming/producing normalized findings/events.

42. Threat Context Provider — MISP/OpenCTI-class optional Home Base provider. Beast should not become an enterprise threat-intelligence platform, but can ingest selected structured indicators/taxonomies/context for owner assets, incident enrichment and learning. Reserve unless a concrete use case justifies it.

43. Bettercap Caplets -> Beast Procedures. Bettercap caplets are reusable scripted command sequences. Beast should be able to discover/catalog caplets, describe their declared behavior, dependencies and risk class, and where appropriate wrap safe/authorized caplets as managed Procedures. Sensitive caplets remain Full Tool/Owner Space; Beast should not blindly execute unknown caplets as trusted code.

44. Bettercap REST/Event Provider. Prefer structured Bettercap APIs/events over scraping terminal output. Normalize session stats, packet counters, modules, endpoint observations and other useful data into Beast Signals/Events/Evidence. This strengthens Pwnagotchi Truth Cockpit and Doctor without modifying Bettercap core.

45. Security Capability Packs. Build curated install/integration bundles by job rather than by arbitrary distro categories: Wireless Analysis, Web/App Lab, Firmware/RE, Hardware Debug, Forensics, Defensive Sentinel, CAN/Industrial, Mobile App Analysis, Security Range. Packs install manifests/providers/help/integrations, not necessarily every heavyweight tool on the Pi. Hardware and board suitability remain explicit.

## Emerging principles

- Security posture should include the Beast's own software supply chain, not only external targets.
- Hardware Bench and Security Workspace overlap strongly around firmware, logic, buses, USB, MCU and radio hardware.
- Home Base is the natural heavy-analysis tier for DFIR, vulnerability management, mobile analysis, full reverse engineering and SIEM-class services.
- Bettercap already has reusable caplets and REST/event surfaces; Beast should consume those mature interfaces rather than repeatedly patching Bettercap or parsing console text.
- Every dangerous write/flash/bus-transmit operation must be explicit, scoped, logged and recoverable where technically possible.
