# Beastagotchi Master Continuity Ledger v1.0

**Status:** Authoritative anti-forgetting index.  
**Rule:** useful ideas are never silently removed. They become **implemented**, **partial**, **planned**, **reserved**, **experimental**, or **retired with an explicit reason**.

This file complements, rather than replaces, the Design & Architecture Bible, Foundation Roadmaps, Master Completion Matrices, physical validation reports, and subsystem specifications already in this repository.

## Product identity that must survive every milestone

Beastagotchi is a modular Raspberry Pi field-computer environment built around a protected Pwnagotchi/Bettercap engine. It should simultaneously feel like a living digital creature, cyberdeck/field terminal, real-time RF/system monitor, modular app platform, configurable instrument panel, persistent exploration/progression system, and self-explaining/self-maintaining device.

The project must remain live-data-first, offline-capable, touch-friendly, extensible, reversible, highly customizable, and usable without SSH for normal operation.

## Main page / tab experience — retained

The **pages/tabs/swipe carousel concept is permanent**. The main carousel is curated for frequent field use; it is not an architectural limit on the number of apps or tools.

The primary landing experience remains a **Beast/Home page** centered on the creature and its live state, including identity, face/animal presentation, level, XP/growth, evolution stage, mood/personality, session aura and meaningful status. Supporting pages expose different live information sets rather than turning the home page into a dense dashboard.

Current/reference page families include Home/Beast, Recon, Networks, Spectrum, Captures, Map, System and related high-frequency pages. Detailed tools may open as apps/studios/decks rather than consuming permanent carousel slots. Stored files, Field Library content, Capture Vault, Memory/Expedition records, logs, backups and support artifacts must remain reachable from the Beast experience even when deep editing is better suited to the WebUI.

## Progression, secrets, specials and delight — retained

The following are explicit product commitments, not disposable extras:

- finite level progression (1–100) and meaningful evolution stages;
- persistent XP/progression tied to real activity rather than fake/demo counters;
- Beast personality driven by real operational context;
- session aura and context-reactive presentation;
- achievements/awards with rarity, progress and discovery presentation;
- rare, epic/legendary-style moments and scarce witnessed events;
- secrets, hidden interactions, codes, ciphers and future Cipher Console/puzzle systems;
- seasonal, calendar, day-phase, weather/celestial/moon context where real data is available;
- Rare Moments with omens, witnessing rules and dedicated cinematic presentation;
- 5–60 second rare cinematics and multiple presentation families;
- trophy cabinet / collections / BeastDex-style records;
- long-tail achievement families and hidden awards;
- Expedition/session records, visual replay and scrapbook/Memory Vault concepts;
- peer-Beast encounters, special discoveries and future distributed-world events;
- theme-reactive sound, optional haptics/LED reactions and other sensory rewards;
- Easter eggs that can be discovered without compromising reliability or truthful telemetry.

Canonical detailed references include `Beastagotchi_Secrets_Achievements_Seasonal_Spec_v0.9.md`, `SPOILERS_SECRETS_AND_ACHIEVEMENTS.md`, `Beastagotchi_Rare_Cinematic_Pipeline_v0.9.1.md`, `Beastagotchi_Adaptive_Behavior_Progression_Spec_v0.1.md`, and `Beastagotchi_Expeditions_Spec_v0.11.md`.

## Structural customization — retained

Data, widgets, renderers, layouts, themes, face packs and Beast personality remain separate layers. Themes are structural identities, not simple recolors. Layouts remain independently selectable/editable. Visualizer Studio, Theme Studio, Spatial Studio/custom Boards, Context Decks and user-authored combinations remain part of the planned platform.

Reserved visual/theme identities include Classic, Matrix, Starcore, Black Ice, Hunter, Minimal, Synthwave, Amber Tactical, Ghost Minimal, Cyberpunk, Stealth/Red Alert, Forest, Vaporwave, Space, Holographic, Golden, Samurai, WOPR/NORAD, Steampunk, Blueprint, Terminal+, Biohazard, Glitch, Comic, seasonal/user packs, sonar/submarine, Mission Control, Oscilloscope Lab and other retained identities documented elsewhere.

## Beast Packs / downloadable ecosystem — new explicit direction

The base installation should stay comparatively small and stable while optional content and capabilities can be installed as versioned **Beast Packs**. Candidate pack types include themes, face/animation/audio packs, dashboards/layouts, apps, hardware adapters, Mission Packs, offline map/data bundles, optional renderers and experimental capabilities.

A future Beast Depot/Library should support install, update, disable, remove, compatibility checks, dependencies, resource/thermal metadata, signatures/checksums where practical, and rollback. Downloaded-but-inactive content should consume storage, not continuous CPU/GPU/thermal budget.

## Presentation ownership — retained and expanded

Stock/native Pwnagotchi, Korrie71 Theme Manager and Beast UI must be able to coexist without racing for the framebuffer/touch device. A Presentation Broker should provide an exclusive persistent owner lease and transactional handoff. Initial presentation owners:

- `native` — stock/Jayofelony Pwnagotchi presentation;
- `theme_manager` — Korrie71 Theme Manager presentation + touch;
- `beast` — Beastagotchi presentation + touch.

The selected owner keeps control until another presentation explicitly requests it. Failed acquisition should roll back to the previous healthy owner. Non-owning systems may remain alive for WebUI/API/data functions when compatible.

## WebUI / companion experience — retained and expanded

The physical display is the **cockpit**; the responsive local WebUI is the **workshop**. Deep configuration should favor phone/tablet/desktop WebUI while essential field operation remains available on-device.

Native Pwnagotchi capabilities should not disappear simply because Beastagotchi is installed. Beast should preserve, expose, link to or safely adapt useful native Pwnagotchi settings/interfaces. Phone/tablet connectivity architecture must account for local Wi-Fi, Ethernet/dock, USB/RNDIS where supported, and Bluetooth/BLE capabilities where technically appropriate. A local-first PWA-style Beast companion is approved direction; no cloud account is required for normal use.

## Multi-display / screen strategy — retained

480×320 ILI9486 is the physically validated reference/minimum target, not the only final target. The platform should prudently support other common screens when doing so can be accomplished cleanly through responsive layout/display transforms rather than per-screen forks. Targets include 640×480/800×480 compatibility, common 5-inch HDMI/DSI-class displays, larger HDMI/DRM displays/Command Center, and responsive browser surfaces on phones/tablets/desktops.

No resolution is declared production-supported until it has appropriate automated and, where practical, physical validation.

## Reliability records must exist independently of WebUI

The WebUI is a view/controller, never the sole storage location for critical records. Important state must remain on persistent storage so it survives browser loss, UI crashes and reboots.

Existing durable paths include:

- `/var/lib/beastagotchi/beast.db` — canonical Beast database/state history;
- `/var/lib/beastagotchi/backups/` — verified recovery backups;
- `/var/lib/beastagotchi/config-snapshots/` — configuration snapshots;
- `/var/lib/beastagotchi/restore-staging/` — staged restore inspection/apply preparation;
- `/var/lib/beastagotchi/support/` — privacy-sanitized support bundles;
- `/var/lib/beastagotchi/library/` — offline Field Library;
- `/var/lib/beastagotchi/missions/` — Mission Pack state;
- `/var/lib/beastagotchi/ui/` — persistent UI preferences/runtime records;
- durable Black Box incidents/jobs/actions in the Beast database.

Service logs should remain accessible through the underlying system journal and Beast UI/WebUI. A bounded persistent log/export policy should ensure troubleshooting evidence can be recovered locally without creating uncontrolled SD-card write amplification.

## Thermal/resource efficiency — retained and elevated

Heat is a first-class engineering constraint. Optimization order is: eliminate duplicate work, share telemetry, suspend non-owning render engines, make collectors event-driven/adaptive, cache static layers, reduce framebuffer writes, stop unused optional services, profile expensive modules, and only then use graceful degradation during genuine pressure.

Resource Governor is protection, not an excuse for an inefficient normal state. Future module/package metadata should expose expected background/resource/thermal class where useful.

## Plug-and-play / documentation — retained and elevated

The final public experience should approach plug-and-play within the limits of Raspberry Pi/Pwnagotchi hardware variation: clear supported-hardware matrix, installer/upgrader/uninstaller, preflight checks, automatic capability discovery, safe defaults, rollback, diagnostics, screenshots, concise quick-start, detailed manuals, troubleshooting/runbooks, contributor docs and explicit validation status.

## Expansion universe — retained

Still approved/reserved: BEAST/SCOUT/SPECTRUM/SKY/MESH/FIELD/SYSTEM/LAB modes; RF Universe; Kismet/passive survey; Bluetooth encounter persistence; RTL-SDR spectrum/waterfall and lawful decoders; ADS-B aircraft radar; rtl_433-compatible unencrypted sensor views; Meshtastic/LoRa; offline maps; Home Base/dock mode; peer Beast networking; distributed Pi/ESP32 sensors; Beast Bus; hardware enrollment; RGB/haptics/speaker/fan/RTC/physical controls/NFC; camera/environment/IMU/proximity; MQTT/Home Assistant/NAS integration; optional local AI/voice; Container Center; external-display Command Center; Desktop Mode; Monster View; dynamic world animation; theme scheduling/randomization; local file portal; QR workflows; Boot POST; explain-error UX; built-in offline manual; disaster recovery/self-healing; update regression/rollback; and other items retained in the Master Completion Matrices and Roadmaps.

## Change-control rule

Every substantial milestone must update this ledger or the current Master Completion Matrix when it:

1. implements a retained idea;
2. changes an architectural commitment;
3. defers an item;
4. retires an item (with explicit reason); or
5. adds a new approved idea.

No item is considered gone simply because it is not mentioned in a milestone summary.
