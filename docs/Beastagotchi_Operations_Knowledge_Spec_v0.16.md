# Beastagotchi Operations & Knowledge Specification v0.16

## Purpose
v0.16 turns Beastagotchi further outward from a Pwnagotchi UI into a manageable field-computer platform. The milestone preserves the protected Pwnagotchi/Bettercap engine while making system state, incidents, recovery, offline knowledge, optional runtimes and external-display capability first-class Beast concepts.

## Implemented platform surfaces
- Whole-device Overview built only from canonical live state.
- Operations Center and dependency/service topology.
- Task Center backed by durable jobs.
- Universal Search across Field Library, BeastDex, Capture Vault, events and canonical telemetry.
- Field Library indexing for text/Markdown/config/reference files; PDF/EPUB/ZIM are catalogued and reserved for optional richer extractors.
- Black Box durable incidents with state/event snapshots and matching offline runbook references.
- Backup Center with SQLite online snapshots, configuration copy, SHA-256, 0600 archives and bounded retention.
- Known display-owner conflict detection for Theme Manager/Fancygotchi class plugins before physical Beast display handoff.
- Optional Container Center: appears only when Docker/Podman already exists.
- Optional Beast Operator surface: appears only when local AI/model capability actually exists.
- Read-only display and desktop/browser capability discovery; Command Center appears when an external DRM/HDMI display is actually connected.
- Connectivity Center distinguishes route availability from proven Internet reachability.

## AI / Beast Operator privilege model
The intended AI authority tiers are Observer, Operator, Maintainer and time-limited Administrator Session. Powerful actions are allowed by adding typed Action Broker operations, not by handing an always-on model unrestricted root shell. Every mutation is intended to be plan-able, audited and recoverable.

## Display direction
480x320 remains the reference/minimum physical target, not an architectural ceiling. Display discovery now exposes framebuffer geometry and DRM outputs so future HDMI/DSI/capacitive targets can use responsive layouts and explicit display roles. Optional desktop/browser capability is detected but never started automatically merely because it exists.

## Integrity rule
No production instrument may invent measurements. Overview, topology, connectivity, AI availability, containers, display capability, incidents and library counts reflect real collected/persisted state or explicitly state UNKNOWN / NOT INSTALLED / UNAVAILABLE.
