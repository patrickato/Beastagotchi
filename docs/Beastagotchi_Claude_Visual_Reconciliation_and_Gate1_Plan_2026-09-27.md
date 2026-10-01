# Beastagotchi — Claude Visual Review Reconciliation + Corrected Gate 1 Plan

**Date:** 2026-09-27
**Status:** Canonical visual-direction reconciliation before further Gate 1 implementation
**Owner decision context:** The owner does not want to choose a single static render as the visual basis for the whole project. This is correct: Beastagotchi is deliberately highly customizable, and no one drawing should become an accidental cage.

## 1. Core correction

The visual product is not one final picture and not five themed dashboards.

The product should be built as four separable layers:

1. **Shared Beast Shell** — stable interaction/truth/legibility contracts that must work everywhere.
2. **Experience Body** — Atlas / Forge / Observatory / Habitat / Monolith and future Experiences may embody the same Beast truth in genuinely different visual grammars.
3. **Customization Layer** — themes, palettes, assets, face/creature packs, typography within legibility limits, decorative environments, optional layouts and content packs.
4. **Truth Translation Layer** — one canonical machine/event/state truth may be expressed differently by each Experience without changing its factual meaning.

This removes the false requirement that the owner must approve one drawing as the universal visual foundation.

## 2. Claude review — accepted findings

Claude's independent visual review identified several measurable problems that are accepted and promoted into the project plan.

### A. Shared semantics were bypassed

The five Experience bodies became visually distinct, which is good, but the renderers separately reinvented or omitted truth presentation, navigation, attention/fault behavior, typography, touch behavior and creature representation.

**Decision:** create a thin Shared Beast Shell rather than forcing a shared visual body.

### B. Unknown must never silently become zero

Cold-start or unavailable values currently risk rendering as `0`, `00`, `0 C`, `CH 00`, etc. This violates the project's standing rule that unknown remains unknown.

**Decision:** introduce shared Reading/truth-state primitives with explicit states such as:
- known/live
- known/captured
- stale
- unavailable
- unknown
- estimated/derived where applicable
- fault/invalid where applicable

A renderer must not invent a numeric zero merely because a source value is absent.

### C. No hard-coded truth claims

Examples found by Claude include a canned Atlas route labelled live, Forge declaring radio online regardless of failure, and Observatory declaring capture quality regardless of actual provenance.

**Decision:** every factual visual claim must be data-bound or explicitly decorative. Decorative graphics must not masquerade as measurements, topology, geography, health, activity or provenance.

### D. Typography must be designed for the actual 3.5-inch 480×320 panel

The current proof renderers use too much 6–9 px text for primary meaning.

**Decision:** define and physically validate a shared TFT type ramp. Microtext may exist only for genuinely secondary detail and may not carry required state, alarms, actions or navigation.

The physical Pi/TFT test card becomes a required early validation artifact.

### E. One attention/alarm contract

Health/fault truth cannot be independently interpreted five different ways.

**Decision:** create a shared attention ladder and fault semantics. Each Experience may *translate* the same state differently, but severity, urgency, acknowledgement state and evidence link remain canonical.

Example: the same radio failure may appear as:
- Atlas: field observation went quiet / unavailable.
- Forge: radio bay fault/offline.
- Observatory: frozen trace + stale/unavailable provenance.
- Habitat: creature reacts, but diagnosis remains explicit and separate.
- Monolith: `RADIO / OFFLINE`.

This “same truth, five translations” pattern is promoted as a defining Beastagotchi visual principle.

### F. Shared navigation semantics, Experience-native embodiment

The existing named prev/next runtime navigation is useful and learnable.

**Decision:** preserve common navigation semantics and touch behavior, but allow each Experience to paint/embody the navigation differently. Do not force one identical footer aesthetic onto every Experience.

### G. One creature identity rig, many visual projections

Current Experience creatures drift into unrelated identities.

**Decision:** define a shared creature identity/expression contract (identity, stage, level, core expression, attention/health cues, lineage/traits where applicable). Each Experience may render that same creature differently:
- Atlas field sketch
- Forge machine/core embodiment
- Observatory observer/lens embodiment
- Habitat full companion portrait/body
- Monolith sculptural/minimal embodiment

This is not “one drawing everywhere.” It is one canonical creature expressed through five visual languages.

### H. CI must exercise state diversity, not only a healthy fixture

Claude's review matrix exposed failures hidden by the current healthy-only proof fixture.

**Decision:** adopt a deterministic state-matrix visual regression set including at minimum:
- healthy/live
- cold boot / unknown
- radio/provider offline
- GPS unavailable/searching/fixed
- low-power or constrained state
- thermal/critical attention
- stale/captured data
- dense/busy radio observations

Synthetic review fixtures remain clearly labelled synthetic and are never presented as live telemetry.

### I. Experience runtime integration is real work and must occur before physical acceptance

The current Experience proof renderers are not yet the actual TFT runtime path, lack a complete touch/navigation map, and overlap the current runtime footer band.

**Decision:** Gate 1 cannot jump directly from isolated proof PNGs to “physical-only fixes.” A small integration tranche is required first so the thing tested on the physical TFT is actually the Experience system we intend to ship.

## 3. Claude findings accepted selectively, not blindly

Claude's personal visual ranking is advisory only and is not canonical.

We retain the strongest motifs identified across the current Experiences:

### Atlas
Retain:
- field-canvas/notebook identity
- ruled margin / expedition ledger
- field-sketch creature projection

Modify:
- no fake/live route geometry
- no decorative compass unless driven by real heading
- no animated “terrain” that implies moving geography
- RF observations must not imply bearing/location unless actually known

### Forge
Retain:
- one chassis / machine-bay metaphor
- real system bus/dependency expression
- large high-value machine readings
- Doctor/fault lamp as a native motif

Modify:
- remove decorative mechanical labels/ports/ticks with no informational function
- machine lights/bus segments must correspond to real state
- creature becomes the machine's living core rather than a disconnected logo

### Observatory
Retain:
- open scientific axes
- observer-in-lens creature projection
- signal/history/provenance emphasis

Modify:
- all axes need meaningful units/ticks
- provenance margin contains actual source/freshness/sample/capture provenance, not unrelated CPU/RAM filler
- live vs captured vs stale must be explicit from truth state

### Habitat
Retain:
- creature-first composition
- habitat objects as information carriers
- perception/growth/memory language

Modify:
- decorative shapes must not look tappable if they are not
- progression/growth visuals must say what they measure
- creature reaction may interpret events but never replace factual diagnosis

### Monolith
Retain:
- restraint / negative space
- sculptural creature presence
- strong readable single-fact presentation
- health/body-language cue concept

Modify:
- do not let minimalism hide required controls or evidence
- sparse is allowed; ambiguous is not

## 4. Visual architecture going forward

### Shared Beast Shell owns
- canonical page/status sentence slot
- Reading truth states
- attention/alarm contract
- typography limits/type ramp
- touch target minimums and hit maps
- navigation semantics
- focus/selection/disabled affordances
- accessibility/reduced-motion hooks
- creature identity/expression contract
- provenance/freshness semantics
- action confirmation/risk semantics where applicable

### Experience Body owns
- composition
- spatial metaphor
- visual hierarchy within shell constraints
- environment
- ornament, if it cannot be mistaken for telemetry/control
- native navigation styling
- native creature projection
- transitions/ambient motion within performance/truth constraints
- which truthful signals are foregrounded

### Customization owns
- palette/theme variants
- textures/background assets
- font families that satisfy the validated type metrics
- creature/face assets following the shared rig
- optional presentation packs
- decorative motion packs
- user-created Experience/Packs through stable contracts

## 5. Corrected Gate 1 order

1. **Shared shell primitives** — Reading states, attention ladder, type ramp, nav/touch contract, creature rig skeleton.
2. **Truth corrections** — remove hard-coded claims and unknown-as-zero behavior in all five current Experience proofs.
3. **State-matrix CI** — exercise multiple deterministic truth states.
4. **Runtime integration slice** — wire Experience selection/rendering/navigation/touch into the actual TFT runtime path without destroying existing recovery path.
5. **Physical type/touch card** — validate readable type sizes, contrast, hit targets, RGB565 behavior and actual viewing distance on the 3.5-inch display.
6. **Five Experience family refinement** — refine the bodies with the now-stable shared shell rather than continuing isolated moodboards.
7. **Physical Gate 1 session** — Pi/TFT/touch/framebuffer/thermal/performance + owner visual judgment.
8. **Only then** record visual/physical Gate 1 acceptance.

## 6. Owner interaction rule

The owner should not be asked to choose an entire product identity from one render.

Future owner review should use specific, bounded decisions when genuinely necessary, for example:
- “Does this type size/readability feel right on the actual TFT?”
- “Does Habitat feel sufficiently creature-first compared with Observatory?”
- “Is this amount of motion distracting?”
- “Does this fault state make sense at a glance?”

OpenAI remains responsible for converging the overall design and presenting increasingly complete candidates, rather than repeatedly handing the owner an unconstrained style-choice problem.

## 7. Immediate next implementation recommendation

Do **not** generate another broad set of image moodboards now.

Implement the Shared Beast Shell and the deterministic visual state matrix first on `openai/v019-visual-redesign-v2`, then migrate/refine the five Experience families against those contracts.

This is the shortest path to a dynamic, visually interesting, truthful and highly customizable Beastagotchi without turning any one concept drawing into an architectural cage.
