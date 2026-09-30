# Beastagotchi Audio / Visual / I/O — Live Preview Correction

**Date:** 2026-09-27  
**Status:** owner correction to the Audio / Visual / I/O capability-expansion cluster

## Correction

The prior Audio / Visual / I/O pass incorrectly categorized the following as future/later features:

- asset preview;
- real theme/animation preview.

The owner correctly noted that **live preview is already part of the Beastagotchi WebUI direction**.

Therefore the actual requirement is not "add preview later". The requirement is:

> **Preserve the existing WebUI live-preview capability and make its preview fidelity trustworthy.**

## Updated interpretation

### NOW — WebUI live preview exists as part of the planned product

The WebUI/Studio experience should be able to preview Beast UI/themes/assets/layouts/animations as part of normal creation/customization work.

This is not a new post-release capability.

### NOW — preview fidelity is the quality gate

The important engineering problem is ensuring that preview output corresponds closely to the real Beast runtime.

Where possible, preview should reuse:
- the same assets;
- the same layout definitions;
- the same animation/state definitions;
- the same theme variables;
- the same capability/presentation contracts;
- the same rendering logic or a deliberately compatible rendering path.

The preview must not be presented as exact when it is only an approximation.

### Exact-render provenance remains important

When a preview differs from physical Pi output because of browser/runtime/display differences, Beast should be able to identify the rendering context rather than silently treating all screenshots as equivalent.

This ties back to the existing visual-regression / exact-render-provenance direction.

### Physical Gate 1 remains authoritative

WebUI preview quality does not replace physical-device validation on the reference Raspberry Pi + 3.5-inch TFT.

The preview is intended to make iteration fast and trustworthy; final hardware validation remains a separate gate.

## Owner direction

The owner is otherwise satisfied with the Audio / Visual / Camera / Media / Expression / I/O cluster and explicitly notes that capabilities can continue to be changed or added later or during implementation.
