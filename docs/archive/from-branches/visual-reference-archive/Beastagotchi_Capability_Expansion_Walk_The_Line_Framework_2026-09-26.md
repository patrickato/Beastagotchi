# Beastagotchi Capability Expansion — “Walk the Line” Framework

**Date:** 2026-09-26  
**Status:** approved discussion rule for the remaining capability-expansion pass; not a promise to implement every example  

## Core intent

During Capability Expansion, do **not** artificially narrow the project to only the safest/most conventional tools simply because Beastagotchi sits on top of Pwnagotchi, Bettercap and Linux.

At the same time, do not turn Beast into an indiscriminate automation engine for harmful or unauthorized activity.

Use the following distinctions when evaluating software, hardware, integrations and workflows:

1. **Beast-managed** — Beast can directly ship/support/integrate the workflow with normal safety, authority, rollback and UX contracts.
2. **Compatible / integrated** — Beast can detect, configure, launch, visualize, provide status, expose dependencies, or consume outputs from an external/full tool without reimplementing it.
3. **Owner Space** — the owner may install/use software manually on their own Linux machine; Beast should coexist cleanly, preserve raw/full-tool access, and expose generic capability/provider hooks where appropriate.
4. **Documented gap / external capability** — Beast may explain that a capability exists, what class of software/hardware provides it, what dependencies/interfaces are involved, and why it is not included in the managed workflow.
5. **Do not automate/facilitate** — where a specific managed workflow would materially cross into unsafe, unauthorized, destructive, privacy-invasive, or otherwise inappropriate operation, Beast does not provide a purpose-built automated path. This does not require pretending the underlying Linux ecosystem does not exist.

## Owner sovereignty

Preserve the existing platform rule:

> **Beastagotchi is an open platform with a managed core, not a locked appliance. Unsupported does not mean forbidden. Owner-controlled extensions may coexist with Beast, but Beast only guarantees what remains inside its managed contracts.**

Guided Software is an additional doorway, never a replacement for the full program or Owner Space.

## How to apply this to every capability cluster

For each tool/domain discovered during Capability Expansion, explicitly consider:

- what Beast can safely manage directly;
- what full upstream applications should remain available;
- what outputs/providers Beast can integrate even when it does not own the application;
- what can be made beginner-friendly through Guided Software;
- what belongs in Owner Space;
- what capability gaps should be documented rather than silently omitted;
- what hardware/software dependencies are needed;
- what the user can still add/build/download independently;
- whether Beast can detect that external capability and expose generic integration hooks afterward.

## Applying the framework to RF / SDR

### Strong Beast-managed receive-side candidates

- AM/FM broadcast reception;
- spectrum/waterfall viewing;
- ADS-B aircraft tracking;
- AIS vessel tracking;
- weather-radio reception where available;
- wireless sensor decoding such as rtl_433-compatible devices;
- satellite reception/processing where practical;
- location-aware receive presets;
- RF beginner/tutorial experiences;
- recording/visualization and field/session integration where lawful and appropriate.

### Full-tool access retained

Where installed and feasible, owners may still launch full applications such as:

- SDR++;
- GQRX;
- GNU Radio;
- SDRTrunk;
- SatDump;
- other compatible SDR/radio applications.

Beast may provide focused Guided experiences above them without hiding the complete tool.

### Transmit-capable radio

Transmission is a distinct capability class from receive.

Potential legitimate contexts exist (for example appropriately licensed amateur-radio operation, permitted digital/mesh radio, or owner-controlled test hardware), but transmission requires separate hardware, band/licensing/regulatory/authority awareness and should not inherit permission merely because a receive workflow exists.

During expansion, Beast may:

- recognize transmit-capable hardware/software;
- explain requirements and dependencies;
- provide educational/reference information;
- integrate status/configuration where appropriate;
- consider managed transmit workflows only where the use is clearly bounded, owner-controlled and lawful.

Do not globally pretend transmit capability does not exist; do not automatically treat every possible transmit action as a normal SDR preset.

## Pwnagotchi / network-security tooling

Because the base platform already includes Pwnagotchi/Bettercap and runs on general-purpose Linux, Capability Expansion should honestly inventory adjacent network/security tooling and integration possibilities.

The scan may cover categories such as:

- network discovery/inventory;
- packet capture/analysis;
- Wi-Fi adapter qualification and monitor-mode tooling;
- Bluetooth inspection;
- protocol analysis;
- local lab/testing tools;
- defensive/network-health utilities;
- password/audit tooling in authorized contexts;
- security reference/education;
- full upstream applications that owners may choose to install.

For each, classify managed vs compatible vs Owner Space vs documented gap. Do not erase the category simply because some uses can be dual-use.

## “Fill the gap” principle

When Beast itself should not provide a specific managed workflow, the user should still be able to understand:

- what capability class is missing;
- what external software/hardware commonly provides it;
- required dependencies/interfaces;
- whether Beast can detect/use generic outputs afterward;
- where Owner Space/custom providers/extensions can fill the gap.

This preserves openness without making every possible external workflow a first-party Beast feature.

## Presentation principle

Do not burden every normal user with legal/safety prose on every screen.

Instead:

- make capability class and source clear;
- surface important limitations at the point they matter;
- explain why a managed path stops where it stops;
- keep full technical detail available;
- preserve Owner Space and expert/full-tool access.

## Rule for the remainder of Capability Expansion

Every cluster should be explored broadly first and filtered second.

> **Ask “what is possible/useful?” before asking “what becomes a first-party managed Beast workflow?”**

That distinction should prevent premature self-censorship while still keeping implementation and automation responsible.
