# Beastagotchi Architecture Contract Review — Part 5: Runtime & Resource Contract

**Date:** 2026-09-25  
**Status:** proposed architecture contract  
**Goal:** make "fat ecosystem, thin runtime" enforceable.

---

# 1. Resource philosophy

Beastagotchi may know about/install a very large ecosystem.

The active runtime working set must remain small.

> **Known != installed != enabled != active != resident.**

Heat, CPU, memory, SD writes and render cost are real product resources.

The ResourceGovernor is a safety/optimization authority, not a substitute for efficient design.

Normal operation should be efficient enough that permanent throttling/load-shedding is unnecessary.

---

# 2. ModuleRuntime owns recurring work

No new subsystem should create an untracked permanent loop directly in Core.

A Module declares how it runs.
ModuleRuntime/Scheduler owns:
- wakeups;
- cadence;
- timeouts;
- cancellation;
- backoff;
- governor scaling;
- lifecycle ordering;
- health;
- runtime telemetry.

Existing loops can be wrapped incrementally.

---

# 3. Execution modes

A Module may be:
- periodic;
- event_driven;
- signal_driven;
- on_demand;
- startup;
- idle_maintenance;
- dormant_until_capability.

Prefer event/signal/on-demand operation where practical.

Polling remains appropriate for hardware/OS facts that have no better event source.

---

# 4. Resource classes

Exact names can evolve, but the semantic classes should remain stable.

## critical_control
Examples:
- Core health;
- thermal/power safety evidence;
- Action/Transaction recovery;
- presentation ownership safety;
- essential Pwnagotchi bridge truth.

Properties:
- guaranteed minimum scheduling;
- never disabled merely for cosmetic thermal relief;
- strict timeout/error policy.

## operational_live
Examples:
- radio state;
- GPS;
- essential provider health;
- touch/input;
- current presentation data.

Properties:
- freshness matters;
- cadence may reduce only inside declared limits;
- interactive input receives latency priority.

## derived
Examples:
- topology;
- overview synthesis;
- compatibility calculation;
- search indexing;
- aggregate analytics.

Properties:
- can run less frequently under pressure;
- stale-but-labeled output is preferable to heat.

## background_optional
Examples:
- Depot refresh;
- preview generation;
- inactive content indexing;
- decorative enrichment.

Properties:
- can pause entirely;
- should normally be dormant when not useful.

## ambient_visual
Examples:
- particles;
- glow animation;
- nonessential cinematic layers.

Properties:
- first visual workload shed;
- never blocks input/state/Doctor truth.

Do not let a Module self-declare "critical" without trusted registration policy.

---

# 5. Freshness contract

Each Module/Signal may declare:
- normal cadence;
- minimum cadence;
- expected freshness;
- stale threshold;
- hard maximum execution time.

Governor/Scheduler may stretch cadence only within allowed bounds.

If freshness cannot be maintained:
- State quality becomes stale/degraded;
- consumers are told honestly.

---

# 6. Budget dimensions

Resource policy should eventually reason about:
- CPU time;
- wall-clock tick duration;
- wakeups/sec;
- memory/RSS;
- decoded asset/cache bytes;
- framebuffer/render time;
- disk writes;
- SQLite/WAL growth;
- network bandwidth;
- temperature/throttle evidence;
- optional battery/power state.

Do not invent false precision where Linux cannot attribute cost accurately.

---

# 7. Scheduler behavior

For each Module, Scheduler tracks:
- last start/end;
- duration;
- overrun count;
- next eligible run;
- failures;
- backoff;
- health;
- governor-adjusted cadence;
- wake reason.

Rules:
- one slow Module does not block unrelated Modules;
- external/subprocess work is timeout-bounded;
- blocking calls use appropriate worker/thread/process boundary;
- repeated failure triggers bounded backoff;
- critical failure becomes Doctor/Incident evidence;
- runaway retry loops are forbidden.

---

# 8. ResourceGovernor contract

Governor consumes resource/health Signals.

Governor publishes policy such as:
- global pressure level;
- budget percentage;
- visual detail allowance;
- cadence multipliers;
- cache budget;
- background/ambient allowance.

Current `FULL/GUARDED/REDUCED/SURVIVAL` modes are a valid implementation but **not sacred contract names**.

The stable contract is:
- pressure can escalate quickly;
- recovery uses hysteresis;
- critical/control work retains service;
- optional/ambient work is reduced first;
- policy is observable/explainable.

---

# 9. Thermal behavior

Target:
> prevent sustained thermal pressure rather than merely report throttling after it happens.

Reduce optional work before operational truth.

Doctor should distinguish:
- transient warm;
- sustained hot;
- actual throttle;
- historical throttle.

---

# 10. Interactive priority

Human interaction gets temporary latency priority.

Touch/gesture handling:
- is operational_live/latency-sensitive;
- may preempt/delay optional indexing/preview work;
- should acknowledge input visually before expensive secondary work.

A touch should never feel laggy because Depot is refreshing thumbnails.

---

# 11. Render contract

Render only when:
- relevant Signal changes;
- interaction changes;
- animation cadence requires;
- transient/cinematic state advances.

Scene dirty regions should eventually drive partial composition before full-frame generation.

Framebuffer dirty-row/span comparison remains the final physical output safety net.

A static page should not redraw merely because an FPS ceiling exists.

FPS is a ceiling, not a command to render.

---

# 12. Display cadence

Do not model the SPI TFT as a desktop 60/120 Hz display.

DisplayProfile should expose measured:
- full-frame write cost;
- typical dirty write cost;
- practical animation cadence;
- pixel format/geometry.

RenderScheduler adapts to the real physical target.

---

# 13. Asset/runtime memory budget

Future cache should be byte-budgeted rather than only entry-count bounded.

Track:
- decoded bytes;
- object id/hash;
- target size;
- decode cost;
- last use;
- active references;
- pinned/warm state;
- cache hit/miss.

Evict cold/reproducible content first.

Never evict the active Surface's required assets in a way that causes visible thrashing.

---

# 14. Working-set rule

Default UI working set:
- active Experience;
- active Surface stack;
- immediate navigation neighbors where useful;
- declared Signals;
- required fonts/primitives;
- current transient/cinematic assets.

Not:
- every installed Experience;
- every face;
- every graph history;
- every Pack.

Inactive content stays cold.

---

# 15. Lazy loading

Prefer:
- asset load on first need;
- Scene compile on demand;
- Signal subscription while Surface is active;
- release subscriptions/cache after inactivity;
- dormant Modules until Capabilities exist.

Avoid import-time side effects.

---

# 16. Signal/event transport

Normal TFT live path should migrate toward:
- initial full snapshot;
- WebSocket state patches/events;
- HTTP history/bulk on demand;
- full resync on sequence gap/reconnect.

Event subscribers should be bounded and observable:
- queue depth;
- drops;
- lag.

A slow optional subscriber must not stall Core.

---

# 17. Disk/SD policy

Use:
- batched samples;
- SQLite WAL;
- measured checkpoint policy;
- bounded logs;
- `/run`/tmpfs for ephemeral state;
- change-gated writes;
- slow indexing cadence;
- immutable/content-addressed assets where useful.

Do not write high-frequency telemetry to SD merely because it exists in RAM.

---

# 18. SQLite runtime contract

Keep SQLite.

Define:
- connection ownership/concurrency;
- ordered migrations;
- WAL checkpoint policy;
- bounded transaction durations;
- backup-safe snapshot API.

Fix current Action worker-thread connection risk before expanding mutation systems.

---

# 19. Studio preview budget

Studio preview is optional relative to physical TFT interaction.

Policy:
- coalesce rapid requests;
- latest generation wins;
- cancel/ignore obsolete work;
- bounded render worker;
- reuse static assets/context;
- governor may reduce preview cadence/quality;
- multiple browser clients cannot create unlimited parallel compositor work.

---

# 20. Choreography/cinematic budget

Cinematics are meaningful but not sacred to system health.

Each Choreography has:
- resource class;
- reduced-motion fallback;
- lightweight fallback;
- optional media components.

Under pressure:
- preserve the semantic event/reward;
- fall back to cheaper presentation.

---

# 21. Power awareness

Where available, resource policy may consider:
- battery estimate;
- external power;
- low-power state.

Unknown power state stays unknown.

Optional work may reduce before operational truth.

---

# 22. Module dormancy

An enabled Module with no current need may be dormant.

Expose:
- enabled;
- active;
- dormant reason;
- last active time.

Dormancy is healthy, not failure.

---

# 23. Health / Doctor

ModuleRuntime emits generic health:
- healthy;
- starting;
- dormant;
- degraded;
- failed;
- backoff;
- stopped.

Doctor interprets domain meaning.

Scheduler does not contain domain diagnosis.

---

# 24. Performance observability

Expose compact telemetry:
- tick duration;
- overruns;
- failures/backoff;
- render/compose/write times;
- cache bytes/hit rate;
- network/download activity;
- WAL/db sizes;
- governor state/reasons.

Do not make performance telemetry itself expensive.

---

# 25. CI/resource gates

Add regression coverage for:
- frame render budget;
- dirty-region behavior;
- static-page no-redraw;
- cache budget/eviction;
- Module timeout/backoff;
- governor scaling;
- WebSocket patch/resync;
- preview coalescing.

Physical Pi tests remain necessary for real thermal/input truth.

---

# 26. Runtime invariants

1. Known/installed content does not imply active resource use.
2. Interactive input outranks optional/background work.
3. Critical/control work cannot be starved by visual policy.
4. Stale data is labeled stale rather than silently reused as live.
5. Static Surfaces do not redraw without cause.
6. Optional Modules may sleep completely.
7. Resource pressure sheds ambient/background work before operational truth.
8. Runtime cache limits are byte-aware.
9. Preview/background clients cannot monopolize the Pi.
10. Governor decisions are observable and reversible with hysteresis.
11. Physical measurements, not desktop assumptions, define TFT cadence.
12. No subsystem may create uncontrolled retry/wakeup loops.

