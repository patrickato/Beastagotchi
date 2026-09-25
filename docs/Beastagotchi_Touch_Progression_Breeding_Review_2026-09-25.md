# Beastagotchi Touch, Progression, Maturity & Endgame Review

**Date:** 2026-09-25  
**Status:** design/foundation review; numbers are provisional until physical and field telemetry validate them.

## 1. Touch interaction is a release-critical subsystem

A visually excellent Beastagotchi with unreliable touch/navigation is a failed product.

The reference device is a 480x320 resistive ADS7846/XPT2046-class single-touch panel. The input
architecture must therefore be designed and physically accepted around the real panel rather than a
desktop/mobile multitouch assumption.

### Current strengths
Current `beastui/input.py` already:
- re-discovers the ADS7846 event node after reboot;
- samples complete SYN_REPORT frames;
- avoids stale mixed-axis starts;
- median/trend filters gesture endpoints;
- emits touch_down, drag, tap, long_press, swipe and touch_up;
- keeps bounded volatile gesture traces in `/run`.

### Current gaps
- no ABS_PRESSURE handling;
- no first-class continuous scroll semantic;
- no kinetic/inertial scroll model;
- no centralized gesture-arbitration state machine;
- long-press/swipe thresholds are fixed constants;
- no formal target-size/hit-slop contract;
- no touch capability profile;
- no automated physical gesture acceptance suite;
- no per-Surface gesture contract/gesture conflict diagnostics.

### Pressure
Linux ADS7846 can expose ABS_PRESSURE when supported/configured by the driver.

Pressure must be treated as **optional capability**, not required navigation:
- detect via evdev capability query;
- capture raw pressure;
- calibrate per device/panel;
- normalize only after observed min/max/stability;
- use hysteresis/debounce;
- never infer pen-up from pressure alone;
- provide equivalent non-pressure interaction for every essential action.

Potential uses:
- optional harder-press secondary action;
- drawing/visualizer intensity;
- diagnostic/touch-characterization information;
- playful interactions.

Do not make basic navigation or destructive confirmation pressure-dependent.

### Touch contract
Every interactive Surface should declare the gestures it accepts.

Input pipeline target:

    evdev/raw touch
       -> calibration/transform
       -> TouchSample stream
       -> GestureRecognizer
       -> GestureArbiter
       -> SurfaceStack/InputRouter
       -> Surface action

Gesture recognition must distinguish:
- tap;
- double-tap only if it proves reliable/valuable;
- touch-and-hold/long press;
- drag;
- continuous vertical/horizontal scroll;
- page swipe;
- edge gestures only if physically validated;
- optional pressure gesture.

### Scroll versus page swipe
A central conflict on a 480x320 UI is vertical/horizontal content scrolling versus page navigation.

Rules should be explicit:
- a scrollable control claims the drag once movement exceeds its slop;
- page swipe only occurs when the active Surface has not claimed the gesture;
- horizontal child controls may claim horizontal drags;
- direction lock after initial threshold prevents diagonal oscillation;
- reaching a scroll boundary does not accidentally trigger page change unless an explicit overscroll
  contract allows it.

### Hit targets
Provisional reference target:
- prefer ~48x48 logical pixel hit regions where possible;
- avoid essential targets below ~40x40;
- visual glyph may be smaller than its invisible hit region;
- apply hit slop around small icons;
- keep critical controls away from difficult bezel edges.

Physical validation, not a generic design guideline, decides final thresholds.

### Long press
Long press is useful but must never be the only discoverable path for a critical operation.
Current ~0.70s threshold is a good experimental starting point, not a permanent constant.

### Feedback
Every recognized interaction should provide immediate visible response:
- press/highlight;
- button flash;
- ripple/glow/pulse appropriate to Experience;
- transition start;
- optional sound/haptic only when hardware/content supports it.

The user must never wonder whether the resistive panel registered the press.

### Touch Lab / acceptance gate
Create a first-class Touch Characterization Procedure and physical release gate.

Test:
- all four corners;
- bezel-adjacent targets;
- center;
- repeated tap;
- long press;
- short/long swipe;
- slow drag;
- fast drag;
- vertical scroll;
- horizontal scroll;
- diagonal ambiguity;
- touch lift noise;
- stylus vs finger where relevant;
- pressure distribution if available;
- warm/cold runtime state;
- portrait/rotation transforms;
- remote-input equivalence.

Collect:
- raw coordinates;
- mapped coordinates;
- pressure if available;
- gesture result;
- false-positive/false-negative result;
- latency;
- path;
- target hit/miss.

Generate a heatmap/confusion report from the bounded test session.

Touch/nav acceptance should be an explicit release gate separate from visual acceptance.

---

## 2. Current progression math

Current XP threshold:

    XP(level) = round(45 * (level - 1)^1.60)

Key thresholds:
- L5: 414
- L10: 1,514
- L20: 5,003
- L35: 12,693
- L50: 22,779
- L60: 30,660
- L65: 34,922
- L70: 39,389
- L85: 53,958
- L100: 70,182

Current normal XP sources include:
- runtime: ~1 XP / 10 min = ~6 XP/hour;
- device-first AP discovery: 1 XP each;
- familiar-to-device/new-to-Beast APs: ~1 XP per 3, daily cap 20;
- new vendor: 8 XP;
- GPS lock acquired: 3 XP;
- cataloged capture: 5 XP;
- achievement bonuses.

Current achievement definitions provide roughly 10,030 XP total if every current bonus is eventually
earned, but some bonuses are themselves late Level achievements. The current catalog is therefore a
supplement, not the whole path to L100.

## 3. Time sensitivity by effective average XP/day

Because AP/vendor discovery saturates with repeated locations, exact calendar estimates depend heavily
on how mobile/active the owner is. Effective average XP/day is the most honest first model.

Approximate calendar time:

| Avg XP/day | L50 | L70 | L100 |
|---:|---:|---:|---:|
| 75 | 10.0 mo | 17.3 mo | 30.7 mo |
| 100 | 7.5 mo | 12.9 mo | 23.1 mo |
| 150 | 5.0 mo | 8.6 mo | 15.4 mo |
| 200 | 3.7 mo | 6.5 mo | 11.5 mo |
| 300 | 2.5 mo | 4.3 mo | 7.7 mo |

These are not promises. They are calibration targets until real field telemetry provides a better
distribution.

## 4. Critical breeding-time observation

Current synthesis requires **two distinct L70 parents**.

Only the active creature currently accrues normal ProgressionEngine activity.

Therefore the first local Monster effectively requires about:

    2 * XP(L70) = 78,778 combined parent XP

before the synthesis itself.

Approximate first-Monster time at current L70 parent gate:

| Avg effective roster XP/day | First two L70 parents |
|---:|---:|
| 75 | 34.5 mo |
| 100 | 25.9 mo |
| 150 | 17.3 mo |
| 200 | 12.9 mo |
| 300 | 8.6 mo |

This is much longer than "time for one Beast to reach L70."

### Recommendation
Do **not** freeze L70 as breeding maturity merely because it was the first prototype value.

A better working design is:
- **L50 = Mature / first synthesis eligible**;
- **L70 = Prime parent bonus**;
- **L85 = Apex parent bonus**;
- **L100 = Ascended/Legend legacy bonus**.

Then current first-parent-pair requirement becomes about:

    2 * XP(L50) = 45,558 combined XP

Approximate first-Monster time:

| Avg XP/day | Two L50 parents |
|---:|---:|
| 75 | 20.0 mo |
| 100 | 15.0 mo |
| 150 | 10.0 mo |
| 200 | 7.5 mo |
| 300 | 5.0 mo |

This still takes meaningful time while making the Monster system reachable.

Final threshold should be tuned from beta field data, not chosen solely by aesthetics.

## 5. Monster growth

Current Monster:
- begins at L1;
- shares the same XP curve;
- has a separate named Stage track;
- receives inherited deterministic traits.

At the same effective XP rate, a Monster requires the same calendar time from L1->L100 as a Beast:
~7.7 to ~30.7 months across the example 300->75 XP/day range.

Do not create a second numerical Level system for Monsters.

Monster-specific richness should come from:
- Growth Track / Stage names/forms;
- inherited traits;
- Monster-only achievements/unlocks;
- lineage memories;
- mutations;
- Choreography;
- Ascension/endgame.

If Monster growth proves too slow in field testing, prefer additional legitimate Monster-specific
progression opportunities rather than a hidden blanket XP multiplier.

## 6. Growth / life phase

The project already has the needed conceptual layer: Growth Track + Stage.

Do not add another XP ladder for baby->adult.

Refine the semantics:
- **Level** = continuous numeric lifetime progression;
- **Growth Stage/Form** = lineage-specific visual/narrative form milestones;
- **Maturity state** = derived eligibility such as juvenile / adult / mature / prime;
- **Rarity/Mutation tier** = intrinsic outcome rarity, orthogonal to age/Level;
- **Ascension state** = optional post-L100 transformation, not L101.

Current stage names mix age terms, roles and status (Hatchling/Cub/Scout/Tracker/Hunter/Beast/Alpha/
Apex/Monstergotchi). Treat them as provisional content, not permanent semantic categories.

## 7. Mutation odds need reconsideration

Current mutation chance:
- base: 3.5%;
- cross-lineage: +1.5%;
- each L100 parent: +2.5%;
- cap: 10%.

These are prototype design choices, not field-calibrated probabilities.

With one result per parent pair, a 3.5% base mutation is very scarce:
- 5 syntheses: ~16.3% chance of seeing at least one;
- 10 syntheses: ~30.0%;
- 20 syntheses: ~51.0%.

At a 10% chance:
- 5 syntheses: ~41.0%;
- 10 syntheses: ~65.1%;
- 20 syntheses: ~87.8%.

If each pair takes months of progression, 3.5% may be too punitive for a feature intended to be seen,
not merely datamined.

### Better model: outcome tier + special mutation
Every Monster is worthwhile.
A deterministic rarity/outcome roll can classify the inherited result.

Canonical internal tiers might be:
0. Standard
1. Uncommon
2. Rare
3. Epic
4. Legendary
5. Mythic
6. Singular / Apex / God-tier equivalent

Display vocabulary can vary by Experience/lineage:
- Common/Uncommon/Rare/Epic/Legendary/Mythic/Singular;
- D/C/B/A/S/SS/EX;
- Standard/Tuned/Prototype/Relic/Singularity;
- lineage-specific labels.

Do not make "first Monster" a rarity tier; it is a global milestone/achievement.

Special mutation can be one factor that raises/changes the outcome tier.

## 8. Hidden combinations / resonance

Hidden parent/lifetime combinations can legitimately influence offspring, provided they are bounded.

Possible modifiers:
- cross-lineage;
- complementary/opposed traits;
- both parents at Prime/Apex/L100;
- specific lineage pair;
- selected lifetime Mastery marks;
- rare inherited marker;
- first-generation/legacy ancestry;
- optional secret conditions.

Design rules:
- modifiers alter weights/chances rather than guarantee every top outcome;
- no single hidden secret is required to get an excellent Monster;
- deterministic seed/provenance remains inspectable for debugging;
- exact secret formulas may be hidden from normal UI while still versioned in code/data.

This creates discoverable breeding "recipes" without making the game solvable only by a checklist.

## 9. L100 should cause something substantial

Level 100 should remain the numerical cap.

Do not solve the endgame by simply adding L101-L500.

Recommended concept: **Ascension / Morph / Apotheosis / Apex Evolution** (final name later).

At L100:
- Hall of Legends eligibility remains;
- creature becomes Ascension-eligible;
- major one-time Choreography occurs when Ascension is chosen/unlocked;
- visual form may materially change;
- permanent signature aura/effect may unlock;
- new face/form/accessory family may unlock;
- lineage gains a legacy marker;
- offspring inheritance/rarity weighting may improve modestly;
- special Surfaces/secrets/content may become available.

### Optional Mastery condition
If more than L100 is desired before the transformation, require a *choice-based* set of Mastery Marks,
not total completion.

Example:
- L100 plus any 3 of 6 Mastery domains.

Possible domains:
- Exploration;
- Longevity;
- Expeditions;
- Discovery/collection;
- Rares/secrets;
- Lineage/relationships.

Do not require every domain.

Avoid rewarding device failures/repairs as a Mastery path; progression should never incentivize
breaking the system.

## 10. Suggested orthogonal lifetime model

    XP -> Level 1..100
            |
            +-> Growth Stage/Form
            |
            +-> Maturity
            |
            +-> Achievements / Unlocks / Memories
            |
            +-> breeding/synthesis eligibility
            |
            +-> L100 Ascension gate

    ancestry + traits + hidden resonance
            |
            +-> Monster outcome rarity
            +-> mutation
            +-> inherited appearance/temperament
            +-> legacy markers

This adds depth without creating conflicting duplicate Level systems.
