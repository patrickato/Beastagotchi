# Korrie71 Theme Manager Reintegration Audit — 2026-09-23

Status: design/interop audit, not an implementation claim.

Reviewed upstream:
- https://github.com/Korrie71/pwnagotchi-theme-manager
- current public `main` as reviewed 2026-09-23
- README, `theme_manager.py`, installer behavior, documented tests and UI/runtime behavior

This audit asks a specific question: now that Theme Manager has grown substantially,
what should Beastagotchi **reuse, translate, interoperate with, or learn from** without
turning Beast into a duplicate monolithic Theme Manager?

## Executive conclusion

Theme Manager has become much more than a recoloring plugin. It is now a compact
presentation/workshop system with a theme DSL, scenery/effects, mood-reactive visuals,
face packs, a direct-manipulation web editor, touch controls, plugin/system views,
cracking/radar views, achievements, thermal/display policies, partial framebuffer
updates, caching and a substantial test surface.

That strengthens—not weakens—the existing Beastagotchi architecture decision:

1. **Do not merge the two renderers wholesale.**
2. **Do make Theme Manager a first-class Presentation Engine behind the Beast
   Presentation Broker.**
3. **Promote the strongest reusable ideas into neutral contracts and Beast-native
   services** so Beast UI, Theme Manager and future renderers can all benefit.
4. **Translate compatible Theme Manager assets into Beast Packs/Experiences where
   fidelity is possible; launch the Theme Manager engine when exact fidelity is
   required.**
5. Keep Beast Core authoritative for telemetry, actions, persistence, progression,
   recovery and capability state so the two projects do not duplicate collectors or
   disagree about truth.

## What Theme Manager now does that matters to Beast

Observed upstream capabilities include:

- JSON themes with palette, gradients, per-element colors and bounded FPS;
- effects such as glow, scanlines, vignette, noise, pulse, rainbow, glitch, rain,
  stars, borders and scene backgrounds;
- many scene families including environmental, seasonal, space/console and
  vaporwave/pixel identities;
- custom text with live placeholders;
- mood-reactive colors/effects and handshake reaction;
- PNG/GIF face packs;
- browser editor with live preview, drag-to-position and click-to-recolor;
- touch theme switching, element movement, plugin toggles, system controls,
  achievements, cracking and radar pages;
- scheduled/idle dimming, warnings and optional thermal shutdown behavior;
- timed theme trial with automatic revert;
- static-render caching and partial/changed-row framebuffer writes;
- lazy/TTL-backed live-value providers;
- explicit theme validation bounds and fuzz/regression tests;
- install/uninstall behavior that backs up config and preserves user themes unless
  purge is explicitly requested;
- a repository privacy scan intended to keep personal data out of published content.

The main implementation is still concentrated in one large Python plugin, which is a
good reason for Beast **not** to copy its internal structure even when borrowing ideas.

## High-priority reintegrations

### 1. Dirty-region / changed-row physical framebuffer writer

**Recommendation: adopt the technique, not the implementation coupling.**

Theme Manager's partial-row writes directly address a real SPI-display cost. Beast
already measures render/write costs, so the next step should be a reusable physical
writer layer:

`compose -> frame diff -> dirty rows/rectangles -> RGB565 write -> metrics`

Suggested Beast components:
- `DirtyRegionPlanner`
- `FrameDiffWriter`
- full-frame fallback after I/O error or excessive dirty coverage
- metrics: dirty-row %, dirty-pixel %, bytes written, compose ms, write ms, frame
  deadline misses and full-refresh count

This should feed Resource Governor/Operations rather than live only inside Beast UI.

### 2. Canonical live token registry

Theme Manager's lazy placeholders are a strong UX concept: only fetch a value if the
active text asks for it, with TTLs for slower providers.

Beast can do a better version because Beast Core already has canonical state.

Add a `TemplateTokenRegistry` mapping safe tokens to canonical state keys/derived
formatters, for example:

`{temp}`, `{cpu}`, `{gps}`, `{sats}`, `{battery}`, `{beast.level}`,
`{beast.name}`, `{expedition.distance}`, `{peer.count}`, `{capture.total}`

Rules:
- no duplicate polling from the renderer;
- missing/stale data renders unavailable honestly;
- tokens declare sensitivity and publication scope;
- user text is length/rate bounded;
- the same registry can serve Themes, Boards, Context Decks, notifications,
  Experiences and future companion surfaces.

### 3. Visual Effects / Scene primitive contract

Beast Theme Packs currently describe structural properties and Beast Animation Packs
describe bounded face motion. Theme Manager demonstrates that a compact declarative
effects vocabulary creates much stronger identities.

Create a Beast-native declarative effect layer with bounded primitives such as:
- scanline
- vignette
- glow
- noise/grain
- pulse
- color-cycle/rainbow
- glitch
- particle/rain/star field
- border
- scene/background layers

Each effect should declare:
- static/animated;
- estimated resource/thermal class;
- update rate;
- cacheability;
- target layer;
- accessibility/reduced-motion behavior.

Scene definitions should live in Packs rather than become an ever-growing hardcoded
core list. This is a direct path toward the genuinely different WOPR, LCARS,
sonar/submarine, field-computer, aircraft, retro-terminal and other Experiences the
project wants.

### 4. Timed physical preview with automatic rollback

Beast Studio already uses draft -> preview -> explicit APPLY. Theme Manager adds a
useful physical safety pattern: temporarily try a visual state and automatically
revert.

Add:
- `TRY ON TFT 30s`
- visible countdown
- `KEEP` / `REVERT NOW`
- automatic rollback if Studio disconnects, renderer fails, or timeout expires

Use the existing Action/transaction/recovery machinery. This is especially valuable
for themes, layouts, Experiences and later presentation-engine switching.

### 5. Direct-manipulation Studio editor

Theme Manager's drag-to-place and click-to-recolor workflow is materially better than
forcing users to edit every visual property through forms.

Beast Studio should eventually provide:
- drag/reposition;
- resize where the widget supports it;
- snap/grid/alignment aids;
- 480x320 safe-area and touch-target overlays;
- click a semantic layer/widget to inspect its source and styling;
- theme-role palette editing;
- responsive preview targets;
- undo/redo;
- all edits remain Studio drafts until explicit apply.

Important: Beast renderers should expose **semantic element/layer IDs directly** rather
than infer ownership by comparing pixels as Theme Manager must do around Pwnagotchi.

### 6. Theme Manager as a real Presentation Engine adapter

The existing Presentation Broker concept should now become a concrete adapter
contract rather than a one-off plugin toggle.

Proposed neutral interface:

- `capabilities()`
- `status()`
- `prepare_release()`
- `release()`
- `acquire(profile=None)`
- `health()`
- `snapshot()`
- `preview(asset)`
- `events()`

Theme Manager adapter behavior should prefer an upstream-supported
`managed`/`web_only`/standby mode if Korrie adds one. Until then, the whole-plugin
toggle remains only a compatibility fallback.

This contract can also serve Native Pwnagotchi, Beast UI and future full-screen apps.

### 6A. Existing `STAT_SOURCE` hook may be the lowest-friction telemetry bridge

Current Theme Manager source already contains a module-level `STAT_SOURCE` callback
used by its lazy live-token formatter for values that need Pwnagotchi live state.
That is a particularly useful interop seam.

Rather than teach Theme Manager to poll Beast databases/files directly, propose a
small upstream-compatible adapter whereby, when Beast Core is present,
`STAT_SOURCE(key)` can query a **read-only, bounded Beast state provider** for approved
tokens such as creature name/level/stage, Expedition state, PeerDex count or Beast
health. Theme Manager would remain the renderer; Beast Core would remain the source of
truth.

This could produce a useful early interoperability win **before** physical
Presentation Broker switching is finished: a Korrie-rendered screen could optionally
show Beast-derived state without importing Beast's renderer or duplicating collectors.

The mapping should be allow-listed and read-only, and absence of Beast Core must leave
Theme Manager fully standalone.

### 7. Theme Manager asset bridge / translator

Add a read-only integration adapter that can discover Theme Manager assets and expose
them in Beast Studio without pretending they are native Beast assets.

Useful operations:
- list current/available Theme Manager themes;
- show preview;
- launch/edit in Theme Manager;
- import a compatible subset as a Beast Theme/Experience draft;
- export a Beast-compatible subset when explicitly requested;
- report unsupported features rather than silently dropping them.

A neutral **Visual Asset Interop v1** subset could cover:
palette roles, mood overrides, face mappings, text overlays, basic effects and metadata,
with engine-specific extensions namespaced `korrie.*` and `beast.*`.

### 8. Transactional plugin/config mutation

Theme Manager documents an important Pwnagotchi behavior: plugin toggling can cause
Pwnagotchi to rewrite `config.toml` from in-memory configuration, and its touch path
contains a special preservation workaround.

Beast should solve this generically with a `PwnagotchiConfigTransaction`:
1. read + parse current disk configuration;
2. snapshot/backup;
3. calculate an exact diff;
4. preserve unrelated keys;
5. apply one bounded change;
6. restart/reload only if required;
7. observe health;
8. verify intended key and protected keys;
9. roll back on failure.

This belongs underneath Plugin Manager, Presentation adapters and Update Manager.

### 9. Pack/theme fuzzing and privacy CI

Theme Manager's testing direction is worth copying aggressively:
- schema/property/fuzz tests for Theme/Face/Animation/Experience/Data/Map content;
- renderer crash-resistance against malformed-but-bounded inputs;
- import archive tests;
- interaction/state tests for touch/editor actions;
- repository/artifact privacy scans for accidental real SSIDs/BSSIDs, GPS traces,
  credentials, device names and other private material.

Beast already has strong conventional regression coverage; fuzz + privacy scanning is
a natural next hardening layer.

### 10. User-data preservation semantics

Adopt the installer behavior as a product rule:
- upgrades never overwrite user themes/Experiences/layouts;
- uninstall preserves user content unless an explicit purge is requested;
- generated/imported content is clearly separated from built-in content;
- migrations are versioned and reversible.

This aligns with Beast's Founder migration and recovery philosophy.

## Medium-priority ideas worth adapting

### Display comfort policy
Night/idle dimming, warning overlays and capability-aware backlight control fit Beast's
portable-device role. Implement through Hardware/Display capabilities and Action
Broker, not hardcoded direct device writes.

### Unified confirmation/countdown pattern
Theme Manager uses second-tap confirmation for disruptive power actions and a
cancelable countdown for thermal shutdown. Beast should establish a reusable critical
action component for reboot/shutdown/restore/update/presentation handoff and similarly
high-impact actions.

### Render-cost aware Experiences
Pack manifests already carry resource and thermal classes. Extend them with optional
render-budget hints and **measured** runtime cost:
- compose ms;
- display-write ms;
- dirty coverage;
- memory delta;
- sustained CPU;
- target FPS.

Depot/Studio can then say what an Experience actually costs on the reference Pi rather
than relying only on declared metadata.

### Managed memory experiments
Theme Manager deliberately tunes glibc allocation and calls `malloc_trim()` because
Pillow/image buffers plus request threads can retain heap pages.

Do **not** copy global allocator tuning blindly. Instead:
- reproduce a long-running render/WebUI memory test on Pi 4;
- measure RSS/PSS before and after repeated previews/theme swaps;
- if retention is confirmed, test explicit trim or isolate image-heavy preview work in
  a worker process whose memory can be reclaimed completely.

The lesson is important even if the exact `mallopt` values are not.

### Touch calibration wizard — diagnostic only
Theme Manager's four-point first-run flow is useful for onboarding. Beast can add a
calibration/diagnostic wizard that proposes a candidate and visually A/B tests it.

The physically accepted original/restored Beast calibration remains authoritative.
Never silently replace it; the earlier numerically attractive affine candidate was
physically rejected.

### External achievements/events adapter
Do not maintain two competing achievement universes. If Theme Manager exposes useful
milestones, ingest them as namespaced external semantic events such as
`korrie.theme.tried` and decide in Beast's achievement/progression policy whether
they matter.

### Korrie views as UX references, not duplicate collectors
Radar, cracking, System and plugin views contain useful interaction ideas. Beast should
reuse compact presentation patterns while reading Beast Core's canonical Networks,
Capture Vault, services and plugin state rather than starting another set of pollers.

## Things Beast should deliberately NOT copy

1. **The monolith.** Theme Manager's large single plugin is impressive for deployment
   simplicity, but Beast is already a platform; rendering, WebUI, system actions,
   telemetry and optional features should remain modular.
2. **Duplicate truth sources.** Theme Manager reads Linux/Pwnagotchi/WPA-sec state
   directly because it has to. Beast should route visuals through canonical Beast Core
   state whenever available.
3. **Approximate metrics presented as exact telemetry.** Upstream derives a CPU-like
   percentage from load average. Beast has a stricter real-telemetry rule; keep true
   CPU/load metrics distinct.
4. **Direct thermal shutdown from a renderer/plugin.** Beast should route thermal
   decisions through Resource Governor + authorized Action Broker/power policy.
5. **Unreviewed live Web edits.** Preserve Beast's draft/preview/apply transaction.
6. **Automatic replacement of production touch calibration.** Candidate calibration
   must be compared physically and explicitly accepted.
7. **Heat throttling as the primary design strategy.** Optimize duplicate work,
   framebuffer writes, polling and inactive modules first. Adaptive visual quality is a
   guardrail for real pressure, not an excuse for inefficient architecture.
8. **Tight dependence on Pwnagotchi monkey-patching as Beast's core renderer.** It is a
   useful adapter technique for Native/Theme Manager integration and snapshots, not the
   long-term Beast Core contract.

## New lightbulb: Experiences can orchestrate presentation engines

An Experience currently composes Theme + Face + Motion + Board/Layout + Context Deck.

A future higher-level **Presentation Profile** could additionally select an engine:
- Beast renderer;
- Korrie Theme Manager;
- Native Pwnagotchi;
- future full-screen renderer/app.

This should not be slipped into ordinary Experience apply until Broker switching is
physically trustworthy. A safer model is:

`Experience` = presentation content/configuration  
`Presentation Profile` = Experience + chosen presentation engine + engine adapter

That keeps creature progression independent while allowing something like:

- “Native Classic” -> native engine;
- “Korrie Aurora” -> Theme Manager engine + named theme;
- “Beast WOPR Command” -> Beast engine + WOPR Experience.

The user can then switch coherent **ways of experiencing the same Beastagotchi**
without conflating renderer ownership with creature identity.

## New lightbulb: semantic render layers as a shared interop boundary

Korrie's per-element recoloring has to infer which Pwnagotchi pixels came from which UI
element. Beast owns its rendering stack and can do better.

Every Beast renderer should optionally emit a small semantic layer map:
- element/widget ID;
- bounds;
- data source;
- style roles;
- touch action;
- dirty state;
- render cost.

That map enables:
- click-to-edit Studio;
- accessibility inspection;
- automatic touch-target auditing;
- render-cost attribution;
- screenshots with diagnostic overlays;
- theme translation;
- responsive reflow tooling;
- future AI-assisted layout review.

This could become one of the highest-leverage internal contracts in the UI.

## New lightbulb: one Visual Runtime, many producers

Rather than make Themes, Face Packs, Animation Packs, Rare Moments, Monster reveals,
Context Decks and Korrie imports each implement their own effect machinery, create a
small bounded **Visual Runtime**.

It owns:
- layer composition;
- declarative effects;
- cached static surfaces;
- motion clock;
- dirty-region reporting;
- transition/reveal timing;
- reduced-motion policy;
- resource budget.

Content systems produce declarative scenes for it. This reduces duplicated image work
and makes the thermal model measurable.

The Visual Runtime should remain optional behind current working render paths until it
proves itself off-screen and physically.

## Proposed implementation order

1. Land this audit as documentation only.
2. Build a tiny Theme Manager capability probe/adapter that reads status/version and
   detects whether managed ownership APIs exist; no handoff yet.
3. Prototype dirty-region metrics/writer behind a feature flag and benchmark against
   full-frame writes using captured real state.
4. Add canonical TemplateTokenRegistry.
5. Add semantic render-layer metadata to a small number of high-frequency Beast
   components and use it in Studio inspection.
6. Define Visual Effects/Scene schema and one reference Pack rather than hardcoding
   many effects.
7. Add timed TFT preview/revert using Action Broker.
8. Add config transaction primitive before using Beast to mutate Theme Manager or
   Pwnagotchi settings.
9. Add Theme Manager asset discovery/translation preview.
10. Only after the current visible v0.19 UX physical gate: implement real Broker
    release/acquire adapters and repeatedly test Native <-> Theme Manager <-> Beast.
11. Discuss a minimal upstream-managed-mode/API contract with Korrie once our adapter
    contract is concrete and tested.

## Licensing / reuse note

Both projects presently identify as GPL-3.0-family projects. That makes code reuse much
more practical than with incompatible licenses, but copied/derived code should still
retain required copyright/license notices and attribution. Prefer shared contracts and
small clearly-attributed reusable components over silently copying large portions of
the monolithic plugin. Exact `GPL-3.0-only` versus `GPL-3.0-or-later` compatibility
should be settled before substantial source is exchanged.

## Continuity rule

This audit adds **candidate improvements and integration directions**. It does not mark
them implemented. The current source tree/tests remain authoritative for implementation
status, and physical Presentation Broker ownership remains gated until the documented
TFT validation step.


## Current 3.0 source-level follow-up

A second source pass reviewed current Theme Manager 3.0 behavior rather than relying
only on its older theme/editor shape. Several additions materially strengthen the
interop case.

### Gallery/store UX is now a useful Beast Depot reference

Theme Manager now separates discovery from installation, preserves the active screen
across updates, supports install/uninstall from a Gallery/touch store, filters content,
shows structural live previews, offers a phone QR handoff, supports a GitHub-oriented
share flow, and can acquire a dependent face pack in the background.

Beast should **not** weaken its stronger trust/staging/transaction model to match this,
but Beast Depot should borrow the human workflow:

- discover -> inspect -> install -> activate remain distinct;
- catalog refresh never changes active presentation;
- dependency acquisition is explicit and visible;
- phone handoff should be first-class;
- preview/search/filter should be pleasant enough that Packs feel like a real
  ecosystem rather than a manifest browser.

### Beast Doctor / Explain is now a high-value convergence target

Theme Manager's Doctor turns recent evidence into a compact answer to:
"What appears wrong, why, and what should I do?"

Beast already owns richer structured ingredients through canonical health, Operations,
Black Box incidents, service topology and Support Bundles. The correct reintegration
is therefore a Beast-native **Doctor/Explain layer**, not another raw log parser.

It should produce bounded findings containing:
- severity;
- affected subsystem;
- concise explanation;
- evidence references;
- safe suggested next step;
- whether Beast has an audited action that could perform the remediation;
- explicit uncertainty when evidence is incomplete.

No automatic remediation should occur merely because a diagnostic rule matched.

### Existing pwngrid is a stronger candidate for Beast nearby transport

Current Theme Manager + `node_pwn.py` demonstrate lightweight peer metadata piggybacked
on the existing Pwnagotchi peer advertisement, with no shared IP network required and
IP discovery as a fallback.

That maps closely onto Beast's existing PeerDex / Nearby / future Party plan. Before
inventing another presence protocol, Beast should investigate a versioned,
privacy-safe, size-bounded Beast capability descriptor carried through the existing
peer substrate. Ordinary Pwnagotchi peers must still remain useful locally.

Initial Beast use should be read-only/social/Expedition-oriented. Theme Manager's
optional teammate targeting/whitelist behavior is **not** inherited as a default Beast
policy.

### Wardrive presentation can enrich Expeditions without duplicate persistence

Theme Manager's trip route, distance, unique-network and capture summary is useful UX.
Beast already has the more general Expedition persistence model, so the right move is
to reuse the presentation idea: a cheap route silhouette / journey card generated from
Beast Expedition history, rather than creating a second Wardrive database.

### PWA installability is a low-cost Studio/companion improvement

Theme Manager exposes manifest/icon/service-worker endpoints so its live WebUI can be
installed to a phone home screen without pretending to be an offline standalone app.
Beast Studio should consider the same lightweight PWA shell while keeping its paired,
local-first security model.

### Do not tunnel long-lived streams through Pwnagotchi's own web server

Theme Manager's recent design discussion rejected SSE/WebSocket use through the
upstream single-threaded Pwnagotchi web server because a held request could block the
rest of that UI. Beast Studio owns its own server and may use richer streaming there,
but Pwnagotchi/Theme Manager integration should keep upstream requests bounded.

## First implementation taken from this audit

The first low-risk source change is now implemented on the active v0.19 branch:

- `beastcore/theme_manager_interop.py` adds a bounded, cached, read-only
  `ThemeManagerProbe`;
- the probe reads installed Theme Manager source **without importing or executing it**;
- it reports version and interoperability evidence such as `STAT_SOURCE`,
  clean unload/live install, structural themes, Doctor, Gallery, changed-row writer,
  touch, PWA, Nodes and Wardrive support;
- it deliberately distinguishes compatibility evidence from a real explicit managed
  presentation release/acquire contract;
- PluginIntegrationEngine exposes the probe through canonical plugin state;
- PresentationBroker exposes the resulting version/capabilities but keeps the physical
  executor locked.

Current code-bearing checkpoint:
`574c7e48144cb2cc088a2260ed57d80015b617d4`

Validation:
- **343 tests passed**
- Python compile passed
- shell syntax passed
- GitHub Actions run `35952293274`

This is source/CI evidence only. No target/off-screen or physical TFT handoff claim is
made.

## Execution priority after the audit

The audit does **not** justify abandoning the current visible v0.19 UX gate for another
long backend detour. The best course is:

1. keep the read-only interop probe as the safe foundation now completed;
2. return to the substantial visible Unified UX / captured-state gallery work and get
   the next physical 480x320 acceptance checkpoint;
3. in parallel-sized bounded blocks, add the canonical token registry and semantic
   render-layer metadata because both help Beast UI and Theme Manager interop without
   taking display ownership;
4. add Beast Doctor/Explain and the improved Depot human workflow;
5. prototype measured dirty-region writes behind a feature flag;
6. define Visual Asset Interop v1 and a Theme Manager import/preview path;
7. only after current v0.19 physical UX acceptance, activate real Presentation Broker
   adapters and repeatedly validate Native <-> Theme Manager <-> Beast rollback;
8. once that adapter is concrete, approach Korrie with the smallest useful managed-mode
   API rather than asking either project to adopt the other's architecture wholesale.
