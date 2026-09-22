# Beastagotchi Master Completion Matrix v4.0

This is the anti-forgetting ledger. It combines the original Design & Architecture Bible, every A–G roadmap gate, the physical-test decisions, the recovered pinned-conversation idea dumps, and the later ideas added during development. v4.0 was produced by the September 2026 project-continuity audit before the v0.11 physical gate. Items move from `[ ]` to `[~]` to `[x]`; they are not silently deleted because development attention moved elsewhere.

Legend: `[x]` implemented/passed stated gate · `[~]` partially implemented or foundation exists · `[ ]` planned/reserved.

## Gate A — Hardware / Source Truth

- [x] Raspberry Pi 4 8 GB inventory and verified OS/runtime environment
- [x] 480×320 ILI9486 `/dev/fb1` source truth
- [x] ADS7846 resistive touch identification
- [x] GPS/gpsd source discovery
- [x] onboard Wi-Fi/monitor-mode/channel capability audit
- [x] Bettercap/Pwnagotchi live-state source audit
- [x] service/config/storage/cache/capture path audit
- [x] canonical data-key namespace and source priority
- [x] source freshness/health tracking
- [x] safe probe and validation archives
- [x] known-good installed Pi checkpoint
- [ ] repeatable hardware inventory export for public support bundles

## Gate B — Beast Core / Data Platform

- [x] Beast Core daemon separate from Pwnagotchi
- [x] canonical State Registry
- [x] Event Bus
- [x] SQLite durable store
- [x] time-series sampler / retention foundation
- [x] Pwnagotchi callback bridge
- [x] Bettercap/system/GPS/service collectors
- [x] semantic Wi-Fi encounter engine
- [x] lifetime encounter/vendor counters
- [x] progression/profile persistence
- [x] context engine: PWN / WALK / TRAVEL / WARDRIVE
- [x] Dock/Field foundation
- [x] ambient season/day-phase/moon foundation
- [x] Rare Moment scheduler/history/witness foundation
- [x] read-only local API and history endpoints
- [~] Rules Engine condition/action architecture
- [ ] full rule editor
- [ ] notification/event persistence policy
- [ ] richer time-series query/downsampling
- [ ] self-healing/incident manager

## Gate C — Physical Display / Touch / Ergonomics

- [x] reversible display ownership handoff
- [x] automatic rollback safety timer
- [x] native RGB565 framebuffer writer
- [x] reliable SYN_REPORT touch sampling
- [x] reliable taps/swipes/long-press
- [x] non-wrapping horizontal page swipes
- [x] 3× stylus + 3× finger Touch Lab characterization
- [x] pressure capability characterized
- [x] alternate affine calibration physically tested
- [x] original/restored calibration selected as production
- [x] rejected calibration quarantined as experimental
- [x] visual bounds separated from touch bounds
- [x] minimum target-size rules established
- [x] non-overlapping Achievement Explorer partitions
- [~] global edge-aware touch target policy applied across new screens
- [ ] final whole-UI interaction regression
- [ ] optional pressure-sensitive secret/puzzle mechanics
- [ ] drawing/gesture laboratory utility inside Developer Tools

## Gate D — UI Shell / Layout / Themes / Visualizers

### Main navigation and shell
- [x] 9-page carousel: Home / Recon / Networks / Spectrum / Captures / Map / Expedition / Beast / System
- [x] persistent footer arrows/home/page dots
- [x] Control Center drawer
- [x] context help/touch-zone debug
- [x] Theme Library
- [x] Theme Detail / Theme Studio foundation
- [x] Visualizer Studio foundation
- [ ] full Apps launcher
- [ ] notification center
- [ ] user-editable page/widget layout studio

### Original Pwnagotchi preservation
- [x] Replica Dark/Light/Chroma fallback family
- [x] Native Pwnagotchi frame source `/var/tmp/pwnagotchi/pwnagotchi.png`
- [x] Native RAW preserving actual Jayofelony frame/action/expression
- [x] Native Dark / Native Light
- [x] Native Chroma using real Pwnagotchi frame as mask/source
- [~] Korrie71-inspired color/glow/effect direction implemented natively
- [ ] larger original-face Classic+ effect/palette library
- [ ] import/export format for community classic-face themes

### Structural theme families
- [x] Classic Beast
- [x] Matrix Beast
- [x] Starcore
- [x] Black Ice
- [x] Hunter
- [x] Minimal Field
- [x] Native Pwnagotchi family
- [~] non-Matrix Theme Studio controls begin in v0.10.0
- [x] Synthwave
- [x] Amber Tactical
- [x] Ghost Minimal
- [ ] Cyberpunk
- [ ] Stealth
- [ ] Red Alert
- [ ] Forest/Nature
- [ ] Vaporwave
- [ ] Space/Orbital
- [ ] Holographic
- [ ] Golden
- [ ] Samurai
- [ ] WOPR/NORAD
- [ ] Steampunk
- [ ] Blueprint
- [ ] Terminal+
- [ ] Biohazard
- [ ] Glitch
- [ ] Comic
- [ ] holiday/seasonal theme families
- [ ] user/community theme packs

### Theme controls
- [x] live preview strip
- [x] apply/cancel semantics
- [x] Matrix density/speed/trail/glyph/layer controls
- [x] Matrix true single color
- [x] Matrix 1/2/3/4 color architecture
- [x] Matrix background/mixed/foreground rain
- [x] Matrix reaction toggle
- [x] Native Chroma mood/fixed palette/glow/effects
- [~] Classic grid/scanline/pulse controls
- [~] Starcore star/twinkle/orbit controls
- [~] Black Ice frost/drift/crystal controls
- [~] Hunter grid/reticle/ember controls
- [~] Minimal ambient/panel controls
- [ ] arbitrary color picker/sliders on companion web UI
- [ ] primary/secondary/tertiary/quaternary weighting sliders
- [ ] save-as-variant / favorites / tags
- [ ] import/export/share theme package

### Visualizer / graph renderer library
- [x] Sparkline
- [x] Line
- [x] Area
- [x] Multi-line
- [x] Bars
- [x] Stacked bars primitive
- [x] Histogram
- [x] Heatmap
- [x] Waterfall/history strip
- [x] Oscilloscope waveform
- [x] Radial gauge
- [x] Donut
- [x] Radar/spider
- [x] Polar plot
- [x] Signal meter
- [x] Timeline/event raster
- [x] numeric + microtrend hybrid
- [~] renderer selection on Recon/Spectrum/Captures/System
- [ ] stacked area
- [ ] true RF spectrogram fed by SDR data
- [ ] RSSI trail renderer
- [ ] channel occupancy block renderer
- [ ] theme-specific graph skins and animations
- [ ] data-aware eligibility UI so nonsensical renderers are hidden
- [ ] per-widget renderer selection, not just page-level

### Layout system
- [~] structural geometry varies by theme
- [ ] Minimal density profile
- [ ] Classic density profile
- [ ] Balanced density profile
- [ ] Dense density profile
- [ ] Field density profile
- [ ] Monster density profile
- [ ] widget move/resize/show/hide
- [ ] layout save/load independent of theme
- [ ] context-driven automatic layout changes

## Gate E — Beast Experience / Personality / Progression / Secrets

### Beast personality
- [x] current mood/mode-aware Beast face foundation
- [x] progression stages: Hatchling / Cub / Scout / Tracker / Hunter / Beast / Alpha / Apex / Monstergotchi
- [x] finite Level 1–100 system
- [x] session aura foundation
- [ ] mature blink/squint/eye tracking/dilation
- [ ] richer mouth/ear/horn/tail animation where style supports it
- [ ] capture excitement / hunting / sleep / heat / GPS-lost / level-up reactions
- [ ] face packs / evolution forms / alternate personas
- [ ] habitat/orbiting-hardware/2.5D Beast scenes

### Achievements / awards / collections
- [x] rarity: Common / Uncommon / Rare / Epic / Legendary / Mythic
- [x] long-tail milestone catalog
- [x] interactive Achievement / Awards browser
- [x] lock/unlock state
- [x] progress counters and bars
- [x] filter All/Unlocked/Locked/Near
- [x] sort Progress/Rarity/Name
- [x] detail view and rewards
- [ ] Secrets tab
- [ ] Collections tab
- [ ] badges/trophies/visual cabinet
- [ ] hundreds of achievements across exploration/hardware/themes/seasons/sessions/secrets
- [ ] ultra-long-tail 1,000 / 10,000+ legendary/mythic unlock chains

### Rare Moments / Easter eggs
- [x] private deterministic yearly schedule foundation
- [x] powered-off opportunity can be missed
- [x] occurred/rendered/witnessed distinction
- [x] deliberate tap acknowledgement model
- [x] rarity-dependent durations
- [x] preview mode that does not consume real opportunities
- [x] fade presentation
- [x] drift presentation
- [x] cross-screen presentation
- [x] orbit presentation
- [x] ghost presentation
- [x] storm presentation
- [x] apparition presentation
- [x] procedural cinematic presentation
- [ ] production-quality 5–60 second pre-rendered cinematics
- [ ] rare symbols/messages hidden inside Matrix rain
- [ ] theme-specific hidden artifacts
- [ ] secret timing/date/vendor/channel/hardware combinations
- [ ] intentionally subtle one-frame/ghost/background discoveries
- [ ] Easter-egg reward catalog and spoiler documentation

### Cipher Console / secret entry
- [ ] keypad mode
- [ ] numpad mode
- [ ] phone-pattern dots
- [ ] retro D-pad + A/B/Start/Select
- [ ] combination lock
- [ ] puzzle/symbol modes
- [ ] Konami-style sequences without conflicting with global gestures

### Seasonal / celestial / environmental
- [x] season calculation groundwork
- [x] dawn/day/dusk/night groundwork
- [x] moon phase/illumination groundwork
- [ ] sunrise/sunset/moonrise/moonset presentation
- [ ] solstice/equinox events
- [ ] spring/summer/fall/winter visual modifiers
- [ ] Halloween / Christmas / New Year content
- [ ] weather source integration
- [ ] rain/snow/wind/heat overlays
- [ ] sensor-driven local environment themes
- [ ] astronomy/zodiac optional presentation

### Sessions / Expeditions / Memory
- [~] Begin Expedition — automatic core-session begin/recovery exists; manual named start remains
- [~] end-session recap — summary data persists; polished recap UI remains
- [~] route/distance/AP/capture/hardware/temp/error/XP summary — route/distance/AP/capture/temp/CPU/battery/XP foundation exists; hardware/error enrichment remains
- [ ] session naming/notes/tags
- [ ] replay session
- [ ] Memory Vault / scrapbook
- [ ] automatic milestone screenshots/cards
- [ ] best/longest/hottest/coldest/rarest records

## Gate F — Apps / Plugins / Hardware Expansion

### Core apps
- [~] Logs foundation via collected journals
- [~] Diagnostics/health foundation
- [~] Services data foundation
- [~] Storage data foundation
- [~] GPS/Map foundation
- [~] Performance/history foundation
- [~] Themes/Layouts/Faces
- [ ] full Logs app
- [ ] Diagnostics app
- [ ] Services app
- [ ] Storage app
- [ ] Notifications app
- [ ] Timeline app
- [ ] Backup/Restore app
- [ ] File/Export app
- [ ] Terminal app
- [ ] Developer Tools app

### Networks / captures / maps
- [x] live Networks table foundation
- [x] Recon radar/list foundation
- [x] Spectrum visualization foundation
- [~] Capture Vault placeholder/analytics
- [~] map/grid/GPS placeholder
- [ ] searchable/sortable Network Encyclopedia / BeastDex
- [ ] AP detail pages / first/last seen / vendor / history
- [ ] Capture Vault indexing/validation/session linking
- [ ] map tile download/cache/import
- [ ] breadcrumb/full-session route
- [ ] AP encounter/capture markers
- [ ] heatmaps / return encounters
- [ ] Bluetooth / ADS-B / Meshtastic / sensor layers
- [ ] 2.5D perspective encounter maps and signal towers

### Plugin system
- [x] extension architecture specification
- [x] AVAILABLE → STAGED → INSTALLED → ENABLED model
- [ ] Plugin Manager catalog
- [ ] multiple repository discovery
- [ ] staged install
- [ ] compatibility/dependency checks
- [ ] restart-required metadata
- [ ] last-error/health display
- [ ] per-plugin config editor
- [ ] `/etc/pwnagotchi/conf.d/` managed fragments
- [ ] config broker: snapshot/parse/validate/apply/watch/rollback
- [ ] Beast adapters for plugins that otherwise draw hard-coded coordinates
- [ ] custom Beast module SDK

### Hardware Capability Bus / Hardware Studio
- [x] capability architecture foundation
- [x] USB/I2C/GPIO device-class concept
- [x] remember-role-by-ID/serial design
- [ ] Hardware Studio UI
- [ ] USB tree / driver / capability / role / errors
- [ ] AWUS036ACM enrollment and role profile
- [ ] TP-Link T2U Nano capability detection
- [ ] Edimax RTL8188CUS capability detection
- [ ] Bluetooth dongle roles
- [ ] RTL-SDR enrollment
- [ ] secondary storage enrollment
- [ ] keyboard/mouse/gamepad hints
- [ ] audio/mic/haptic/RGB devices
- [ ] IMU/compass/environment sensors
- [ ] NFC/RFID/IR/GPIO/UART/logic-analyzer devices
- [ ] LoRa/Meshtastic/Zigbee/Thread classes
- [ ] camera/thermal classes

### RF / SDR apps
- [ ] Spectrum Analyzer
- [ ] Signal Hunter
- [ ] RF Recorder
- [ ] Frequency Book
- [ ] ADS-B Sky
- [ ] rtl_433 Weather RF
- [ ] Broadcast FM/RDS
- [ ] Marine/AIS
- [ ] Radio Explorer
- [ ] modular receive-focused app framework

### Power / dock / rules
- [x] Power Core foundation
- [x] Dock definition: external power + Ethernet + enrolled home network
- [ ] INA219/UPS telemetry final hardware hookup
- [ ] battery runtime/charge trends
- [ ] Dock automation: backup/sync/index/update/map downloads
- [ ] Rules Engine editor
- [ ] mode/profile automation

### Replay / simulation / demo
- [ ] recorded-session replay
- [ ] synthetic state simulator
- [ ] showcase/demo mode
- [ ] visual test scene generator

## Gate G — Operations / Performance / Public GitHub Release

### Performance / Resource Governor
- [x] cached DataFeed separates API work from render loop
- [x] compose/write timing telemetry
- [x] adaptive FPS foundation
- [x] thermal bands observed in physical tests
- [x] Resource Governor FULL / GUARDED / REDUCED / SURVIVAL foundation
- [x] thermal-aware animation/effect budgets foundation
- [~] per-effect cost classes — ambient/foreground/cinematic/history classes exist; finer module classes remain
- [x] graceful UI/history load shedding foundation
- [ ] SD-card write budget enforcement
- [ ] framebuffer benchmark profiles
- [ ] cinematic playback benchmark

### Boot / shutdown / recovery
- [x] reversible display handoff/recovery scripts
- [x] validation bundles
- [ ] Beast boot POST
- [ ] shutdown animation/status
- [ ] crash recovery UI
- [ ] self-healing incident log
- [ ] backup/restore workflow

### Web / phone companion
- [x] read-only local API foundation
- [ ] desktop web UI
- [ ] phone-optimized companion UI
- [ ] Theme Studio color sliders/pickers on web
- [ ] layout editor on web
- [ ] plugin/config/hardware management on web
- [ ] session/map/export browser

### Public project / GitHub
- [x] living master README
- [x] versioned A–G roadmaps
- [x] changelog
- [x] contributing draft
- [x] spoiler/secret docs
- [x] source/reference specs
- [ ] canonical repository structure
- [ ] `main` / `develop` / `feature/*` workflow
- [ ] issue/PR templates
- [ ] semantic release/version policy
- [ ] clean installer/upgrader/uninstaller
- [ ] migrations and rollback
- [ ] complete user guide
- [ ] complete developer architecture guide
- [ ] theme authoring guide
- [ ] plugin/module authoring guide
- [ ] troubleshooting/recovery guide
- [ ] attribution/license inventory
- [ ] community pack format
- [ ] automated CI tests
- [ ] reproducible release packaging/checksums
- [ ] release candidate gate
- [ ] public v1.0

## Current priority after v0.10.0 physical review

The repeated Matrix work was bug-driven, not a change in product scope. With v0.10.0 physically passed and v0.11.0 preparing for its physical gate, development continues across the complete product:

1. Expand the graph/visualizer engine and expose it through Visualizer Studio.
2. Give Classic, Starcore, Black Ice, Hunter and Minimal their own customization controls and stronger motion/background personalities.
3. Close the remaining whole-UI physical touch regression.
4. Continue Theme Studio from page-level options toward palettes, saved variants and layout independence.
5. Continue the Beast experience: collections/secrets, sessions, BeastDex, Capture Vault, Cipher Console and Memory Vault.
6. Implement Hardware Studio / Plugin Manager / Resource Governor.
7. Convert the mature tree into the GitHub-ready repository structure and public release workflow.

Nothing above is considered dropped merely because it is not in the next physical gate.

## Recovered pinned-conversation commitments — continuity audit 2026-09-21

The items below were recovered from the original long-form Beastagotchi/Monstergotchi conversation and source files. They are deliberately written into the canonical ledger so they cannot disappear merely because they were once discussed as “later” ideas.

### Operating modes / whole-device identity
- [ ] first-class mode selector: BEAST / SCOUT / SPECTRUM / SKY / MESH / FIELD / SYSTEM / LAB
- [ ] Authorized LAB mode arming screen, explicit target/authorization controls, timeout and activity log
- [ ] Monster View ultra-dense all-systems dashboard
- [ ] command palette for fast navigation/actions
- [ ] profile automation by location/dock/time/context
- [ ] geofenced Home / Away / Field / Lab profiles
- [ ] Beast DNA export/import: identity, progression, themes, settings, plugins and durable history
- [ ] multiple Beast identities and authenticated Beast-to-Beast encounters

### Field awareness / RF Universe
- [ ] RF Universe unified map/timeline for Wi-Fi + Bluetooth + SDR objects + aircraft + mesh + sensors
- [ ] passive Bluetooth observer with encounter history/RSSI/GPS enrichment
- [ ] Kismet/Scout integration using a secondary radio without destabilizing the Pwnagotchi radio
- [ ] aircraft-radar touchscreen experience layered over ADS-B data
- [ ] 433/915 MHz “world around me” object view from rtl_433-compatible observations
- [ ] Meshtastic/LoRa terminal and map layer
- [ ] optional APRS/pager/weather/other lawful receive-only visualization adapters
- [ ] Frequency Book / learned local RF environment
- [ ] explanatory “What am I looking at?” detail mode for networks/devices/signals
- [ ] defensive awareness annotations: open/obsolete encryption, duplicate/hidden SSID, anomalous signal/name patterns without exploit scoring

### Plugin / update integrity
- [ ] dependency manager for Pwnagotchi plugins and Beast modules
- [ ] generated plugin configuration UI from known schemas/TOML
- [ ] plugin health sandbox/quarantine path for crashing/incompatible extensions
- [ ] plugin repository Installed / Available / Updates / Broken / Incompatible views
- [ ] patch auditor: PATCH PRESENT / PATCH LOST / UPSTREAM FIX DETECTED
- [ ] automatic post-update regression suite with rollback on failed gate
- [ ] immutable/replaceable Beast-owned runtime tree with explicit migration boundaries

### Diagnostics / self-healing / forensics
- [ ] full Live Logs app: Pwnagotchi, Bettercap, journal, kernel, Beast Core, plugins, boot, event log
- [ ] one-tap Diagnostic Center with green/yellow/red checks and repair actions
- [ ] controlled self-repair actions: monitor-interface rebuild, service restart, GPS reset, remount/recovery actions
- [ ] Black Box recorder retaining pre-failure state and related logs
- [ ] incident timeline/flight-recorder correlation view
- [ ] “Explain this error” human-readable incident interpretation
- [ ] Boot POST sequence ending in BEAST ONLINE
- [ ] shutdown/status animation and safe-shutdown state
- [ ] Debug Mode with developer overlays and one-tap diagnostic package
- [ ] built-in searchable offline manual/wiki containing platform notes and known fixes

### Hardware Studio / accessory universe
- [ ] powered-USB/per-port reset integration for wedged GPS/SDR/Wi-Fi devices
- [ ] RTC (for example DS3231 class) support for trustworthy offline timestamps
- [ ] PWM fan controller, thermal history and optional RPM/duty telemetry
- [ ] RGB status light / light-pipe output adapter
- [ ] haptic motor output adapter
- [ ] speaker/buzzer/audio feedback and optional theme sound packs
- [ ] rotary encoder and physical Back/Home/Select controls
- [ ] NFC reader and user-defined safe macro tags
- [ ] USB gadget service profiles where target Pi hardware supports them
- [ ] camera adapter for QR/session/documentation use
- [ ] environmental sensor station: temperature/humidity/pressure first, extensible to air quality/light/particulates
- [ ] IMU / magnetometer / heading / motion adapter
- [ ] proximity/wake/dock-presence sensor class
- [ ] distributed Pi Zero/ESP32 satellite sensors
- [ ] Beast Bus accessory protocol over JSON/MQTT/serial for self-describing accessories

### Connectivity / companion / home base
- [ ] isolated secondary management AP without stealing the Pwnagotchi radio
- [ ] local file portal for captures/reports/screenshots/logs/backups
- [ ] QR presentation for management URL, session/diagnostic IDs and other temporary local information
- [ ] optional MQTT telemetry/command bridge
- [ ] optional Home Assistant integration
- [ ] Dock/Home Base automation: NAS archive, backup, index, map downloads, updates and heavier post-processing
- [ ] authenticated Beast peer mesh and coordinator role

### Experience / personality / world
- [ ] dynamic world animation reacting to time, environment, RF activity and optional aircraft/weather/sensor data
- [ ] ambient screensavers: recent-SSID Matrix, spectrum waterfall, LCARS diagnostics, rotating map, Beast animation
- [ ] optional local AI for device help/log interpretation, kept outside the critical Pwnagotchi path
- [ ] optional local voice commands/status personality
- [ ] session photos/notes/tags and visual Expedition replay
- [ ] per-session Beast mood/theme history
- [ ] peer-Beast encounter animations
- [ ] dock transition animations

### Reserved visual identities / authoring
- [ ] LCARS / starship-computer structural family beyond the current Starcore interpretation
- [ ] Retro CRT green/amber family
- [ ] Oscilloscope Lab theme
- [ ] Sonar/Submarine theme
- [ ] Mission Control theme
- [ ] Industrial Cyberdeck theme
- [ ] Wireframe theme
- [ ] Retro Game theme
- [ ] Pride/community celebration packs
- [ ] theme-reactive sound packs
- [ ] procedural theme randomizer
- [ ] theme scheduler by time/location/profile
- [ ] user-shareable theme/layout/face bundles
- [ ] hardware RGB/LEDs synchronized with current theme/status

### Offline-first / data durability
- [ ] offline map tile packs and import/export management
- [ ] local OUI/vendor database update pipeline
- [ ] offline documentation/help bundle
- [ ] optional dock-side export to richer telemetry stacks such as InfluxDB/Grafana without making them runtime dependencies
- [ ] configurable SD-card write budget and retention policies

## v0.11.0 physical-gate focus

1. Resource Governor mode transitions and graceful recovery under real Pi temperature/load conditions.
2. Verify saved theme settings are not destroyed by temporary load shedding.
3. Verify Expedition persistence, GPS route growth, AP uniqueness and clean restart recovery.
4. Physically evaluate Synthwave, Amber Tactical and Ghost Minimal for readability and touch ergonomics.
5. Confirm Expedition/Map/System additions did not regress footer/navigation or Native Pwnagotchi mode.
6. Review thermal behavior before allowing heavier apps to build on top of the new budget system.

