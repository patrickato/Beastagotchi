# Beastagotchi Doctor Presentation Decision

**Date:** 2026-09-26  
**Status:** owner-approved direction

## Decision

> **Build Doctor completely as a functional diagnostic/repair system first. Doctor presentation is a replaceable/skinnable Experience layer.**

Doctor's diagnostic reasoning, probes, cases, repairs, Global knowledge, progress, evidence, Transactions and verification must not depend on a live animated creature/avatar.

### TFT
- functionality and touch/readability first;
- compact live status/progress;
- heart/vitals waveform remains a strong visual motif;
- personality/animation is optional and resource-budgeted;
- Doctor must remain fully usable with decorative animation disabled.

### WebUI / phone / richer surfaces
- may use larger visual system graphs, case timelines, Global knowledge, animation and creature-linked presentation;
- may skin the active Beast as Doctor or use another theme/presentation style;
- all surfaces operate on the same underlying Doctor case/state.

### General principle

> **Doctor is the capability. The visual Doctor is an Experience.**

This lets Beastagotchi theme, animate, simplify or restyle Doctor later without coupling the medical/diagnostic function to one character or visual treatment.

## Remaining Doctor deep-dive item

Presentation fork is considered resolved for this discussion phase.

The primary remaining Doctor topic before Capability Expansion is:

- source/evidence reputation;
- Global fleet learning confidence;
- how official provenance, empirical success, hardware/software similarity, recency and local patient evidence combine into repair recommendations and automation thresholds.
