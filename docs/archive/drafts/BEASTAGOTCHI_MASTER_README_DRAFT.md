# Beastagotchi Master README — Living Draft

> This is the single-file operator/developer manual that will become the final Beastagotchi README. It is intentionally maintained inside every release from v0.7 onward so installation, operation, recovery, modification, extension and file locations do not become tribal knowledge.

## 1. What Beastagotchi is

Beastagotchi is a modular Raspberry Pi 4 field-computer platform built around a protected Pwnagotchi engine. Pwnagotchi remains responsible for its core Wi-Fi behavior. Beast Core sits beside it and provides canonical state, events, history, hardware discovery, GPS/context, dock/power logic and future action/config management. Beast UI owns the 480×320 touch display when claimed and renders all Beast pages/themes.

Architecture:

```text
Pwnagotchi / Bettercap / Linux / GPS / hardware
                    |
               Beast Core
      collectors -> state -> events/history
                    |
            local HTTP/WebSocket API
                    |
                Beast UI
        pages / widgets / renderers / themes
```

## 2. Current release model

The project is currently distributed as versioned release trees/tarballs, not as a live Git checkout on the Pi. Do not assume a `main`/`develop` Git branch exists on the device yet.

Current development convention:

```text
beast_core_foundation_v0_X/     release source tree
/opt/beast-core/                deployed Beast Core runtime
/opt/beast-ui/                  deployed Beast UI runtime
/etc/beastagotchi/              Beast configuration
/var/lib/beastagotchi/          persistent Beast state/preferences/database
```

A proper Git workflow is planned before the final 1.0 handoff. The intended long-term model is:

```text
main                last validated stable release
develop             current integration work
feature/<name>      isolated feature work
release/vX.Y        release stabilization when needed
```

The final README will state the exact repository path and commands once that repository is established.

## 3. Fast path: where everything lives on the Pi

### Beast Core runtime

```text
/opt/beast-core/beastcore/
```

Important code:

```text
/opt/beast-core/beastcore/core.py
/opt/beast-core/beastcore/api.py
/opt/beast-core/beastcore/state.py
/opt/beast-core/beastcore/events.py
/opt/beast-core/beastcore/context.py
/opt/beast-core/beastcore/dock.py
/opt/beast-core/beastcore/collectors/
```

### Beast UI runtime

```text
/opt/beast-ui/beastui/
/opt/beast-ui/themes/
/opt/beast-ui/config/
/opt/beast-ui/bin/
```

Important UI code:

```text
/opt/beast-ui/beastui/engine.py
/opt/beast-ui/beastui/pages.py
/opt/beast-ui/beastui/face.py
/opt/beast-ui/beastui/backgrounds.py
/opt/beast-ui/beastui/controls.py
/opt/beast-ui/beastui/input.py
/opt/beast-ui/beastui/widgets/
/opt/beast-ui/themes/*.json
/opt/beast-ui/config/touch.json
```

### Beast configuration and persistent data

```text
/etc/beastagotchi/core.toml
/var/lib/beastagotchi/
/var/lib/beastagotchi/ui/preferences.json
/var/lib/beastagotchi/display-handoff/
```

### Pwnagotchi integration

```text
/etc/pwnagotchi/config.toml
/etc/pwnagotchi/conf.d/
/etc/pwnagotchi/custom-plugins/
/run/beastagotchi/pwnagotchi_bridge.json
```

The Beast Bridge Pwnagotchi plugin is installed separately and emits callbacks/state for Beast Core. Beastagotchi should avoid invasive edits to Pwnagotchi source whenever possible.

### systemd services

```text
/etc/systemd/system/beast-core.service
/etc/systemd/system/beast-ui.service
pwnagotchi.service
bettercap.service (or the image's Bettercap launcher/service path)
gpsd.service
```

Useful commands:

```bash
systemctl status beast-core
systemctl status beast-ui
systemctl status pwnagotchi
journalctl -u beast-core -f
journalctl -u beast-ui -f
journalctl -u pwnagotchi -f
```

Beast Core health:

```bash
curl -s http://127.0.0.1:8090/health | python3 -m json.tool
```

Canonical state:

```bash
curl -s 'http://127.0.0.1:8090/state?meta=0' | python3 -m json.tool
```

Run `beast-paths` after installation for a compact copy/paste reference.

## 4. Display ownership and recovery

Pwnagotchi and Beast UI must not both own `/dev/fb1` at the same time.

Reversible test:

```bash
sudo /opt/beast-ui/bin/claim_display_test.sh 15
```

Confirm Beast display ownership:

```bash
sudo /opt/beast-ui/bin/confirm_display.sh
```

Restore Pwnagotchi display ownership:

```bash
sudo /opt/beast-ui/bin/release_display.sh
```

Status:

```bash
sudo /opt/beast-ui/bin/display_status.sh
```

## 5. Touch controls

The on-device CONTROLS / HELP screen is generated from the same interaction registry used by Beast UI.

Current global controls:

- Tap: select/open; footer buttons.
- Long press: open/close Visual Control.
- Swipe left/right: next/previous main page.
- Swipe down: open Visual Control.
- Swipe up: close drawer/help.
- Bottom left/right: large reliable previous/next touch zones.
- Footer center: Home.
- Touch Zones: developer overlay showing active global hit targets.

The final README will include every page-specific interaction as those interactions become production features.

## 6. Themes and visual files

Theme manifests:

```text
/opt/beast-ui/themes/*.json
```

Theme code is intentionally separated into data/layout/renderer/theme/face/animation concepts so future themes do not require rewriting Beast Core.

Current structural themes include Classic Beast, Matrix Beast, Starcore, Black Ice, Hunter and Minimal Field. These are engine-validation themes, not the final extent of the visual library.

## 7. Editing Beastagotchi later

### Important rule

Runtime files under `/opt` can be inspected, but do not treat ad-hoc edits there as your only copy. A future release install may replace runtime code.

During pre-1.0 development, make changes in the extracted release source directory under `/home/pi/`, then run the release installer to deploy the changed files. Example:

```bash
cd /home/pi/beast_core_foundation_v0_9
nano beastui/backgrounds.py
sudo ./install_ui.sh
```

Core example:

```bash
cd /home/pi/beast_core_foundation_v0_9
nano beastcore/context.py
sudo ./install.sh
sudo systemctl restart beast-core
```

Theme example:

```bash
cd /home/pi/beast_core_foundation_v0_9
nano beastui/themes/matrix.json
sudo ./install_ui.sh
```

Before 1.0, this will be replaced by the documented Git/dev-tree workflow so local custom changes can be committed, diffed and preserved across upgrades.

## 8. Pwnagotchi plugins

Current Jayofelony Pwnagotchi separates repository sources, the custom-plugin install directory and plugin configuration.

Typical locations on this Beast:

```text
main.custom_plugins = "/etc/pwnagotchi/custom-plugins/"
main.confd = "/etc/pwnagotchi/conf.d/"
```

Repository ZIP URLs live in the `main.custom_plugin_repos` list in `/etc/pwnagotchi/config.toml`.

Important: adding a repository and running `pwnagotchi plugins update` updates/discovers the plugin catalog. It does **not** mean every plugin in every repository is automatically installed, configured and enabled.

Normal workflow:

```bash
sudo pwnagotchi plugins update
sudo pwnagotchi plugins list
sudo pwnagotchi plugins install <plugin-name>
```

Then configure the plugin and explicitly enable it. Each third-party plugin may have different dependencies and configuration keys.

### Beastagotchi's intended plugin workflow

Beast will manage four states:

```text
AVAILABLE -> STAGED -> INSTALLED -> ENABLED
```

Beast will maintain a curated compatibility/config registry containing, per plugin:

- source repository
- plugin name/version/hash
- compatible Pwnagotchi versions
- dependencies
- required hardware/services
- known-good configuration schema/defaults
- restart requirement
- Beast adapter/integration level
- health/errors

Trusted plugins can be pre-installed with `enabled = false`, then toggled from Beast UI. Unknown/unreviewed repository code should not be blindly bulk-enabled.

### Config fragments

Beast will prefer separate managed TOML fragments under:

```text
/etc/pwnagotchi/conf.d/
```

rather than turning the main config into an enormous hand-edited file. Example conceptual fragment:

```toml
[main.plugins.example]
enabled = false
interval = 30
```

Before mutation is enabled, Beast's config broker will snapshot, validate, apply, restart only if necessary, watch for failure and roll back on failure.

## 9. Hardware / capability model

Beast treats hardware by detected capability and remembered role rather than hard-coding every product name.

Planned/known classes include:

- onboard Wi-Fi
- AWUS036ACM and other USB Wi-Fi adapters
- GPS
- RTL-SDR
- Bluetooth adapters
- storage
- keyboard/mouse/gamepad
- Ethernet
- UPS/power telemetry
- environmental sensors
- LoRa/Meshtastic
- NFC/IR/serial/GPIO accessories

Hardware Studio will expose device identity, driver, capabilities, role, status and associated apps.

## 10. Dock mode

For this build, `DOCKED` means both:

1. external/wired power is detected; and
2. Ethernet is connected to the enrolled home network.

No physical dock accessory is required.

## 11. Backups and safety philosophy

Beastagotchi is designed so the working Pwnagotchi engine remains protected underneath it. Before any future mutating action, the design target is:

```text
snapshot -> validate candidate -> apply -> health-check -> keep or rollback
```

The final project will include config history, last-known-good rollback, incident capture and a diagnostic bundle workflow.

## 12. Final documentation promise

At project completion this file will be promoted from LIVING DRAFT to the canonical Beastagotchi README and will contain, in one place:

- full installation from a fresh supported Pwnagotchi image
- all files/directories and what they do
- complete service/API map
- all controls and gestures
- every page/app/module
- theme/layout/face/widget customization
- plugin repository/install/configuration workflow
- hardware enrollment
- battery/UPS setup
- dock/home enrollment
- backup/restore/recovery
- database/session/capture locations
- developer workflow and Git branch structure
- how to add a collector, module, adapter, page, widget, renderer, theme and face pack
- troubleshooting and diagnostic commands
- upgrade/uninstall paths
- release/version history

The goal is that a future owner—including the original builder months or years later—can understand and modify Beastagotchi without needing this chat history.


## 13. Progression / Beast DNA (v0.8)

Beast progression is cosmetic/identity-oriented and never changes RF behavior. Persistent state is stored at:

```text
/var/lib/beastagotchi/profile.json
```

The level cap is finite:

```text
1    Hatchling
5    Cub
10   Scout
20   Tracker
35   Hunter
50   Beast
70   Alpha
85   Apex
100  Monstergotchi
```

After level 100, collections, lifetime encounter records, achievements, cosmetics, BeastDex progress and session records may continue without an endless prestige-level treadmill.

Current safe XP sources include lifetime-first AP discoveries, first-time vendor discoveries, GPS locks, cataloged captures and long-running uptime milestones. Repeated sightings of the same AP do not repeatedly award lifetime-new AP XP.

The first achievement framework is also persistent. Unlocks generate normal Beast events and may award a small one-time XP bonus.

Session auras are temporary and are currently driven by session-unique AP counts:

```text
0     none
10    static
25    spark
50    electric
100   inferno
200   apex
```

Theme-specific aura artwork will continue to evolve.

## 14. Lifetime encounter database / BeastDex foundation

Lifetime Wi-Fi encounters live inside:

```text
/var/lib/beastagotchi/beast.db
```

The `wifi_encounters` table stores the BSSID, first/last seen time, observed session count, SSID, vendor, channel and strongest observed RSSI.

Read-only summary API:

```bash
curl -s 'http://127.0.0.1:8090/encounters?limit=20' | python3 -m json.tool
```

This table is the beginning of the Network Encyclopedia / BeastDex layer. It is deliberately separate from the ephemeral Bettercap AP list.

## 15. UI data feed and renderer model

Beginning in v0.8, Beast UI does not perform state/history HTTP requests inside the framebuffer composition path. A background data-feed thread maintains cached snapshots. Rendering consumes the cache.

This split is intentional:

```text
Beast Core API/history
       |
 background data feed
       |
 cached UI snapshot
       |
 compositor -> RGB565 framebuffer
```

The runtime performance file:

```text
/run/beastagotchi/ui-runtime.json
```

records total render time, composition time and framebuffer-write time separately.

Spectrum is the first page with a user-switchable visualization renderer. Tap its main graph to cycle:

```text
Bars -> Line -> Heatmap -> Radar -> Bars
```

The selected renderer is persisted in:

```text
/var/lib/beastagotchi/ui/preferences.json
```

The same data-source/renderer separation will be extended to additional widgets.

## 16. Event Reaction Governor

Beast UI selects the highest-priority recent event before showing full-screen/background reactions. Critical system/thermal failures outrank cosmetic progression events.

Typical priority order:

```text
collector/system fault
thermal warning
evolution
level-up
capture
achievement
dock/GPS
vendor/AP discovery
context mode
```

Each theme remains free to express the selected event differently.

## 17. Current read-only local API

```text
GET /health
GET /state
GET /events
GET /history
GET /encounters
WS  /ws
```

The API binds to `127.0.0.1` by default. Mutating configuration/action endpoints are intentionally deferred until the config/action broker and rollback layer are ready.


### Visual motion rule (v0.8.1)

The long, screen-spanning CRT scanline is intentionally singular: one horizontal line moves downward through the content area. Theme reactions must not create additional full-width/full-height scan bars. Matrix reactions use localized glitch fragments; Starcore uses perimeter segments. This rule exists because the physical v0.8 test showed that multiple large scan bars overwhelmed the 480×320 display.


### Physical readability / Matrix motion rule (v0.8.2)

The 3.5-inch physical panel is the final authority for legibility. The BEAST progression page uses large dedicated status rows and never places micro text inside progress bars. This layout is shared across themes so theme styling cannot reduce the information below the validated readability floor.

Matrix digital rain uses fixed X columns with independent per-column speeds, starting phases, and trail lengths. Animation changes Y only; no rain stream may move laterally. The sole screen-spanning moving horizontal effect is the dedicated one-pixel scanline, which travels from the top of the content region toward the bottom independently of Matrix rain and event reactions.


## 10. v0.9 Theme Studio and effect customization

The old small six-button theme picker is replaced by a large-card **Theme Library**. Long-press or swipe down opens the Beast Control Center; Theme Library opens a vertically browsable list of large touch targets. Tapping a card opens a full-screen Theme Detail screen. Changes preview live and are persisted only when APPLY is pressed.

Matrix currently exposes the first per-theme runtime controls:

```text
Layer:   BACKGROUND / MIXED
Density: NORMAL / DENSE / STORM
Speed:   NORMAL / FAST / FURY
Palette: GREEN / CYAN / VIOLET / RED / AMBER / RAINBOW / HOLIDAY
```

Per-theme options are persisted in:

```text
/var/lib/beastagotchi/ui/preferences.json
```

The schema is deliberately extensible so future themes can register their own palettes, particles, face packs, animation intensity, seasonal behavior, layout presets and reaction options without rewriting Beast Core.

## 11. Achievements, rarity and progression

Beast progression has a finite maximum level of 100, while achievements/collections/lifetime records continue after the cap. The achievement catalog uses Common, Uncommon, Rare, Epic, Legendary and Mythic presentation tiers.

Read-only achievement API:

```bash
curl -s http://127.0.0.1:8090/achievements | python3 -m json.tool
```

The catalog intentionally contains long-tail goals such as 10,000 lifetime-first signals and level 100. Achievement state is stored in the persistent Beast profile:

```text
/var/lib/beastagotchi/profile.json
```

The on-device Achievements screen is accessible from the Beast Control Center.

## 12. Rare Moments, omens and secret content

Rare Moments are scarce cosmetic events. Beast creates a private per-device seed under:

```text
/var/lib/beastagotchi/secrets/
```

That seed derives a deterministic 1–4-event annual schedule without exposing future event times to the normal UI. If Beast is powered off for an entire eligible event window, that opportunity is recorded as missed rather than rescheduled.

Before a Rare Moment, faint vector sigils may fade over the ordinary UI. When the Rare Moment itself appears, a deliberate screen touch records the event as **witnessed**. Merely rendering the event is not treated as proof the user noticed it.

The current v0.9 cinematic is procedural. Future Rare Cinematic Packs can provide pre-rendered 480×320 frame/video assets after physical decode-performance testing.

Safe visual preview commands (do not consume a real event or unlock the witness achievement):

```bash
beast-rare-preview omen 20 --sigil eye
beast-rare-preview moment 15 --sigil eye --rarity legendary
beast-rare-preview clear
```

Full spoiler documentation lives in:

```text
/usr/local/share/beastagotchi/SPOILERS_SECRETS_AND_ACHIEVEMENTS.md
```

Future secret codes will live inside a dedicated **Cipher Console** rather than hijacking long-press/swipe gestures used by normal navigation.

## 13. Seasonal and celestial context

Beast Core now publishes low-cost ambient context keys such as season, day phase and approximate moon phase. These are intended for theme overlays, achievements and secrets. Weather is never guessed: weather effects must eventually come from a real online source or physical sensor.

Representative keys:

```text
ambient.season
ambient.day_phase
celestial.moon.phase
celestial.moon.illumination_pct
```

## 14. Intended public GitHub packaging

The final public repository should remain understandable both to people who only want to install Beastagotchi and to people who want to extend it. Planned top-level documentation includes:

```text
README.md
CHANGELOG.md
CONTRIBUTING.md
docs/DEVELOPMENT.md
docs/HARDWARE.md
docs/THEME_STUDIO.md
docs/ACHIEVEMENTS.md
docs/SECRETS_AND_EASTER_EGGS.md
```

The spoiler document is deliberate: users can avoid it if they want discovery, while builders who need to know that a secret/unlock exists have a canonical reference.

## v0.9.1 — physical UI interaction and Matrix de-Moire corrections

Physical testing of v0.9 showed that two otherwise-correct designs were still awkward on the real 3.5-inch resistive TFT:

- vertical scrolling through three small Theme Library cards required more precise swipes than desired;
- Matrix option rows hid their action behind a whole-row tap and did not provide enough visible granularity.

v0.9.1 changes the physical interaction model rather than merely changing thresholds.

### Theme Library

The touchscreen now shows **two larger cards per page**. The full card remains tappable, while large `PREV`, `BACK`, and `NEXT` controls provide a reliable alternative to vertical swipes. Vertical swipes still page through the library but are no longer required.

### Matrix Theme Studio

Each setting row now has large visible `<<` and `>>` steppers. Density expands to:

`Sparse / Light / Normal / Dense / Heavy / Storm / Deluge`

Speed expands to:

`Drift / Slow / Normal / Fast / Fury / Torrent`

Layer remains `Background / Mixed`, while palette retains the current preset choices. More advanced primary/secondary/tertiary color editing remains planned for Theme Studio rather than forcing tiny color controls onto the 480×320 device.

### Matrix diagonal-pattern correction

The physical LCD/camera revealed diagonal/Moire bands even though every Matrix stream had a fixed X coordinate. The cause was the overly regular column and glyph lattice. v0.9.1 intentionally varies spacing between columns and glyph cadence within each vertical stream. Streams still fall vertically; only the regular grid that produced the visible diagonal interference pattern is removed.

### Rare Moment final-quality target

The existing procedural Rare Moment animation is a validation fallback, not the final cinematic quality target. See `Beastagotchi_Rare_Cinematic_Pipeline.md`. Final rare events are intended to support short pre-rendered 480×320 cinematic assets after decode-performance testing on the Pi 4.

## v0.9.2 — Touch Lab integration and original Pwnagotchi identity

### Measured touch profile

Three stylus passes and three natural-finger passes were used to derive a pooled affine calibration candidate. It was later physically A/B tested and **rejected** because the restored/original calibration felt better in actual use. The production installer therefore preserves `/opt/beast-ui/config/touch.json` and installs the old candidate only as the clearly marked reference file `/opt/beast-ui/config/touch_experimental_rejected_v092.json`. Normal validation must not activate it.

`beast-touchcal status` reports the production decision. Deliberate developer diagnostics require the explicit `--experimental` switch. Touch Lab remains authoritative for target sizing, edge padding, gesture behavior and pressure characterization rather than for replacing the active coordinate transform.

The measured interface policy is now:

- less than 48 px: avoid for direct finger controls;
- 48–52 px: constrained secondary control only;
- 56–64 px: ordinary controls;
- 72+ px: primary/critical actions;
- visible artwork may be smaller than its invisible hit box;
- edge controls receive additional invisible padding where possible.

### Stock-style Pwnagotchi replica themes

v0.9.2 introduced Beast-rendered stock-style replicas. These preserve the original text-face language, but they are not the Jayofelony renderer itself. The built-in replica family is:

- **Pwnagotchi Replica Dark** — black background, white stock-style text face;
- **Pwnagotchi Replica Light** — white background, black stock-style text face;
- **Pwnagotchi Replica Chroma** — original text-face vocabulary with mood-reactive color styling and Beast effects.

The original themes use a deliberately sparse stock-inspired Home screen, while still retaining Beastagotchi navigation and access to the wider platform.

### Korrie71 theme-manager direction

Reference: `https://github.com/Korrie71/pwnagotchi-theme-manager`

Beastagotchi adopts the useful concepts natively rather than requiring the plugin at runtime: original-face colorization, mood-aware colors/effects, live preview, per-element styling, effect stacks, animated backgrounds, touch editing and shareable theme definitions. Round/blob face packs are not part of the built-in Classic family by project choice.

The integration remains independently implemented so Beast UI keeps sole framebuffer ownership and its own compositor/state/touch architecture. Any future imported source or assets must preserve upstream attribution and licensing.


## v0.9.3 — Native Pwnagotchi Frame Bridge

The user explicitly required the **actual live Jayofelony Pwnagotchi face/actions**, not merely a Beastagotchi reproduction. v0.9.3 solves this without returning physical framebuffer ownership to Pwnagotchi.

Jayofelony's own `View.update()` renders the live Pwnagotchi UI and writes its current PNG canvas to:

```text
/var/tmp/pwnagotchi/pwnagotchi.png
```

That web-frame generation continues while `ui.display.enabled = false`. Beastagotchi can therefore keep sole ownership of `/dev/fb1`, read the frame Pwnagotchi itself generated, and display it full-screen. The Pwnagotchi engine, mood selection, random face variants, status strings and plugin UI remain authoritative.

Native profiles:

- **Pwnagotchi Native RAW** — the live Jayofelony canvas itself with configured physical rotation;
- **Pwnagotchi Native Dark** — exact native composition normalized to white ink on black;
- **Pwnagotchi Native Light** — exact native composition normalized to black ink on white;
- **Pwnagotchi Native Chroma** — exact native foreground/layout used as the mask for Beast color/glow treatment.

Native RAW/Dark/Light deliberately suppress Beast header/footer/scanline/reconstructed face. Long-press or a downward swipe opens Beast Control Center without stopping Beast Core. Rare omens/moments remain permitted as a final wrapper overlay.

Diagnostic:

```bash
beast-pwn-native
```

The command reports whether the source exists, its dimensions, age and whether it is exactly 480×320. If no source frame is available, Native mode shows an explicit diagnostic instead of silently substituting a replica.

### Touch-calibration decision

The pooled v0.9.2 affine candidate was physically A/B tested. The user reported the restored pre-v0.9.2 calibration feels better in normal use. That original calibration is therefore the production choice. Touch Lab remains valuable for hitbox sizing, pressure characterization, edge padding and gesture design, but its candidate coordinate transform is **not** the new default.


## v0.9.5 — UX / Theme / Achievement convergence gate

v0.9.5 is based on the exact source checkpoint copied from the physical Pi after Native RAW worked correctly. The checkpoint is a forensic/reference baseline; it does not retroactively mark v0.9.2 or v0.9.3 as stable releases.

### Touch geometry instead of touch remapping

The restored/original calibration remains production. A reusable hitbox layer now separates visible control artwork from the finger target. The measured policy is approximately 48 px minimum for constrained controls, 56–64 px for ordinary controls and 72+ px for primary actions. Edge expansion shifts inward instead of being clipped by the bezel.

### Matrix customization and de-Moiré work

Matrix Theme Studio now exposes Layer, Density, Speed, Trail, Glyph set, Palette, Accent mixing, foreground percentage and Custom Primary/Secondary/Tertiary/Quaternary slots. Secondary through quaternary may be independently disabled. A strict single-color selection no longer receives a hidden red accent.

The physical-TFT de-Moiré strategy keeps each stream at a fixed X coordinate but breaks the regular raster pattern using irregular column spacing, stream-specific cadence and tiny deterministic per-glyph vertical jitter. The protected normal scanline remains a separate compositor layer and must stay one full-width horizontal line moving top-to-bottom.

### Native Chroma effect family

Native Chroma continues to use `/var/tmp/pwnagotchi/pwnagotchi.png` as the authoritative layout/face source. v0.9.5 adds mood/fixed ink, fixed color palettes, glow strengths and Clean/Scanlines/Vignette/Grain/Pulse/Glitch/Halo effects. Beast still does not reconstruct the stock face in Native mode.

### Interactive Achievements / Awards

Core now publishes detailed progress rows with current value, target, percentage, category, rarity, XP reward, lock state and description. The on-device explorer provides Achievements/Awards tabs, All/Unlocked/Locked/Near filters, sorting, paging, progress bars and detail cards.

### Rare Event presentation vocabulary

Rare Moment metadata can now select `fade`, `drift`, `cross`, `orbit`, `ghost`, `storm`, `apparition` or `cinematic`. These procedural paths validate presentation mechanics; the final scarce Legendary/Mythic experiences still target much higher-quality short cinematic assets after a Pi-4 playback benchmark.

### Validation artifacts

Off-screen/source gate:

```text
/home/pi/beast-core-validation-v095.tar.gz
```

Physical gate:

```text
/home/pi/beast-display-validation-v095.tar.gz
```

The current roadmap is `Beastagotchi_Foundation_Roadmap_v2.3.md`.


### v0.9.5 physical follow-up: Matrix reaction isolation

The v0.9.4 physical validation separated a transient pink/magenta diagonal sweep from the actual Matrix rain. The captured framebuffer showed vertical green rain, while event history recorded a critical thermal transition at 80.34 C. The Matrix danger reaction moved its short bars in X and Y together; v0.9.5 replaces that with fixed-X vertical pulses and stationary danger corner brackets. Matrix Theme Studio now provides a `REACTIONS` On/Off option.

The same validation showed the Achievement Explorer was usable but still physically tight. v0.9.5 changes its interaction model from overlapping expanded hitboxes to non-overlapping screen partitions for tabs, filters, cards and paging.


## v0.10.0 — Visualization and theme-breadth expansion

v0.10.0 deliberately ends the period where Matrix consumed most visual-development attention. That focus was caused by physical TFT bugs, not by a change in project scope. The project-wide source of truth is now `Beastagotchi_Master_Completion_Matrix_v3.0.md`, which keeps every committed idea visible until it is implemented, deliberately deferred, or explicitly retired.

### Visualizer Studio

The Control Center now exposes Visualizer Studio. Recon, Spectrum, Captures and System each have renderer families that can be changed independently of the active theme. Direct graph taps also cycle the renderer where appropriate, while footer hit zones retain priority.

The renderer library now contains line, area, multi-line, bars, stacked-bar primitive, histogram, heatmap, waterfall/history strip, oscilloscope waveform, radial gauge, donut, radar, polar, signal meter, event timeline/raster and numeric+microtrend primitives. This is the beginning of the originally planned data-visualization system rather than a finished chart catalog.

### Non-Matrix Theme Studio breadth

Classic Beast gains configurable grid density, protected scanline enable and ambient pulse. Starcore gains star density, twinkle and orbit controls. Black Ice gains frost density, drift and foreground crystals. Hunter gains grid density, reticle and embers. Minimal Field gains ambient and panel-emphasis controls. These are structural/runtime settings, not just color swaps.

The next visual milestones include theme-native chart skins, additional structural themes from the original reference boards, per-widget renderer assignment, layout density profiles, movable/resizable widgets, saved variants and companion/web color controls.

### Performance and thermal note

Physical v0.9.x testing reached roughly 80 C during some sessions. The graphics goal is not being reduced; instead the planned Resource Governor remains a Gate F/G requirement so the system can lower expensive ambient work intelligently under thermal pressure while keeping Pwnagotchi/Beast Core responsive.

### v0.10 physical validation focus

The physical gate intentionally spends little time on Matrix. It validates Visualizer Studio, representative renderer families, non-Matrix Theme Studio variants, generalized graph hit zones, Native RAW regression and overall performance/thermal behavior.

## v0.11.0 — Resource Governor, Expeditions and continuity audit

v0.11.0 begins the reliability/platform phase that the earlier physical thermal observations required. The Resource Governor exposes FULL, GUARDED, REDUCED and SURVIVAL budgets and temporarily sheds optional visual/history work before protected Pwnagotchi/Bettercap/GPS paths are considered. Current Raspberry Pi throttle bits are distinguished from historical bits so a past event cannot permanently pin Beast in SURVIVAL.

The first persistent Expedition engine now records a recoverable session in SQLite: GPS route/distance, unique APs, capture/XP deltas and selected system extrema. The touchscreen receives an Expedition main page and Map integration. This is deliberately a foundation; manual named start/end, notes, attached hardware/incidents, recap, records and replay remain on the canonical plan.

Synthwave, Amber Tactical and Ghost Minimal broaden structural theme identity. They participate in the same transient governor load-shedding rules without destroying saved Theme Studio preferences.

A full continuity audit of the original pinned conversation and retained source/spec files produced `Beastagotchi_Project_Continuity_Audit_v1.0.md` and `Beastagotchi_Master_Completion_Matrix_v4.0.md`. The latter is now the anti-forgetting source of truth and explicitly preserves previously chat-only concepts such as RF Universe, operating modes, Beast Bus, incident forensics, powered USB recovery, RTC/fan/physical feedback, management AP/file portal, distributed sensors, AI/voice options, additional structural themes and home-base/peer features.


## v0.16 Operations / Knowledge platform additions

The application universe is no longer constrained by the main swipe-page count. The high-frequency deck remains curated while Apps/Context Decks expose deeper tools. v0.16 adds implemented destinations for Overview, Operations, Service Topology, Task Center, Field Library, Black Box incidents and Backup Center. Container Center, Beast Operator and Command Center are capability-driven and only appear when their required runtime/hardware is actually present.

The `/health` result now includes critical protected dependencies after startup grace. A failed Pwnagotchi/Bettercap service or read-only root filesystem cannot remain hidden behind otherwise healthy collectors.

Field Library roots begin with `/var/lib/beastagotchi/library` and `/home/pi/beast-library`. Plain text, Markdown and common config/reference formats are indexed locally. PDF/EPUB/ZIM files are catalogued without pretending their content was extracted when an extractor is not installed.

Recovery backups are created through the Action Broker and stored under `/var/lib/beastagotchi/backups/` with mode 0600, bounded retention, an online SQLite backup and SHA-256 result. Restore remains a separate future staged workflow; v0.16 does not provide a casual one-tap restore.

Display ownership now checks known legacy display-rendering plugin conflicts before Beast claims the framebuffer. A disabled Theme Manager/Fancygotchi-style plugin may remain installed; an enabled conflicting renderer blocks handoff until resolved.

480×320 remains the reference/minimum target. Beast now also inventories framebuffer geometry and DRM/HDMI outputs. Optional desktop/browser runtimes are discovered read-only and are never launched merely because they exist. This is groundwork for future responsive displays, HDMI Command Center and multi-display roles.

The future Beast Operator privilege model is Observer → Operator → Maintainer → time-limited Administrator Session. The architectural rule is powerful but recoverable automation: typed Action Broker operations, plans, audit history and rollback where appropriate rather than an always-on arbitrary root-shell API.


## v0.17 Platform / Compatibility additions

Beast now distinguishes Core STARTING from real DEGRADED/CRITICAL health and target validation waits for semantic readiness rather than an open port. Plugin inventory is reconciled immediately after the Pwnagotchi collector publishes it.

The UI now has an explicit logical/physical display boundary. 480×320 remains the validated reference canvas; 640×480 and 800×480 are compatibility-scaled output proofs with reverse touch mapping. They are not yet native responsive layouts. Beast Studio labels this distinction and keeps spatial editing on the reference canvas.

Field Library supports safe authenticated Studio imports, dependency-free EPUB extraction, optional PDF extraction when PyMuPDF/pypdf is already available, local document opening, and ranked FTS5 search when the system SQLite build provides FTS5. It falls back cleanly when FTS5 is unavailable. ZIM remains catalogued pending deliberate Kiwix integration.

Beast Operator now has a privilege-tiered structured tool registry. Read tools are separated from Operator mutations, which continue through the audited Action Broker. There is intentionally no implicit generic shell primitive in this foundation.

Container Center may observe any detected Docker/Podman runtime, but only explicitly Beast-managed labeled containers are mutable. Bluetooth adapter state is read-only and does not auto-scan. Cached Pi ARM/core clock and GPU-memory values extend whole-Pi telemetry without high-frequency `vcgencmd` overhead.

Privacy-sanitized Support Bundles can be created through Beast actions/Task Center/Studio. They omit network identities, GPS coordinates, credentials, raw configuration and raw logs by default.

Recovery backups can now be verified before any future restore: Beast checks archive boundaries/links, manifest format and SHA-256 and runs SQLite `quick_check` on the embedded database. v0.17 still does not apply a restore; verified archives only reach the **ready to stage** boundary.
