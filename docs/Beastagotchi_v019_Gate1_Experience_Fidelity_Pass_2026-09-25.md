# Beastagotchi v0.19 — Gate 1 Experience Fidelity Pass
## 2026-09-25

Branch: `v0.19-unified-experience`

Status: **off-screen renderer fidelity improved; owner acceptance still pending.**

This checkpoint does not close Gate 1 and does not authorize physical TFT staging.

## Why this pass happened

The first five Experience proofs were structurally different, but several still visibly carried
the old dashboard/card language. The owner had already rejected that direction as materially
below the earlier polished concept intent.

This pass evaluated the actual CI-rendered 480×320 PNGs rather than judging source structure
alone.

## Changes retained after pixel review

### Atlas

Before:
- dominant field canvas was correct;
- four repeated rounded telemetry cards remained on the right.

After:
- the field canvas bleeds across the body;
- telemetry is a narrow ruled field-notebook margin rather than cards;
- expedition state is a full-width bottom ledger;
- compass/GPS/RF observations live inside the field composition.

### Forge

Before:
- five rounded subsystem modules made the machine bay read like a dashboard.

After:
- one continuous chassis owns the body;
- compute is a physical gauge/memory rail;
- radio is an integrated channel/frequency deck;
- power is an embedded train with truthful unavailable state;
- a shared machine bus physically connects the subsystems and Beast core;
- I/O ports and Doctor/Governor read as mounted mechanisms rather than floating widgets.

### Observatory

Before:
- primary plot, secondary plot and provenance were separate bordered panels.

After:
- one continuous research surface owns the screen;
- primary RF measurement uses open scientific axes;
- observed-band distribution is an integrated comparison strip;
- observer/provenance occupy a ruled lab margin;
- truth footer remains explicit: no synthetic history.

### Habitat

Before:
- the Beast was a large circle-cat with dot eyes.

After:
- layered body/shoulders, head silhouette, ear interiors, cheek planes, shaped eyes,
  mood-driven mouth and collar identity tag;
- habitat telemetry remains environmental/subordinate.

The creature remains procedural project-owned proof art. Rich Pack-ready source art and
behavior choreography remain future fidelity work.

### Monolith

Before:
- focal creature was a simple circle outline with triangle ears and dot eyes.

After:
- sculptural/faceted head silhouette;
- restrained depth rings and planes;
- fine eye slits + minimal expression;
- identity engraved into the lower facet;
- negative space and single-primary-fact hierarchy remain intact.

## Exact evidence

The final comparison was rendered by CI from commit:

`6f80042e83c519cb54cb57b0c4e3b5d22a3082ef`

CI result: green.

Artifact:
- `v019-experience-home-proofs`
- artifact digest: `sha256:781ee7b3b258773ac8a81fe7d41099df7ba312c4251197ee4eb58e66b2ffa579`

The comparison proves implementation progress. It is **not** an owner-acceptance record.

## Gate 1 truth

Still pending:
1. owner review/acceptance of the actual off-screen renderer;
2. cross-page fidelity consistency;
3. reference-Pi physical readability/touch/QR/glare/smoothness/thermal/framebuffer validation;
4. physically validated Presentation Broker executor;
5. bounded TRY ON TFT execution with mandatory rollback.

No `experience.gate1.offscreen_accepted` state should be set until the owner explicitly accepts
the generated renderer direction.
