# Beastagotchi Sandbox Direction

**Date:** 2026-09-26
**Status:** owner-selected direction for the pre-implementation sandbox discussion; approved to revisit and implement later with guided setup

## Goal

Create a practical Windows-hosted Beastagotchi sandbox that moves the large majority of software development, UI work, destructive testing, simulated hardware scenarios, and replayable debugging away from the physical Raspberry Pi while preserving the Pi as final hardware truth.

## Owner implementation preference

The owner is willing to try the selected sandbox architecture when the project reaches the appropriate implementation phase, provided setup and use are guided step-by-step and the user-facing workflow stays simple.

This means:
- WSL2 should be taught/operated directly with clear setup and daily-use instructions.
- Docker is acceptable to try if BeastLab hides most Docker-specific complexity behind simple commands/controls.
- Beast-native virtual hardware inside WSL is selected and should not require learning a separate virtualization stack.
- SSH/copy-paste/manual file transfer to the physical Pi remains an acceptable and useful bridge for real hardware truth.
- QEMU remains out of scope unless the owner explicitly reopens it later.

Do not require the owner to become proficient in Docker, virtualization, or infrastructure tooling merely to use the Beast Sandbox.

## Selected architecture

### 1. WSL2 Beast Sandbox — required

WSL2 is the primary everyday Beastagotchi development environment on Windows.

Expected uses include Beast Core, Beast Studio, services, databases, Packs, Procedures, Transactions, Doctor logic, progression, configuration, plugins, UI rendering, virtual 480x320 display/touch preview, logs, and normal tests.

The owner is willing to learn and use this layer directly with guided setup and simple operating instructions.

### 2. Docker — accepted if hidden behind simple BeastLab controls

Docker is acceptable for disposable/destructive test environments provided the owner is not required to become a Docker administrator.

Preferred UX is simple BeastLab commands or controls such as clean-test, failed-update-test, bad-pack-test, reset-test-environment, etc. Docker-specific implementation detail should remain underneath this interface where practical.

Primary purpose: reproducible temporary Beast instances that can be deliberately broken, migrated, corrupted, rolled back, and discarded without risking the physical Pi.

### 3. QEMU — explicitly not part of the selected direction

The owner does not want to spend time learning or operating QEMU. QEMU should therefore not be a required sandbox dependency and should not be reintroduced by default.

If a future concrete problem proves that ARM/Pi emulation would provide unique value that cannot be obtained reasonably through WSL, Docker, virtual providers, record/replay, CI, or SSH-connected physical validation, it may be discussed again with the owner. Until then, it is out of scope.

### 4. Beast-native virtual hardware inside WSL — selected

Virtual hardware should be implemented as Beastagotchi development/simulation providers running inside the WSL sandbox, not as chip-level hardware emulation.

Examples may include virtual radio, TFT/display, touch, GPS, power, thermal, storage, USB, GPIO, sensors, and other future providers.

These providers feed the same canonical Signals/Events/Capabilities/contracts used by real providers while preserving provenance that clearly marks simulated truth as simulated.

This enables deterministic failure scenarios such as interface disappearance, Bettercap stall, undervoltage, USB reset, storage read-only, sensor failure, overheating, display failure, etc. without requiring actual physical faults.

### 5. SSH-connected real Pi — first-class complementary path

The owner is comfortable copying/pasting commands and transferring information to/from the Pi over SSH. The sandbox should use this instead of unnecessary virtualization complexity whenever real hardware truth is required.

A future BeastLab remote-hardware bridge may use SSH to gather probes, capture diagnostics, run bounded test commands, export incident bundles, or validate hardware-specific behavior on the real Pi while analysis/testing remains in WSL.

This is complementary to virtual hardware rather than a replacement for it:

- virtual providers = deterministic safe simulation;
- SSH Pi = actual hardware observation/validation.

### 6. Record/replay — strongly selected

Real Pi incidents should eventually be capturable into portable, privacy-aware bundles containing relevant canonical Signals, Events, capability changes, service transitions, Doctor evidence, transaction/history context, and other selected diagnostics.

These incident bundles can be copied from the Pi and replayed inside the WSL sandbox repeatedly for debugging and regression testing.

Initial workflow may use manual SSH/SCP/FileZilla-style transfer; automatic synchronization is not required to gain value.

## Preferred overall flow

Windows 11
-> WSL2 Beast Sandbox (primary development)
-> Docker test cells (optional disposable/destructive testing)
-> Beast-native virtual hardware providers (simulation inside WSL)
-> Record/replay of real incidents
-> SSH-connected physical Pi for real hardware evidence and targeted validation
-> Physical Pi as final hardware truth

## Product/UX principle

The owner should operate the **Beast Sandbox**, not the underlying infrastructure.

Complex technology such as Docker should be hidden behind understandable BeastLab commands or controls wherever practical. The sandbox should follow the same product principle as Beastagotchi itself: complex machinery underneath, understandable controls on top.

## Explicitly rejected requirement

Do not require QEMU or ARM/Pi emulation for normal sandbox operation.
