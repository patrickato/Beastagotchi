# Beastagotchi Roadmap

This is the public orientation layer. The current detailed checklist is
`docs/Beastagotchi_Master_Completion_Matrix_v5.0.md`. The continuity ledger
remains the anti-forgetting authority.

## Release state

### Stable baseline — v0.18.1 on `main`
v0.18.1 is the current stable baseline. Its source gate passed 194/194 tests,
Python compile, shell syntax and the 32-frame validation gallery. It includes
owner-authorized Operator sessions, verified recovery staging + dry-run restore
planning, Mission Packs, canonical Beast personality state and the first
native-responsive Dashboard/Board renderer.

480×320 remains the physically validated reference display. Larger legacy pages
are not yet claimed as native-responsive.

### Active development — v0.19 Unified Experience
Development lives on `v0.19-unified-experience` in Draft PR #9. The current
source gate is 253 passing tests plus compile/shell validation.

v0.19 is deliberately doing two jobs at once:

1. make Beastagotchi feel polished, coherent and pleasant rather than merely
   feature-rich; and
2. convert optional features/content into safe modular packages so growth does
   not make every installation permanently larger/hotter/more complex.

## v0.19 execution order

### Gate 1 — Unified UX / visual acceptance
- finish hierarchy/interaction cleanup across the high-frequency page carousel;
- preserve Home/Beast + page/tab/swipe identity;
- reduce box-grid/clutter patterns and improve type/touch hierarchy;
- finish shared dialogs/lists/toasts/loading/error/empty states;
- deepen structural theme differences rather than palette-only variation;
- create real-state comparison galleries;
- perform another physical Pi/TFT visual + touch + heat review;
- use that review before declaring the v0.19 visual language accepted.

### Gate 2 — Beast Packs / Depot
Already implemented:
- manifest registry, intake, SHA-256 verified staging and transactional registry install;
- safe content-only enable/disable;
- Theme Pack runtime discovery;
- Board Pack read-only launcher destinations;
- Layout Pack templates importable as editable personal Boards;
- Beast Pack SDK examples;
- bounded Depot Catalog v1 parser with trust kept separate from discoverability.

Next:
- Face Pack consumer — implemented;
- Animation Pack consumer — implemented;
- local Depot browser/import/search/filter — implemented;
- Experience draft/preview composition — implemented;
- audio/data/map asset consumers;
- downloadable metadata/cache UX;
- compatibility/version presentation;
- remove/update flows and clearer rollback history;
- dedicated adapters for code-bearing app/renderer/integration/hardware Packs.

### Gate 3 — Presentation ownership / Theme Manager coexistence
- validate stock/Jayofelony release/acquire semantics;
- validate Korrie71 Theme Manager release/acquire semantics;
- implement real Presentation Broker adapters;
- persistent owner selection: Native / Theme Manager / Beast;
- transactional handoff with health observation and rollback;
- keep non-owning WebUI/API/data functions alive where compatible;
- physically validate repeated switching without framebuffer/touch races.

### Gate 4 — Update Center
Already implemented:
- trusted-source metadata checks;
- SHA-256 verified download staging;
- Pack transaction history;
- policy intent: manual / notify / auto-stage / auto-install;
- safe Pack auto-install boundary for verified eligible Packs.

Next:
- full compatibility fingerprinting;
- user-facing update history/status;
- maintenance-window/docked/Internet-online policy;
- component-specific adapters for Beastagotchi, Pwnagotchi and Theme Manager;
- backup/health probation/rollback before any broader unattended component update;
- never turn a Depot listing into automatic trust.

### Gate 5 — Performance / thermal / hardware
- continue per-process and per-render cost attribution;
- remove duplicate polling/render loops before degrading the experience;
- suspend inactive optional services/content;
- validate sustained Pi 4 heat/load on the target enclosure;
- Hardware Studio / accessory role enrollment;
- second Wi-Fi role UX;
- cooling/fan, battery/power and dock telemetry/control where hardware exists;
- Bluetooth/SDR/Meshtastic/etc remain capability-driven optional modules.

### Gate 6 — Responsive displays / companion surfaces
- migrate legacy pages to native responsive composition;
- common 5-inch HDMI/DSI-class target;
- external Command Center;
- responsive Beast Studio / local companion PWA;
- phone/tablet settings, logs, files, backups and control;
- local Wi-Fi/Ethernet/USB and appropriate Bluetooth/BLE connectivity paths.

### Gate 7 — Beast Roster / Lineages / Monstergotchi

Implemented foundation:
- persistent multi-Beast SQLite roster;
- Founder migration path for the existing single progression profile;
- independent XP/levels and active/resting state;
- ancestry and Monster synthesis records;
- Alpha/level-70 v1 synthesis gate for both parents;
- parents preserved after synthesis;
- first Monster unlocks the future `monstergotchi.core` layer.

Next:
- cut live progression over to the active Beast without losing legacy data;
- Roster/switcher UI;
- global versus per-Beast achievement/collection split;
- Beast-first versus device-first encounter rewards;
- per-Beast preferred Experiences;
- deterministic inheritance + curated mutation traits;
- Monster reveal/evolution presentation;
- Hall of Legends + ancestry tree;
- later evaluate additional generations and privacy-safe cross-device Lineage Capsules.

### Gate 8 — Experience depth
- richer progression/evolution/personality presentation;
- achievements/awards/rarity/trophy cabinet;
- secrets/codes/ciphers/Cipher Console;
- Rare Moments and 5–60 second Rare Cinematics;
- seasonal/day-phase/weather/celestial presentation from real context;
- Expedition archive/replay and Memory Vault/scrapbook;
- peer-Beast encounters and other retained delight systems.

### Gate 9 — Recovery / self-maintenance
- live restore transaction with rescue backup;
- service quiesce/apply/verify/rollback;
- self-healing actions with explicit limits;
- Kiwix/ZIM reader;
- offline runbook UX;
- bounded persistent log/export policy validated for SD-card wear.

### Gate 10 — Public beta / v1.0
- supported-hardware matrix;
- installer/upgrader/uninstaller + migration framework;
- clean-machine preflight;
- screenshots/video/quick-start/manual/troubleshooting;
- Pack author/contributor documentation;
- stable release packaging and checksums;
- physical regression matrix;
- tagged public beta followed by v1.0.

## Permanent protected scope

The following are not removed just because they are not in the current sprint:
pages/tabs/swipes; Beast/Home creature identity; levels/growth/evolution;
achievements/awards/secrets/rares/legendaries/ciphers; Expeditions/replay/Memory
Vault; Theme/Visualizer/Spatial Studios; files/logs/backups/incidents; phone and
tablet surfaces; multi-display support; second Wi-Fi/Bluetooth/GPS/SDR/ADS-B/
Meshtastic/sensors; offline maps/RF Universe; dock/Home Base; peer Beasts/Beast
Bus; optional local AI/voice; containers; WOPR/NORAD, sonar, Mission Control,
Oscilloscope and other retained visual/app concepts.

## GitHub development cadence

Normal development:
`main` (stable) → milestone branch → bounded development commits + CI → physical
gate where required → merge/tag/release.

Development commits are allowed on the active branch because they provide
rollback points and CI. They are **not** treated as releases. `main`, tags and
GitHub Releases are updated only for meaningful validated milestones.

## Sources of truth

- Detailed status: `docs/Beastagotchi_Master_Completion_Matrix_v5.0.md`
- Anti-forgetting scope: `docs/Beastagotchi_Master_Continuity_Ledger_v1.0.md`
- Architecture: `docs/Beastagotchi_Design_Architecture_Bible_v1.0.md`
- Active checkpoint: `docs/Beastagotchi_v019_Active_Checkpoint_Delta.md`
- UX gate: `docs/UX_POLISH_MILESTONE_v0.19.md`
- Development/release workflow: `docs/Beastagotchi_Development_Release_Workflow.md`
