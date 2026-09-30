# Beastagotchi Architecture Contract Review — Part 7: Lifecycle, Progression, Lineage & Discovery

**Date:** 2026-09-25  
**Status:** proposed foundation contract; discussion-quality, not yet implementation freeze  
**Inputs:** current v0.19 progression/roster/lineage implementation, Structure Deep Dive, Architecture Parts 1-6,
Touch/Progression/Breeding Review, owner discovery/Easter-egg guidance, Life Ledger/integrity direction.

---

# 1. Purpose

Beastagotchi's creature system is not decorative metadata layered on top of a technical dashboard.

The Beast is a persistent identity that accumulates:

- life history;
- progression;
- memories;
- accomplishments;
- discoveries;
- lineage;
- temperament/personality;
- presentation preferences;
- rare moments;
- provenance;
- owner interaction.

The lifecycle/progression contract must remain deep enough for years of expansion without becoming:

- one giant XP counter;
- a pile of incompatible level systems;
- an exact-completion checklist;
- a fragile set of hard-coded thresholds;
- owner-hostile anti-cheat;
- a system where every rare outcome is determined only by random chance;
- a system where one secret or Pack becomes mandatory for a strong lineage.

Stable direction:

> **One primary Level. Many orthogonal lifetime dimensions.**

and:

> **Deeper discoveries may matter more, but no single discovery should mathematically own the future.**

---

# 2. Identity layers

Keep these distinct.

## Device identity

The local Beastagotchi installation/device.

Owns:
- device-global accomplishments;
- local install history;
- owner preferences;
- Patient Chart/known-good state;
- device-level unlocks where appropriate.

## Beast identity

One persistent creature.

Owns:
- id/name;
- kind;
- lineage;
- birth/creation provenance;
- level/XP;
- life phase;
- growth form;
- temperament/personality;
- creature-specific achievements;
- memories;
- discoveries;
- presentation preference;
- rarity;
- mastery/Ascension state;
- lineage legacy.

## Monster identity

A Monster is not merely "a Beast over some level".

Monster is a creature kind/growth path produced by synthesis/lineage rules.

It has the same durable identity principles while permitting different:

- forms;
- growth logic;
- reveal choreography;
- rarity semantics;
- endgame behavior.

## Owner/operator identity

Do not confuse creature identity with Part 2 ActorRef/operator authority.

The Beast is a progression subject, not an administrative actor.

---

# 3. Persistent roster

The roster is authoritative durable creature identity state.

Stable guarantees:

- multiple Beasts/Monsters may coexist;
- one active creature may drive active progression/presentation;
- switching active creature does not destroy inactive history;
- inactive creatures retain independent progression;
- parents survive synthesis unless a future explicit recipe says otherwise;
- identity ids remain stable across rename/presentation changes;
- Founder migration remains non-destructive;
- roster truth is independent from one Experience/theme.

The roster is Beast-domain authority, not UI state.

---

# 4. One primary numeric Level

Use one primary numeric **Level 1-100** track for ordinary Beast/Monster progression.

Do not add competing numeric ladders that merely rename Level.

Level means broad accumulated lifetime progression.

It does not directly encode:

- age;
- visual form;
- rank/title;
- rarity;
- mastery;
- personality;
- lineage generation;
- Ascension;
- owner relationship.

These are orthogonal.

Level 100 is a meaningful long-term target, not automatic completion of all content.

---

# 5. XP economy

XP is one input to Level.

Stable rules:

- XP comes from truthful canonical events/state/history;
- normal Beast/Pwnagotchi use remains a major source;
- many overlapping sources exist;
- no single category must be exhausted;
- repeatable sources may have caps/diminishing returns;
- raw uptime alone should not dominate;
- missed rare/seasonal/optional content must not permanently strand Level progress;
- future Packs may add new valid progression opportunities;
- historical XP truth remains tied to the rule/version that granted it.

Do not freeze final coefficients/reward values in the architecture contract.

Final economics require simulator/beta evidence and owner-facing balance review.

---

# 6. Usage calibration

Progression must reflect real Pwnagotchi duty cycles.

Reference usage profiles should include approximately:

- light: ~4 h/week;
- typical: ~8-10 h/week;
- active: ~12-16 h/week;
- heavy/field enthusiast: 20+ h/week.

Current exploratory design band:

- typical use reaches L100 roughly in 8-12 months;
- lighter use roughly 14-20 months;
- active use roughly 5-8 months;
- heavy use should not finish trivially in weeks.

These are tuning targets, not frozen promises.

The current exploratory ~20k-30k L100 total may be more appropriate than the older ~70k scale,
subject to simulation.

Architecture freezes the **method of calibration**, not the final coefficient.

---

# 7. Progression Rule Engine

Replace growing hard-coded progression conditions with typed rules.

A ProgressionRule may declare:

- stable id/version;
- source Event/Signal/metric;
- subject scope:
  - device;
  - active Beast;
  - specific Beast;
  - lineage/global;
- eligibility;
- one-shot/repeatable;
- cap/cooldown/diminishing policy;
- XP/reward output;
- rarity/discovery classification;
- provenance requirements;
- integrity requirements;
- optional content dependency;
- privacy/publication behavior.

Rules are deterministic over truthful evidence where possible.

Random outcome systems must record the inputs/modifiers/ruleset used.

---

# 8. Life Ledger

The Life Ledger is the durable progression/provenance history.

Each progression-relevant entry should record enough evidence to explain:

- sequence;
- creature/device subject;
- timestamp;
- source Event/State reference;
- rule id/version;
- ruleset hash/version;
- XP/reward delta;
- bounded context;
- previous-entry hash;
- entry hash;
- provenance class;
- optional transaction/content/achievement references.

The exact cryptographic implementation may evolve.

Stable goal:
- progression can be reconstructed/explained;
- one cached number is not the only truth;
- modifications become detectable;
- historical rules remain identifiable.

---

# 9. Materialized progression state

Fast runtime fields such as:

- xp;
- level;
- current phase;
- counters;
- active unlock summary;

may be materialized caches.

They are not the sole provenance authority.

If cache and Ledger disagree:

- do not silently accept the cache;
- recompute/compare;
- mark integrity state;
- expose Doctor explanation;
- preserve owner data;
- allow recovery/customized adoption paths.

---

# 10. Life Phase / maturity

Life Phase is a broad semantic age/maturity dimension.

Possible vocabulary may include concepts such as:

- Origin/Newborn;
- Juvenile;
- Growing;
- Mature;
- Prime;
- Apex;
- Ascended-eligible.

Exact names and thresholds remain owner-facing design decisions to finalize later.

Life Phase may consider:

- Level;
- lifetime activity;
- age/time where appropriate;
- accomplishments;
- lineage/kind policy.

Do not make maturity an arbitrary giant checklist wall.

Maturity should feel like natural development, not bureaucratic gating.

---

# 11. Growth Form

Growth Form is lineage/kind-specific visual/narrative development.

A lineage may define:

- 5 forms;
- 6 forms;
- 8 forms;
- 10 forms;
- another sensible count.

Not every form requires a completely new sprite/model.

Forms may alter:

- geometry;
- posture;
- eyes;
- horns;
- markings;
- aura;
- equipment;
- facial structure;
- animation;
- scene relationship.

Growth Form is not another numeric Level.

---

# 12. Rank / Title

Rank/Title reflects accomplishment.

Examples:
- Explorer;
- Veteran;
- Cartographer;
- Collector;
- Pathfinder;
- Legend.

Rank/title should derive from meaningful accomplishments rather than simple age.

Multiple ranks/titles may coexist as earned history while one may be selected/displayed.

Do not force all users down one prestige ladder.

---

# 13. Archetype / Role

Archetype may emerge from actual behavior.

Examples:

- Explorer-heavy;
- Collector-heavy;
- stationary Sentinel;
- expedition specialist;
- Doctor/maintenance-oriented;
- social/peer-oriented;
- capture-oriented.

Archetype may influence:

- flavor;
- animation;
- presentation;
- hidden reactions;
- some future eligibility/weighting.

Do not use it to permanently lock the owner out of other play styles.

---

# 14. Rarity

Rarity is an intrinsic outcome/identity dimension.

It is independent from Level.

Rarity may originate from:

- birth/Genesis;
- synthesis;
- lineage;
- mutation;
- rare resonance/discovery interactions;
- special content/rules.

Rarity vocabulary/presentation may vary by Experience.

Canonical underlying tier semantics should remain stable enough for provenance.

Rarity must not mean "stronger at everything".

Prefer:
- identity;
- unusual form;
- special presentation;
- uncommon eligibility;
- bounded modifier differences.

---

# 15. Mastery

Mastery represents deep accomplishment domains, especially later game.

Mastery may be domain-specific:

- exploration;
- collection;
- radio/network observation;
- Expeditions;
- Doctor/maintenance;
- secrets/discovery;
- lineage;
- community/peer systems;
- future domains.

Mastery is not another XP/Level clone.

It may influence:
- titles;
- cosmetics;
- Ascension eligibility/variants;
- special interactions;
- rare outcome weighting.

---

# 16. Ascension

Ascension is a post-L100 transformation/state.

Level remains 100.

Ascension may depend on:

- maturity;
- Mastery;
- lineage;
- major accomplishments;
- discoveries;
- owner choice;
- rare eligibility;
- content availability.

There may be multiple Ascension paths/forms.

Do not make one canonical "best ending".

Ascension should deepen the lifetime rather than invalidate everything before it.

---

# 17. Achievements, Awards and Trophies

Keep vocabulary semantically useful.

## Achievement
A rule-backed accomplishment.

## Award/Trophy/Badge
A durable recognition/display object that may be granted by an Achievement or special event.

Not every Achievement needs XP.

Not every Award changes progression.

Each high-value recognition should preserve:

- source rule/event;
- subject;
- ruleset/provenance;
- timestamp;
- relevant Ledger head/sequence.

Community content may define local/namespaced Achievements.

Canonical global XP contribution remains policy-controlled.

---

# 18. Memories

Memory is durable personal history, not necessarily reward.

Examples:

- first handshake/capture milestone;
- first Expedition;
- rare encounter;
- major Doctor recovery;
- synthesis;
- Monster birth;
- owner-selected moment;
- exceptional field session;
- secret discovery;
- unusual environmental/context event.

Memories may affect presentation/personality without awarding XP.

A MemorySpec/registry may define semantics later.

---

# 19. Rare Moments, Secrets and discoveries

Treat these as a broad discovery system, not a fixed list.

Discovery may be:

- ordinary hidden interaction;
- uncommon condition;
- rare field event;
- deep systemic exploration;
- lineage combination;
- contextual/environmental event;
- owner interaction;
- Expert/developer challenge;
- future community-defined discovery.

A discovery should have stable provenance even when its presentation remains secret.

Do not expose every hidden condition in normal UI simply because data exists.

Expert/debug tools may expose deeper provenance where appropriate.

---

# 20. Discovery depth

Discovery reward may scale with:

- rarity;
- intentionality;
- difficulty;
- depth of system understanding;
- number/quality of independent conditions;
- persistence over time;
- exceptional real-world evidence;
- risk of accidental trigger.

Stable principle:

> **The deeper and rarer the discovery, the more meaningful its reward may be.**

Do not reduce every secret to "more XP".

Possible reward dimensions:

- bounded XP;
- unique Achievement/Trophy;
- permanent aura/cosmetic;
- hidden face/form;
- secret Surface;
- rare Choreography;
- Mastery mark;
- lineage legacy marker;
- title/rank;
- unique Memory;
- synthesis/breeding resonance modifier;
- mutation weighting;
- Morph/Ascension eligibility/weighting.

---

# 21. Outcome influence from discoveries

High-tier discoveries may influence future probabilistic/eligibility systems.

They should normally:

- bend probability;
- unlock candidate outcomes;
- add resonance;
- influence weighting;
- expose hidden forms;

rather than guarantee a top outcome.

A strong discovery lineage may become more interesting without becoming mathematically unbeatable.

Record which modifiers contributed to a synthesis/morph/Ascension result.

Hidden modifiers may remain hidden in normal UI while inspectable in Expert/debug evidence.

---

# 22. Diminishing stacking

Multiple rare modifiers must combine with diminishing returns/caps.

Example semantic combination:

- strongest modifier contributes fully;
- second contributes partially;
- later modifiers contribute progressively less;
- hard cap preserves uncertainty.

Do not raw-add every bonus.

No heavily decorated lineage should reach 100% mythical/top-tier outcome probability merely through
modifier accumulation.

---

# 23. Synthesis / breeding

Synthesis combines persistent parent identities under a registered recipe/policy.

Stable guarantees:

- parents remain intact by default;
- offspring receives a new stable identity;
- ancestry is persisted;
- lineage/generation is persisted;
- recipe/ruleset/provenance is persisted;
- resulting creature normally begins its own lifetime at L1;
- outcome inputs/modifiers are recorded;
- reveal/creation is a Choreography concern;
- synthesis does not rewrite parent histories.

Current level-70+ two-parent v1 rule is an implementation checkpoint, not a permanent architecture law.

Final eligibility thresholds belong to later balance/owner review.

---

# 24. MaturityPolicy and SynthesisRecipe

Separate these concerns.

## MaturityPolicy
Determines semantic readiness/maturity state.

## SynthesisRecipe
Defines a particular combination process.

Recipe may declare:

- eligible kinds/lineages;
- maturity requirements;
- parent count;
- required discoveries/masteries;
- optional resonance modifiers;
- rarity/mutation tables;
- content requirements;
- output kind/path;
- Choreography;
- provenance rules.

Do not hard-code all future breeding into one function.

---

# 25. Heritage

Heritage describes inherited traits/lineage influence.

Potential inherited dimensions:

- lineage;
- visual markers;
- temperament tendencies;
- rare trait candidates;
- growth-form variants;
- ancestry markers;
- resonance;
- future affinity domains.

Heritage should not blindly copy every parent field.

Use explicit inheritable traits with versioned rules.

Preserve privacy for any fields that could leak device/user context when lineage is shared.

---

# 26. Mutation

Mutation is a special outcome dimension, not simply the highest rarity.

Use a model such as:

1. resolve broad outcome/rarity/lineage result;
2. independently resolve special mutation opportunities where applicable.

Mutation may produce:

- visual trait;
- unusual form;
- hidden behavior;
- special resonance;
- rare Choreography;
- future evolution path.

Do not make mutation so rare or so dominant that normal lineages feel irrelevant.

Final probabilities are balance values, not architecture constants.

---

# 27. Genesis / creation lifecycle

Initial Beast creation should be content/choreography-driven.

Possible metaphors:

- hatch;
- assemble;
- boot;
- awaken;
- excavate;
- synthesize;
- emerge;
- forge;
- discover.

Do not hardwire "all Beasts hatch from eggs".

Genesis should establish:

- stable identity;
- initial kind/lineage;
- initial provenance;
- owner choices;
- initial Experience/presentation preferences where relevant;
- initial Memory;
- creation Choreography;
- known-good durable persistence.

---

# 28. Monster reveal

Monster reveal is a major lifecycle event.

It should generally feel more significant than ordinary Beast creation.

Possible flow:

- eligibility/readiness;
- owner confirmation/choice;
- pairing/input review;
- synthesis sequence;
- incubation/formation;
- reveal;
- classification/rarity/lineage;
- roster/history update;
- Achievement/Memory;
- larger Choreography for exceptional outcomes.

The semantic result exists independently from premium media availability.

---

# 29. Progression integrity states

Use a derived provenance/integrity classification such as:

- verified;
- restored;
- imported;
- customized;
- integrity_warning;
- sandbox/development.

Exact vocabulary may evolve.

Stable behavior:

- ordinary local use remains possible;
- unexplained inconsistency affects **verified claims**, not ownership of the machine;
- customized state is factual, not moral failure;
- restoration/import may preserve valid provenance where evidence supports it.

---

# 30. Layered integrity

Do not rely on one editable XP field.

Layered cross-checking may include:

- materialized cache;
- Life Ledger hash chain;
- independent checkpoints;
- achievement/award provenance;
- Patient Chart/known-good references;
- backup/Capsule metadata;
- ruleset/build provenance.

Changing one layer may reveal disagreement with another.

The goal is:

- supportability;
- provenance;
- trivial-cheat resistance;
- interesting owner exploration;

not impossible DRM against root.

---

# 31. Owner sovereignty and anti-tamper boundary

Never use progression integrity to:

- delete a Beast;
- wipe awards;
- corrupt owner files;
- brick boot;
- create reboot loops;
- encrypt data as punishment;
- hide recovery;
- lock unrelated local features.

A root owner can ultimately patch the system.

At that point the honest semantic result is **customized**, not an arms race.

Verified-only community recognition may be withheld when provenance no longer validates.

Local owner fun remains available.

---

# 32. Integrity anomaly responses

Doctor may explain:

- cache/Ledger mismatch;
- missing provenance;
- modified ruleset;
- inconsistent awards;
- checkpoint drift.

Owner-facing choices may include:

- restore verified state;
- show difference;
- repair/rebuild cache;
- inspect provenance;
- adopt customized timeline in Expert mode.

No silent punishment.

---

# 33. Integrity Easter eggs

Reading/opening files is ordinary owner behavior and triggers nothing.

Trigger depth should depend on increasingly intentional state-changing understanding.

## Tier 0 — observation

Examples:
- open source;
- inspect SQLite;
- read Ledger/checkpoint;
- dump progression state;
- inspect validator code.

Result:
- no penalty;
- no Easter egg.

## Tier 1 — harmless derived-state manipulation

Example:
- modify cached XP/level and save;
- restart;
- reconciliation detects mismatch.

Possible:
- humorous anomaly/Doctor response;
- tiny secret marker;
- no major reward.

## Tier 2 — Ledger/provenance manipulation

Examples:
- alter entries;
- attempt to rebuild chain;
- attempt to align checkpoints.

Possible:
- rare discovery where intentionality is clear.

## Tier 3 — validator-level understanding

Examples:
- intentionally replace/override validation;
- use an advanced developer path;
- force a custom ruleset coherently.

Candidate:

**THE AUDITOR BLINKED**  
*"You checked the checker."*

## Tier 4 — deliberate owner-sovereignty completion

Examples:
- modify rules;
- modify Ledger/provenance;
- explicitly adopt the resulting coherent custom timeline;
- return the system to internally consistent customized operation.

Candidate:

**ROOT OF ALL EVIL**  
*"Reality is whatever you compile it to be."*

These are concept candidates, not permission to encourage destructive database corruption.

A clean hidden developer challenge may be preferable to reckless file damage.

---

# 34. Easter-egg trigger rules

Do not trigger by:

- file open;
- source read;
- database viewing;
- one accidental corrupt write;
- repeated meaningless corruption attempts.

Prefer evidence of:

- deliberate progression-state change;
- deeper provenance manipulation;
- successful traversal of integrity layers;
- explicit Expert/customized adoption.

Repeated failed attempts may vary flavor messages but should not endlessly increase reward.

Reward correlates to **depth of understanding**, not raw number of damaged files.

---

# 35. High-depth reward policy

Developer/root-tier discoveries may receive unusually meaningful rewards.

Potential rewards:

- unique permanent title;
- lineage legacy marker;
- special aura;
- hidden form;
- secret Surface;
- unique Choreography;
- Mastery mark;
- significant but bounded XP;
- future synthesis resonance;
- Morph/Ascension candidate unlock;
- rare Memory.

Because these are intentionally difficult discoveries, they may be substantially more meaningful than
ordinary secrets.

But they still must obey diminishing/capped downstream influence.

---

# 36. Global versus creature-specific accomplishments

Every progression/reward definition must identify scope.

Possible scopes:

- device-global;
- active Beast;
- specific Beast;
- lineage;
- roster/global;
- owner-profile/local installation.

Example:
A "first ever system recovery" may be device-global.

A "this Beast explored N new contexts" achievement is creature-specific.

Do not award everything globally just because the device observed it.

---

# 37. Beast-first versus device-first discovery

Some events should attach to the active creature.

Some are device/platform facts.

The rule definition must decide intentionally.

When ambiguous:

- prefer creature attachment when the event is part of that creature's lived experience;
- prefer device/global when it represents installation/platform history independent of active creature.

Preserve enough provenance to avoid double-credit mistakes after switching Beasts.

---

# 38. Per-Beast presentation preferences

A Beast may remember preferred presentation identity.

Examples:

- preferred Experience;
- face;
- motion profile;
- aura;
- presentation variants.

These preferences do not alter progression truth.

Switching active Beast may restore its preferred Experience where policy/availability permits.

Missing content falls back honestly without erasing the preference.

---

# 39. Personality / owner interaction

Owner interaction may influence:

- personality expression;
- hidden interactions;
- Memories;
- flavor;
- some rare discoveries;
- presentation reactions.

Avoid making the Beast a punitive virtual-pet chore system.

Do not require daily streak maintenance to preserve progress.

Owner absence should not create guilt-driven regression.

---

# 40. Optional content and future expansion

Initial release does not need every future L100/Ascension/legendary branch finished if the contract
supports them honestly.

If a future-facing control exists before content is available, show:

- coming soon;
- unavailable with reason;
- under construction;
- version/roadmap hint where useful.

Never pretend unfinished lifecycle content is live.

---

# 41. Community progression content

Community Packs may define:

- namespaced local Achievements;
- Memories;
- secret conditions;
- visual rewards;
- lineage/content-specific unlocks;
- optional synthesis recipes where policy allows.

Canonical global XP contribution is controlled by policy.

Community rules must declare:

- source;
- caps;
- cooldowns;
- version;
- scope;
- reward bounds;
- provenance.

No unbounded repeatable XP rule.

No arbitrary direct write to canonical XP.

---

# 42. Progression and Pack removal

Removing a content Pack must not erase historical truth.

If an Achievement/Memory/reward was legitimately earned under a now-removed rule/content version:

- preserve the historical record;
- preserve provenance;
- presentation may fall back when its asset is unavailable;
- do not silently revoke the fact merely because source content disappeared.

Future re-evaluation may be needed only where rules explicitly define ongoing eligibility.

---

# 43. Rule versioning

Every progression result should be attributable to the rule version that existed when it occurred.

Do not rewrite history merely because reward balance changes later.

Possible policies:

- old reward remains historical truth;
- new rule applies prospectively;
- explicit migration event may adjust where truly necessary;
- migration itself becomes Ledger provenance.

This prevents silent economy rewrites.

---

# 44. Simulation before freeze

Build a progression simulator before final economy freeze.

Representative inputs:

- light/typical/active/heavy weekly use;
- different activity mixes;
- offline-heavy use;
- Expedition-heavy use;
- capture-heavy use;
- ordinary casual use;
- rare-discovery lucky/unlucky cases;
- multiple Beasts;
- synthesis timing;
- Pack contributions.

Outputs:

- median hours/days to L10/L25/L50/L70/L85/L100;
- XP source contribution;
- earliest/median maturity/synthesis;
- Monster progression timing;
- effect of rare modifiers;
- repeatable-source dominance;
- exploit sensitivity;
- content-missing scenarios.

Balance from evidence, then beta telemetry.

---

# 45. Owner-input boundary

Implementation should keep moving without requesting approval for every internal detail.

Ask/confirm owner input when choosing:

- final Level curve/reward values;
- synthesis/maturity thresholds;
- major rarity/mutation odds;
- final Life Phase/Rank naming;
- Ascension/endgame balance;
- major visible interaction model;
- irreversible public compatibility semantics;
- materially different product-direction forks;
- major reward depth/value policy.

Do not interrupt for:

- helper structure;
- ordinary tests;
- schema migrations;
- registry wiring;
- internal names;
- standard bug fixes;
- clear provenance/security improvements;
- mechanical refactors preserving agreed semantics.

This is a project-process rule, not merely convenience.

---

# 46. Migration from current v0.19

Incremental path:

1. Preserve current roster/Founder/Monster data model.
2. Introduce ProgressionRuleRegistry around existing canonical rules.
3. Add rule/version provenance to Life Ledger.
4. Make XP/Level materialization explicitly rebuildable from Ledger where practical.
5. Add integrity-state derivation and Doctor explanation.
6. Separate Life Phase from current overloaded Stage semantics.
7. Introduce Growth Form metadata.
8. Introduce Rank/Title and Mastery without new numeric Level ladders.
9. Convert current Achievements/Rares/Secrets to typed catalog/rule entries.
10. Add discovery-depth/reward metadata.
11. Introduce MaturityPolicy/SynthesisRecipe registry.
12. Add modifier provenance/diminishing combination.
13. Preserve current synthesis as one versioned recipe during migration.
14. Add simulator and freeze final economy only after evidence.
15. Add Ascension contract/content later without changing Level beyond 100.

No flag-day rewrite of existing creature state is required.

---

# 47. Lifecycle/progression invariants

1. One primary numeric Level 1-100.
2. Level is not age, rarity, rank, mastery or Ascension.
3. Progression comes from truthful canonical evidence.
4. No single category is required to reach L100.
5. No unbounded repeatable XP source.
6. Progression rules are versioned/provenanced.
7. Historical valid rewards are not silently rewritten by later balance changes.
8. Roster creatures retain independent durable histories.
9. Switching Beast does not destroy inactive progression.
10. Parents remain intact by default after synthesis.
11. Offspring receives a new stable identity/history.
12. Synthesis/result modifiers are recorded.
13. Rare discoveries may bend future outcomes but do not guarantee the top result.
14. Modifier stacking is bounded/diminishing.
15. Rarity is not synonymous with universally stronger.
16. Monster is a kind/path, not simply high Level.
17. Ascension is post-L100 and does not create Level 101+ by default.
18. Memories need not award XP.
19. Owner interaction does not become punitive daily-streak maintenance.
20. Reading files/source/database is not tampering.
21. Integrity checking is tamper-evident, not owner-hostile DRM.
22. Customized local progression remains usable.
23. Verified claims may require valid provenance.
24. No destructive anti-tamper.
25. Deep Easter eggs reward deliberate understanding, not accidental corruption.
26. High-tier rewards can be meaningful across many dimensions, not XP only.
27. Removing a Pack does not erase legitimately earned historical facts.
28. Community progression content cannot directly bypass canonical reward authority.
29. Final economy values are evidence-tuned, not guessed into architecture.
30. Owner consultation is reserved for consequential end-state decisions.

---

# 48. Part 7 conclusion

Beastagotchi progression should feel like a life, not a meter.

The architecture therefore keeps:

- one understandable Level;
- many orthogonal dimensions of growth;
- durable personal history;
- lineage and inheritance;
- meaningful synthesis;
- room for Monsters and Ascension;
- deep secrets and rare events;
- rewards whose significance can scale with discovery depth;
- provenance strong enough to make history meaningful;
- owner sovereignty strong enough that the machine never becomes hostile to its owner.

The next Architecture Contract Review should define the **Extension SDK, compatibility and trust contract**:
how third-party Packs/apps/plugins/providers/primitives/modules can extend Beastagotchi, what declarative
content may do, what executable extensions may do, how bounded handles/permissions work, compatibility
versioning, signatures/provenance, and how the ecosystem remains wild without allowing installed
content to silently acquire Core/root/privacy/mutation authority.
