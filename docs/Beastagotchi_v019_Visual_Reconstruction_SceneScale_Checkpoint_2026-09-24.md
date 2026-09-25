# Beastagotchi v0.19 Visual Reconstruction Checkpoint — Scene Scale + Semantic Dirtiness
## 2026-09-24

Branch: `v0.19-unified-experience`

Gate 1 remains **ACTIVE — VISUAL RECONSTRUCTION**. This checkpoint is source/off-screen evidence only; it is not physical TFT acceptance.

## What changed

### 1. Flagship concept creature now actually fills its scene

The concept-fidelity renderer assigned a large stage to Classic/Cyberpunk/Black-Ice creature art, but `_paste_concept_creature()` used Pillow `thumbnail()`. `thumbnail()` only shrinks and never enlarges, so the compact embedded concept raster remained near native size and visually read as a small pasted icon.

The compositor now performs explicit aspect-preserving resize into the assigned scene region, supports spatial edge feathering and retains the low-cost luminance pulse.

Flagship creature regions are also enlarged/rebalanced so the Beast owns meaningful visual space before the live HUD begins.

A regression test now requires the Classic concept creature to occupy materially scene-scale bounds rather than regress to native-thumbnail dimensions.

### 2. SceneRuntime now has signal-aware dirtiness

`SceneRuntime` remains a semantic registry/performance lens and still does not poll telemetry or draw pixels.

It now additionally tracks partial canonical state snapshots and exposes:
- changed canonical signal keys;
- dirty semantic layer IDs;
- de-duplicated dirty layer bounds;
- explicit handling of ambient vs live vs interaction vs static/protected layers.

Missing keys in a partial snapshot are not treated as changes.

This enables the intended future flow:

`Signal change -> semantic layer dirty -> redraw semantic region -> framebuffer dirty-row write`

without confusing decorative ambient animation with telemetry changes.

### 3. Engine integration

`BeastUI._compose()` now feeds the current canonical state snapshot into SceneRuntime immediately after beginning the page Scene. Motion-proof/runtime telemetry therefore carries truthful changed-signal/dirty-layer metadata alongside render-cost and compositor-cache telemetry.

## Off-screen evidence

The deterministic multi-frame Home proof from CI was manually inspected before and after the creature-scale fix.

Before:
- Classic/Cyberpunk creature art remained close to compact native raster size despite a large scene allocation;
- the interface still read as instrumentation with a small mascot pasted into it.

After:
- Classic creature occupies most of the left visual field;
- Cyberpunk creature now anchors the neon city/perspective scene;
- live values remain runtime-drawn and separate from decorative scene activity;
- no physical-acceptance claim is made.

The remaining visible limitation is now primarily source-art fidelity: enlarging the compact embedded raster exposes its low native resolution. This is a better-defined next problem than further rearranging the UI.

## Validation

Run 461: green after concept-creature scale/import correction.

Run 464: green after SceneRuntime state binding.

Run 465: green after scene-scale regression coverage; **436 tests passed**.

Subsequent roadmap/gate-document synchronization is documentation-only and does not change the underlying visual evidence.

## Next visual block

1. Improve flagship source-art fidelity using project-owned concept-derived assets or equivalent high-fidelity Pack-ready visual sources.
2. Keep artwork as a Scene layer; never bake live telemetry into the asset.
3. Add semantic dirty-region use to the bounded Visual Runtime/framebuffer path only after the current registry evidence remains stable.
4. Extend the accepted scene language from Home into Recon/Spectrum/Expedition rather than converting every page into the same dashboard geometry.
5. Regenerate captured-real-state evidence and seek owner off-screen visual acceptance before any physical TFT staging.

## Truth boundary

Decorative particles, glows, skyline, perspective grids, scan passes and creature luminance are visual activity only. They must remain marked decorative/ambient and must never imply measured RF/GPS/system activity.