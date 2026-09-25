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

---

## 11. OS-grade touch/display architecture

Desktop Linux feels polished because "touch" is not one function. It is a stack.

Beastagotchi should intentionally mirror that separation even though its final renderer is a compact
framebuffer appliance rather than Wayland/GNOME/KDE.

Target structure:

    Kernel / device tree / evdev / framebuffer
              |
       Beast Device HAL
        /           \
    DisplayProfile  TouchProfile
        |              |
    RenderScheduler  TouchSample stream
        |              |
    Compositor      GestureRecognizer
        |              |
    Framebuffer     GestureArbiter
         \             /
           SurfaceStack
               |
          UI controls

### DisplayProfile
Discover/measure rather than assume:
- framebuffer node;
- pixel geometry;
- logical geometry;
- rotation;
- pixel format / bpp;
- physical dimensions if available;
- configured SPI/display fps;
- actual full-frame and dirty-update write time;
- driver identity;
- brightness/backlight capability if exposed.

An SPI ILI9486 does not behave like a 60/120 Hz HDMI desktop monitor. Render cadence should be based
on the real panel/driver/write budget, with immediate interaction feedback prioritized over chasing
an arbitrary refresh-rate number.

### TouchProfile
Query the Linux input device rather than hard-code only X/Y:
- supported event/absolute axes;
- ABS_X/ABS_Y minimum/maximum;
- fuzz/flat/resolution;
- ABS_PRESSURE when present;
- BTN_TOUCH;
- transform/rotation;
- calibrated affine matrix;
- bezel/dead zones;
- measured noise/slop;
- pressure calibration if available.

Linux evdev already exposes much of the raw capability metadata that desktop input stacks consume.

### Calibration
Replace "one static touch.json forever" with a versioned calibration/profile contract:
- 5- or 9-point guided calibration;
- outlier rejection;
- affine transform solve;
- verification pass;
- per-rotation profile;
- quality score/error heatmap;
- easy re-calibration;
- safe fallback.

### Widget/gesture layer
Create reusable touch-native controls:
- Button;
- Toggle;
- Slider;
- ScrollList;
- ScrollView;
- Tabs;
- Carousel;
- Context menu;
- drag/reorder handle;
- modal confirmation.

These controls own hit slop, pressed state, scroll claiming, visual feedback and accessibility
instead of every Surface implementing touch geometry independently.

### Acceptance targets
Final numbers require physical evidence, but define measurable targets for:
- tap hit rate;
- edge/corner hit rate;
- false swipe rate;
- false tap-after-scroll rate;
- long-press accuracy;
- scroll continuity;
- gesture latency;
- release/lift noise;
- pressure repeatability if supported.

Touch/navigation acceptance is a release gate equal in importance to visual fidelity.

---

## 12. Progression provenance / tamper-evident Life Ledger

Beastagotchi is open-source and owner-sovereign. A root owner can ultimately replace any local
check. The goal is therefore **not impossible anti-cheat**.

The useful goal is:
> ordinary progression should not be defeated by changing one obvious XP/level value.

Introduce a per-creature **Life Ledger**.

Each progression entry records:
- sequence;
- creature id;
- source Event/action;
- rule id + rule-set version/hash;
- XP delta;
- relevant bounded context;
- timestamp;
- prior-entry hash;
- entry hash;
- optional device-local HMAC/signature.

Canonical XP/Level is derived/verified from the ledger.
The mutable `beast_progress.xp` field becomes a cache/materialized value, not unquestioned truth.

### Effects
- directly editing `xp=999999` is detected/rebuilt from ledger;
- deleting/reordering ledger entries breaks the hash chain;
- changing XP rules changes the rule-set provenance;
- official release/build hashes can be recorded with awards;
- backup/restore can validate lineage history.

### Owner sovereignty
Expert/root owner can still:
- use an explicit `admin_adjustment` progression entry;
- adopt/import a customized timeline;
- run a development/sandbox profile;
- patch/replace validation code entirely.

Managed Beast then labels provenance honestly:
- Verified;
- Restored;
- Imported;
- Customized;
- Reconstructed / integrity warning.

No remote server or DRM is required.

### Fun response to crude tampering
A detected mismatch may produce a playful non-destructive event such as:
- "Temporal anomaly detected";
- glitch aura;
- Doctor finding;
- corrupted-timeline visual;
- hidden Easter egg.

It must not destroy data or permanently lock the owner out.

Offer:
- Restore From Ledger;
- Explain Difference;
- Adopt Customized Timeline (Expert).

This creates the desired "nice try" behavior while respecting local ownership.

### Important limitation
A determined root owner with source access can remove/fake every local check.
Do not market this as secure competitive anti-cheat.
It is provenance, integrity and friction against trivial editing.

---

## 13. Recalibrate progression around real Pwnagotchi duty cycles

Previous calendar estimates implicitly assumed daily effective XP accumulation that is unrealistic
for many Pwnagotchi owners.

Reference usage should include:
- light: ~4 hours/week;
- typical: ~8-10 hours/week;
- active: ~12-16 hours/week;
- heavy/field enthusiast: 20+ hours/week.

The current ~70,182 XP L100 threshold is likely too large unless XP awards are multiplied so heavily
that their numbers become needlessly inflated.

### Preferred direction
Keep:
- levels 1..100;
- curved progression shape.

Reconsider:
- absolute XP coefficient;
- all reward values together.

Likely useful L100 design band:
**~20,000-30,000 total XP**, subject to simulation/beta telemetry.

For example, keeping the current 1.60 curve but reducing the coefficient from 45 to 16 produces
approximately:
- L10: 538 XP;
- L20: 1,779;
- L35: 4,513;
- L50: 8,099;
- L70: 14,005;
- L85: 19,185;
- L100: 24,954.

This is an example calibration, not a committed formula.

### Calendar target
A reasonable design target to test:
- typical 8-10 h/week mixed use: L100 in roughly 8-12 months;
- lighter ~4 h/week use: roughly 14-20 months;
- active 12-16 h/week use: roughly 5-8 months.

Heavy users should not trivially finish in weeks.

### Reward design
Avoid relying on raw uptime alone.

Use a mixture:
- modest active-runtime progression;
- session milestones;
- real discovery;
- captures;
- vendors;
- Expeditions;
- Achievements;
- Rares;
- progression/content events.

Use diminishing returns/caps for highly repetitive sources so 24/7 uptime does not dominate.

Do not use daily streak punishment.

### Progression simulator
Before freezing values, build a simulation/test harness with representative usage profiles and
real/replayed field traces.

Outputs:
- median days/hours to L10/L25/L50/L70/L85/L100;
- source contribution percentages;
- earliest/median synthesis;
- Monster L100 timing;
- effect of Achievements/Packs;
- exploit/repeatable-source dominance.

Tune from evidence, then beta telemetry.

---

## 14. Richer lifetime axes without competing Level systems

Level 1-100 remains the single primary numeric level.

Add orthogonal dimensions rather than another XP ladder.

### Life Phase / maturity
Broad universal semantic phase, for example:
- Origin / Newborn;
- Juvenile;
- Growing;
- Mature;
- Prime;
- Apex;
- Ascended-eligible.

Exact thresholds remain provisional.

### Growth Form
Lineage-specific visual/narrative form.

A lineage may have 6, 8, 10 or another number of Forms.
Forms do not all need a completely separate sprite set; some may be substantial geometry/forms and
others may add horns/aura/posture/markings/equipment/etc.

### Rank / Title
Earned status based on accomplishments rather than age.

Examples:
- Explorer;
- Veteran;
- Cartographer;
- Collector;
- Pathfinder;
- Legend.

Rank/title should not be another numeric Level.

### Archetype / Role
May emerge from behavior:
- Explorer-heavy;
- Collector-heavy;
- stationary sentinel;
- expedition specialist;
- etc.

This can alter flavor/visual reactions without locking progression.

### Rarity
Intrinsic birth/synthesis outcome tier.
Independent from Level/maturity.

### Mastery
Late-game accomplishment domains used for optional Ascension variants/endgame depth.

### Ascension
Post-L100 transformation/state.
Level remains 100.

This model separates:
age/maturity, visual form, accomplishment, behavior, rarity and endgame state instead of forcing all
of them into one Stage label.


---

## 15. Layered progression integrity: tamper-evident, not owner-hostile

The project owner wants trivial progression cheating to be intentionally frustrating/funny rather
than one-line easy, while preserving open-source/root sovereignty.

The design goal is **defense in depth for progression provenance**, not impossible local anti-cheat.

### Principle

No single editable value should be sufficient to manufacture a fully "verified" high-level Beast.

Changing one layer should create inconsistencies detectable by another layer.

### Layer A — materialized progression cache

Fast runtime tables may contain:
- xp;
- level;
- stage;
- counters.

These are caches/derived state.

They are periodically recomputed/verified from the Life Ledger.

If cache != ledger:
- mark integrity mismatch;
- rebuild cache from ledger;
- record Doctor finding;
- do not destroy owner data.

### Layer B — Life Ledger hash chain

Every progression-granting event records:
- sequence;
- creature id;
- event/rule id;
- rule-set version/hash;
- XP delta;
- bounded context;
- previous entry hash;
- entry hash;
- optional device-local MAC/signature.

Reordering/deleting/editing entries breaks the chain.

### Layer C — independent checkpoints / Merkle-style summary

Do not rely on only the ledger's own final hash.

Periodically store independent progression checkpoints derived from:
- ledger head hash;
- total XP;
- level;
- achievement/unlock set digest;
- creature identity/lineage id;
- ruleset id.

Possible stores:
- separate SQLite table/domain;
- Patient Chart technical history;
- Recovery/known-good metadata;
- signed Capsule/backup metadata where relevant.

The purpose is cross-checking, not secrecy.

### Layer D — achievement/award provenance

High-value Achievements/Awards should record:
- source event;
- required rule id;
- source ledger sequence/head;
- creature id;
- build/ruleset provenance;
- unlock timestamp.

Therefore directly inserting an Achievement row without matching provenance can be detected.

### Layer E — integrity eligibility state

Introduce a derived state such as:

- `verified` — current history validates under an accepted ruleset;
- `restored` — valid history restored from trusted backup;
- `imported` — imported history with valid provenance;
- `customized` — owner intentionally modified progression/rules;
- `integrity_warning` — unexplained mismatch;
- `sandbox` — development/testing progression.

Normal local functionality always remains available.

However, **verified-only** recognition may be suspended while the state is unexplained.

Examples:
- official verified badge;
- "clean lineage" marker;
- verified Hall-of-Legends status;
- certain global/shared leaderboard/community badges if such systems ever exist.

Do not disable ordinary local play simply because the owner customized their machine.

### Layer F — Doctor/integrity explanation

Doctor can say:

    PROGRESSION INTEGRITY WARNING

    Cached XP: 28,450
    Ledger-derived XP: 12,730
    Achievement provenance: 3 mismatches
    Last known-good checkpoint: <timestamp>

    [ RESTORE VERIFIED STATE ]
    [ SHOW DIFFERENCE ]
    [ ADOPT CUSTOM TIMELINE — EXPERT ]

This is preferable to silent punishment.

### Circular cross-check / "whack-a-mole" behavior

The desired playful friction can be achieved by having multiple independently derived invariants.

Example:

1. Owner edits XP cache.
   - Ledger disagrees.

2. Owner edits ledger totals/entries.
   - Hash chain/checkpoint disagrees.

3. Owner edits the checkpoint.
   - Achievement/unlock provenance and Patient Chart/backup history disagree.

4. Owner inserts/edits achievements.
   - Award provenance/ledger sequence/ruleset validation disagrees.

5. Owner patches one validator.
   - Build/ruleset provenance becomes customized, so the device may no longer claim
     `verified` progression unless the owner also replaces the higher-level integrity policy.

Eventually the owner can patch the entire integrity system because they are root and have source.
At that point the correct state is **customized**, not an endless hostile arms race.

### No destructive anti-tamper

Never:
- delete a Beast;
- corrupt saves intentionally;
- brick boot;
- wipe awards;
- encrypt owner data as punishment;
- create reboot loops;
- hide recovery paths.

The "loop" should be semantic/provenance friction, not sabotage.

### Awards/Achievements during unexplained integrity failure

A sensible default:
- existing local history remains visible;
- new **verified** achievements/awards can be held in a pending/unverified state;
- XP derived from unverifiable entries is not accepted into verified progression;
- once repaired/adopted, pending items are re-evaluated.

If the owner explicitly chooses **Adopt Customized Timeline**, normal local progression can continue
under a customized provenance label.

This preserves fun while keeping the "verified" path meaningful.

### Easter-egg opportunity

A determined owner who intentionally defeats or replaces the integrity validator through a documented
Expert/developer path could unlock a harmless hidden Achievement/Easter egg.

Examples:
- `THE AUDITOR BLINKED`
- `ROOT OF ALL EVIL`
- `TEMPORAL ENGINEER`
- `YOU CHECKED THE CHECKER`

Do not award it merely for corrupting state accidentally.
Trigger only through an explicit advanced/developer path or recognized validator override state.

### Important boundary

This is not security against a malicious root user.

It is:
- integrity checking;
- provenance;
- trivial-cheat resistance;
- a fun owner-facing puzzle;
- supportability.

A technically skilled owner can always fork/remove the system.
That is acceptable and should be acknowledged rather than fought indefinitely.

