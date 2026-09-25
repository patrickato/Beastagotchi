# Beastagotchi Structure Deep Dive

**Date:** 2026-09-25  
**Status:** active architectural review  
**Method:** inspect current docs and actual code, preserve strengths, identify structural debt without
assuming a rewrite is required.

---

# Layer 1 — Linux/Pi, Pwnagotchi and Beastagotchi boundary

## Core structural principle: three distinct layers

Treat these as related but distinct ownership domains:

1. **Linux / Raspberry Pi platform**
   - hardware;
   - kernel/drivers;
   - filesystem/storage;
   - systemd/services;
   - networking;
   - packages;
   - thermals/power;
   - framebuffer/input devices.

2. **Pwnagotchi platform**
   - Pwnagotchi agent/runtime;
   - Bettercap relationship;
   - radio behavior;
   - Pwnagotchi plugin callbacks;
   - Pwnagotchi configuration;
   - native Pwnagotchi UI/frame;
   - Pwnagotchi session/capture semantics.

3. **Beastagotchi platform**
   - canonical Beast state;
   - Doctor;
   - progression/identity/roster;
   - Experiences/Scenes;
   - Packs/Apps/Procedures;
   - Studio;
   - Beast-managed Actions/Transactions;
   - Beast persistence/content/recovery.

A cross-layer feature may span all three, but it must not erase ownership boundaries.

Procedures and Doctor should explicitly know/report which layer a finding or Action belongs to.

---

## Three-lane Pwnagotchi boundary

### Lane A — OBSERVE

Beast may observe Pwnagotchi through supported/read-only mechanisms.

Current strong implementations:
- `pwnagotchi_plugin/beast_bridge.py` uses supported plugin callbacks and performs no Bettercap/
  radio mutation;
- bridge output is written atomically under `/run`;
- `BridgeCollector` caches unchanged JSON and gives live callback data high source priority;
- `PwnagotchiCollector` reads version/config/session/cache/plugin inventory without mutating them;
- secret-bearing config fields expose presence/type but not credential values.

Desired rule:
> Observation adapters may learn broadly, but do not acquire behavioral authority merely because
> they can see Pwnagotchi internals.

### Lane B — PRESENT

Physical display/touch ownership is a separate concern from data observation.

Current strong implementations:
- ADR 0003 requires exactly one physical presentation owner;
- `PresentationBroker` models Native / Theme Manager / Beast ownership independently;
- current executor remains disabled until physical handoff adapters are validated;
- Native Pwnagotchi Bridge consumes Pwnagotchi's own rendered frame rather than reconstructing the
  stock UI, allowing Beast to remain the display owner while preserving real upstream visuals.

Desired rule:
> Reading Pwnagotchi state, rendering a Pwnagotchi-derived view, and owning the framebuffer are
> three different permissions/capabilities.

### Lane C — MUTATE

Normal observation/plugin bridge code must not silently mutate Pwnagotchi.

Future supported changes to:
- config;
- plugin state;
- service state;
- presentation settings;
- package/dependency state;

should pass through explicit Beast Actions/Transactions with:
- plan;
- ownership/privilege check;
- backup/snapshot when relevant;
- owner consent according to risk;
- execution;
- verification;
- rollback/probation where relevant;
- audit/provenance.

Manual/root owner escape remains available outside the managed path.

---

## What is especially good today

1. **Pwnagotchi remains an upstream substrate rather than becoming a hidden Beast implementation
   detail.**
2. **The bridge is intentionally read-only.**
3. **Live callback telemetry and slower filesystem/config observation are separated.**
4. **Native UI fidelity uses the actual upstream frame rather than guessing at Pwnagotchi state.**
5. **Presentation ownership is explicit and intentionally not yet auto-executed.**
6. **Beast can evolve substantially without requiring Jayofelony/Pwnagotchi to absorb Beast-specific
   progression/UI/Doctor logic.**

These are structural strengths worth preserving.

---

## Fresh-eye concerns / improvements

### A. Formalize upstream authority per Signal

Live bridge and slower Pwnagotchi collectors can both produce related state.

Current StateRegistry priorities reduce conflicts, but authority should become explicit for important
Pwnagotchi Signals:
- authoritative source;
- fallback source;
- freshness threshold;
- historical-only source.

Example:
- live AP/channel activity -> bridge/Bettercap live provider;
- historical capture/cache metadata -> filesystem collector;
- configured plugin inventory -> config/plugin collector.

Do not rely indefinitely on numeric source priority as the only documentation of semantic
authority.

### B. Bridge event sequence restart bug-risk

`BeastBridge` starts its event sequence at zero on plugin process/reload.

`BridgeCollector` keeps a local `_last_seq`.

If Pwnagotchi/bridge restarts while Beast Core remains alive, new events may begin again at sequence
1 while the collector remembers a larger old sequence and may ignore the new events until the
sequence exceeds the previous value.

Recommended correction:
- bridge instance/session UUID;
- boot/process generation;
- or explicit sequence-regression detection/reset.

This should be test-backed.

### C. Bridge file local privacy

The bridge currently writes mode `0644` while event content may include peer identity and
AP/client identifiers.

Review whether:
- `0640` with a Beast/Pwnagotchi group;
- `0600` with matching service ownership;
- or a sanitized split between general state and sensitive event detail

is more appropriate.

The answer should preserve practical interoperability while following least-privilege principles.

### D. Upstream path/version assumptions are scattered

Current code knows Pwnagotchi-specific paths such as:
- `/etc/pwnagotchi/config.toml`;
- handshake/session directories;
- custom plugin directory;
- native frame path;
- service names.

These assumptions are valid today but vulnerable to upstream changes.

Consider a versioned **Pwnagotchi Adapter / Upstream Platform Adapter** that centralizes:
- detected Pwnagotchi version/build;
- path discovery;
- feature/callback availability;
- native-frame source;
- configuration layout;
- service identities;
- supported managed mutations;
- compatibility profile.

Beast Core modules then ask the adapter rather than each hardcoding upstream details.

This adapter should not become an authority over Pwnagotchi behavior; it is an isolation boundary
against upstream churn.

### E. Bettercap/radio behavioral ownership must stay clear

Pwnagotchi owns normal radio/agent behavior.

Beast may:
- observe;
- diagnose;
- display;
- restart/recover through explicit Actions where appropriate.

The telemetry bridge itself should never become a covert Bettercap command channel.

If future Lab/advanced functionality intentionally controls radio behavior, it should be a separate
explicit capability/mode with its own authority, consent and audit—not an expansion of the read-only
bridge.

---

## Structural direction

Preferred relationship:

    Linux / Pi
        |
        +-- Pwnagotchi
        |      |
        |      +-- read-only callbacks / native frame / config evidence
        |      |
        |      +-- managed mutation adapters (only through Actions/Transactions)
        |
        +-- Beast Core
               |
               +-- canonical State / Signals / Events
               +-- Doctor / Procedures
               +-- Experience / Scene / UI / Studio

Possible isolation seam:

    Pwnagotchi Adapter
        |- version / compatibility
        |- paths / service identities
        |- observation sources
        |- native-frame source
        |- supported mutation adapters
        |- health evidence

The adapter should make upstream changes cheaper without turning Pwnagotchi into a Beast-owned
implementation detail.

---

## Layer-1 questions to carry forward

- Which Pwnagotchi data is truly canonical versus merely evidence/fallback?
- Which mutations should Beast ever support as managed Actions?
- Should the read-only bridge remain a file contract permanently, or gain an optional event-stream
  transport while retaining the file as a robust fallback?
- How should Pwnagotchi compatibility profiles be versioned/tested against upstream releases?
- What should Doctor be allowed to repair automatically versus only recommend?
- How do owner manual edits get detected and incorporated into known-good/customized state?

