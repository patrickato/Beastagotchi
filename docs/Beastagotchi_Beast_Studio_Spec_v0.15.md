# Beastagotchi Beast Studio Specification v0.15

## Product direction
Beast Studio is the primary end-user authoring environment for Beastagotchi. It must stay cleaner than the complexity it exposes: immediate exact-device preview, reversible drafts, real telemetry, and progressive disclosure rather than a wall of controls.

## v0.15 spatial composer
The built-in Dashboard is no longer a fixed six-slot surface. Instruments are declarative objects on the same 12x8 logical grid used by the physical 480x320 compositor. Studio can add/remove instruments, bind canonical scalar telemetry, select renderers, edit labels, move, resize, hide/show and change z-order. The overlay on the browser preview manipulates the same geometry rendered on the TFT.

Every production instrument remains tied to canonical Beast state. Missing sources render unavailable; Studio never substitutes decorative values.

## User-created Boards
A Board is a named user composition backed by the same live-instrument model. Boards are registered dynamically into the App universe as `board:<id>` destinations. They are therefore not constrained by the fixed high-frequency main carousel and may be included in Context Decks.

Examples:
- Field Ops
- Thermals
- Radio Lab
- GPS Trip
- Dock / Home Base
- SDR instruments when that capability exists

This is the first production step toward arbitrary user-created pages. Future Board/widget classes will add purpose-built structured-data widgets, text/media, maps, lists, plugin surfaces and rule/context-driven switching.

## Safety / resource policy
The preferences validator retains a high corruption/DoS guard based on the logical grid size. This is not a product UX limit. Normal usability is controlled by screen area, renderer cost and available Pi resources rather than an arbitrary page-count policy.

## Still planned
- resize/move/edit existing built-in page widgets, not only Dashboard/Boards;
- structured-data widgets (AP lists, maps, captures, services, plugin cards);
- per-widget thresholds/smoothing/history windows/formatters;
- layers, grouping, lock/alignment/snapping and multi-select;
- context/rules-driven Board activation;
- Try On Device with timed rollback;
- import/export/community packs and dependency manifests.
