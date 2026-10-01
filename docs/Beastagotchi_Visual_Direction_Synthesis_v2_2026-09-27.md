# Beastagotchi Visual Direction Synthesis v2

Date: 2026-09-27
Status: Canonical visual-direction synthesis for Gate 1 refinement. No render in this document is owner-approved unless explicitly recorded elsewhere.

## Why this pass exists

Recent visual work revealed a repeated failure mode: we were too often designing five attractive themed dashboards instead of five genuinely different Beast experiences built on one truthful system. The next iteration must stop chasing generic dashboard polish and instead design the screen as a real field instrument, companion object, lab instrument, machine bay, or austere artifact depending on the active Experience.

## Core visual law

**One Beast truth model; five distinct experiential grammars.**

The five Experiences may share data contracts, interaction semantics, accessibility, touch target rules, navigation logic, status meaning, and rendering substrate. They should not share the same page composition with different colors.

## Research conclusion

The best references are not ordinary SaaS dashboards. The strongest applicable patterns come from:
- diegetic game interfaces where maps, instruments, notebooks, radios, and gauges feel like things that belong to the world/device;
- rugged cyberdeck and field-computer interfaces;
- real scientific instruments and spectrum/measurement software;
- industrial HMIs and machine-control panels;
- restrained companion/pet interfaces that privilege presence over ornament;
- brutalist/minimal interfaces where negative space and typography are structural rather than decorative.

Useful public references from this research pass:
- https://indexstyle.org/styles/diegetic-ui
- https://gamemechanics.org/patterns/diegetic-interface
- https://www3.cs.stonybrook.edu/~tony/ui/lectures/game_design/gameUI.pdf
- https://www.reddit.com/r/cyberDeck/comments/1t6xefe/ui_design_for_cyberdeck/
- https://www.behance.net/gallery/236308597/TheTrail-App-Travel-Dashboard-UX-UI-Design
- https://www.behance.net/gallery/122700065/Deadly-Virus-and-Scientific-Dashboard-Dark-UI
- https://www.behance.net/gallery/58896639/Orion-Network-Dashboard-IOT-UIUX-Design

## Shared Beast visual rules

1. **480×320 first.** Design for the actual TFT. Marketing-board renderings are references only.
2. **Truth first.** Never draw fake history, fake maps, fake GPS, fake battery, invented trends, or decorative telemetry presented as real.
3. **Readable at arm's length.** Tiny type is metadata, not the primary carrier of meaning.
4. **Touchable.** Main actions and navigation must survive real fingers, not just mouse clicks.
5. **No generic card soup.** Containers exist only when the visual grammar calls for them.
6. **No arbitrary sameness.** Pages inside an Experience should feel related, while different Experiences should feel meaningfully different.
7. **Creature is a real system participant, not clip art.** Its presence can be subtle or central depending on Experience, but its state must derive from the same semantic creature layer.
8. **Color means something.** Accents indicate state, hierarchy, focus, or Experience identity; they are not decoration alone.
9. **Reduced motion must still look intentional.** No experience may rely on animation to make a weak static composition feel complete.
10. **WebUI may be richer, but TFT must remain complete.** The 3.5-inch interface is not a crippled remote control.

## Experience DNA

### ATLAS — Field notebook / expedition instrument

Purpose: exploration, movement, location/context, RF discovery, route/session history, field observations.

Visual grammar:
- map/notebook/compass/topographic language;
- annotation rails, stamps, marginalia, field marks;
- route and observation graphics only when backed by real data;
- warm restrained field palette rather than fantasy parchment overload;
- creature as expedition companion, not the entire screen;
- screen should feel like a useful object somebody would actually carry outdoors.

Avoid:
- fantasy-RPG quest map styling;
- huge scenic illustrations that consume data space;
- decorative fake geography;
- generic four-card dashboards.

### FORGE — Machine bay / workshop control surface

Purpose: hardware, system health, power, thermals, modules, devices, jobs, bench workflows, repair/maintenance context.

Visual grammar:
- installed subsystems, rails, buses, ports, gauges, service labels;
- industrial amber/steel or similarly disciplined palette;
- dense but hierarchical; physical-machine metaphor;
- status should read immediately from structure and light/state indicators;
- creature may appear as the Beast-in-the-machine, technician companion, or core identity rather than a pet-game panel.

Avoid:
- fake sci-fi spaceship UI;
- ornamental machinery with no informational role;
- excessive microtext;
- turning every subsystem into a rounded card.

### OBSERVATORY — Scientific measurement station

Purpose: RF, spectrum, signal observation, network/radio context, scientific views, provenance and measurement.

Visual grammar:
- real axes, traces, histograms, polar/radar views, scientific annotations;
- dark quiet lab palette with disciplined signal colors;
- provenance/freshness/truth labels are first-class;
- clear separation between measured, captured, derived, estimated, and unknown;
- creature as observer/research companion, secondary to the phenomenon being measured.

Avoid:
- decorative graphs;
- faux starfield unless contextually justified;
- meaningless radar circles;
- hiding measurement truth behind visual spectacle.

### HABITAT — Living companion space

Purpose: creature relationship, state, growth, memory, perception, expressions, homecoming, contextual life layer.

Visual grammar:
- creature-first but still grounded in real Beast data;
- warm, calm, tactile, expressive;
- living-space feeling without becoming a mobile pet game;
- memories and reactions should reference real sessions/events/places/data;
- progression is meaningful and structured, not a streak/reward treadmill.

Avoid:
- fake hunger/food mechanics unless they map to an approved creature-state system;
- generic mobile game currency/progression language;
- over-cute mascot treatment that trivializes Beast's instrument side;
- making the creature cover technical truth.

### MONOLITH — Austere artifact / intentional minimalism

Purpose: calm high-signal operation, essential status, deliberate commands, ritual/identity, low-distraction use.

Visual grammar:
- black/near-black, high contrast, spare typography, one restrained accent if needed;
- large negative space used intentionally;
- very few elements per screen;
- actions feel deliberate and consequential;
- creature presence can be silhouette, eyes, posture, or minimal semantic expression.

Avoid:
- empty-for-empty's-sake screens;
- unreadably tiny labels used to simulate sophistication;
- decorative brutalism;
- hiding important status in pursuit of minimalism.

## The new implementation discipline

Before coding any page, define:
1. job of the page;
2. required real signals/actions;
3. dominant visual object/metaphor;
4. primary glanceable answer;
5. secondary interaction path;
6. what should not be shown;
7. how the page behaves with unknown/missing data;
8. what the creature does, if anything;
9. what the page becomes under reduced motion;
10. what must remain consistent across all five Experiences.

## Gate 1 implication

Do not ask the owner to approve five isolated home-screen images. Gate 1 visual acceptance should be based on coherent Experience families showing at least:
- Home;
- one operational/data page;
- one system/utility page;
- one creature/history/context page where applicable;
- the same truth/state represented consistently across pages.

This document supersedes the assumption that the previously generated concept boards are candidate finals. They are exploratory references only.
