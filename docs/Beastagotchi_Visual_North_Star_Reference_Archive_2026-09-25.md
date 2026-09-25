# Beastagotchi Visual North Star / Reference Archive

**Date:** 2026-09-25  
**Status:** design reference, not implementation specification  
**Applies to:** v0.19 Experience DNA work and later UI/Studio/Doctor evolution

## Why this exists

The project accumulated two important visual reference groups:

1. the original concept renders produced near the beginning of Beastagotchi;
2. the current on-device end-vision concepts rendered after the v0.19 Experience/Patient-Chart work.

The source images are preserved in the user's persistent ChatGPT Library:

- `/Beastagotchi/Visual References/Original Concepts/`
- `/Beastagotchi/Visual References/Current End Vision/`
- `/Beastagotchi/Visual References/original-concept-reference-board.jpg`
- `/Beastagotchi/Visual References/current-end-vision-device-board.jpg`

These images are **visual references only**. They are not screenshots, pixel-perfect templates,
or promises that Pillow at 480×320 can reproduce painterly concept art literally.

Their purpose is to preserve the project's visual ambition, composition vocabulary, hierarchy,
density, emotional tone and product identity while allowing the actual renderer to stay truthful,
legible and physically realistic on the 3.5-inch ILI9486 display.

---

## Original concept references

### 1. Amber Tactical Field Ops
Strong ideas:
- strong mode identity;
- map is unmistakably the page's primary task;
- side data supports the task rather than competing with it;
- excellent high-information hierarchy;
- status, navigation and mission context feel like one product.

Do not copy literally:
- too much tiny copy for 480×320;
- too many simultaneous modules;
- assumes much more pixel density than the physical TFT;
- danger of becoming a desktop dashboard if compressed unchanged.

Best source material for:
- Atlas / Expedition / Recon / Map;
- Hunter-state visual intensity;
- contextual side rails;
- route, breadcrumb and target emphasis.

### 2. Theme Studio
Strong ideas:
- visual customization is treated as a first-class product feature;
- live preview makes configuration understandable;
- family/style selection feels visual rather than config-file driven;
- clear separation of theme, graph style, widget pack, icon set and density.

Do not copy literally:
- desktop-scale control density;
- too many controls visible simultaneously for the TFT;
- better suited to Beast Studio/web than the 3.5-inch runtime.

Best source material for:
- Beast Studio;
- Experience DNA editor;
- live preview / TRY ON workflow;
- appearance packs and visual-family editing.

### 3. Hunter Mode
Strong ideas:
- dramatic state change is immediately obvious;
- the Beast's expression becomes part of system state;
- target priority and live pursuit dominate the page;
- color and motion can communicate urgency.

Do not copy literally:
- aggressive red treatment should be rare, event-driven and bounded;
- dense live-target panels cannot become the everyday Home surface;
- avoid implying capabilities/data the platform does not actually possess.

Best source material for:
- Rare Moments;
- hunt/focus state;
- alert cinematics;
- target-acquired transitions;
- event-specific temporary UI transformations.

### 4. Orbital Companion / Aurora Form
Strong ideas:
- strongest example of Beastagotchi as a living companion rather than a dashboard;
- creature is the unmistakable focal point;
- personality, memory, plugins and world all orbit the Beast;
- excellent emotional/product identity.

Do not copy literally:
- visual effects density is beyond current 480×320 raster budget;
- glass/orbit effects can become unreadable noise on the TFT;
- navigation must remain simpler and more tactile.

Best source material for:
- Beast page;
- Habitat;
- Rare Moments;
- progression/evolution;
- memory and relationship visualizations;
- "living system" feeling.

### 5. Frostline Network Inspector
Strong ideas:
- extremely good network-analysis hierarchy;
- selected network has clear context and analytical depth;
- graph + quality + threat + traffic + inspector feel coherent;
- visual skin and analytical semantics reinforce each other.

Do not copy literally:
- desktop inspector density is too high for a 3.5-inch primary page;
- much of this belongs in drill-down pages or Studio;
- a permanent left network list would consume too much TFT space.

Best source material for:
- Network Inspector;
- Observatory;
- capture/network drill-down;
- per-network dossier surfaces.

### 6. Orange Home / Space Companion
Strong ideas:
- strong family identity;
- character, telemetry and tools coexist;
- navigation is highly discoverable;
- strong relationship between creature and environmental/world context.

Do not copy literally:
- too many equally weighted modules;
- thick framing consumes precious 480×320 area;
- risks the exact boxed-dashboard look v0.19 is moving away from.

Best source material for:
- family-specific navigation grammar;
- playful companion mode;
- world/context panels;
- page-to-page visual translation.

### 7. Matrix Rain Recon
Strong ideas:
- unmistakable operational identity;
- excellent radar / target-list / spectrum relationship;
- strong "live system" energy;
- a good example of a specialized Experience having its own grammar.

Do not copy literally:
- green matrix motif should remain a family/style, not a universal skin;
- dense target rows must be bounded;
- avoid decorative live-looking data that is not real.

Best source material for:
- Recon;
- Observatory;
- cyber/terminal Experience families;
- scan/search states.

### 8. Neon Live Home
Strong ideas:
- strongest early example of combining creature, telemetry, evolution, plugins and live charts;
- makes the Beast feel like the center of an operating system;
- excellent "alive" quality;
- clear game/progression influence without becoming a game-only UI.

Do not copy literally:
- still fundamentally a multi-card dashboard;
- too many charts compete with the creature;
- tiny chart labels would not survive the TFT.

Best source material for:
- live Home telemetry;
- progression rail;
- plugin/status indicators;
- subtle animated data;
- creature-led system identity.

### 9. Classic Page Grid
Strong ideas:
- page coverage is broad;
- establishes Beast-native alternatives to stock Pwnagotchi surfaces;
- simple geometry proves that functionality can be mapped clearly;
- useful as a functional inventory / compatibility reference.

Weakness:
- visually the least ambitious reference;
- reads like an application dashboard rather than a living product;
- this is the visual direction v0.19 has intentionally moved beyond.

Best source material for:
- completeness checks;
- information architecture;
- legacy/compatibility surfaces only.

---

## Current end-vision device concepts

### Habitat Home device concept
What it gets right:
- Beast dominates without preventing glanceable telemetry;
- environmental art and telemetry feel integrated;
- Home can feel like a place, not a dashboard;
- bottom navigation remains understandable;
- at real-device scale the hierarchy is immediately obvious.

Use as a north star for:
- creature prominence;
- atmosphere;
- integrated telemetry;
- environmental storytelling;
- premium finished-product feeling.

### Beast page device concept
What it gets right:
- creature-led profile is clearly the page purpose;
- progression lives around the Beast rather than in a giant card;
- a narrow facts/progression rail works better than multiple equal panels;
- progression, mood and identity feel emotionally connected.

This directly supports the current v0.19 Beast-page fidelity work.

### Doctor / Patient Chart device concept
What it gets right:
- Doctor feels like a real subsystem rather than debug text;
- Patient Chart, recurrence, drift and known-good baseline are visible concepts;
- health/action information is understandable at a glance;
- visual seriousness matches the importance of diagnostics.

Caution:
- this concept is intentionally denser than Home;
- runtime Doctor pages should progressively disclose detail;
- the 3.5-inch version must retain larger text/touch targets and may split content across pages.

---

## The useful design language to preserve

The references repeatedly point toward the same end product:

1. **The Beast is a system actor, not a logo.**
   It should react to health, mode, progress, discoveries, incidents and Rare Moments.

2. **Every major Experience should feel like a place/tool, not the same dashboard recolored.**
   Atlas should feel field-built; Forge mechanical; Observatory analytical; Habitat alive;
   Monolith sculptural/premium.

3. **Telemetry should belong to the scene.**
   Progress arcs, gauges, traces, maps, machine indicators and environmental cues should carry
   real values without forcing every value into a card.

4. **Specialized pages may be dense; Home should not be.**
   Inspector/Doctor/System/Recon can support higher information density. Home/Beast should have
   stronger visual focus and faster recognition.

5. **Modes and Rare Moments are allowed to transform the visual language.**
   Hunter/focus/fault/evolution/recovery can temporarily change palette, motion and hierarchy.
   Those changes should be event-bound rather than the everyday baseline.

6. **Customization should be visual and live.**
   Beast Studio should eventually approach the Theme Studio reference in capability, while
   runtime TFT controls remain compact and touch-safe.

7. **Real data only.**
   Charts, target counts, signal, coordinates, progress, health, incidents, plugins and provider
   state must come from canonical runtime data. Decorative motion may be synthetic; factual UI
   must not be.

8. **480×320 is a design constraint, not permission to lower ambition.**
   The renderer should use fewer stronger elements, progressive disclosure, readable type and
   careful animation rather than copying desktop-density layouts.

---

## What the project has moved beyond

Beastagotchi should not return to:
- one generic card grid used by every page;
- stock-Pwnagotchi coordinate thinking;
- tiny desktop-dashboard text everywhere;
- fake/demo telemetry;
- seven-page or fixed-widget assumptions;
- "theme" meaning only palette/font changes;
- a static mascot face disconnected from the live system.

The v0.19 Experience DNA architecture, Scene layers, Patient Chart, provider system, real
telemetry, semantic page groups and Studio model are stronger foundations than the original
concepts had. The old renders now function as **art-direction fuel for that architecture**.

---

## Practical visual target

The desired final product is not one screenshot.

It is a coherent device whose visual behavior ranges from:
- calm immersive Home;
- creature-led Beast/profile;
- dense analytical Observatory/Network/Doctor;
- mechanical Forge/System;
- field-oriented Atlas/Recon/Map;
- organic Habitat/relationship/memory;
- restrained Monolith/status;
- dramatic bounded Rare Moments.

The common identity should come from typography, interaction rules, semantic color, Beast
identity, navigation, motion timing and data truth—not from forcing every page into the same
layout.

---

## Acceptance rule

Concept renders may inspire implementation, but a visual change is accepted only after:
1. it is implemented using real renderer/runtime constraints;
2. the actual 480×320 CI artifact is inspected;
3. text/hierarchy survive small-screen viewing;
4. it preserves canonical data truth;
5. it does not compromise touch targets or performance;
6. owner visual feedback is incorporated;
7. physical TFT validation occurs before presentation ownership changes.

This archive exists specifically so later implementation work can ask:

> Does this still feel like the Beastagotchi we intended to build?

without confusing concept art with executable UI.
