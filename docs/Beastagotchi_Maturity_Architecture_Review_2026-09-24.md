# Beastagotchi Maturity Architecture Review — 2026-09-24

Status: **Architectural decision record / active v0.19 direction**

This review compares the recovered project vision, current roadmap, current v0.19 source, real Pi constraints, Theme Manager interoperability work, and the latest concept-fidelity feedback.

## Executive conclusion

Beastagotchi does **not** need a total rebuild.

The strongest long-lived architecture is already present:
- protected Pwnagotchi / Bettercap engines;
- Beast Core canonical state, events, persistence and health;
- audited Action Broker / transactional mutation;
- capability/dependency/provider resolution;
- Pack/Depot foundations;
- persistent roster, progression, memory and lineage;
- explicit source/target/physical validation boundaries;
- recovery-first project discipline.

The maturity risk is elsewhere: presentation, routing and customization are becoming broader faster than their internal contracts are becoming reusable.

The next phase should therefore be a **contract consolidation and experience-runtime phase**, not a feature freeze and not a rewrite.

The goal is to make new capability multiply existing capability. A new signal, renderer, Pack, hardware provider, scene, action or companion surface should automatically become useful to many other parts of the platform without hard-coding another one-off path.

## Product identity to preserve

Beastagotchi is simultaneously:
1. a serious field instrument;
2. a persistent living creature;
3. a customizable visual operating environment;
4. a local workshop and extension platform;
5. a recoverable long-lived history of devices, expeditions, creatures, discoveries and events.

No one of those roles should consume the others.

The TFT is the immediate field cockpit. Apps provide depth. Studio is the workshop. Companion/large displays may expose more space. The protected Pwnagotchi remains independently usable.

## What is already structurally strong

### Canonical truth

`StateRegistry` remains the right foundation. Live/stale/unavailable/source metadata is more valuable than letting every renderer/plugin poll its own version of reality.

The Template Token Registry is also directionally correct, but tokens should become one presentation view over a richer typed Signal contract rather than the final abstraction.

### Action and recovery boundaries

Owner-authorized actions, snapshots, health observation, rollback and provenance are exactly the right bias. Future configuration, Pack, presentation, update and hardware mutations should converge on common transaction machinery instead of each growing a custom transaction pattern.

### Capability/provider model

The Dependency & Capability Resolver and provider arbitration are high-leverage architecture. Optional hardware, plugins and services should continue to advertise abstract capabilities rather than forcing consumers to depend on specific implementations.

### Extension model

Pwnagotchi Plugin / Beast Pack / Beast App / Companion Expansion is a useful user-facing taxonomy. Internally, content roles and capabilities matter more than proliferating technical package types.

### Long-lived identity

The Device → Roster → Active Beast → Experience split is one of the most important mature decisions in the project. Creature identity must remain independent of presentation and optional modules.

## Maturity risks visible in current source

### 1. Beast UI is becoming a control/render monolith

`beastui/engine.py` is now roughly 2,184 lines / 160 KB and owns too many responsibilities:
- preference/theme state;
- input routing;
- navigation;
- app launching;
- many overlays;
- rendering;
- frame scheduling;
- telemetry presentation;
- platform browsers;
- achievements;
- help;
- runtime metrics.

This is still maintainable today, but continuing to add features there would eventually make every UI change risky.

Decision: **decompose behind existing behavior**, not rewrite.

### 2. Beast Studio has the same pressure

`beaststudio/server.py` is roughly 903 lines / 127 KB and has become both HTTP router and orchestration façade for roster, Capsules, global policy, platform operations, Packs, updates, presentation and library functions.

Decision: retain the existing server/process, but move route groups into explicit controllers/services and use a route registry.

### 3. Experience is currently too shallow for the promised customization

The existing Experience draft is mostly:
- Theme;
- Face;
- Animation;
- Board/Layout;
- Context Deck.

That is a good first composition model but cannot by itself deliver the requested abundance of depth, structural variety and scene-level customization.

Decision: evolve Experience into a versioned compiled specification rather than keep adding fields ad hoc.

### 4. Presentation semantics are spread across several mechanisms

Today visual identity is split across:
- Theme JSON;
- `backgrounds.py`;
- `home_scenes.py`;
- page render code;
- face/animation packs;
- engine overlays;
- widget renderers;
- theme runtime options.

Decision: introduce one neutral **Visual Runtime / Scene Contract** behind existing paths and migrate incrementally.

### 5. Generic Dashboard customization is useful but not a universal UI model

A 12×8 instrument board is appropriate for dashboards. It should not become the shape every customized experience is forced into.

Decision: keep Boards, but add Scenes as a separate richer composition primitive.

## Architecture decision: universal platform contracts

The next mature Beast architecture should center on five versioned contracts.

### A. Signal

A Signal is typed canonical information.

It extends today's StateRegistry/token metadata with:
- stable ID;
- value type / structure;
- unit;
- source/provider;
- quality/freshness;
- update class;
- history support;
- privacy classification;
- publication policy;
- formatting hints;
- optional semantic range/category.

Template tokens, widgets, scenes, Doctor, Operator, Packs and companion clients can all consume the same Signal definitions.

### B. Action

A structured thing Beast can do.

Every action should declare:
- ID;
- parameters/schema;
- authorization tier;
- preconditions;
- capabilities required;
- blast radius;
- whether it is transactional;
- expected restart/reboot impact;
- rollback/undo support;
- audit behavior.

The current Action Broker becomes the authority rather than UI code performing mutations directly.

### C. Capability

Keep the existing capability/provider/dependency model and make it the common compatibility language for Apps, Experiences, Scenes, Packs and Hardware Studio.

### D. Scene

A Scene is a semantic visual composition, not a bitmap and not just a dashboard grid.

Proposed bounded layer types:
- group;
- image/art;
- creature/face;
- text/token;
- live instrument;
- shape/panel;
- graph/visualizer;
- effect;
- notification/reaction anchor;
- conditional/context layer;
- interaction region.

Each layer can declare:
- stable semantic ID;
- bounds/constraints/anchors;
- Signal bindings;
- Action bindings;
- z-order;
- visibility condition;
- update class;
- animation/effect tracks;
- style roles;
- touch behavior;
- cacheability;
- resource class;
- reduced-motion behavior;
- target/display compatibility.

This contract is the route to real depth and customization without hardcoding hundreds of mutually incompatible screens.

### E. Experience

An Experience becomes a user-facing compiled bundle that may select:
- presentation engine;
- Scene set / page mappings;
- Theme/skin;
- Face;
- motion/effects;
- Board(s);
- Context Deck;
- sound/haptic profile;
- notification style;
- input bindings;
- target/display variants;
- context variants such as Field, Docked, Night or Reduced Motion.

The user edits a draft. Beast compiles it into an immutable runtime plan, reports missing capabilities/dependencies/unsupported semantics/resource expectations, previews it, and only applies it explicitly.

## Architecture decision: Experience Compiler

Introduce an Experience Compiler between Studio content and runtime presentation.

Input:
- user draft;
- installed Packs/assets;
- target display;
- current capabilities;
- provider decisions;
- user policy;
- selected presentation engine.

Output:
- resolved components;
- exact Scene/layer plan;
- Signal bindings;
- Action bindings;
- required capabilities;
- missing/optional requirements;
- target/display compatibility;
- privacy implications;
- resource/thermal estimate;
- fallbacks;
- warnings;
- provenance.

This makes “TRY ON TFT”, Depot compatibility, Presentation Profiles, responsive displays and troubleshooting all use one explanation model.

## Architecture decision: Visual Runtime

The new layered compositor should mature into a small Visual Runtime shared by Beast UI content systems.

Responsibilities:
- scene/layer composition;
- cached static assets;
- precomputed visual effects;
- motion clock/timelines;
- transitions/reveals;
- semantic layer metadata;
- dirty propagation;
- reduced-motion policy;
- render-cost attribution;
- output to the existing dirty-row framebuffer writer.

Important: do not move telemetry polling or OS policy into the renderer.

### Render efficiency

Current dirty-row framebuffer writing is already a strong foundation.

The next improvement is to avoid doing expensive work before the row diff:
- compile Scene specs once;
- cache fitted images and masks;
- precompute static glows/backgrounds;
- invalidate only layers whose bound Signals changed;
- run different layer update cadences;
- keep hidden/background Scenes dormant;
- use semantic dirty rectangles/rows before final framebuffer diff;
- isolate heavy Studio previews from the physical UI process when measurements justify it.

The first scene-compositor prototype must therefore be treated as architecture proof, not a license to apply Pillow blur/resize/file-open operations every frame.

## Architecture decision: semantic layer registry

Every rendered element should be able to expose:
- semantic ID;
- Scene/page;
- bounds;
- Signal source(s);
- Action;
- current quality/live state;
- touch target;
- renderer/style;
- dirty state;
- last render cost;
- privacy class where relevant.

This enables several “thought of everything” features from one contract:
- direct manipulation in Studio;
- touch-target audit;
- clipping/contrast lint;
- data-truth inspector;
- “where did this value come from?”;
- performance heat map;
- responsive translation;
- Theme Manager/foreign-theme translation;
- automated visual regression;
- AI-assisted UI explanation.

## Architecture decision: split shell from content

Beast UI should become a thin runtime shell around registries.

Target decomposition:
- Runtime/Scheduler;
- Navigation/Input Router;
- Scene Registry;
- Overlay/App Registry;
- Preference/Experience Runtime;
- Presentation/Theme adapter;
- framebuffer/display output;
- diagnostics instrumentation.

Existing pages/overlays become registered content modules. Migration is incremental: a legacy page may remain a valid Scene renderer until migrated.

No flag-day rewrite.

## Architecture decision: Studio controller split

Retain the existing lightweight Beast-owned server, but extract route families:
- Experience/visual;
- Packs/Depot;
- roster/lineage;
- Capsules/social;
- operations/diagnostics;
- update/recovery;
- files/library;
- presentation;
- owner/expert policy.

The HTTP handler should dispatch to a versioned route table rather than become the permanent location for new product logic.

## Architecture decision: one Transaction Engine

Generalize the repeated safe-change pattern:

**plan → snapshot → validate → apply → restart impact → probation → verify → commit or rollback → audit**

Use it for:
- Pwnagotchi config edits;
- plugin toggles;
- Pack activation;
- updates;
- presentation ownership;
- Experience apply;
- restore;
- hardware-role changes where applicable.

Individual systems provide adapters; the transaction framework owns lifecycle/provenance.

## Customization target

The architecture should support abundance without turning every install into clutter.

Users should eventually be able to independently choose or edit:
- complete Experiences;
- Scene compositions;
- layouts/Boards;
- data bindings;
- renderer for compatible data;
- Theme/skin;
- palette;
- typography;
- icons;
- creature face/art;
- motion;
- ambient effects;
- transitions;
- boot/shutdown presentation;
- notifications;
- Rare/reveal treatment;
- sound;
- haptic/LED response where hardware exists;
- footer/navigation treatment within functional constraints;
- Field/Dock/Night/display variants.

Curated presets remain valuable, but combinations should come from compatible independent parts rather than requiring every possible combination to be hand-authored.

## “Thought of everything” product behaviors

Several high-leverage features should emerge from the contracts instead of being isolated gimmicks.

### Universal Inspect

Long-press an instrument/value/layer and optionally expose:
- what it is;
- current value;
- live/stale/unavailable;
- source/provider;
- freshness;
- short history;
- what uses it;
- relevant action;
- customize;
- performance cost.

### Design Lint

Studio can automatically flag:
- undersized touch targets;
- clipping;
- poor contrast;
- missing Signal binding;
- unsupported target;
- expensive effect;
- privacy-sensitive public binding;
- unavailable capability;
- layer overlap;
- reduced-motion incompatibility.

### Performance Lens

Show per Scene/layer:
- render ms;
- dirty percentage;
- framebuffer bytes;
- effective FPS;
- CPU/RSS;
- target reference measurement.

### Truth Lens

Developer/Expert overlay showing which visible values are:
- live;
- derived;
- historical/replay;
- stale;
- unavailable.

Production still presents these appropriately; the lens makes correctness inspectable.

### Rewind / Replay

The same Scene contract can later render persisted Expedition/history data in an explicitly labeled replay mode. This makes Memory Vault and Hall of Legends feel alive without inventing telemetry.

## Responsive-display strategy

Do not scale a 480×320 screenshot forever and do not weaken the reference TFT.

Scenes should support:
- target classes;
- constraints/anchors;
- optional target-specific variants;
- minimum touch policy;
- content priority.

An Experience may contain a handcrafted 480×320 variant and a richer phone/800×480/large-display variant while sharing the same Signal/Action semantics.

## Monstergotchi strategy

Monstergotchi should remain a second chapter on the same platform contracts, not a fork.

Lineage/inherited traits can parameterize:
- Face;
- motion;
- palette DNA;
- effect vocabulary;
- Scene accents;
- temperament presentation.

The kernel, Signal/Action/Capability model, persistence, Packs and recovery remain shared.

## Testing strategy for maturity

Add/strengthen:
- schema/version migration tests;
- Scene compile/property/fuzz tests;
- semantic-layer bounds/touch audits;
- golden/perceptual visual regression where useful;
- real-state replay fixtures;
- render performance budgets;
- long-run memory/RSS soak tests;
- repeated theme/Experience swap tests;
- Pack import/privacy fuzzing;
- transaction failure-injection tests;
- target Pi sustained render/write/thermal tests;
- repeated physical Presentation Broker rollback tests.

Source/CI, target/off-screen and physical acceptance remain separate evidence levels.

## Migration sequence

This architecture is specifically designed to avoid a rebuild.

1. Restore the active branch to green and keep PR #9 Draft.
2. Stabilize/cache the new layered compositor and migrate Home as the first Scene proof.
3. Define Signal v1 as metadata around existing StateRegistry rather than replacing it.
4. Define Scene/Layer schema v1 + semantic layer registry.
5. Add Experience Compiler v1 that can compile current Theme/Face/Animation/Board/Deck inputs as a compatibility subset.
6. Extract input/navigation and overlays from `engine.py` behind registries.
7. Extract Studio route groups behind controllers.
8. Migrate Recon/Spectrum/Expedition/Beast into richer Scenes where the new model proves useful.
9. Add Studio direct manipulation, Design Lint and timed TRY ON TFT.
10. Generalize the Transaction Engine and use it for presentation/config/update operations.
11. Add responsive Scene variants and companion/large-display targets.
12. Continue deeper Packs, Hardware Studio, social, recovery and Monstergotchi work on top of the contracts.

At every step existing data and behavior remain valid until migrated.

## Decisions about current scope

Keep:
- Core/UI/Studio separation;
- page/tab/swipe cockpit;
- Apps for depth;
- Packs/Depot;
- Native + Theme Manager + Beast presentation choice;
- progression/roster/lineage;
- Expeditions/Memory;
- PeerDex/social/privacy model;
- optional hardware capability model;
- local-first/offline exchange;
- Owner Sovereignty;
- recovery/update discipline.

Strengthen/generalize:
- State tokens → Signals;
- repeated mutation flows → Transaction Engine;
- themes/pages/effects → Scene/Visual Runtime;
- Experience draft → Experience Compiler;
- UI element knowledge → semantic layer registry;
- current performance metrics → layer/module cost attribution.

Refactor before further growth:
- `beastui/engine.py`;
- `beaststudio/server.py`;
- hard-coded theme-specific visual branches that should become Scene content.

Do not rebuild:
- StateRegistry;
- roster/persistence;
- Packs intake/install safety;
- dependency/provider model;
- Action Broker authorization;
- framebuffer dirty-row writer;
- Pwnagotchi protection boundary.

## Final direction

The target is not “more features”.

The target is a platform where:
- more features do not make the core brittle;
- more customization does not require more hard-coded branches;
- richer visuals do not require fake data;
- more hardware does not burden users who do not own it;
- more power does not weaken rollback/recovery;
- more presentation engines do not fight over the TFT;
- more display sizes do not destroy the 480×320 experience;
- years of progression/history survive UI redesigns.

That is the architecture most likely to make Beastagotchi feel unusually complete while still being understandable and maintainable years later.
