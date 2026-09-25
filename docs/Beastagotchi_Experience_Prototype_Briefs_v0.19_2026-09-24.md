# Beastagotchi v0.19 — First Experience Prototype Briefs
## 2026-09-24

Purpose: define the first five Experience-DNA visual proofs strongly enough that implementation cannot collapse into five palette variants of the same screen.

These are **composition briefs**, not final art direction. Palette is intentionally secondary.

---

## Atlas — Expedition / Field

### Silhouette test

Even in grayscale, Atlas should read as a **field map / journey instrument**.

Primary shape:
- dominant spatial/canvas region rather than boxed telemetry grid;
- route/position/heading/nearby context own the largest visual area;
- creature appears as a field companion/marker, not the screen's main portrait;
- small live instruments hug edges or corners.

### Home hierarchy

1. current field context / map-like environmental canvas;
2. Beast + heading/location state;
3. nearby discoveries / journey progress;
4. compact RF/system status;
5. navigation/actions.

### Motion

- slow map drift / route progression when real position history changes;
- subtle compass/heading response when genuine heading changes;
- ambient weather/environment movement may be decorative but must be labeled ambient;
- no fake route movement.

### Doctor

Contextual. Health appears as a field-readiness cue. Serious incidents promote a recovery/navigation-to-safety layer without replacing Atlas identity.

### Page translations

- Recon becomes nearby field-survey view;
- Spectrum becomes terrain-like signal distribution / directional instrument;
- Expedition becomes the natural center of the experience;
- Doctor findings can be pinned as field-readiness markers.

### 480x320

Keep the map/context canvas simple and legible. Do not attempt a desktop GIS UI in miniature.

### Large display

Gain route history, wider map/context, persistent side instruments and richer environmental layers.

---

## Forge — Industrial / Machine

### Silhouette test

Forge should read as a **machine room / equipment panel**, not cyberpunk.

Primary shape:
- clustered machine subsystems;
- strong physical grouping around compute, radio, storage, power and attached hardware;
- visible connection/role relationships;
- creature is ambient—part of the machine, not a portrait card.

### Home hierarchy

1. machine readiness / hardware topology;
2. active radio + services;
3. power/thermal/storage;
4. Doctor/incident state;
5. actions and peripheral roles.

### Motion

- restrained mechanical response tied to real state transitions;
- fan/power indicators only move when backed by real signals where applicable;
- decorative mechanical ambience may exist but remains visually distinguishable from live gauges.

### Doctor

Prominent by default. Doctor feels native here: fault lamp -> evidence -> subsystem -> runbook -> action.

### Page translations

- Recon becomes radio subsystem bay;
- Spectrum becomes instrument rack / analyzer;
- Hardware Studio feels first-class rather than an app bolted on later;
- Recovery Vaults appear as physical storage/backup endpoints.

### 480x320

Use 3–5 large subsystem clusters, not dozens of tiny gauges.

### Large display

Expand topology, per-device detail, service graph, storage map and Doctor evidence without changing the industrial identity.

---

## Observatory — Scientific / Instrument

### Silhouette test

Observatory should read as a **research instrument / measurement station**.

Primary shape:
- one dominant live plot or instrument;
- one secondary comparison/history region;
- precise labels and units;
- creature is a subtle observer/identity cue rather than decorative mascot.

### Home hierarchy

1. current measured phenomenon;
2. history/correlation;
3. quality/freshness/provenance;
4. compact system health;
5. navigation.

### Motion

- live charts move only from real samples;
- scientific cursor/scanning aids may animate but must be visually distinct from measured traces;
- stale/unavailable data is explicitly visible.

### Doctor

Contextual and evidence-heavy. Findings should expose source, freshness, causal chain and verification quality.

### Page translations

- Spectrum is a flagship scientific surface;
- Recon emphasizes measured observations rather than 'targets';
- Correlation Lab becomes native to the experience;
- Replay should look like recorded experiment data and be clearly labeled replay.

### 480x320

One major chart + one secondary metric region. Avoid graph confetti.

### Large display

Multiple synchronized plots, richer history, correlation matrices and provenance panels.

---

## Habitat — Creature / Companion

### Silhouette test

Habitat should read as a **living creature space**, not a dashboard containing a mascot.

Primary shape:
- Beast dominates the visual environment;
- state/telemetry is expressed through habitat objects, subtle instruments and contextual overlays;
- navigation recedes until needed.

### Home hierarchy

1. Beast / mood / current state;
2. immediate environment and meaningful reactions;
3. progression/memory/relationship cues;
4. small operational truth indicators;
5. apps/navigation.

### Motion

- creature behavior and reactions are the primary motion language;
- mood/progression/event animations are driven by real state/event contracts;
- environmental ambience can remain decorative;
- no meaningless constant twitching just to appear alive.

### Doctor

Background normally. Health issues first appear as truthful companion-language cues, but serious incidents transition into explicit Doctor evidence/actions.

### Page translations

- progression/roster/memories feel like rooms/areas of the habitat;
- Expeditions become remembered journeys;
- Rares and secrets can be deeply integrated;
- technical pages may temporarily shift toward instrument language without losing identity.

### 480x320

Give the Beast space. Telemetry must not reclaim the whole screen.

### Large display

Richer environment, persistent memory/progression affordances, more expressive animation and optional secondary instruments.

---

## Monolith — Premium / Modern

### Silhouette test

Monolith should read as a **finished premium product**, not 'minimal cyberpunk'.

Primary shape:
- strong negative space;
- one clear focal object/creature;
- very few simultaneous instruments;
- typography and hierarchy matter more than ornament;
- transitions are quiet and intentional.

### Home hierarchy

1. Beast / primary state;
2. one or two high-value live facts;
3. contextual action;
4. discreet status/navigation.

### Motion

- slow, polished, bounded transitions;
- no scanlines/grids by default;
- no constant particle field required;
- motion should communicate focus/state change or subtle life.

### Doctor

Contextual. Routine health disappears into subtle status. Important incidents surface as a clear, elegant intervention—not a wall of diagnostics unless opened.

### Page translations

- each page has a strong single purpose;
- advanced density is available by drill-in, not shown by default;
- Universal Inspect becomes an important route to depth;
- larger displays use space, not merely more boxes.

### 480x320

Extremely disciplined information hierarchy and touch targets.

### Large display

Keep restraint. Do not fill new pixels simply because they exist.

---

## Cross-prototype non-negotiables

1. The five prototypes must be distinguishable in grayscale silhouette/layout.
2. Their primary content hierarchy must differ.
3. Creature presence must materially differ.
4. Doctor must feel native to each Experience rather than identically overlaid.
5. Motion language must differ while preserving truth.
6. The same telemetry may be rendered differently without changing canonical Signal truth.
7. 480x320 variants must be handcrafted; large-display variants must add structure rather than upscale screenshots.
8. Constrained/compact variants preserve identity.
9. None of these prototypes is required to inherit the old grid/scanline/neon language.
10. Old themes remain available, but they are not the visual starting point for these five proofs.

## Recommended rendering order

1. Atlas Home
2. Forge Home
3. Observatory Home
4. Habitat Home
5. Monolith Home

After those five Home silhouettes are accepted off-screen, choose one or two to extend into Recon/Spectrum/Expedition and prove that Experience DNA changes whole product behavior, not only the landing screen.