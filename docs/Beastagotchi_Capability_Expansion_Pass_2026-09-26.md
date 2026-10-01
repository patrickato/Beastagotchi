# Beastagotchi Capability Expansion Pass

**Date:** 2026-09-26  
**Status:** ACTIVE interactive jam / research pass  
**Purpose:** identify genuinely new capabilities, tools, software, hardware integrations and cross-layer experiences Beastagotchi can provide because it sits on top of Raspberry Pi/Linux/Pwnagotchi/Bettercap plus the Beast architecture.

## Explicit rule

This pass is **not** primarily about more logs, dashboards, telemetry pages or diagnostics. Those may support a capability, but they do not count as the capability itself.

Core question:

> **What new things can Beastagotchi actually DO?**

## Layer model

1. physical Pi / board / attached hardware;
2. Linux/kernel/system services;
3. networking/radios/USB/Bluetooth/GPIO/SPI/I2C/serial/sensors;
4. Pwnagotchi + Bettercap;
5. Beast Core/contracts;
6. Tools/Procedures/Providers/extensions;
7. UI/Experiences/creature;
8. phone/desktop/Home Base/local network/other devices;
9. optional Internet/external services.

At every layer ask:

- what can we access?
- what can we add?
- what useful tools/packages/libraries/services already exist?
- what hardware expands capability?
- what can Beast make easier through Guided Software?
- what dependencies are needed and how can Beast resolve/queue them?
- what should be managed vs merely compatible vs Owner Space?
- what becomes possible when this combines with another layer?

## Principles already carried into this pass

- Guided Software: Focused / Advanced Guided / Full Tool / Owner Space where appropriate.
- Overlapping, not conflicting: one provider may power many experiences; arbitrate true resource conflicts.
- Perception <-> Expression: hardware/providers may give the Beast new senses; displays/audio/LED/haptics/etc. may give it new ways to express.
- Home Base may acquire/sync heavy resources and queued user work.
- Federated Search and Doctor knowledge may supply tutorials/manuals/dependencies.
- Owner keeps full access to underlying Linux/full applications.
- Capability discovery should clearly explain available / missing hardware / missing software / optional enhancement / incompatible state.
- Capability expansion should not be artificially narrowed just because every possible owner-installed workflow is not Beast-managed.

## Pass format

Run interactively. For each cluster:

- IDEA / capability;
- why it is possible;
- real software/hardware candidates;
- guided vs full-tool experience;
- cross-layer tie-ins;
- dependencies/resource conflicts;
- owner riff/questions;
- status: candidate only until final reconciliation.

## First exploration cluster

Start with **hardware/radio/sensor expansion** because it demonstrates the capability model strongly, then broaden across Linux utility, field/offline, local-network, hardware bench, media/input/output, automation, companion-device and other layers.
