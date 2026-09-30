# Beastagotchi Guided Software Pattern

**Date:** 2026-09-26  
**Status:** strong candidate platform pattern; preserve for Capability Expansion and final reconciliation

## Core idea

> **Make complex software approachable without hiding, crippling, or replacing the real software.**

Beastagotchi may present task-focused, beginner-friendly, preconfigured experiences over complicated applications/packages while still preserving direct access to the complete underlying program for owners who want it.

This is not SDR-specific. It is a reusable platform pattern.

## User-facing levels

A compatible software capability may expose one or more of:

1. **Focused / Guided** — accomplish one clear job with sane defaults and minimal required knowledge.
2. **Advanced Guided** — reveal more controls and explanation without abandoning Beast's task-oriented workflow.
3. **Full Tool** — launch/use the complete underlying application or native interface when feasible.
4. **Owner Space / raw path** — manual CLI/config/root access remains available outside Beast's managed UX.

Not every program requires all four layers.

## What the guided layer may do

- detect required hardware/software/capabilities;
- resolve dependencies;
- choose known-good defaults;
- generate configuration;
- start/stop required services;
- claim/arbitrate shared hardware;
- load location/profile-specific data;
- provide tutorials/contextual help;
- translate expert terminology into task-oriented language;
- expose useful visualization;
- provide saveable presets;
- hand off to the full application;
- restore/suspend shared resources cleanly afterward.

The guided layer should **compose existing software**, not unnecessarily reimplement mature software engines.

## Potential domains to explore

Examples only; not approved feature commitments:

- SDR/radio suites;
- GNU Radio flowgraphs / decoder stacks;
- mapping/GIS tools;
- packet/network analysis tools;
- Bluetooth tooling;
- serial/GPIO/I2C/SPI hardware utilities;
- storage/backup tools;
- media/audio tools;
- system monitoring/administration tools;
- developer/build/test tools;
- offline reference/search/documentation tools;
- sensor platforms;
- future AI/model tooling;
- other complex Linux/Pi software discovered during Capability Expansion.

## Integration principle

> **Guided does not mean restricted.**

The owner retains access to complete installed software and the normal Linux machine. Beast's focused UX is an additional doorway.

## Capability composition

Guided experiences should reuse Providers/Capabilities/Tools/Procedures rather than own hardware independently.

This supports the related principle:

> **Overlapping, not conflicting.**

Where two experiences require incompatible exclusive ownership of one device/resource, Beast should arbitrate or sequence the claim and explain the conflict. Where they can share data/capabilities, they should.

## Dependency awareness

A guided experience should be able to explain:

- available now;
- hardware missing;
- package/library missing;
- optional enhancement missing;
- downloadable/queueable;
- incompatible version/architecture;
- full application installed/not installed;
- what the user gains by adding the missing dependency.

Where practical, Acquisition Queue/Home Base can obtain missing resources according to owner policy.

## Beginner-learning pattern

For programs where education adds value:

> **show -> explain -> let user change -> visualize/experience result -> restore/recommend baseline**

Tutorial content may pull from Field Library/Search/manuals and remain available offline where practical.

## Anti-goals

- do not remove expert/full-program access;
- do not recreate giant mature applications merely to make them look Beast-native;
- do not force every program into an oversimplified UI;
- do not duplicate configuration/truth unnecessarily;
- do not hide important limitations from beginners;
- do not pretend a guided preset is the only valid way to use the underlying software.

## Where to revisit

- Capability Expansion Pass — identify programs/packages that benefit from this pattern.
- X+Y=>Z jam — combine guided experiences with hardware/context/search/tutorials/creature behaviors.
- Final reconciliation — decide whether this becomes a formal architecture/product contract and what implementation substrate it needs.
