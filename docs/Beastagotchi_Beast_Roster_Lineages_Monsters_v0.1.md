# Beast Roster, Lineages & Monster Synthesis — Architecture v0.1

## Decision

Beastagotchi progression becomes a **two-layer persistent system**:

1. **global/device progression and collections** — discoveries and accomplishments
   that belong to the installation/user as a whole;
2. **individual Beast progression** — each creature owns its own XP, level 1–100,
   evolution state, achievements, unlocks, personality history and records.

Changing Theme/Layout/Experience does not reset a Beast. Switching the active
Beast changes which individual creature receives personal progression. Resting
Beasts consume effectively zero runtime resources.

The current single `profile.json` becomes the **Founder Beast** during migration
and is never discarded.

## Roster semantics

A roster may contain many persistent Beasts. Example:

- Hex — Beast — level 43
- Orbit — Beast — level 73
- Nova — Monster — level 1
- retired level-100 Beasts in the Hall of Legends

Only one Beast/Monster is active at a time. Others are resting records.

## Identity versus presentation

These are separate:

- **Beast/Monster identity** — persistent save/progression slot;
- **lineage** — species/archetype/evolution vocabulary;
- **Face profile** — rendering vocabulary;
- **Animation profile** — motion;
- **Experience** — reusable UI composition;
- **Theme** — visual language;
- **Board/Layout** — information geometry.

A user may redesign a Beast repeatedly without losing its history. An Experience
may be assigned as a preferred presentation but does not become the save slot.

## Sex/gender

Core does not require sex or gender for synthesis. Packs/lineages may expose
identity metadata or use animal-style terminology where appropriate, but the
mechanic is lineage-compatible rather than male/female-gated.

This lets the same engine support animals, robots, AI cores, ghosts, aliens,
abstract entities and other community lineages.

## Monster synthesis

Initial v1 rule:

- global synthesis concept becomes relevant at **Alpha / level 70**;
- both parents must be distinct Beast-class creatures at level 70+;
- parents are never consumed, reset or de-leveled;
- each unordered parent pair produces one v1 Monster;
- offspring starts at Monster level 1 with its own independent progression;
- ancestry and parent levels at synthesis are permanently recorded;
- first successful synthesis unlocks `monstergotchi.core`.

The threshold is deliberately data/config friendly and may be tuned after
playtesting.

### Why one Monster per pair initially

This gives ancestry meaning, prevents unlimited reroll farming and turns the
roster into a long-term collection problem. A later level-100 or rare unlock
could explicitly grant an additional synthesis slot rather than silently
changing the rule.

## Monster inheritance

The first storage milestone records a deterministic inheritance seed plus parent
lineages/preferences. It deliberately does **not** pretend we already have a
finished genetic art generator.

The intended inheritance system has two complementary outputs:

### Procedural heritage
Deterministically combine safe declarative traits such as:
- silhouette/family;
- eyes/mouth/expression vocabulary;
- accents/aura;
- animation tendencies;
- palette/visual motifs;
- preferred information emphasis;
- temperament biases.

The same Monster always regenerates identically from its persisted seed.

### Hand-authored mutation unlocks
Specific lineage pairs, achievements, Rare Moments, seasons or Packs may unlock a
curated Monster archetype/Experience. This prevents every hybrid from feeling
like a mechanical 50/50 mashup.

The best result is therefore:
**recognizable ancestry + occasional surprising mutation + artist-authored rare forms.**

## Monstergotchi unlock

Creating the first Monster is the natural transition from Beastagotchi into the
future Monstergotchi layer.

That unlock may reveal, over time:
- Monster Roster/Hall of Legends;
- advanced lineage/evolution presentation;
- Monster-only Experiences/Packs;
- additional progression/collection systems;
- peer/mesh Monster encounters;
- more advanced RF/field modules as they mature;
- Monster View / dense tricorder-style surfaces;
- higher-order secrets and cinematic events.

The unlock should reveal capabilities; it must never silently enable intrusive
radio behavior.

## Anti-farming progression

Global-first and Beast-first discoveries must be distinguished.

A new Beast may receive modest personal discovery credit for encountering
something it has never seen, even if the device already knows it. A truly
device-new discovery receives the larger global/new-world reward. Repeated
identical observations use caps/diminishing returns.

Creating more Beasts therefore extends engagement without multiplying the same
easy XP source.

## Global versus individual records

### Global/device
- lifetime BeastDex / world encounter database;
- Capture Vault;
- Expeditions and geographic history;
- Pack/content collection;
- device-wide Rare Moment schedule;
- global achievements/unlocks;
- number of Beasts raised / level-100 completions;
- Hall of Legends;
- Monster/lineage discovery collection.

### Per Beast
- XP / level / evolution;
- active/resting/legend status;
- personal achievements and unlocks;
- personal runtime/Expeditions/records;
- temperament/personality history;
- witnessed Rare Moments while active;
- cosmetics/titles/aura variants;
- preferred Experience/Theme/Face/Motion/Board;
- ancestry for Monsters.

## Rare Moments

Rare schedules remain device-global so creating ten Beasts never creates ten
rare-event schedules. A witnessed Rare Moment records the active Beast/Monster,
Experience, Expedition/location context where appropriate and resulting
personal/global rewards.

## Hall of Legends

Level-100 creatures remain available. The user may leave them active, rest them,
or mark them as Legends. A Hall of Legends should preserve:
- dates;
- final/peak level and evolution;
- personal trophies;
- rare witnesses;
- favorite/important Expeditions;
- ancestry/descendants;
- lifetime records.

There is no prestige-reset treadmill.

## Long-term completion possibilities

Examples:
- first level-100 Beast;
- two/three/five/etc level-100 Beasts;
- level 100 in every starter lineage;
- all currently released lineages to 100;
- first Monster;
- first level-100 Monster;
- complete a lineage family;
- witness a Legendary event with multiple distinct Beasts;
- multiple generations of Monster ancestry;
- global Master Collection completion.

Adding a new community lineage in the future therefore creates new meaningful
progression without invalidating existing creatures.

## Storage foundation

v0.19 adds additive SQLite structures for:
- `beasts`
- `beast_progress`
- `beast_achievements`
- `beast_unlocks`
- `beast_ancestry`
- `monster_syntheses`
- `global_unlocks`

The legacy live ProgressionEngine remains unchanged during the first migration
milestone. Cutover to the active roster Beast happens only after migration tests
prove that XP, achievements, counters and records survive exactly.

## Next implementation gates

1. source/CI validation of roster + founder migration;
2. canonical state publisher for active Beast and roster summary;
3. ProgressionEngine storage adapter using active Beast;
4. Beast Roster UI / switcher;
5. global-vs-personal achievement split;
6. Beast-first encounter memory and anti-farming XP;
7. Experience preference per Beast;
8. synthesis unlock/confirmation UI;
9. deterministic hybrid trait generator;
10. Monster-specific evolution vocabulary;
11. Hall of Legends / ancestry tree;
12. physical usability review.


## Deterministic heritage engine — implemented foundation

Monster synthesis now produces a persisted schema-2 heritage profile rather than
only reserving an inheritance seed.

The first declarative trait vocabulary covers:
- silhouette;
- eyes;
- mouth;
- accent;
- aura;
- motion tendency;
- palette/blend mode;
- information emphasis;
- temperament axes: curiosity, social, focus, boldness and nocturnal bias.

Explicit lineage/appearance traits override deterministic lineage defaults.
Each categorical child trait is deterministically inherited from one parent or
shared when identical. Temperament axes blend both parents plus a small
seed-derived bounded variation.

A separate mutation roll is deterministic and persisted. The current foundation
uses a conservative 3.5% base chance, +1.5 percentage points for cross-lineage
parents, and +2.5 points for each level-100 parent, capped at 10%. The initial
generic mutation vocabulary is intentionally small; later Lineage Packs and
curated pair rules may replace/add artist-authored forms.

Level-100 ancestry creates visible `apex_lineage` legacy markers but does not
copy the parent's achievements to the child. Cross-lineage ancestry likewise
records a `cross_lineage` marker.

This engine generates declarative identity only. It does not yet force a Monster
Face/Theme or bypass the user's presentation preferences.


## User-facing synthesis gate

Beast Studio now exposes Lineage Synthesis only when at least two distinct
Beast-class roster members are eligible.

The flow is:
1. choose Parent A and Parent B;
2. enter the proposed Monster name;
3. preview a non-mutating synthesis plan;
4. review parent preservation, offspring level and current mutation chance;
5. explicitly confirm;
6. execute through the audited Action Broker;
7. persist ancestry, heritage and the Monstergotchi global unlock.

No synthesis occurs merely because two eligible Beasts exist or because a user
switches between them.

## Monster fallback evolution vocabulary

Until individual Lineage Packs can provide their own evolution vocabulary,
Monster-class creatures use:

Origin → Awakened → Morph → Adapted → Chimera → Ascendant → Prime → Mythic →
Monstergotchi

at the same numeric level thresholds used by Beast progression. Numeric
progression therefore stays compatible while presentation can diverge by kind
and, later, by lineage.


## Per-creature memory timeline

The roster now has a deliberately low-volume memory layer.

Stored as per-creature memories:
- level-ups;
- evolution/stage changes;
- personal achievement unlocks;
- acknowledged Rare Moments;
- Expedition start/recovery/checkpoint milestones;
- Monster origin and descendant lineage events;
- personality/mood transitions only after the new mood remains stable for 10s.

Detailed Wi-Fi, peer and GPS telemetry is **not copied** into the memory table.
BeastDex, PeerDex and Expedition stores remain authoritative and may be linked by
future Memory Vault views.

A `beast_expeditions` join table records which creatures actually participated
in an Expedition. Touch updates are throttled so this feature does not create a
new high-rate SD-card write path.


## Hall of Legends and ancestry graph

Hall membership is deliberately separate from runtime `active/resting` state.
A creature must reach level 100 before it can be inducted. Once inducted, it may
still be awakened, used normally, rested again, or have its preferred Experience
changed without losing Hall status.

The Hall foundation reports inducted Legends, level-100 candidates, achievements,
memory totals, Rare witnesses, Expedition participation, parent/descendant
relationships, generation and mutation information.

Beast Studio includes a Hall surface and textual ancestry-tree viewer. The
underlying graph is renderer-neutral so a richer visual family-tree/constellation
presentation can be added later without changing persistent ancestry data.
