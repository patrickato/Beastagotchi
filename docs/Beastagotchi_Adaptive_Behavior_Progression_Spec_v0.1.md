# Beastagotchi Adaptive Behavior & Progression Spec v0.1

This specification turns the Beast from a static mascot/dashboard into a persistent creature and context-aware field interface. Automatic context is **presentation/passive-logging only**. It never arms Lab Mode or initiates intrusive radio actions.

## 1. Progression model

### Level cap

**100 levels** is the proposed permanent cap for the first complete progression system. It is long enough to remain meaningful for a long time but still gives Beastagotchi an obtainable final goal. Level 100 is a genuine completion milestone, not a prestige-reset treadmill.

### Evolution stages

Levels are continuous; major visual evolution happens at milestones. Initial proposal:

1. L1 — Hatchling
2. L5 — Cub
3. L10 — Scout
4. L20 — Tracker
5. L35 — Hunter
6. L50 — Beast
7. L70 — Alpha
8. L85 — Apex
9. L100 — Monstergotchi

Names and artwork remain theme/face-pack configurable. Evolution stages can unlock additional cosmetic layers, animations, dashboard layouts, aura slots, titles, sounds, idle scenes, and Easter eggs without changing radio capability.

### XP philosophy

XP should reward varied, passive or explicitly authorized use rather than repetitive activity. Candidate sources include unique AP/vendor discoveries, new channels/bands observed, GPS distance, new mapped areas, session completion, uptime milestones, diagnostics completed, captures cataloged, new hardware types, Beast peer encounters, and achievements. Repeated identical events receive diminishing returns or per-session caps.

At max level, lifetime stats, achievements, collections, sessions and rare discoveries continue. Level 100 remains the max rather than resetting the user.

## 2. Automatic context modes

Beast Core derives context from sensors and state, with hysteresis so the UI does not flap between modes.

Initial GPS motion classes:

- `<1.5 mph` — stationary → **PWN** visual context
- `1.5–7 mph` — walking → **WALK** context
- `7–15 mph` — moving/riding → **TRAVEL** context
- `>=15 mph` — driving → **WARDRIVE** context

The v0.3 Context Engine requires a GPS fix, waits several seconds before accepting a changed class, and falls back to PWN when motion cannot be determined. Thresholds become user-configurable later.

These modes can alter page emphasis, map behavior, face animation and visual effects. They do **not** automatically enable Lab Mode or intrusive actions.

### Examples

- WARDRIVE: goggles/visor on compatible faces, wind streaks, larger map/radar, route and new-AP counters, reduced tiny text while moving.
- WALK: walking animation, breadcrumb trail, nearby discoveries, distance/pace, map-first quick page.
- PWN/stationary: normal Pwnagotchi-focused home, deeper detail panels, normal face behavior.
- TRAVEL: motion-reactive background and route summary without assuming a car.

A manual lock/override will later let the user keep any visual context regardless of detected motion.

## 3. Theme-specific event reactions

Themes define reactions rather than relying on one global flash effect. The same event may therefore feel completely different in each theme.

Examples:

- handshake stored — Matrix code shockwave; Black Ice crystal flash; Hunter ember burst; Classic Beast cyan pulse
- GPS lock — map/grid sweep; eye focus animation; constellation snap-in
- new vendor — Beast curiosity animation + collectible card edge glow
- level up — full theme transformation sequence
- thermal warning — heat shimmer/red pulse appropriate to theme
- new hardware — electrical/portal/scan-in effect
- peer encounter — paired aura/ripple animation

Effects are layered and short-lived so data remains readable. Accessibility settings can reduce or disable flashes and motion.

## 4. Session auras

A session may accumulate visual aura layers based on temporary milestones. These are deliberately separate from permanent level/evolution.

Candidate triggers: discovery streak, distance traveled, channel coverage, capture streak, perfect-health session, GPS coverage, new-vendor count, new-area exploration. The theme decides how the aura is rendered: flame, particles, circuitry, frost, halo, scan rings, Matrix glyphs, etc.

Auras disappear or reset at session end unless a specific achievement permanently unlocks a cosmetic version.

## 5. Map subsystem

Maps are first-class, not merely a GPS coordinate page. Planned layers:

- current position and heading
- breadcrumb/dotted route
- session route
- AP encounter markers
- first/last-seen locations
- capture locations
- signal/encounter heatmaps
- known/return encounter distinctions
- later Bluetooth, aircraft, Meshtastic, sensor and Beast-peer layers

Online connectivity can fetch/cache map data through a configured map source. Offline operation should use cached tiles or an imported local map package. Map data remains usable without Internet after caching.

## 6. 2.5D / 3D

True lightweight 3D is possible on Pi 4, but it is an optional renderer rather than a dependency. The 480×320 screen means 2.5D/isometric/perspective visualization may often look better and cost less.

Potential uses:

- perspective encounter map with extruded signal towers
- 3D/2.5D Beast habitat idle scene
- channel landscape where AP strength becomes terrain/towers
- orbiting hardware/service status around the Beast
- map tilt when moving
- animated evolution sequences

The core UI must remain functional when all 3D effects are disabled.

## 7. Easter egg framework

Easter eggs should exist throughout the OS, not only leveling. Triggers can include level numbers, unusual combinations of state, gesture sequences, uptime milestones, dates/times, rare vendor discoveries, exact channel sets, special GPS/session patterns, themes, hardware combinations and hidden menu interactions.

Easter eggs may unlock animations, titles, faces, sounds, theme fragments, idle scenes or temporary visual modes. They should never silently change critical system/radio configuration.

## 8. Architectural consequence

Adaptive behavior is another independent layer:

`live state → context engine → personality/progression → visual tags/events → theme-specific reaction`

This keeps environmental behavior compatible with every theme and layout rather than hard-coding “goggles mode” into one screen.
