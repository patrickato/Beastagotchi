# Beastagotchi v0.19 — Unified Experience Implementation Plan

## Purpose
v0.19 is the first milestone where Beastagotchi deliberately treats product experience, presentation ownership and modular growth as architecture rather than later polish.

## Non-negotiable continuity
The main page/tab/swipe experience remains first-class. The Home/Beast experience is not replaced by an app launcher. Apps, studios and downloadable Beast Packs deepen the system without erasing the primary pages.

Reference page set:
- Home
- Overview
- Dashboard
- Recon
- Networks
- Spectrum
- Captures
- Map
- Expedition
- Beast
- System

The set may grow or be reorganized as usability testing dictates; it is not an arbitrary hard ceiling.

## Workstream A — visual system
- Shared semantic spacing/touch/animation tokens.
- Stronger hierarchy and fewer repeated diagnostic rectangles.
- A polished reference Home/Beast composition.
- Consistent dialogs, lists, alerts, loading/no-data/error states.
- Structural theme identity preserved.
- Physical 480×320 review after a meaningful visual delta.

## Workstream B — Presentation Broker
Create a small transactional owner broker below Beast UI. Initial owners:
- `pwn-native`
- `korrie-theme-manager`
- `beast-ui`

Handoff is transactional and rollback-aware. The first code milestone provides the state machine and adapter contract; hardware-specific adapters follow after collaboration/API details are agreed.

## Workstream C — web workshop
The physical TFT remains the cockpit. Deep configuration moves toward the responsive local WebUI/PWA:
- themes/layouts
- plugins
- Beast Packs
- updates
- backups/recovery
- logs
- hardware roles
- presentation ownership

Critical data is persisted on-device; the WebUI is never the only copy.

## Workstream D — efficiency
Measure before degrading:
- identify duplicate polling
- suspend non-owning presentation render loops
- centralize canonical telemetry
- profile frame composition and writes
- track per-module resource cost where practical
- keep emergency governor behavior as a safety net rather than normal operation

## Workstream E — public development
- branch/PR workflow
- CI remains mandatory
- continuity ledger and completion matrix stay authoritative
- physical-device validation results are committed as evidence
- collaborator/AI feedback becomes traceable issues or design notes rather than untracked chat decisions

## Current v0.19 foundation
- semantic UX tokens and preserved page model
- transactional Presentation Broker core with rollback tests
- Theme Manager integration specification
- Update Manager and Beast Packs design specifications
- public roadmap issues for UX, presentation ownership, thermal efficiency, companion connectivity, onboarding, updates and continuity
