# Beastagotchi Changelog

## Repository bootstrap — 2026-09-22

- Published the validated v0.18.1 runtime baseline as a structured public repository.
- Added GPLv3 licensing, contributor/security/support guidance, CI and issue/PR templates.
- Added the v0.19 continuity/navigation/connectivity/recovery/Beast Packs planning layer and ADRs.
- Runtime version remains 0.18.1; these repository/documentation changes do not claim a new runtime release.

## v0.18.1

- Packaging hotfix: restored the v0.18 Platform Compatibility specification required by install.sh.
- Added release reference-audit coverage so installer source dependencies must exist in the packaged tree.
- No runtime feature behavior changed from v0.18.0.

# Changelog

## 0.18.1 — Recovery / Personality / Responsive Boards milestone

- Added expiring owner-authorized Beast Operator privilege sessions with automatic Observer fallback.
- Added verified backup staging and dry-run restore diff/preflight; live restore remains deliberately gated.
- Added declarative Mission Packs with capability-aware readiness.
- Added canonical living-Beast personality state derived from real health/RF/GPS/Expedition/time/progression conditions.
- Face packs now consume canonical Beast expression state with Pwnagotchi mood fallback.
- Added first native-responsive Board renderer for 640x480/800x480 Studio output while legacy pages retain compatibility scaling.

## 0.17.0 — Platform / Compatibility milestone

- Make Core startup health semantically truthful: STARTING during normal collector warm-up, DEGRADED after missed readiness, CRITICAL for protected-engine/root failures.
- Reconcile Plugin Manager immediately when Pwnagotchi publishes plugin inventory, removing the post-restart empty-catalog race.
- Add logical-to-physical DisplayTransform with aspect-preserving scaling, centered compatibility viewport and reverse touch mapping.
- Add 640×480 and 800×480 compatibility-output proofs while retaining 480×320 as the validated reference layout.
- Add Beast Studio output-proof selection with explicit compatibility/non-responsive labeling and reference-only spatial editing.
- Expand Field Library with dependency-free EPUB extraction, optional PDF extractors, authenticated safe imports and local document opening.
- Add privilege-tiered Beast Operator structured tool registry without a generic shell primitive.
- Limit container mutation to explicitly Beast-managed/enrolled Docker/Podman workloads.
- Add read-only Bluetooth capability state plus cached ARM/core clock and GPU-memory telemetry.
- Add privacy-sanitized Support Bundles with SHA-256, bounded retention, Action Broker/Task Center integration and Beast Studio control.
- Add read-only recovery-backup verification for restore staging: archive boundary/link checks, manifest validation, SHA-256 and SQLite quick_check; no live restore is performed.
- Add FTS5-ranked Field Library search when available, with graceful SQL LIKE fallback on SQLite builds without FTS5.
- Harden in-place upgrades by stopping Beast Core/UI/Studio before replacing their runtime Python trees.
- Advance Completion Matrix to v4.6 and Roadmap to v2.9 without dropping prior approved scope.


## 0.16.0 — Operations / Knowledge milestone

- Add truthful whole-device Overview and attention model.
- Add Operations Center, live dependency topology and Task Center.
- Add Universal Search and offline Field Library foundation.
- Add Black Box incident persistence, snapshots and offline runbook links.
- Critical Pwnagotchi/Bettercap/root-filesystem failures now affect overall Beast health.
- Add audited allow-listed service restart actions.
- Add bounded recovery Backup Center with online SQLite snapshot, SHA-256 and private archive permissions.
- Add display-owner conflict checks before physical framebuffer handoff.
- Add capability-driven Container Center and local AI/voice/model discovery.
- Add display/DRM and optional desktop/browser capability discovery plus external-display Command Center groundwork.
- Add Connectivity Center with explicit route-vs-Internet semantics.
- Expand Context Deck defaults for the larger application universe.
- Reconfirm original reserved visual/experience ideas in Completion Matrix v4.5.

# Beastagotchi Changelog

## 0.15.1 — validation/rebind hotfix

- Correct v0.15 validator version assertions to 0.15.1.
- Run action-channel validation with the dedicated `beastagotchi` group.
- Wait for the Beast Studio API itself, not only systemd state.
- Emit a diagnostic failure bundle if Studio cannot become ready.
- Allow immediate Studio HTTP port reuse after stop/start validation cycles.
- Correct stale UI schema version metadata.
- Reconfirm original project/visual roadmap continuity in Completion Matrix v4.4.

# Changelog

## 0.15.0

- Replaced the fixed six-slot Dashboard editor with a spatial live-instrument composition model.
- Added direct drag/move/resize selection over Beast Studio's exact live 480x320 compositor preview.
- Added instrument add/remove, visibility, z-order/front, geometry and source/renderer editing.
- Added user-created named live Boards using the same canonical telemetry and compositor pipeline as the built-in Dashboard.
- Registered custom Boards dynamically as real Apps so they can appear in the launcher and Context Decks without adding hard-coded main pages.
- Preserved honest unavailable states and live telemetry provenance throughout custom compositions.
- Expanded automated coverage for variable instrument counts, custom Boards, board navigation, persistence and the spatial Studio surface.

## 0.13.0

- Added a tenth main page: six-slot user-bound Live Dashboard.
- Added canonical Dashboard data binding and Metric/Bar/Radial/Microtrend renderers in Beast Studio.
- Expanded Beast Studio with exact live compositor preview, Visual/Dashboard/Plugins surfaces, draft/undo/redo/reset/apply and transactional Plugin controls.
- Added root-owned local Unix action channel while keeping public Beast Core HTTP read-only.
- Added transactional plugin snapshot/apply/verify/restart/rollback and action auditing.
- Added category-filtered expandable App Launcher.
- Added Timeline, Notifications, Diagnostics, Services, Hardware and Storage app foundations.
- Added persistent BeastDex and real Capture Vault application surfaces from the v0.12/v0.13 development branch.
- Added Telemetry Inspector and process/render/framebuffer performance attribution.
- Corrected production visualizations to real route/per-channel/unit semantics.
- Added dirty-row framebuffer writes, batched local API reads, cached slow facts and static-page render suppression to reduce heat without sacrificing live data or touch response.
- Added Master Completion Matrix v4.2, Roadmap v2.7, Live Telemetry Integrity, Thermal Efficiency and Beast Studio specifications.

## 0.11.0

- Added Resource Governor modes FULL / GUARDED / REDUCED / SURVIVAL with immediate escalation and recovery hysteresis.
- Added thermal/CPU/RAM/current-throttle/battery pressure policies and fixed live-vs-historical Raspberry Pi throttle-bit semantics.
- Wired governor budgets into UI FPS/effects, high-cost Rare Moment fallback and time-series sampling intervals without rewriting saved theme preferences.
- Added persistent Expedition SQLite tables/engine with restart recovery, GPS route/distance, unique AP membership, capture/XP deltas and thermal/CPU/battery extrema.
- Added read-only `/expeditions` and `/expedition` API endpoints.
- Added an Expedition main page plus Map and System integration.
- Added Synthwave, Amber Tactical and Ghost Minimal structural themes with Theme Studio controls.
- Performed a pinned-conversation continuity audit and promoted recovered chat-only commitments into Master Completion Matrix v4.0.
- Added v0.11 Resource Governor, Expeditions, Experience Gate and Checkpoint documentation plus Roadmap v2.6.
- Expanded release tests to include current-vs-historical throttle behavior, governor thermal bands, Rare Moment load shedding and all structural themes across every main page.

## 0.10.0

- Deliberately pivoted development from Matrix-specific corrective work back to full-product visual breadth after the v0.9.5 physical pass.
- Added Visualizer Studio as a first-class Control Center surface for selecting page renderers.
- Generalized renderer switching across Recon, Spectrum, Captures and System instead of treating Spectrum as the only graph playground.
- Expanded the visualization primitive library with multi-line, stacked bars, histogram, waveform, waterfall/history strip, donut, polar, signal meter, event timeline and numeric+microtrend renderers in addition to existing line/area/bars/radial/radar/heatmap modes.
- Expanded DataFeed history caching for CPU, temperature, memory, AP/client/handshake counts, channel, GPS satellites, motion speed and power metrics so future renderers have real histories to consume.
- Added direct graph-tap renderer cycling to Recon, Spectrum, Captures and System while explicitly preserving footer hit-zone priority.
- Added live Theme Studio controls for Classic Beast (grid/scanline/pulse), Starcore (stars/twinkle/orbit), Black Ice (frost/drift/crystals), Hunter (grid/reticle/embers) and Minimal Field (ambient/panel emphasis).
- Added corresponding background/foreground effect implementations so non-Matrix themes now have meaningful runtime variation.
- Preserved Native Pwnagotchi, production/restored touch calibration, Achievement Explorer, Rare Event Director and the v0.9.5 Matrix fixes.
- Added `Beastagotchi_Master_Completion_Matrix_v3.0.md`, a comprehensive anti-forgetting ledger covering all previously committed architecture, themes, visualizers, progression, secrets, apps, plugins, hardware, RF, power, sessions, maps and GitHub/public-release work.
- Added Roadmap v2.5 and Visualization Studio v1.0 documentation.

## 0.9.5

- Identified the temporary pink/magenta diagonal Matrix artifact from the physical v0.9.4 validation as the Matrix event-reaction animation, not the rain renderer. The old reaction advanced X and Y together and was especially visible during severe thermal events.
- Reworked Matrix reactions so bars remain on fixed X coordinates and animate only in height/intensity. Severe events use stationary danger corner brackets instead of a diagonal sweep.
- Added a Matrix `REACTIONS` On/Off Theme Studio option to isolate/customize event visuals without changing rain.
- Reworked Achievement Explorer touch regions into non-overlapping full-width physical partitions so enlarged hitboxes no longer compete at row boundaries.
- Enlarged Achievement tabs/filter/sort/cards/navigation artwork to better match the physical hit geometry.
- Preserved the v0.9.4 rain renderer, Native Pwnagotchi bridge, restored touch calibration, achievement catalog and Rare Moment presentation system.

## 0.9.4

- Built from the exact v0.9.3 source checkpoint captured from the Pi after Native RAW physically passed. The checkpoint is a known-good reference, not a declaration that v0.9.2/v0.9.3 are stable releases.
- Locked the restored/original touch calibration as production and moved the rejected Touch-Lab affine candidate behind an explicit `--experimental` diagnostic gate.
- Added reusable hitbox geometry that separates visual bounds from touch bounds and preserves minimum target size at screen edges.
- Applied enlarged measured hitboxes across Theme Library/Studio, drawer, footer, help, Spectrum and the new Achievement Explorer.
- Expanded Matrix Layer/Density/Speed/Trail/Glyph/Palette/Accent/Foreground controls and custom 1–4 color slots.
- Fixed Matrix preset behavior so a single-color selection with accents disabled does not invent unrelated colors.
- Added per-glyph vertical micro-jitter to the Matrix de-Moiré strategy while preserving fixed X positions and vertical-only stream motion.
- Expanded Native Chroma on the actual Jayofelony native frame with fixed/mood ink, palettes, glow and clean/scanlines/vignette/grain/pulse/glitch/halo effects.
- Added detailed achievement progress metadata and award catalogs.
- Replaced the static achievement page with an interactive Achievements/Awards browser, filters, sorting, paging, progress bars and detail views.
- Expanded Rare Moment presentation metadata and renderer support for fade, drift, cross, orbit, ghost, storm, apparition and cinematic variants.
- Added `--presentation` to `beast-rare-preview`.
- Added v0.9.4 combined physical Experience Gate validation and Roadmap v2.3.

## 0.9.3

- Locked the original pre-v0.9.2 touch calibration after the physical A/B test showed it feels better than the Touch-Lab-derived candidate.
- Added the Native Pwnagotchi Frame Bridge, reading Jayofelony's own live `/var/tmp/pwnagotchi/pwnagotchi.png` UI canvas while its physical renderer remains disabled.
- Added Pwnagotchi Native RAW, Native Dark, Native Light and Native Chroma as first-class profiles.
- Native Dark/Light intentionally omit Beast header/footer/reconstructed face so the live Pwnagotchi composition remains the display.
- Added long-press/down-swipe escape into Beast Control Center while native mode is active.
- Added `beast-pwn-native` diagnostics for source availability, dimensions and freshness.
- Relabeled v0.9.2 stock-style themes as Replica Dark/Light/Chroma so they cannot be confused with the true native bridge.
- Added native-frame capture to target and physical validation archives.
- Added Native Pwnagotchi Bridge design documentation and Roadmap v2.2.

## 0.9.2

- Integrated the pooled Touch Lab affine calibration as a reversible candidate profile.
- Added `beast-touchcal` with timed rollback, confirm, restore and status operations.
- Added measured platform touch-size policy and enlarged/re-paged Theme Library / Theme Studio controls.
- Added Pwnagotchi Original Dark and Original Light first-class themes.
- Added Pwnagotchi Chroma, preserving the stock text-face vocabulary with mood-reactive colors.
- Added a stock-inspired original Pwnagotchi Home composition while retaining Beast navigation.
- Documented Beast-native integration principles for Korrie71/pwnagotchi-theme-manager without adding a runtime dependency.
- Kept Touch Lab as a permanent diagnostic/developer utility.

## 0.9.1

- Reworked Theme Library into a two-card pager with large explicit controls for the 3.5-inch resistive touch panel.
- Reworked Matrix Theme Studio rows into visible left/right steppers.
- Expanded Matrix density and speed ranges.
- Broke the regular Matrix glyph lattice to remove physical-TFT diagonal/Moire artifacts without introducing horizontal motion.
- Added rarity-scaled Rare Moment durations.
- Added Rare Cinematic Pipeline documentation.


## 0.9.0
- Added Theme Library and fullscreen Theme Detail workflow.
- Added persisted per-theme option namespaces.
- Added Matrix front/back compositing, runtime density/speed/palette controls and additional palette modes.
- Expanded achievement catalog and rarity metadata.
- Added `/achievements` API and on-device achievement overlay.
- Added deterministic per-device Rare Moment scheduler, missed-window accounting, omen layer and witness acknowledgement.
- Added procedural Rare Moment cinematic placeholder.
- Added ambient season/day-phase/moon-phase state.
- Added public/spoiler documentation structure for eventual GitHub publication.
