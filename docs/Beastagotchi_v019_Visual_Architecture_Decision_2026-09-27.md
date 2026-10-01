# Beastagotchi v0.19 Visual Architecture Decision

Date: 2026-09-27
Status: Design-lead direction for the next Gate 1 proof pass. Owner has not yet accepted final visual output; this document defines what we will build/prove.

## Decision summary

Beastagotchi will use **shared interaction semantics with Experience-native visual embodiment**.

Atlas, Forge, Observatory, Habitat, and Monolith are not five recolored dashboards. They are five different ways of inhabiting the same Beast truth/action system.

The shared layer defines:
- what Home means;
- what Status means;
- what Back means;
- how alerts/attention are signaled;
- how touch targets behave;
- how truth/provenance states are represented;
- how the owner reaches Search, Doctor, Broad AI, Full Tool, and Owner Space;
- how the same Action/Procedure is confirmed and executed.

The Experience layer decides:
- spatial composition;
- typography hierarchy;
- surface/material language;
- creature prominence;
- navigation embodiment;
- motion style;
- information density;
- how data becomes a visual object.

## Shared Beast Shell

The shell should be semantically consistent but visually quiet.

### 1. Truth marks

Every data view can label information using compact truth states:
- LIVE
- CAPTURED
- REPORTED
- DERIVED
- ESTIMATED
- UNKNOWN

These are semantic states, not decorative badges. Experience skins may render them differently, but meaning is invariant.

### 2. Attention levels

The same logical levels apply everywhere:
- normal
- notice
- attention
- urgent
- unavailable/unknown

Color is never the sole carrier; shape/icon/text also changes.

### 3. Navigation semantics

Each Experience exposes the same *kind* of navigation targets, but not necessarily the same visible labels or chrome.

Core semantic destinations:
- Home
- Experience Primary Workspace
- System/Tools
- History/Journal/Log
- Beast/Companion when contextually relevant

Secondary/global destinations live in an explicit system drawer/index rather than consuming permanent TFT space:
- Search
- Doctor
- Broad AI
- Software/Tool Catalog
- Settings
- Help/Learn
- Full Tool
- Owner Space

No important function should depend on a hidden gesture alone. Gestures may accelerate but not gate discoverability.

### 4. Progressive disclosure

Beast should teach the user through depth:
- Glance: one obvious answer.
- Tap: understandable detail.
- Inspect: technical truth and provenance.
- Full Tool: mature program/raw interface.

This is the visual equivalent of Guided → Advanced Guided → Full Tool → Owner Space.

### 5. Universal physical constraints

- 480×320 landscape first.
- Main touch targets should be finger-sized; tiny text is metadata only.
- Bottom/top chrome should not consume the screen merely to look like a phone app.
- Primary values should remain readable at arm's length.
- Reduced motion must preserve visual hierarchy.
- Missing data must look intentional, not like a broken widget.

## Experience navigation embodiment

### Atlas
Navigation appears as **field tabs / notebook indexes / stamped map controls**. The user should feel they are moving among pages of one expedition instrument, not switching app tabs.

### Forge
Navigation appears as **hard-key machine controls / labeled subsystem bays / service selectors**. It should feel like changing machine stations.

### Observatory
Navigation appears as **instrument modes** such as Observe / Spectrum / Survey / Capture. It should feel like changing measurement modes on a lab instrument.

### Habitat
Navigation appears as a **living-space dock** centered on Companion / Explore / Growth / Journal, with technical/system access still present but visually subordinate.

### Monolith
Navigation appears as a **spare text/index command strip**. Minimal, deliberate, no decorative icon row unless an icon is semantically superior.

## Experience screen families for Gate 1

Gate 1 should prove coherent families, not isolated Homes.

### Atlas family
1. **Field Home** — current context, companion, location truth, nearby discovery summary.
2. **Recon** — nearby AP/radio observations represented as field findings, not generic rows where avoidable.
3. **Map / Route** — only actual location/route data; otherwise clearly labeled schematic field view.
4. **Field Ledger** — captures, discoveries, session notes, provenance.

Dominant object: **field notebook/map instrument**.

### Forge family
1. **Machine Home** — core health and machine identity.
2. **Systems** — compute/power/storage/thermal/network as installed subsystems.
3. **Hardware / Bench** — attached devices, ports, radios, sensors, roles.
4. **Jobs / Service Queue** — installs, updates, repairs, tasks, procedures.

Dominant object: **machine chassis / service bay**.

### Observatory family
1. **Observe** — live phenomenon overview.
2. **Spectrum** — actual RF/channel/measurement view.
3. **Survey** — AP/device/radio relationships and observations.
4. **Capture Detail** — provenance, packet/capture quality, measured facts.

Dominant object: **scientific instrument / measurement bench**.

### Habitat family
1. **Home** — creature presence and current interpreted state.
2. **Perception** — what the creature is currently noticing from real Beast signals.
3. **Growth / Traits** — structured progression, affinities, traits, unlocked expression states.
4. **Memory / Journal** — real sessions/events/places and creature memory derived from them.

Dominant object: **living companion space**.

### Monolith family
1. **Home** — essential Beast identity/state with deliberate negative space.
2. **Status** — only the most important health/capability truths, with explicit drill-down.
3. **Event Log** — significant events only; quiet chronology.
4. **Control / Index** — direct high-confidence actions and routes into the wider Beast.

Dominant object: **austere artifact / command object**.

## Visual consistency that should survive all five

### Semantic iconography
Icons can change rendering style but not meaning. Radio, GPS, power, storage, alert, capture, Doctor, AI, search, and owner-space symbols must not become ambiguous between Experiences.

### Type hierarchy
Each Experience may use a different family/voice, but the functional hierarchy remains:
- primary glance value/title;
- secondary explanation;
- metadata/provenance;
- interactive label.

### State transition rules
The same logical event should produce equivalent urgency across Experiences even if the animation/material differs.

### Creature semantic expression
Creature state is emitted semantically first: calm, curious, focused, wary, proud, tired, etc. Each Experience renders that state in its own language.

## Experience-specific motion

Motion should reveal identity without becoming fake telemetry.

- Atlas: subtle page/ink/route/compass movement tied to real context or ambient low-rate motion.
- Forge: indicators, relays, bus pulses, fan/gauge response tied to actual state where possible.
- Observatory: trace updates, cursor movement, observation pulses driven by real/captured signals.
- Habitat: posture, gaze, breathing, ambient room response tied to semantic creature/context state.
- Monolith: nearly still; rare deliberate state changes carry weight.

## What we are explicitly rejecting

- five Home screens with the same boxes and different palettes;
- marketing-art backgrounds that overpower data;
- faux RPG map/quest language for Atlas;
- faux spaceship chrome for Forge;
- decorative fake graphs for Observatory;
- mobile pet-game progression for Habitat;
- empty-for-empty's-sake minimalism for Monolith;
- status bars copied from phone apps without a functional reason;
- tiny text used merely to look sophisticated;
- fake weather/location/history/battery/graphs;
- approval based only on image-generation concept boards.

## 'Holy shit' interaction ideas worth proving

### 1. Semantic cross-Experience state translation
The same event is visually translated by the active Experience.

Example: `radio monitor interface lost`
- Atlas: field observation goes quiet and the radio margin is marked unavailable.
- Forge: radio bay visibly drops offline.
- Observatory: trace freezes with provenance/freshness warning.
- Habitat: creature becomes wary/confused, but a tap reveals the real technical fault.
- Monolith: one stark line appears: `RADIO // OFFLINE`.

Same truth. Five identities. This is a stronger differentiator than five color themes.

### 2. Context becomes composition
Instead of adding widgets, real context can subtly restructure the screen.

Examples:
- GPS fix causes Atlas to privilege route/map context; no GPS keeps it in RF field-notebook mode.
- Attached hardware can physically 'populate' Forge bays.
- A live capture can become the dominant Observatory phenomenon.
- Returning Home can shift Habitat into a homecoming state.
- Monolith changes only when something truly matters.

### 3. Inspect anywhere
Long-press/tap-and-hold on a data object opens a compact Truth Sheet:
- source;
- freshness;
- confidence/truth class;
- raw value;
- responsible provider;
- related Doctor evidence;
- Open Full Tool where appropriate.

This makes beginner simplicity and expert transparency coexist in the same visual system.

### 4. The Beast is not drawn the same way everywhere
The creature has one identity and semantic state, but each Experience may represent it differently:
- Atlas: field companion/sketch/marker;
- Forge: machine spirit/core silhouette/technician companion;
- Observatory: observer/optic/sensor silhouette;
- Habitat: fully expressive living creature;
- Monolith: minimal silhouette/eyes/presence.

This preserves identity while letting Experiences genuinely transform the presentation.

## Next proof sequence

1. Build low-risk deterministic 480×320 proofs for the four-screen Atlas family.
2. Apply the same truth-state fixture to Forge, Observatory, Habitat, and Monolith.
3. Compare *families*, not isolated Homes.
4. Run readability/touch-density review.
5. Only then ask for owner visual acceptance.
6. Physical TFT trial follows owner acceptance of the coherent digital families.
