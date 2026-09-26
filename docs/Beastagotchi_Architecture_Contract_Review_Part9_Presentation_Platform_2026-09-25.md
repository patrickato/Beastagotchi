# Beastagotchi Architecture Contract Review — Part 9: Presentation Platform

**Date:** 2026-09-25  
**Status:** proposed foundation contract; discussion-quality, not yet implementation freeze  
**Inputs:** Architecture Parts 1-8, completed Structure Deep Dive, current v0.19 SceneRuntime/
Experience work, Gate-1 visual reconstruction, PlatformProfile, touch architecture, Presentation
Broker direction, visual north-star archive, owner open-ended visual-system guidance.

---

# 1. Purpose

Beastagotchi's presentation system must support:

- a 480x320 resistive-touch reference TFT;
- smaller constrained displays;
- larger HDMI/DSI displays;
- browser/Studio surfaces;
- remote exact mirrors;
- Native Pwnagotchi presentation;
- Korrie71 Theme Manager coexistence;
- radically different Experience visual grammars;
- creature-centered and instrument-centered layouts;
- overlays, drawers, Apps, pages, cinematics and Doctor interventions;
- future community Experiences/Surfaces;
- many more pages/features than can fit in one primary navigation strip.

It must do this without collapsing into:

- one card-grid dashboard recolored many ways;
- one fixed page-count ceiling;
- one renderer function per feature forever;
- one giant input priority chain;
- multiple framebuffer owners;
- decorative fake telemetry;
- desktop-web assumptions forced onto an SPI TFT;
- "responsive" claims that are really naive image scaling.

Stable principle:

> **Surface owns the semantic job. Experience owns the visual grammar.**

and:

> **Presentation may transform truth; it may not invent truth.**

---

# 2. Presentation concepts remain distinct

Do not collapse these concepts.

## Physical owner

Who currently controls the physical framebuffer/input device.

Examples:
- Native Pwnagotchi;
- Korrie71 Theme Manager;
- Beast UI.

Exactly one physical owner at a time.

## Presentation source

What semantic visual source is currently being shown.

Examples:
- Beast Scene;
- Native Pwnagotchi frame;
- Theme Manager output;
- cinematic;
- recovery/critical Surface.

## Surface

A user-visible destination/state with semantics, availability and input policy.

## Scene

A renderable composition for a Surface/state.

## Experience

A coherent presentation grammar that can supply Scene/layout/motion/creature/Doctor variants.

## Choreography

A bounded sequence of presentation stages driven by real events/state and optional owner interaction.

## PresentationSession

Read model of current presentation state.

## Remote viewer/controller

A client observing or controlling presentation remotely.

Remote viewing is not physical ownership.

---

# 3. Surface is the primary presentation abstraction

A Surface is the semantic unit of user-visible presentation.

Possible kinds:

- page;
- overlay;
- drawer;
- transient;
- cinematic;
- workspace;
- native/external;
- inspector;
- setup/acceptance;
- recovery.

SurfaceSpec may declare:

- stable id;
- kind;
- semantic purpose;
- label/category;
- navigation group;
- modality;
- availability;
- Scene/renderer reference;
- Experience variant hooks;
- target/display support;
- required Signals;
- required Capabilities;
- actions/procedures exposed;
- input policy;
- dismiss/back policy;
- layering/z policy;
- privacy class;
- help/Doctor links;
- accessibility metadata;
- source/provenance.

A Surface does not itself gain mutation authority by referencing an Action.

---

# 4. Surface Registry

Use one typed Surface registry instead of unrelated page/app/overlay/cinematic registries.

Filtered views may expose:

- primary pages;
- App destinations;
- overlays;
- cinematic Surfaces;
- Doctor Surfaces;
- workspaces.

This avoids registry explosion while keeping type-specific validation.

A Surface may be:

- primary;
- secondary;
- app-only;
- contextual;
- event-triggered;
- progression-unlocked;
- hidden;
- remote-only;
- large-display-only.

The number of available Surfaces is not limited by primary navigation capacity.

---

# 5. Surface availability

Use explicit availability states such as:

- ready;
- degraded;
- preview;
- coming_soon;
- unavailable;
- hidden.

A non-ready Surface exposes an honest reason.

Examples:
- missing capability;
- content not installed;
- feature not released;
- physical owner conflict;
- display target unsupported;
- progression prerequisite.

Do not render a control as active if it silently does nothing.

---

# 6. Surface Session

A visible Surface instance has runtime state separate from SurfaceSpec.

Candidate SurfaceSession fields:

- Surface id;
- instance/session id;
- opened from;
- target;
- z/layer;
- modal state;
- selected item;
- scroll/page offset;
- detail id;
- input focus;
- transient state;
- opened timestamp;
- Scene variant;
- Experience;
- state generation.

Feature-specific session state stays with that Surface rather than accumulating as permanent fields
inside one giant BeastUI object.

---

# 7. Surface Stack

Presentation composes active Surfaces as a stack.

Illustrative stack:

    critical/recovery
    cinematic
    modal overlay
    drawer/context
    primary Surface
    ambient/background

Stack semantics determine:

- z-order;
- modality;
- input capture;
- visual composition;
- dismiss/back behavior;
- privacy masking;
- screenshot/mirror inclusion.

Priority becomes declarative instead of hidden in code ordering.

---

# 8. Navigation Controller

Navigation is separate from rendering and input acquisition.

NavigationController owns:

- primary carousel index/group;
- back/close;
- Surface deep links;
- App launcher destination;
- context/deck navigation;
- return stack;
- progression/unlock destination;
- remote navigation requests.

The existing swipe/page model remains first-class.

Apps deepen the system; they do not replace pages.

Primary navigation remains curated rather than attempting to expose every possible Surface.

---

# 9. Input acquisition versus input routing

Keep physical input acquisition separate from UI semantics.

TouchInput/device layer handles:

- Linux input;
- calibration;
- filtering;
- gesture recognition;
- noise/debounce;
- raw physical evidence.

InputRouter handles:

- logical gesture/event;
- active Surface stack;
- hit regions;
- modality;
- focus;
- action/deep-link dispatch.

This separation permits:

- physical touch;
- buttons;
- keyboard;
- rotary/encoder;
- remote input;
- future companion input;

to share semantic routing without duplicating feature logic.

---

# 10. Input envelope

Normalized input should carry:

- source;
- timestamp;
- gesture/type;
- logical coordinates;
- device/session;
- operator/session where remote;
- modifier/button info;
- confidence where relevant.

Possible source classes:

- physical touch;
- physical button;
- keyboard;
- local hardware input;
- Studio;
- remote authenticated client;
- automation/test.

Input source does not determine mutation authority.

---

# 11. Local-presence input

Some interactions may require physical/local presence.

Examples:

- dangerous owner-mode confirmation;
- display/touch calibration acceptance;
- recovery confirmation;
- certain hardware tests;
- credential-sensitive setup;
- physical presentation ownership handoff.

InputRouter/Action policy can reject remote equivalents.

Remote control is useful, but not every physical-local interaction should become remotely reproducible.

---

# 12. Touch contract

The 480x320 resistive target remains a first-class handcrafted environment.

Touch design should support:

- sufficiently large targets;
- deliberate spacing;
- drag/swipe disambiguation;
- long-press only where useful;
- visible press acknowledgement;
- consistent back/dismiss behavior;
- scroll versus page-swipe arbitration;
- glove/stylus/finger tolerance where possible;
- calibration independent from layout.

Do not copy phone touch assumptions blindly onto a resistive panel.

Physical acceptance remains authoritative.

---

# 13. DisplayProfile

DisplayProfile describes presentation-relevant target facts.

Possible fields:

- logical size;
- physical pixel size;
- orientation;
- pixel format;
- color/depth constraints;
- physical dimensions/DPI if known;
- touch/input capabilities;
- framebuffer write behavior;
- measured full-frame cost;
- measured dirty-write cost;
- practical animation cadence;
- brightness/backlight capability;
- multiple-display role;
- safe margins;
- target class.

DisplayProfile is evidence/guidance, not a fixed board whitelist.

---

# 14. PlatformProfile relationship

PlatformProfile provides broader compute/display guidance.

Presentation Compiler consumes:

- compute tier;
- display class;
- resource budget;
- target capabilities;
- owner preferences;
- Experience requirements.

Board identity is a hint.

Measured behavior and capabilities are authoritative.

---

# 15. Responsive/adaptive presentation

Do not call a 480x320 bitmap stretched to 800x480 a responsive Experience.

A Surface/Experience may define target variants:

- constrained;
- reference;
- medium;
- large;
- desktop;
- portrait/specialized.

Variants may change:

- hierarchy;
- density;
- number of simultaneous facts;
- layout topology;
- typography;
- touch affordances;
- graph/detail depth.

Semantic Surface identity remains the same.

---

# 16. Graceful target fallback

If no native variant exists:

- use a declared compatible fallback;
- letterbox/scale only when explicitly acceptable;
- reduce detail honestly;
- expose unsupported/degraded reason;
- preserve core semantic controls.

Do not imply native target quality where only compatibility scaling exists.

---

# 17. Experience

Experience is a coherent presentation intent layer.

It may control:

- structural layout grammar;
- density;
- hierarchy;
- creature presence;
- motion language;
- ornament/material vocabulary;
- information emphasis;
- Doctor relationship;
- input feel;
- utility/playfulness balance;
- alert language;
- sound/haptic behavior later.

Experience does not own operational truth.

---

# 18. Experience DNA

Experience DNA remains open-ended.

Built-in axes/families are organizing vocabulary, not a closed taxonomy.

Community content may add namespaced values.

Validation should reject malformed/incompatible definitions, not aesthetic novelty.

Existing named themes remain useful presets/references.

They are not the root categories of all future presentation.

---

# 19. Semantic Surface, varied grammar

The same semantic Surface may look fundamentally different across Experiences.

Example: System.

- Forge: machine service chassis;
- Observatory: measurement/diagnostic station;
- Habitat: living-organism health/environment interpretation;
- Monolith: sparse high-value status;
- Atlas: expedition equipment/field-log treatment;
- future community Experience: entirely different valid grammar.

The underlying system facts and Actions remain canonical.

This prevents feature logic duplication while avoiding visual sameness.

---

# 20. Experience variant resolution

Experience Compiler resolves a Surface presentation from:

- SurfaceSpec;
- Experience DNA;
- target DisplayProfile;
- PlatformProfile;
- Capability availability;
- content availability;
- owner preferences;
- resource policy;
- accessibility preferences.

The output is a presentation plan/Scene target.

Compilation is read-only.

Applying a preference is separate.

Physical ownership mutation is separate again.

---

# 21. Scene

Scene is a renderable semantic composition.

Scene definition may include:

- layers;
- primitives;
- assets;
- Signal bindings;
- layout constraints;
- bounds;
- update classes;
- resource classes;
- input regions;
- privacy;
- reduced-motion behavior;
- semantic inspect metadata.

Scene does not poll hardware directly.

Scene consumes canonical state/signals/context.

---

# 22. Scene layers

Layer metadata should include enough information for:

- incremental rendering;
- Studio inspection;
- exact mirror;
- accessibility;
- privacy;
- resource budgeting.

Current SceneLayerSpec direction is strong:

- id/kind;
- bounds;
- update class;
- resource class;
- Signal bindings;
- privacy;
- touch;
- reduced-motion;
- decorative classification.

Protect and extend this.

---

# 23. Dirty-region pipeline

Preferred pipeline:

    Signal/Event/Input change
          |
    identify affected Scene layers
          |
    invalidate dirty bounds
          |
    compose changed regions/layers
          |
    final logical frame
          |
    framebuffer row/span diff
          |
    physical write

Framebuffer diff remains the physical safety net.

Long-term goal is to avoid generating unchanged full-frame content in the first place.

---

# 24. Render causality

Render only because something relevant changed.

Valid causes:

- Signal/state change;
- Event;
- input/selection;
- animation/choreography phase;
- transient notice;
- Surface transition;
- explicit mirror/preview request.

A static Surface does not redraw merely because an FPS ceiling exists.

---

# 25. Scene primitives

Declarative Scenes use a safe primitive/component vocabulary.

Examples:

- text;
- metric;
- gauge;
- graph;
- icon;
- image;
- face/creature;
- progress;
- list/table;
- field diagram;
- waveform;
- timeline;
- status mark;
- container/mask;
- particle/effect;
- custom registered primitive.

Do not force every Experience into generic cards.

Primitives are capabilities, not mandated layout patterns.

---

# 26. Executable visual primitives

New executable primitives are allowed for genuinely new grammar.

They use Part 8 trusted registration/handles.

A primitive cannot:

- poll arbitrary hardware;
- bypass privacy;
- mutate the system;
- gain raw Core access;
- create untracked permanent work loops.

It renders from declared inputs/context.

---

# 27. Built-ins dogfood the presentation path

Long-term convergence target:

- built-in Experiences;
- community Experiences;
- ordinary Surfaces;

share the Scene/Surface/Experience contracts where practical.

Do not preserve a permanently privileged Python-only built-in path that community content can never match.

However, do not destroy current visual fidelity merely for architectural purity.

Migrate only when the declarative/compiled path can preserve or improve real output.

---

# 28. Visual north-star rule

The early concept images/current north-star references remain inspiration, not pixel-perfect specs.

Acceptance is based on:

- actual renderer output;
- semantic accuracy;
- Experience differentiation;
- usability;
- physical TFT behavior;
- perceived quality.

No generated mockup supersedes actual implementation truth.

---

# 29. Structural differentiation rule

Different Experiences should not be considered meaningfully distinct merely because of:

- palette;
- border style;
- scanline;
- font;
- icon set.

Meaningful differentiation may include:

- grayscale silhouette;
- information hierarchy;
- focal object;
- density;
- creature scale/presence;
- spatial composition;
- motion;
- Doctor integration;
- navigation emphasis.

CI can preserve silhouette/structural proof alongside color renders.

---

# 30. Creature as presentation participant

The Beast may be:

- primary focal subject;
- companion;
- observer;
- instrument operator;
- ambient inhabitant;
- minimized status presence;
- temporarily absent where appropriate.

Do not force one mascot placement into every Experience.

But Beast identity should remain intentionally represented across the product where the Experience calls for it.

---

# 31. Choreography

Choreography presents bounded sequences for meaningful events.

Examples:

- Genesis;
- hatch/assembly/awakening;
- synthesis/breeding;
- Monster reveal;
- mutation reveal;
- Ascension;
- Rare Moments;
- major Achievement;
- Doctor treatment/recovery;
- update/recovery completion.

Choreography consumes semantic truth; it does not create that truth.

---

# 32. ChoreographySpec

May declare:

- stable id/version;
- trigger;
- stages;
- Scene/Surface per stage;
- duration/completion condition;
- owner interaction points;
- skippable policy;
- acknowledgement;
- optional/premium content;
- resource class;
- reduced-motion fallback;
- lightweight fallback;
- rarity/tier variants;
- completion Event.

Truth must survive skipped/failed presentation.

---

# 33. Enhancement ladder

Recommended pattern: presentation objects can declare a semantic core plus enhancement layers.

## Essential
- result identity;
- critical text;
- owner-required action;
- semantic state.

## Standard
- normal creature animation;
- ordinary effects;
- richer layout.

## Enhanced
- particles;
- premium media;
- complex lighting;
- sound/video;
- extended cinematic.

Under resource/content constraints Beast can step down the enhancement ladder without changing semantic truth.

This is more precise than globally turning graphics down.

---

# 34. Reduced motion

Reduced-motion is a first-class presentation preference.

Each animated/choreographed Surface should have a meaningful fallback.

Reduced motion must preserve:

- event significance;
- progress/result;
- owner controls;
- hierarchy.

Do not simply freeze mid-animation.

---

# 35. Accessibility

Presentation contracts should support future:

- reduced motion;
- high contrast;
- larger text;
- alternate color dependence;
- touch-target enlargement;
- screen/mirror assistive metadata;
- keyboard/button navigation;
- left/right-handed layout variants where useful.

Do not hardwire accessibility into one Experience aesthetic.

Experience may render the same accessibility semantics differently.

---

# 36. Doctor presentation

Doctor owns semantic health interpretation.

Experience owns Doctor's visual grammar.

Examples:

- Forge: machine oscillator/service bay;
- Observatory: trace/measurement;
- Habitat: organic vital sign;
- Monolith: restrained health mark;
- Atlas: field medical/status notation.

The same canonical Doctor state can produce different presentation.

Doctor never writes pixels directly.

---

# 37. Doctor heartbeat affordance

A small persistent health affordance may be available across compatible Experiences.

Semantic states may include:

- healthy;
- attention;
- critical;
- observing/recovering.

Exact colors/cadence are presentation policy.

The heartbeat is a deep link into Doctor/Patient Chart, not a separate health authority.

---

# 38. Presentation preferences

Use one shared PresentationPreferenceStore.

It owns:

- schema;
- defaults;
- validation;
- atomic writes;
- migration;
- history/backup;
- generation;
- preference-change Event.

Consumers include:

- Beast UI;
- Studio;
- remote clients;
- roster per-Beast preference adapter.

Do not let each client serialize the same preference file independently.

---

# 39. Preference versus mutation

Safe presentation preferences may be changed through the preference store.

Examples:

- Experience;
- face;
- palette;
- reduced motion;
- layout density;
- context deck;
- selected visualizer.

System-changing operations remain Actions/Transactions:

- physical owner switch;
- enable/disable plugin/service;
- install dependency;
- provider activation;
- display driver/system config.

---

# 40. Per-Beast presentation memory

Each Beast may remember presentation affinities/preferences.

Switching active Beast may restore:

- Experience;
- face;
- motion;
- aura/presentation variant.

If content is unavailable:

- use safe fallback;
- preserve the preferred id;
- explain missing dependency;
- do not erase preference.

---

# 41. Beast Links / semantic deep links

Presentation navigation should use semantic links rather than hard-coded URL assumptions.

A Beast Link may target:

- Surface;
- Doctor finding;
- Signal;
- Capability;
- setting;
- Pack/content;
- Procedure;
- Backup/Recovery action;
- device/hardware;
- Experience editor;
- Expedition replay.

The same semantic link can render as:

- TFT navigation;
- Studio hyperlink;
- remote/phone link;
- QR/local support link.

Authorization remains target/action-specific.

---

# 42. Presentation ownership

Physical ownership remains explicit.

Conceptual owners:

- pwn-native;
- korrie-theme-manager;
- beast-ui.

Only one stack owns the physical framebuffer/input hook at once.

A presentation source/render preview is not ownership.

---

# 43. Presentation Broker

Presentation Broker owns:

- desired physical owner;
- active physical owner;
- transition status;
- generation;
- request provenance;
- error state.

Resolution/planning is separate from execution.

The Broker does not lie about active ownership merely because a preference says Beast.

---

# 44. Physical owner handoff

Physical owner switching is consequential and uses Transaction.

Lifecycle:

    plan
      ->
    snapshot/current owner evidence
      ->
    release current owner
      ->
    acquire candidate
      ->
    probation
      ->
    verify framebuffer/input/health
      ->
    commit
        or rollback

Repeated real hardware switching tests are required before automatic ownership changes are trusted.

---

# 45. Ownership rollback

A failed candidate must not strand the TFT where recoverable.

Rollback plan may restore:

- prior service state;
- prior presentation owner;
- input ownership;
- known-good display config.

Headless/CLI recovery remains available.

---

# 46. Native Pwnagotchi presentation

Native mode is first-class.

Where possible preserve the actual native/upstream composed frame rather than reconstructing a fake approximation.

Native frame source remains useful for:

- compatibility;
- exact upstream look;
- safe fallback;
- comparison/debug.

Upstream path/version knowledge should eventually live behind PwnagotchiAdapter rather than UI hardcoding.

---

# 47. Korrie71 Theme Manager

Theme Manager is an alternate presentation engine, not an enemy or something Beast should absorb blindly.

Interop may include:

- capability/version probe;
- token/stat bridge;
- visual asset interoperability;
- managed presentation ownership handoff.

Do not enable real physical switching until release/acquire/verify/rollback contracts are proven.

---

# 48. PresentationSession

Introduce/standardize a shared read-only PresentationSession.

Candidate fields:

- physical owner;
- presentation source;
- active primary Surface;
- Surface stack;
- active Experience;
- target DisplayProfile;
- preference generation;
- current Scene id/generation;
- current choreography/transient;
- render phase/timebase;
- input focus/source;
- last frame sequence;
- render/write performance;
- mirror/control state.

PresentationSession describes presentation truth only.

It does not duplicate operational telemetry.

---

# 49. Exact Compositor Preview

Studio may render the same compositor/Scene code from canonical state to preview a target.

This is valuable and testable.

But it is not automatically the exact current physical frame.

Call it exactly what it is:

**Exact Compositor Preview.**

---

# 50. Exact Runtime Mirror

A true mirror follows current PresentationSession and final logical frame/Scene state.

Possible features:

- view-only current frame;
- Surface/Scene metadata;
- inspect under pointer;
- signal bindings;
- dirty-region/performance overlay;
- remote input when separately authorized.

Mirror and control permissions remain separate.

---

# 51. Remote viewing

Remote viewing should be possible without granting remote control.

View modes may include:

- exact physical logical frame;
- semantic reconstructed view;
- selected Surface preview;
- performance/inspection view.

Privacy policy may mask sensitive layers for remote viewers.

---

# 52. Remote control

Remote control:

- requires authenticated/authorized operator/session;
- uses InputRouter;
- labels source;
- obeys local-presence restrictions;
- cannot silently bypass Action consent;
- may be disabled while still permitting viewing.

Do not implement remote control as raw mouse injection into framebuffer coordinates without semantic/session context.

---

# 53. Multi-display

Multiple displays may receive roles rather than naive cloning.

Possible roles:

- primary cockpit;
- secondary status;
- marquee/ambient;
- remote/operator;
- large detailed workspace;
- portrait/specialized view.

PresentationSession may track per-target Surface/Scene.

One physical owner rule applies per physical target/resource, not necessarily one owner for every display in the universe.

This should be generalized carefully when multi-display execution is implemented.

---

# 54. Large-screen companion behavior

Larger targets can show more detail rather than merely enlarging the 480x320 layout.

Possible enhancements:

- richer graphs;
- simultaneous context panels;
- larger history;
- detailed maps;
- full Doctor evidence;
- multi-pane Studio-like views.

Do not force the TFT's information density ceiling onto capable displays.

---

# 55. Small-display behavior

Constrained displays should preserve:

- essential state;
- creature identity;
- alerts;
- quick controls;
- navigation.

Reduce:

- simultaneous facts;
- decorative motion;
- graph density;
- secondary labels.

Do not create a separate crippled product.

---

# 56. Presentation privacy

Scene layers carry privacy metadata.

Remote mirror/screenshot/export can:

- include;
- mask;
- omit;
- summarize;

layers according to destination policy.

A visual extension cannot downgrade Signal privacy.

Example:
GPS coordinates may be visible locally but masked in a support screenshot.

---

# 57. Screenshot/gallery evidence

CI-generated galleries are architectural test evidence.

They may verify:

- all registered primary Surfaces render;
- no exceptions;
- Experience structural differentiation;
- target geometry;
- privacy sanitization;
- reduced-motion fallback;
- content-missing fallback;
- target variants.

Gallery success is not physical acceptance.

---

# 58. Pixel and structural review

Visual acceptance can use multiple evidence forms:

- actual PNG review;
- grayscale silhouette comparison;
- semantic Scene manifest;
- dirty bounds;
- text overflow detection;
- hit-target audit;
- color/contrast checks;
- performance telemetry.

Do not accept layouts solely because unit tests say coordinates are valid.

---

# 59. Physical acceptance

Real TFT acceptance remains necessary for:

- readability;
- resistive-touch feel;
- glare;
- viewing angle;
- brightness;
- QR scanning;
- animation perception;
- input latency;
- frame-write behavior;
- CPU/thermal behavior;
- physical polish.

Off-screen acceptance and physical acceptance are distinct gates.

---

# 60. Render/performance observability

Per Scene/Surface expose:

- compose time;
- layer render time;
- dirty region;
- full-frame fallback reason;
- framebuffer bytes written;
- frame sequence;
- cache use;
- dropped/late animation frames;
- resource mode.

This allows Doctor/perf tools to diagnose presentation without guessing.

---

# 61. Presentation failure behavior

If a Scene/renderer fails:

- keep Core alive;
- capture bounded error evidence;
- fall back to safe Surface/renderer;
- mark Experience/extension unhealthy where appropriate;
- preserve navigation/recovery path.

An optional broken Experience must not brick the TFT.

---

# 62. Safe fallback Experience

Ship a lightweight, project-owned fallback Experience/Surface set.

It should:

- use minimal dependencies;
- show essential canonical state;
- expose Doctor/recovery;
- operate under constrained resource mode;
- remain available even when optional content is broken/missing.

This is the presentation equivalent of a recovery shell.

---

# 63. Presentation lifecycle

Presentation components follow explicit lifecycle:

    discover/register
      ->
    compile/resolve
      ->
    instantiate SurfaceSession
      ->
    activate/push stack
      ->
    render/update
      ->
    suspend/background
      ->
    dismiss/pop
      ->
    release caches/subscriptions

Inactive Surfaces should not retain unnecessary Signal subscriptions/decoded assets forever.

---

# 64. Subscription locality

Active Scene/Surface declares required Signals.

Runtime subscribes only to:

- active stack;
- immediate neighbor/prefetch needs;
- critical global presentation signals.

Do not dirty every Surface on every State change.

This links Part 5 working-set policy directly to presentation.

---

# 65. Aha: Surface semantics prevent Experience fragmentation

Without a semantic Surface contract, each Experience can accidentally become its own application.

Then:
- Doctor works differently everywhere;
- actions get duplicated;
- navigation breaks;
- community Experiences fork feature logic.

Surface semantics keep the product coherent.

Experience variants stay radically creative while sharing:
- truth;
- Actions;
- Procedures;
- deep links;
- availability;
- history;
- input policy.

---

# 66. Aha: Experiences are not skins; they are presentation compilers

Treat an Experience as a rule/grammar for translating semantic Surfaces into target Scenes.

This explains why palette swapping was never enough.

It also means a future Experience can transform:
- hierarchy;
- focal point;
- density;
- motion;
- creature relationship;
- Doctor affordance;
- transitions;

without changing the underlying feature.

---

# 67. Aha: enhancement ladders beat global quality modes

A global low-graphics switch is too blunt.

If each Scene/Choreography identifies:

- semantic essential layers;
- standard layers;
- optional enhancements;

the Governor can shed expensive decoration precisely.

Example:
Doctor critical warning never disappears, but its ambient particles can.

Monster reveal still communicates the Monster/result even if premium video is unavailable.

This preserves meaning under pressure.

---

# 68. Aha: PresentationSession can become the universal visual debugging seam

With one PresentationSession + Scene metadata stream, we can support:

- exact mirror;
- Studio inspector;
- physical support session;
- touch replay;
- automated screenshot capture;
- performance profiling;
- Doctor display diagnosis;
- remote assistance;
- regression reproduction.

That can replace several future bespoke debugging paths.

---

# 69. Migration from current v0.19

Incremental path:

1. Formalize SurfaceSpec/SurfaceRegistry over existing pages/Apps/overlays without changing visuals.
2. Add SurfaceSession/SurfaceStack adapters around current overlay state.
3. Introduce InputRouter while retaining current TouchInput.
4. Introduce NavigationController around current page/swipe behavior.
5. Centralize PresentationPreferenceStore.
6. Standardize PresentationSession read model.
7. Migrate current SceneRuntime metadata into the common Surface path.
8. Move one stable page/Experience pair through compiled declarative Scene path while preserving pixels.
9. Expand built-in Experience dogfooding gradually.
10. Add ChoreographySpec around Monster reveal/Rare/Doctor flows.
11. Add enhancement ladders/reduced-motion fallbacks.
12. Add DisplayProfile measured target data.
13. Implement Exact Runtime Mirror after PresentationSession is stable.
14. Implement physical ownership executor only through proven Transaction adapters.
15. Add responsive native variants progressively; do not claim them before they exist.
16. Keep current imperative renderers as adapters until equivalent compiled fidelity is demonstrated.

No flag-day UI rewrite is required.

---

# 70. Presentation invariants

1. Presentation never invents operational truth.
2. Surface owns semantic job; Experience owns visual grammar.
3. Primary navigation is curated, not an architectural page ceiling.
4. App depth does not replace page/swipe navigation.
5. Surface priority/input precedence is explicit, not code-order accident.
6. Touch acquisition is separate from semantic routing.
7. Remote view does not imply remote control.
8. Remote control does not bypass local-presence or Action policy.
9. Physical ownership is distinct from presentation source.
10. Exactly one physical owner controls a given framebuffer/input resource at a time.
11. Owner switching is transactional and rollback-aware.
12. Experience taxonomy remains open-ended.
13. Different Experiences must be able to differ structurally, not merely chromatically.
14. Semantic Surface logic is not duplicated per Experience.
15. Scene consumes canonical Signals/State rather than polling hardware.
16. Scene dirty regions drive composition; framebuffer diff remains final physical safety net.
17. Static Surfaces do not redraw without cause.
18. Optional visual layers are shed before semantic truth.
19. Reduced motion preserves meaning.
20. Important lifecycle events retain lightweight fallbacks.
21. Built-ins use public presentation contracts where practical.
22. Community Scenes do not gain mutation/privacy authority through presentation metadata.
23. Presentation preferences are not system mutation.
24. Per-Beast preferences do not alter progression truth.
25. Native Pwnagotchi remains first-class.
26. Theme Manager coexistence remains explicit.
27. Exact Compositor Preview is not falsely called Exact Runtime Mirror.
28. Gallery/CI evidence is not physical TFT acceptance.
29. Missing optional content degrades gracefully.
30. Broken optional Experience does not brick the TFT.
31. Safe fallback presentation remains locally available.
32. Display responsiveness is claimed only where native/adaptive variants actually exist.
33. PresentationSession does not become a duplicate source of operational telemetry.
34. Inactive Surfaces release unnecessary subscriptions/assets.
35. Physical measurements define real display cadence and touch quality.

---

# 71. Part 9 conclusion

The presentation platform should let Beastagotchi become visually enormous without becoming
structurally incoherent.

The critical separation is:

- **Surface:** what the user is doing/seeing semantically;
- **Experience:** how that meaning is expressed;
- **Scene:** the target composition;
- **Choreography:** how meaningful events unfold over time;
- **PresentationSession:** what is actually active now;
- **Presentation Broker:** who physically owns the device;
- **InputRouter:** where interactions go.

That architecture preserves the current page/swipe identity while allowing dramatically different
visual worlds, more displays, remote mirrors, richer cinematics and community-created presentation.

The next Architecture Contract Review should define **Provisioning, Update, Recovery & Reproducibility**:
Provisioner, Distribution Profiles/BOM, first boot, upgrades, known-good checkpoints, Recovery Vault,
restore transactions, upstream Pwnagotchi updates, support bundles, uninstall/detach, artifact
signing/provenance and how the system becomes installable by ordinary users without losing the
current rollback-first discipline.
