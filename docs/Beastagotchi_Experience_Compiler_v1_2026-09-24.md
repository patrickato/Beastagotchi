# Beastagotchi Experience Compiler v1
## 2026-09-24

Status: read-only planner implemented in v0.19.

Implementation: `beastcore/experience_compiler.py`.

## Purpose

Experience DNA describes intent. The Experience Compiler resolves that intent against the actual platform and the currently implemented Experience surface.

v1 intentionally stops before mutation.

Inputs:
- Experience ID / Experience DNA;
- Platform Profile compute/display class;
- current context such as default/night/incident;
- the shared Dependency & Capability Resolver;
- actual registered Experience page coverage.

Outputs:
- identity-preserving constrained/compact/full/enhanced variant;
- selected visual/layout/motion/creature/Doctor intent;
- required and optional capability evidence;
- implemented/preferred/missing page coverage;
- preview readiness;
- production-navigation readiness;
- explicit non-mutation policy.

## Safety / ownership boundary

The compiler does **not**:
- install packages;
- start/stop services;
- select capability providers;
- write preferences;
- activate Packs;
- fabricate an unimplemented page;
- silently substitute another Experience.

It is a planning/resolution layer only.

## Capability reuse

Experience requirements use the existing shared `DependencyCapabilityResolver` rather than creating a second Experience-only hardware/dependency system.

Current abstract capability examples used by built-in Experiences include:
- `location.position`;
- `radio.wifi.monitor`;
- `system.telemetry`;
- `power.battery.telemetry`;
- `display.primary`;
- `storage.writable`.

Most current first-party Experience capabilities are optional enrichments rather than hard blockers. Atlas can still exist without GPS; it must simply remain truthful about the missing location capability.

## Page coverage

The compiler receives actual renderer coverage from the Experience renderer registry.

Current examples:
- Atlas implements Home + Recon but still lacks preferred Map + Expedition translations;
- Observatory implements Home + Spectrum but still lacks preferred Recon;
- Habitat implements Home + Beast but still lacks preferred Expedition;
- Forge/Monolith currently implement Home only.

Therefore these Experiences are previewable but are **not yet declared production-navigation complete**.

This avoids the old failure mode where an unimplemented Experience page silently falls back to generic geometry and loses identity.

## Resource adaptation

The compiler consumes Platform Profile rather than board-name whitelists.

Constrained/compact/full/enhanced variants alter density/motion/resource guidance while preserving Experience identity.

An incident/recovery context may elevate Doctor visibility without changing the Experience family.

## Current integration

- Experience DNA: implemented;
- platform variant resolution: implemented;
- common DependencyCapabilityResolver adoption: implemented;
- actual renderer/page coverage input: implemented;
- central trusted Experience renderer registry: implemented;
- Beast Studio compiled Experience browser/preview: implemented;
- Core-owned live compiler publication: implemented;
- Studio consumes Core-published plans rather than re-probing capability truth: implemented;
- Mission Packs may carry validated declarative `experience_dna`, `experience_policy` and reusable component references: implemented;
- Pack Experiences compile through the same resolver and may reference an already-registered trusted Beast renderer without injecting Pack rendering code: implemented;
- truthful render-target planning: implemented. Current first-party Experience renderers are explicitly native only for the 480×320 `reference` target; 800×480 scaling is not called native responsiveness;
- bounded `TRY ON TFT` transaction planning with mandatory automatic rollback: implemented;
- `TRY ON TFT` physical execution: deliberately disabled;
- production TFT Experience ownership/selection: deliberately disabled.

The compiler/Studio path remains non-mutating: it does not install dependencies, choose providers, write preferences, persist Experience selection or claim TFT ownership.


## Next

1. Return primary Gate 1 attention to actual generated visual fidelity and obtain owner off-screen acceptance of the renderer.
2. Add real native Scene/reflow variants for non-reference targets instead of treating compatibility scaling as responsiveness.
3. After off-screen acceptance, connect the already-planned bounded TRY ON TFT transaction to the physically validated Presentation Broker/display-handoff executor.
4. Run the reference Pi/TFT readability, touch, QR, glare, smoothness, thermal and framebuffer acceptance session with automatic rollback.
5. Enable persistent production Experience selection only after the physical proof succeeds.
