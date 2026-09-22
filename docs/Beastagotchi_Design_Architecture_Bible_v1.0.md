# Beastagotchi Design & Architecture Bible v1.0

**Status:** Foundation specification — approved direction, intentionally extensible  
**Target hardware:** Raspberry Pi 4 8GB + 480×320 touch display  
**Primary philosophy:** Preserve the working Pwnagotchi core. Build Beastagotchi around it as a modular, live, visual field-computer environment.

---

## 1. Product Definition

Beastagotchi is not a single Pwnagotchi theme and not a single fixed dashboard. It is a modular operating environment layered around a protected Pwnagotchi engine.

The product should feel simultaneously like:

- a living digital creature,
- a cyberdeck / field terminal,
- a real-time RF and system monitor,
- a modular app platform,
- a configurable instrument panel,
- a persistent exploration / progression system,
- and a device that can explain and maintain itself.

The visual identity must retain the strongest traits of the early Beastagotchi UI: dark background, sharp cyan/green instrument language, expressive face, compact readable telemetry, obvious page navigation, and confidence through simplicity. Modern builds add richer graphics, maps, radar, spectra, animation, customization, and advanced control without losing that identity.

### Non-negotiable principles

1. **Pwnagotchi remains protected.** Beastagotchi consumes its data and controls it through defined interfaces rather than repeatedly patching its internals.
2. **Everything useful should be visible or reachable without SSH.** SSH remains the emergency/developer path, not the normal user interface.
3. **Live data first.** If Linux, Pwnagotchi, Bettercap, GPS, hardware, or a plugin knows something useful, Beast Core should expose it.
4. **Themes are structural, not recolors.** A theme may change panel geometry, face treatment, typography, icons, backgrounds, animations, graph appearance, audio, and transitions.
5. **Layouts are separate from themes.** The same data can be presented in Minimal, Classic, Balanced, Dense, Field, Monster, or custom layouts under any compatible theme.
6. **Renderers are separate from data.** A channel-activity data stream can become bars, line, area, waterfall, heatmap, polar, radar, or oscilloscope without changing the collector.
7. **The Beast is a first-class subsystem.** Personality, state, face pack, evolution stage, animations, and theme treatment are independent layers.
8. **Visual richness must degrade gracefully.** The device should remain readable and responsive under load.
9. **Everything is modular.** Optional hardware and heavy services appear only when installed / available.
10. **Nothing visually valuable is discarded.** Unused concepts become themes, layouts, idle modes, widgets, animation packs, or optional apps.

---

## 2. System Hierarchy

```text
Monstergotchi / Beastagotchi OS Layer
        │
        ├── Beast Core daemon
        │     ├── State registry
        │     ├── Event bus
        │     ├── Action broker
        │     ├── Health engine
        │     ├── Session manager
        │     ├── Database layer
        │     ├── Configuration manager
        │     ├── Hardware discovery
        │     └── Plugin / module manager
        │
        ├── Collectors / adapters
        │     ├── Pwnagotchi adapter
        │     ├── Bettercap adapter
        │     ├── Linux/system adapter
        │     ├── GPS adapter
        │     ├── Storage adapter
        │     ├── USB / udev adapter
        │     ├── Plugin adapter
        │     └── Future hardware adapters
        │
        ├── Independent services
        │     ├── Pwnagotchi
        │     ├── Bettercap
        │     ├── optional Kismet
        │     ├── optional SDR services
        │     ├── optional Bluetooth services
        │     ├── optional Meshtastic services
        │     └── optional local AI / voice services
        │
        ├── Beast UI compositor
        │     ├── Touchscreen UI
        │     ├── Web UI
        │     └── Phone UI
        │
        └── Persistent storage
              ├── SQLite encounter/session DB
              ├── time-series telemetry
              ├── events / incidents
              ├── configuration revisions
              ├── theme/layout presets
              └── backups
```

Beast Core should be the only privileged component that performs sensitive OS actions. The graphical UI sends validated action requests to Beast Core and receives success/failure responses and events.

---

## 3. Main Navigation Model

### Main swipe carousel

The default high-frequency pages:

1. **HOME** — Beast Core / summary
2. **RECON** — live RF radar + target/encounter activity
3. **NETWORKS** — searchable/sortable AP/browser
4. **SPECTRUM** — channel/spectrum visualizations
5. **CAPTURES** — Capture Vault
6. **MAP** — GPS / encounter field map
7. **BEAST** — progression, personality, evolution, memories
8. **SYSTEM** — health / services / hardware summary

### Persistent footer

Always available unless a deliberate immersive mode hides it:

- large **Previous** arrow
- **Home** button
- page position indicator / dots
- active page name
- large **Next** arrow

Optional theme variants may change the footer geometry but must preserve functionality.

### Global gesture model

- horizontal swipe: previous / next main page
- vertical swipe: scroll inside current page
- tap: select / open
- long press: context menu / customize
- swipe down: Quick Control Drawer
- swipe up: optional App Launcher / notifications shortcut
- two-finger or explicit edit control: customization mode only

Navigation must never rely exclusively on gestures. Every core action needs a visible touch alternative.

---

## 4. Apps / Modules Universe

The main carousel stays concise. Everything else lives in Apps / Tools.

### Core apps

- Live Logs
- Diagnostics
- Plugin Manager
- Service Manager
- Hardware Manager
- Storage Manager
- Backup / Restore
- Event Timeline
- Notification Center
- Sessions / Expeditions
- GPS Dashboard
- Performance / Processes
- Network Interfaces
- Configuration Manager
- Themes / Layouts / Faces
- Terminal
- Developer Center
- Files / Export
- Help / On-device manual

### Optional modules

Appear dynamically when available:

- Bluetooth observer
- second Wi-Fi adapter / Scout
- Kismet
- SDR / Spectrum
- ADS-B / Sky
- rtl_433 / RF Objects
- Meshtastic / Mesh
- environmental sensors
- power telemetry
- IMU / compass
- camera
- NFC
- GPIO / LEDs / haptics / fan
- dock / home-base services
- local AI / voice

---

## 5. Live Data Model

Beast Core exposes canonical names. UI widgets never scrape implementation details directly.

### System namespace

```text
system.cpu.total
system.cpu.core0..3
system.load.1m
system.load.5m
system.load.15m
system.memory.used_pct
system.memory.used_mb
system.memory.free_mb
system.swap.used_pct
system.temp.cpu_c
system.throttle.flags
system.uptime_sec
system.boot_time
system.clock.synced
system.hostname
system.model
system.ram_mb
system.kernel
system.beast_version
```

### Storage namespace

```text
storage.root.used_pct
storage.root.free_bytes
storage.root.readonly
storage.mounts[]
storage.captures.bytes
storage.logs.bytes
storage.database.bytes
storage.backup.last_success
storage.archive.status
```

### Radio namespace

```text
radio.interfaces[]
radio.primary.name
radio.primary.mode
radio.primary.mac
radio.primary.channel
radio.primary.frequency_mhz
radio.primary.band
radio.primary.supported_channels[]
radio.primary.tx_bytes
radio.primary.rx_bytes
radio.primary.state
radio.hop.current
radio.hop.rate
radio.hop.history[]
```

### Wi-Fi / encounter namespace

```text
wifi.ap_count
wifi.client_count
wifi.hidden_count
wifi.vendor_count
wifi.new_ap_rate
wifi.aps[]
wifi.clients[]
wifi.channel_activity[]
wifi.channel_history[]
wifi.signal_history[]
wifi.encounters.session
wifi.encounters.lifetime
```

AP objects should support, when known:

```text
ssid
bssid
vendor
channel
frequency
band
encryption
cipher
rssi
clients
first_seen
last_seen
encounter_count
strongest_rssi
gps_first
gps_last
capture_count
notes
tags
```

### Capture namespace

```text
captures.total
captures.session
captures.valid
captures.pmkid
captures.eapol
captures.duplicates
captures.storage_bytes
captures.items[]
```

### GPS namespace

```text
gps.fix
gps.satellites_visible
gps.satellites_used
gps.latitude
gps.longitude
gps.altitude_m
gps.speed_mps
gps.heading_deg
gps.hdop
gps.accuracy_m
gps.trip_distance_m
gps.session_distance_m
gps.track[]
```

### Pwnagotchi / Bettercap namespace

```text
pwnagotchi.mode
pwnagotchi.epoch
pwnagotchi.mood
pwnagotchi.peers
pwnagotchi.bonds
pwnagotchi.active
pwnagotchi.blind
pwnagotchi.sad
pwnagotchi.bored
pwnagotchi.missed
pwnagotchi.deauths
pwnagotchi.assocs
pwnagotchi.handshakes
bettercap.state
bettercap.uptime
bettercap.api_latency_ms
```

### Beast namespace

```text
beast.name
beast.level
beast.xp
beast.stage
beast.mood
beast.energy
beast.curiosity
beast.boredom
beast.confidence
beast.streak
beast.badges[]
beast.traits[]
beast.memories[]
beast.current_expression
beast.current_animation
```

### Service / plugin namespace

```text
services[]
plugins[]
notifications[]
events[]
incidents[]
hardware[]
```

---

## 6. Update / Refresh Classes

### Visual animation loop

Target: **8–15 FPS** on the visible page when useful.

Used for:

- Beast animation
- radar sweep
- graph scrolling
- subtle particles / matrix rain
- transitions
- waveform movement

Heavy themes may automatically reduce to 5–8 FPS under load.

### 1 Hz class

- GPS
- current channel
- CPU / memory / temperature
- interface counters
- uptime
- power telemetry

### Event-driven class

- AP discovered
- client discovered
- capture created
- plugin error
- service change
- hardware attached / removed
- GPS fix gained / lost
- storage warning
- achievement

### 5–10 second class

- filesystem utilization
- service health summaries
- plugin health metrics
- hardware inventory changes if not event driven

### 30–60 second class

- update availability
- archive / NAS state
- dependency status
- slow diagnostics

### On-demand class

- expensive diagnostics
- package inventory
- large log queries
- deep filesystem analysis

---

## 7. Visual Composition Model

The UI compositor should be layered:

```text
Data Source
   ↓
Widget Model
   ↓
Renderer
   ↓
Widget Skin
   ↓
Layout
   ↓
Theme
   ↓
Animation Pack
   ↓
Display Compositor
```

### Why this matters

A widget should describe meaning, not appearance.

Example:

```text
Data: wifi.channel_activity
Widget: ChannelActivityWidget
Renderer: WaterfallRenderer
Skin: MatrixThin
Layout: ReconDense
Theme: Matrix Beast
Animation: SoftPulse
```

Change only the renderer:

```text
Renderer: BarRenderer
```

The data collector does not change.

---

## 8. Graph Renderer Library

Initial renderer set:

1. Sparkline
2. Line
3. Multi-line
4. Area
5. Stacked area
6. Bars
7. Stacked bars
8. Histogram
9. Heatmap
10. Waterfall / spectrogram style
11. Oscilloscope waveform
12. Radial gauge
13. Donut
14. Radar / spider
15. Polar plot
16. Signal meter
17. RSSI trail
18. Timeline
19. Event raster
20. Channel occupancy blocks
21. Matrix / particle visualization
22. Numeric + microtrend hybrid

A long-press or graph action menu can change renderer in-place.

Renderer eligibility should be data-aware so nonsense choices are hidden.

---

## 9. Layout System

### Built-in density profiles

- **Minimal** — Beast + essential status
- **Classic** — inspired by v0.2–v0.4
- **Balanced** — general default
- **Dense** — maximum useful information
- **Field** — outdoors / larger touch targets / key telemetry
- **Monster** — intentionally ridiculous information density

### Layout capabilities

Widgets support:

- position
- span / size
- min/max size
- visible/hidden
- priority
- renderer selection
- update class
- tap action
- long-press action
- theme overrides

Layouts should be saveable as presets independent of themes.

---

## 10. Theme Engine

A theme package can define:

```text
manifest.json
palette.json
typography.json
panels.json
icons/
backgrounds/
face-treatment.json
graph-skins.json
animations.json
sounds/
boot/
idle/
footer.json
notification.json
```

### Theme categories already approved as design language

- Classic Beast
- Matrix
- LCARS / starship console
- WOPR / NORAD
- Cyberpunk HUD
- Retro CRT green
- Retro CRT amber
- Terminal / UNIX
- Black Ice
- Dark Ice
- Hunter / Red Alert
- Holographic
- Blueprint
- Wireframe
- Vaporwave
- Synthwave
- Neon Dream
- Space / Galaxy
- Forest / Nature
- Biohazard
- Industrial cyberdeck
- Oscilloscope lab
- Minimal OLED
- Monochrome professional
- Golden / amber tactical
- Samurai
- Steampunk
- Comic
- Retro game
- Holiday / seasonal packs
- Pride
- user-created themes

Theme count should be limited by maintainability, not architecture.

### Theme compatibility rule

Every theme must define a fallback skin for every core widget. Optional highly bespoke renderers may be theme-specific.

---

## 11. Beast / Personality Engine

### Personality values

The Beast can track derived states such as:

- mood
- energy
- curiosity
- confidence
- boredom
- hunger-for-discovery
- stress / fault state
- sleepiness
- excitement

These are cosmetic / experiential values derived from real device events and usage.

### Expression states

Initial canonical states:

- idle
- happy
- curious
- scanning
- focused
- hunting
- capture-success
- surprised
- smug
- bored
- sleepy
- sleeping
- waking
- overheated
- confused
- GPS-searching
- disconnected
- reconnecting
- warning
- fault
- level-up
- evolution
- celebrating

### Face packs

Face art is independent from state.

Examples:

- Classic Pixel
- Classic Geometric
- Matrix Ghost
- Cyber Beast
- Black Ice
- Hunter
- LCARS Hologram
- Wireframe
- CRT ASCII
- Creature / illustrated
- Seasonal

Each pack maps canonical expressions into its own visual treatment.

### Animation layers

Possible independent animation tracks:

- blink
- eye direction
- breathing
- ears / horns
- mouth
- body motion
- ambient glow
- glitch
- particles
- reaction burst

---

## 12. Progression / Evolution

Progression should reward ordinary use and exploration, not unsafe behavior.

Potential XP sources:

- unique APs observed
- unique vendors
- new channels / bands observed
- GPS distance
- sessions completed
- uptime milestones
- diagnostic health streaks
- plugin/module discoveries
- captures cataloged
- new regions visited
- hardware modules added

Evolution initially remains cosmetic / experiential.

### Suggested stage framework

1. Hatchling
2. Scout
3. Beast
4. Hunter
5. Monster
6. Apex
7. Mythic

Exact names can remain theme-pack overrideable.

---

## 13. Notification System

Severity levels:

- info
- success
- attention
- warning
- critical

Presentation modes:

- toast
- banner
- edge pulse
- Beast reaction
- sound/haptic
- full-screen critical card

Examples:

- GPS fix acquired
- capture stored
- new vendor
- new hardware
- plugin crashed
- Bettercap restarted
- storage low
- temperature high
- level up
- session complete

Notifications are logged to the Event Timeline.

---

## 14. Quick Control Drawer

Swipe down from anywhere or tap a persistent status affordance.

Initial controls:

- brightness
- theme quick-switch
- quiet / sound toggle
- screenshot
- start/end session
- Pwnagotchi restart
- Bettercap restart
- radio-stack repair
- GPS toggle / reset
- backup now
- diagnostics
- lock screen
- reboot
- shutdown

Destructive / privileged actions require confirmation and are executed by Beast Core.

---

## 15. Diagnostics & Self-Healing

### Continuous health checks

- Pwnagotchi running
- Bettercap reachable
- monitor interface exists
- monitor mode correct
- supported channels non-empty
- current channel valid
- filesystem writable
- free space healthy
- GPS responding
- database writable
- display/UI heartbeat
- plugin health
- thermal / throttle status

### Incident model

When a meaningful failure occurs, preserve a rolling pre-failure window:

- system telemetry
- radio state
- service state
- event stream
- log excerpts
- hardware state

The UI should show:

```text
INCIDENT #004
wlan0mon disappeared 18:42:17

BEFORE:
channel 161
Bettercap LIVE
CPU 59C
36 supported channels

ACTIONS:
[Rebuild Monitor]
[Restart Radio]
[View Timeline]
[Export Incident]
```

### Patch auditor

Track known local patches and distinguish:

- present
- lost
- changed
- upstream equivalent detected

---

## 16. Sessions / Expeditions

Sessions are a foundational organizational unit.

### Start Expedition

A session groups:

- GPS track
- encounters
- captures
- system telemetry
- hardware state
- errors/incidents
- screenshots
- notes
- achievements
- XP gains

### End Expedition summary

Example:

```text
2h 47m
18.4 mi
326 unique APs
91 vendors
44 BLE devices
3 captures
max CPU 62C
GPS coverage 98.4%
1 Bettercap restart
+420 XP
```

Sessions should be browsable later and exportable to the web UI.

---

## 17. Data Storage Strategy

### SQLite

Use for:

- encounters
- captures metadata
- sessions
- events
- incidents
- achievements
- Beast progression
- user notes/tags
- hardware inventory

### Time-series storage

Start lightweight. Avoid deploying a heavyweight database on-device until required.

Recommended initial approach:

- downsampled SQLite time-series tables or compact append logs
- short high-resolution window
- longer low-resolution historical window

A future dock/web mode may optionally export into InfluxDB/Grafana elsewhere.

### Storage wear policy

- batch writes
- WAL where appropriate
- configurable retention
- compress old incidents/logs
- rolling local cache
- archive to trusted NAS when available

---

## 18. Boot / Shutdown Experience

### Boot POST

The boot animation must be tied to real tests:

```text
DISPLAY      ✓
TOUCH        ✓
STORAGE      ✓
DATABASE     ✓
WIFI PHY0    ✓
MONITOR      ✓
CHANNELS 36  ✓
BETTERCAP    ✓
PWNAGOTCHI   ✓
GPS          ✓
PLUGINS 8    ✓
BEAST CORE   ✓

BEAST ONLINE
```

Themes may render this differently but cannot fake success.

### Shutdown

- stop accepting new actions
- end / checkpoint active session
- flush database
- flush logs
- sync storage
- stop optional services
- stop Beast Core dependents
- display safe-to-power-off state when appropriate

---

## 19. Web / Phone Interface

The touchscreen and web UI use the same Beast Core API.

### Touchscreen

- condensed
- high contrast
- touch-first
- limited text
- fast navigation

### Desktop web UI

- large maps
- long logs
- history charts
- deep database search
- full customization workshop
- theme/layout editor
- backup/restore
- incident review
- session reports

### Phone UI

- quick status
- notifications
- GPS
- restart/service actions
- session controls
- shutdown/reboot

---

## 20. Plugin / Module SDK

Plugins may register:

- data sources
- events
- actions
- widgets
- pages
- app entries
- notifications
- background tasks
- settings schema
- hardware drivers

### Plugin health

Track:

- loaded state
- version
- callback latency
- exceptions
- CPU usage estimate
- memory estimate
- last event
- required dependencies

Bad plugins should fail independently when possible.

---

## 21. Configuration Model

All important settings should be represented by schema so the UI can generate controls automatically.

Supported field types:

- boolean
- integer
- float
- string
- secret
- enum
- multi-select
- range
- color
- file/path
- action

Every configuration save creates a revision.

Capabilities:

- undo
- compare revisions
- restore known-good
- export profile
- import profile

---

## 22. Profiles

Initial profiles:

- Normal
- Quiet
- Travel
- Field
- Low Power
- Docked
- Lab

A profile can alter:

- display behavior
- animation intensity
- theme/layout
- logging
- plugin set
- service set
- update rates
- sync rules
- sound/haptics

---

## 23. Performance Budgets

### Hard priorities

1. Pwnagotchi/Bettercap stability
2. radio functionality
3. Beast Core responsiveness
4. touch responsiveness
5. readable UI
6. animation richness

Animation always loses before radio stability does.

### UI targets

- touch response: visually acknowledged in <100 ms where possible
- page transition: 150–300 ms
- normal visible-page render: 8–15 FPS when animated
- static page: render only on state change where possible
- background pages: no full rendering
- expensive maps/charts: cached layers + incremental redraw

### Load shedding

Beast Core may instruct UI to reduce:

- particles
- glow layers
- animation FPS
- graph sampling density
- background effects

when CPU temperature/load crosses configured thresholds.

---

## 24. Screen / Touch Constraints

Native target: **480×320 landscape**.

Every approved design must be tested at native resolution before implementation.

Rules:

- avoid relying on ultra-fine text visible only in high-resolution concept art
- minimum practical touch target around 34–44 px depending on context
- preserve large Previous/Next targets
- prioritize high-contrast text
- scrolling lists must clip cleanly
- scroll state must be obvious
- detail pages need an obvious Back path
- avoid edge gestures that conflict with hardware/display behavior

---

## 25. Visual QA Pipeline

Every major UI screen goes through:

1. high-resolution concept render
2. 480×320 native downsample proof
3. native-size readability review
4. interaction overlay / touch target check
5. implementation
6. off-device screenshot validation
7. physical display validation

This prevents beautiful concept art from becoming unusable on hardware.

---

## 26. Initial Build Sequence

### Foundation 0 — Freeze spec

This document.

### Foundation 1 — Beast Core skeleton

Build:

- daemon
- state registry
- event bus
- action broker
- basic config
- health heartbeat
- API/WebSocket

No fancy UI yet.

### Foundation 2 — Collectors

Implement:

- system
- radio
- Pwnagotchi
- Bettercap
- GPS
- captures
- storage
- plugins/services

### Foundation 3 — UI shell

Implement:

- 480×320 compositor
- page engine
- footer navigation
- swipe/scroll/tap/long-press
- quick drawer
- notifications
- renderer interface
- theme interface
- face interface

### Foundation 4 — Classic Beast reference theme

The first real theme should deliberately echo v0.4 visually. It becomes the correctness/reference theme.

### Foundation 5 — Core pages

Implement:

- Home
- Recon
- Networks
- Spectrum
- Captures
- Map
- Beast
- System

### Foundation 6 — Customization

Implement:

- renderer switching
- density profiles
- theme switching
- face packs
- layout presets

### Foundation 7 — Operations

Implement:

- logs
- diagnostics
- services
- plugins
- storage
- backups
- events/incidents
- sessions

### Foundation 8 — Web UI

Reuse Beast Core API.

### Foundation 9 — Expansion modules

Second radio, Kismet, Bluetooth, SDR, Meshtastic, sensors, etc.

---

## 27. First Implementation Theme Set

Do not attempt 100 themes before the engine is proven.

Start with themes that stress different capabilities:

1. **Classic Beast** — old v0.x DNA, reference/fallback
2. **Matrix** — animated background + terminal styling
3. **LCARS / Starcore** — radically different panel geometry
4. **Black Ice** — image/texture heavy, cold professional
5. **Hunter** — event-reactive red/orange mode
6. **Minimal Professional** — low-animation benchmark

If all six can share the same widgets/data/layout system successfully, the theme architecture is sound.

---

## 28. First Implementation Renderer Set

Prove renderer swapping with a manageable subset:

- Numeric
- Sparkline
- Line
- Bars
- Area
- Heatmap
- Waterfall
- Radial gauge
- Radar/spider

Then expand.

---

## 29. First Implementation Face Set

Prove the face engine with:

- Classic Pixel
- Matrix
- Cyber Beast
- Black Ice
- Hunter

Each must implement at least:

- idle
- scanning
- curious
- happy
- capture-success
- bored
- sleeping
- warning
- fault
- level-up

---

## 30. Definition of “Base Is Right”

The base is considered correct when:

- Pwnagotchi remains stable underneath Beast Core.
- All major telemetry is available through canonical state keys.
- Touch navigation works reliably.
- Main page arrows always work.
- Vertical scrolling is reliable.
- Theme switching does not require page-specific rewrites.
- Renderer switching works on compatible widgets.
- Face packs react to canonical Beast states.
- Layout presets are independent from themes.
- Optional modules can appear/disappear dynamically.
- UI survives missing data without crashing or filling pages with garbage.
- Beast Core can restart/recover selected services safely.
- Diagnostics can explain failures.
- Configuration changes are revisioned.
- Every core screen is readable at native 480×320.
- The system can grow without rewriting the foundation.

---

## 31. Ideas Reserved for Later Exploration

Keep these in the library even though they are not base blockers:

- animated environmental world reacting to weather / time / RF activity
- aircraft crossing the Beast’s sky when ADS-B sees one
- ambient Matrix rain built from recent SSIDs
- sonar / submarine theme
- mission-control theme
- oscilloscope laboratory
- full WOPR game-like Easter egg
- theme-reactive sound packs
- hardware LEDs matching UI state
- dock transition animations
- peer-Beast encounter animations
- “Monster View” ultra-dense all-sensors screen
- user-shareable theme/layout/face bundles
- procedural theme randomizer
- theme scheduler by time/location/profile
- per-session theme / mood history
- visual replay of an Expedition after it ends

---

## 32. Immediate Next Decision Set

Before production coding begins, create native 480×320 reference designs for:

1. Home / Beast Core
2. Recon
3. Networks
4. Spectrum
5. Captures
6. Map
7. Beast / Evolution
8. System
9. Quick Drawer
10. Notification styles
11. App Launcher
12. Settings / Customizer

Each should be represented in at least Classic Beast plus one radically different theme to validate structural flexibility.

---

## 33. Canonical Statement

**Beastagotchi is a living, themeable, modular field-computer interface built around a protected Pwnagotchi engine. Beast Core owns state, health, hardware, telemetry, persistence and actions. The UI owns presentation. Themes own visual language. Layouts own composition. Renderers own data visualization. Face packs own character expression. None of those layers should be unnecessarily coupled.**

That separation is the foundation that lets Beastagotchi become Monstergotchi later without another rewrite.
