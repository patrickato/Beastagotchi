# Beastagotchi Experience DNA & Abundant Experience Taxonomy
## 2026-09-24

Status: active v0.19 architecture direction.

This document deliberately breaks Beastagotchi out of a narrow theme loop.

The earlier named identities — Classic, Cyberpunk, Black Ice, WOPR/NORAD, LCARS, Hunter, Matrix, Retro CRT, Synthwave, Starcore and similar — remain useful visual presets and references. They are **not** the product taxonomy and must not become the default answer to every new visual/experience question.

Beastagotchi should provide **choice, variety, depth and customization in abundance** without turning the codebase into a pile of unrelated skins.

The solution is an Experience composition system.

---

## 1. Core shift

Old mental model:

`Theme -> Page -> Widgets`

Current Scene model:

`Theme -> Scene -> Layers -> Creature -> Live instruments -> Interaction -> Effects`

New Experience model:

`Experience DNA -> resolved components -> Scene variants -> live behavior`

An Experience is not merely a palette or background.

It expresses intent across several independent axes:

- visual family;
- layout family;
- density;
- motion behavior;
- creature presence;
- utility bias;
- playfulness;
- alert language;
- hardware/display fit;
- input model;
- Doctor visibility;
- mystery/secrets;
- mission bias;
- target quality variant.

Themes, Faces, Animation Profiles, Boards, Context Decks, sound/haptic policy, Scenes and individual renderers remain implementation components underneath this intent layer.

---

## 2. Why Experience DNA exists

Without a higher-level composition model, new designs tend to collapse into:

- recoloring the same geometry;
- reusing the same dashboard arrangement;
- inventing another named theme rather than another experience;
- treating the creature as a thumbnail beside telemetry;
- assuming every user wants the same information density;
- assuming Pi 4 + 480x320 is the only meaningful target;
- treating Doctor as a separate app rather than contextual system intelligence.

Experience DNA provides a stable vocabulary for creating genuinely different worlds while keeping shared Beast contracts underneath.

---

## 3. The composition axes

### Visual family

Defines the broad world/language, not exact colors.

Current taxonomy intentionally includes at least these families:

1. **Expedition / Field** — Atlas, Trailhead, Outpost, Surveyor, Waypoint, Ranger.
2. **Scientific / Instrument** — Observatory, Spectra, Signal Lab, Vector, Helix, Workbench.
3. **Operations / Command** — Mission Control, Sentinel, Watchtower, Relay, Ops Grid, Command Deck.
4. **Industrial / Machine** — Forge, Foundry, Engine Room, Machine Bay, Switchgear, Workshop.
5. **Creature / Companion** — Habitat, Vivarium, Sanctum, Nest, Caretaker, Menagerie.
6. **Arcane / Hidden** — Cipher, Relic, Vault, Obsidian Archive, Warden, Haunt.
7. **Premium / Modern** — Monolith, Prism, Slate, Halo, Studio, Aurum.
8. **Archive / Paper** — Dossier, Field Notes, Ledger, Archive, Operator Journal, Atlas Book.
9. **Ecological / Organic** — Canopy, Mycelium, Tidepool, Biome, Terrarium, Weathered.
10. **Nautical / Marine** — Harbor, Bridge, Sonar, Buoy, Chartroom, Lighthouse.
11. **Aviation / Flight** — Flightline, Radar Room, Airframe, Tower, Approach, Vector Flight.
12. **Analog / Electromechanical** — Bench Meter, Relay Panel, Gaugeworks, Teletype, Patchbay, Control Cabinet.
13. **Urban / Street** — Street Grid, Transit, Night Walk, Blockwatch, City Survey, District.
14. **Educational / Explain** — Tutor, Explainer, Signal School, Anatomy, Lab Notes, Guided Mode.
15. **Calm / Ambient** — Stillwater, Quiet Room, Night Watch, Low Tide, Ember, Drift.
16. **Developer / Bench** — Bench, Trace, Inspector, Wireframe, Profiler, Sandbox.

This list is intentionally broad but **not closed**.

Community Packs may introduce additional families or local variants later, provided they use the same Signal/Scene/Action/Capability contracts.

Implementation rule: custom presentation vocabularies are allowed through **namespaced extension IDs** such as `example.biomech` or `vendor.organism`. Core semantic axes that other subsystems must reason about—density, creature presence, utility bias, playfulness, input model, Doctor visibility and mystery level—remain standardized. This gives Packs creative freedom without breaking interoperability.

### Layout family

Layout is independent of visual style.

Initial vocabulary:

- hero scene;
- split console;
- radial;
- telemetry stack;
- map first;
- creature first;
- module grid;
- notebook;
- terminal first;
- immersive HUD;
- sidebar strip;
- bottom dock;
- cockpit cluster;
- timeline;
- canvas/freeform.

A scientific Experience does not have to use one scientific layout. A companion Experience does not have to be creature-first. Mixing axes is the point.

### Density

- glance;
- balanced;
- dense;
- expert;
- diagnostic.

Density is content priority, not a raw font-scale setting.

### Motion profile

- still;
- subtle;
- calm ambient;
- playful;
- reactive;
- tactical;
- premium;
- arcade;
- ominous;
- scientific.

Motion must remain visually honest. Decorative movement is never allowed to pretend telemetry changed.

### Creature presence

- hidden;
- ambient;
- supporting;
- prominent;
- dominant.

This makes creature identity a deliberate design decision rather than a hard-coded assumption that the Beast always occupies the same rectangle.

### Utility bias

- companion;
- balanced;
- instrument;
- operations.

### Playfulness

- none;
- low;
- moderate;
- high.

### Alert language

- quiet;
- clinical;
- field;
- tactical;
- dramatic;
- companion.

### Input model

- touch first;
- mixed;
- remote first;
- headless first;
- physical controls.

### Doctor visibility

- background;
- contextual;
- prominent;
- operations first.

Doctor visibility is contextual system behavior, not a theme.

During a serious incident an Experience may temporarily promote Doctor to operations-first while retaining its own visual identity.

### Mystery level

- none;
- subtle;
- discoverable;
- deep.

This governs how much an Experience participates in rares, hidden achievements, secret pages, ciphers, reveals and unexplained events.

---

## 4. First new built-in Experiences

The first implementation deliberately avoids the old cyber/retro/fiction UI loop.

### Atlas

Family: Expedition. Layout: Map first.

Purpose: GPS/location, Expeditions, journey history, field discoveries, waypoints, travel context and nearby environmental/context signals.

Creature: supporting rather than dominant.

Atlas proves Beast can feel like a field instrument rather than a themed dashboard.

### Forge

Family: Industrial. Layout: Cockpit cluster.

Purpose: hardware, power, storage, services, peripherals, thermals, Doctor, recovery and bench work.

Creature: ambient.

Forge treats the Pi itself as a physical machine worth understanding and maintaining.

### Observatory

Family: Scientific. Layout: Split console.

Purpose: spectra, real telemetry, histories, correlation, signal quality and research work.

Creature: supporting.

Observatory provides a serious truth-heavy scientific language without using cyberpunk shorthand.

### Habitat

Family: Companion. Layout: Creature first.

Purpose: active Beast, mood, progression, memories, rares, lineage, personality and daily relationship.

Creature: dominant.

Habitat proves the system can be a living companion rather than an instrument panel with a mascot pasted into it.

### Monolith

Family: Premium. Layout: Immersive HUD.

Purpose: polished daily/default/showpiece use, minimal visual noise, high product quality, deliberate motion, balanced utility and creature identity.

Monolith is a route toward a UI that feels like a finished commercial product rather than hobbyist theming.

### Dossier

Family: Archive. Layout: Notebook.

Purpose: Patient Chart, incident history, notes, logs, Expedition summaries, saved evidence and after-action review.

### Stillwater

Family: Calm.

Purpose: night, low-noise daily use, reduced motion, low-power context and companion presence without constant stimulation.

### Bench

Family: Developer.

Purpose: exact state, profiling, Doctor findings, Scene truth/performance overlays, BenchLink, development and recovery.

---

## 5. Adaptive quality ladder

Experience DNA defines identity. Platform Profile defines the starting resource envelope. Resource Governor and real measurements eventually refine it.

A quality ladder should keep the **same Experience** recognizable:

### Enhanced
- richer backgrounds;
- denser particles/effects;
- more concurrent instruments;
- deeper history;
- richer transitions;
- optional local AI surfaces.

### Full
- intended primary design;
- moderate effect density;
- normal histories/services.

### Compact
- simplified environment;
- reduced simultaneous instruments;
- reduced motion density;
- same core layout/identity.

### Constrained
- static/cached environment where needed;
- minimal creature animation;
- glance-first telemetry;
- fewer background services;
- same Experience identity.

**A constrained Atlas is still Atlas.** It must not degrade into an unrelated generic fallback dashboard.

---

## 6. Display adaptation

480x320 remains a handcrafted first-class reference surface. Experience DNA does not mean scaling that screenshot forever.

Target classes:

- micro;
- reference;
- medium;
- large;
- desktop.

An Experience may provide content priority, anchors/constraints, alternate Scene variants, additional instruments for larger surfaces, alternate navigation, companion/remote layout and headless presentation.

Example: Atlas on 480x320 uses creature + nearby field context + compact navigation instruments. Atlas on a 10-inch Pi 5 display can use a larger map/canvas, persistent route/history, side instrumentation and richer overlays while remaining recognizably Atlas.

---

## 7. Doctor integration

Doctor is not a single visual theme.

Every Experience declares how visible Doctor normally is.

Examples:

- Habitat: background normally; companion-language health cue; serious incident temporarily elevates Doctor.
- Forge: prominent by default; hardware/service findings integrate naturally into the machine-room surface.
- Bench: operations-first; evidence, probes and runbooks are part of the primary experience.
- Monolith: contextual; normally quiet, polished intervention only when needed.

During Recovery/Incident context the Experience Compiler may raise Doctor visibility to operations-first without replacing the entire visual family.

---

## 8. Themes are demoted, not deleted

Existing named themes remain useful as palette/effect packs, legacy presets, nostalgia identities, scene references, community examples, or optional complete Experiences if deliberately built as such.

But they no longer define the architecture.

The code explicitly maintains them as `LEGACY_REFERENCE_IDENTITIES`.

Future planning should avoid phrases such as “we need a Cyberpunk version of this” unless Cyberpunk is actually the desired experience.

Prefer asking: what visual family, layout, density, motion, mission and hardware target should this Experience have?

---

## 9. Theme Studio becomes Experience Studio over time

Theme Studio remains valid for editing low-level visual style.

The larger Studio hierarchy should become:

- Experience — intent and bundle;
- Scene/Layout — composition and semantic hierarchy;
- Theme — visual skin/style roles;
- Face/Creature — identity presentation;
- Motion — behavior/effects;
- Board — instrument composition;
- Context Deck — app/navigation curation;
- Sound/Haptic/Accessory — non-visual response.

The user may start from an Experience and then freely edit any constituent layer.

Applying an Experience still follows: `resolve -> preview -> edit -> TRY ON TFT -> explicit apply`.

No Experience selection silently mutates the live device.

---

## 10. Packs and community growth

A future Experience Pack can include or reference:

- Experience DNA;
- Theme;
- Scene definitions;
- Board/Layout;
- Face assets;
- Animation profile;
- sound/haptic profile;
- Context Deck;
- required/optional Capabilities;
- target variants;
- fallback ladder;
- provenance.

Content-only Packs remain content-only. Executable providers/actions remain under their existing trust model.

---

## 11. Secrets and rares

Mystery is an Experience axis rather than a global gimmick.

A deep-mystery Experience may allow hidden pages, ambient unexplained changes, secret achievements, ciphers, rare creature states and seasonal reveal choreography.

A scientific or developer Experience may intentionally expose little or none of that behavior.

The Secret/Rare engine remains the authority for trigger truth. Experience only decides presentation after permission to reveal.

---

## 12. First prototype sequence

To break the visual loop, prototype these first:

1. **Atlas**
2. **Forge**
3. **Observatory**
4. **Habitat**
5. **Monolith**

Do not begin by making five new color schemes.

Each prototype must differ in at least visual family, primary layout family, creature presence, data hierarchy, motion language and Doctor relationship.

The five prototypes should look like five products built on the same platform, not five skins of one screen.

---

## 13. Acceptance criteria

A new Experience is not considered meaningfully distinct if:

- switching it mainly changes colors;
- the same widget geometry remains dominant;
- the same mascot rectangle remains in the same position;
- all pages reuse the same panel language;
- Doctor appears identically everywhere;
- larger displays merely upscale 480x320;
- reduced-resource variants lose identity;
- decorative effects imply live telemetry.

A strong Experience should be recognizable in grayscale silhouette/layout before palette is considered.

---

## 14. Implementation status

Implemented in v0.19:

- `beastcore/experience_dna.py`;
- read-only `beastcore/experience_compiler.py` using Platform Profile, shared dependency/capability resolution and real page coverage;
- 16 visual-family taxonomy entries;
- independent layout/density/motion/creature/utility/alert/input/Doctor/mystery axes;
- built-in DNA for Atlas, Forge, Observatory, Habitat, Monolith, Dossier, Stillwater and Bench;
- explicit legacy-reference identity set;
- capability-first adaptive quality variant resolution using PlatformProfile compute/display classes;
- context-sensitive Doctor visibility;
- Experience DNA/family metadata exposed through Beast Studio schema;
- automated tests protecting breadth and identity preservation.

Still to build:

- actual Scene/asset implementations for the first prototype Experiences;
- Studio Experience browser/editor;
- Experience Compiler v1 planning/resolution is implemented; full component resolution into Theme/Scene/Face/Motion/Board/Deck/Pack references remains to be expanded;
- Pack schema for community Experience DNA;
- responsive target variants;
- per-Experience sound/haptic/accessory behavior;
- visual acceptance evidence for the new families.

---

## 15. Permanent design principle

**Beastagotchi is not a collection of six themes.**

It is a platform capable of many coherent experiences.

Choice and variety should come from combining stable semantic contracts, not from accumulating disconnected hard-coded skins.