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

## Second pixel-review cycle — all five Home families

A second bounded fidelity cycle was completed after the original reconstruction pass. Each change
was isolated to one Experience, committed separately, rendered by CI at the native 480×320 target,
visually inspected, and merged only after the generated pixels were judged to be an improvement.

### Habitat — PR #11
- merged commit: `c0e16a7e423afa03795d7232b707fabf15906cba`;
- source proof head: `9134588f`;
- artifact digest: `sha256:32d22b02deb9ea0560f290074fc235e25fb0a44f564b68445af9cdd81918d45f`;
- retained: less target-like habitat geometry, layered canopy/root/vine depth, deeper creature
  torso/head planes, recessed gaze/highlights and richer muzzle/ear/cheek/chin treatment.

### Observatory — PR #12
- merged commit: `630692e79d68b309e09beba090b01cfc7c50fbf1`;
- final proof head: `134bfa40`;
- artifact digest: `sha256:082070fd6c65df771349ca7c7db074c80344fdf7fc6ea643d061a6cfdcd3312e`;
- retained: generic smiley observer replaced with a scientific optical companion; a label
  collision found in the first render was corrected and re-rendered before merge.

### Atlas — PR #13
- merged commit: `45ad93ebd97ea962465c1fb0f7cd046acd177a04`;
- proof head: `99b57a0d`;
- artifact digest: `sha256:07b125e1301a22ea0b9034fce15ab991753fc57a50ae65ce98378b0cffe52d4e`;
- retained: round cartoon badge replaced with an asymmetric notebook field-sketch companion,
  hatching/directional gaze and a field-note identity callout.

### Forge — PR #14
- merged commit: `4c09878c7d3f6ca7b64204e8e3280d441a5f5751`;
- proof head: `bfaad58f`;
- artifact digest: `sha256:ae83d0e2ef1f72731152e445b3e4aca1976dca7eb507af7e150ebcfbe1717753`;
- retained: clipped/asymmetric chassis, exposed rails/braces/fasteners/conduits, physical
  heat-sink/RF/power details and an open Doctor/Governor stencil instead of a boxed subpanel.

### Monolith — PR #15
- merged commit: `af39c6ab7d49217d5c2eac3637cabe19a340f215`;
- proof head: `61125536`;
- artifact digest: `sha256:ff018b5e7ed5ef854bd6d45e471a0d5ffd4210bea85cdf7128646416ac1d50cc`;
- retained: flat mask/logo read replaced with a restrained bust/plinth sculpture, layered facial
  planes, subtle asymmetry and engraved identity while preserving Monolith's negative space.

### Result

The five Home families now have individually pixel-reviewed current renderers rather than merely
structurally distinct implementations. This is stronger implementation evidence, but **still is
not owner off-screen acceptance** and does not authorize physical TFT ownership/staging.

Cross-page Experience proof also exists for all five families:
- Atlas Home / Recon;
- Forge Home / System;
- Observatory Home / Spectrum;
- Habitat Home / Beast;
- Monolith Home / Overview.

Therefore cross-page structural translation is implemented; remaining Gate 1 visual work is
primarily owner review, any resulting fidelity fixes, and then the bounded physical acceptance
session on the exact accepted CI artifact.

---

## Gate 1 truth

Still pending:
1. owner review/acceptance of the actual off-screen renderer direction;
2. any fidelity changes that result from that owner review;
3. reference-Pi physical readability/touch/QR/glare/smoothness/thermal/framebuffer validation;
4. physically validated Presentation Broker executor;
5. bounded TRY ON TFT execution with mandatory rollback.

Cross-page structural consistency is no longer an unimplemented item: all five Experience families
have at least one translated non-Home page proof.

No `experience.gate1.offscreen_accepted` state should be set until the owner explicitly accepts
the generated renderer direction.
