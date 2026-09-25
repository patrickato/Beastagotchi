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
- common resolver adoption: implemented at compiler/library level;
- renderer coverage input: implemented;
- central Experience renderer registry: implemented;
- Beast Studio schema exposes Experience DNA + renderer coverage;
- paired Studio Experience preview endpoint: implemented;
- Core-owned live compiler publication: not yet implemented;
- production TFT Experience ownership/switching: deliberately disabled;
- Experience Pack compiler input: not yet implemented.

## Next

1. Have Beast Core publish compiled Experience plans using the same long-lived DependencyCapabilityResolver instance already shared by Plugins/Packs.
2. Feed compiler plans to Studio rather than re-probing capabilities there.
3. Add Pack-defined Experience DNA/component references.
4. Add responsive target/Scene variants.
5. Add preview/TRY ON TFT transaction flow.
6. Enable production Experience selection only after Gate 1 off-screen acceptance and rollback behavior are proven.