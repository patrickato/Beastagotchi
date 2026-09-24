# Beastagotchi Doctor — Cross-Pollination from a Pwnagotchi Doctor Plugin

**Status:** external-collaborator note (findings + recommendations, not a spec change)
**Date:** 2026-09-24
**Author:** Claude (working with the owner on a separate, Pwnagotchi-only "gap plugins" project)
**Scope:** insights for `beastcore/doctor.py` (`BeastDoctor`) and `beastcore/incidents.py`
(`IncidentEngine`), left here for the owner and the owner's other AI to integrate.

> Provenance / boundaries: I wrote this while building an autonomous **Doctor plugin for
> stock Pwnagotchi** (a different repository). The plugin is deliberately *not* Beast — it is
> for the plain Pwnagotchi atmosphere. This note only shares patterns and opinions that could
> strengthen Beast's own Doctor. It respects Beast's rules: it is source/CI reasoning only, it
> does not claim physical acceptance, and every remediation idea below stays behind Beast's
> owner-authorized Operator / Action Broker gating and the standing rule that *automatic
> failover/remediation remains disabled until separately validated*. Edit, relocate or archive
> this under `docs/` per `REPOSITORY_HYGIENE.md` as you see fit.

---

## 1. What each side built (they are complementary halves)

Reading `docs/Beastagotchi_Doctor_Explain_v0.1.md`, `beastcore/doctor.py` and
`beastcore/incidents.py`, Beast's Doctor is an **Explain engine** and its IncidentEngine is a
**Black Box**. The Pwnagotchi plugin I built is a **Detect-and-Treat engine**. They solve
opposite, complementary halves of "healing":

| Axis | Beast Doctor (this repo) | Pwnagotchi Doctor (the plugin) |
|------|--------------------------|--------------------------------|
| Core question | *Why is this the way it is, and what breaks if it changes?* | *What is wrong, and can I safely fix it right now?* |
| Method | Causal/graph reasoning over providers, capabilities, dependents, blast radius | Broad structured sensors → condition knowledge base → tiered auto-fix |
| Acts? | No (read-only; automatic failover intentionally disabled) | Yes — tiered, verified, reversible, allow-listed |
| Strength | Honesty, explanation, blast-radius, dependency truth | Autonomy, actual repair, verification loop |
| Weakness | No "treat" half wired yet | No dependency graph → no blast-radius awareness |

**Thesis:** Beast already has the harder, more valuable half (truthful causal explanation over
a real dependency graph). It is missing only the disciplined **treat** half — and the plugin
is a working reference for exactly that half, built to be compatible with Beast's own
"Explain-before-act" flow.

---

## 2. Recommendations for Beast (ranked)

### R1 — Wire a tiered, verified, allow-listed *treat* half onto the existing Explain engine
Beast already has the primitives: `beastcore/actions.py` / `action_server.py` (Action Broker),
`operator_policy.py` / `operator_sessions.py` (owner-authorized tiers), `governor.py`
(Resource Governor) and `incidents.py` (Black Box). What's missing is the loop that turns a
Doctor finding into a *bounded, reversible* action. The plugin implements this loop and it maps
1:1 onto the flow already written in `Beastagotchi_Doctor_Explain_v0.1.md`:

`Explain → Plan → Preview impact → Snapshot → Execute → Observe probation → Rollback/accept → Record`

Concretely, each remediation is: **allow-listed action** (no arbitrary shell) → **circuit
breaker** (stop after N attempts/window) → **snapshot** → **execute via Action Broker** →
**re-collect + re-detect to verify the condition cleared** → **accept or roll back** → **write
an incident outcome**. Keep default posture = *notify/observe*; auto-execute only the safest,
reversible actions, and only when the owner has enabled it. This is the single biggest addition
Beast's Doctor could make, and it reuses machinery you already have.

### R2 — Gate every action on evidence confidence (a truth rule, made executable)
Your `Doctor_Explain` doc already states the right principle ("a recommendation is not an
executed action"; readiness ≠ health). Make it *mechanical*: attach a `confidence`
(`high | medium | low`) to every Doctor item/incident condition, where **high** = direct live
StateRegistry evidence, **medium** = derived, **low** = log/heuristic inference. Then the
Action Broker **refuses to auto-execute any low-confidence finding** — it may only explain it.
The plugin does exactly this and it is the rule that makes autonomous fixing trustworthy.

### R3 — Adopt a shared, data-driven **condition-pack schema**
Both Doctors benefit if "ailments" are *data*, not code — so pwnagotchi, Beast, and the
community can contribute symptoms/causes/fixes without patching a diagnosis engine, and so a
condition authored once can (where signals overlap) serve both projects. Proposed neutral
schema (see §3). Beast's `IncidentEngine._conditions()` and `BeastDoctor` recommendations could
both be re-expressed as condition packs over canonical state keys.

### R4 — Add the verification/probation + circuit breaker to IncidentEngine actions
`IncidentEngine` already does the hard part well: open/resolve lifecycle, severity, and a
**black-box snapshot at open time** (I copied this pattern wholesale — it's excellent, as is the
uptime-gating that suppresses boot-time false alarms). When actions arrive (R1), reuse that same
open/resolve/snapshot machinery to record *attempted fix → probation window → verified
resolved or rolled back*, so the Black Box captures not just failures but the healing.

### R5 — Build "What changed since known-good?" (highest leverage, already on your list)
This is the best unbuilt feature on either side and your `Doctor_Explain` doc already names it.
For Beast it's very buildable from canonical state: fingerprint `{packages, services, enabled
plugins/Packs, providers, hardware, versions, owner customizations, config hash}` at a
user-blessed checkpoint, then diff on demand. "Since your known-good checkpoint, gpsd changed
version and PwnDroid became the preferred Location provider" beats "something broke" every time.
It also makes remediation *safer*: the safest fix is often "revert to the last known-good state
of exactly this component."

### R6 — Use Beast's dependency graph for **blast-radius preview before acting** (your superpower)
The plugin can restart a service but has no idea what depends on it. Beast does. Before any
Action Broker execution, surface the blast-radius the Explain engine already computes
(`used_by`, `dependent_count`, `if_active_provider_is_lost`) as a **pre-action confirmation**:
"This will affect 4 consumers; USB GPS can cover 3; 1 feature has no alternate." No pwnagotchi
plugin can do this; it is Beast's structural advantage and should gate risky actions.

### R7 — Keep readiness labels tied to real runtime probes (a caution)
Building the plugin re-taught me the "readiness ≠ health" trap you already warn about. My honest
worry for Beast: the label vocabulary (`ready_unverified`, `standby_ready`, `needs_attention`,
`blocked`, `unavailable`) is good, but it multiplies quickly, and a label that isn't backed by a
real probe becomes exactly the invented confidence the doc forbids. Suggestion: require every
non-`unknown` health label to name the evidence source that produced it, and let Doctor render
`unknown` proudly rather than guessing.

### R8 — Keep the field status vocabulary identical across both Doctors
Your `Doctor_Explain` field-mode set (`OK / ATTENTION / DEGRADED / ACTION REQUIRED`) is good; I
adopted it verbatim in the plugin. Keeping them identical means shared UI logic, shared
condition packs, and a consistent owner mental model whether they're on plain Pwnagotchi or
Beast.

---

## 3. Proposed shared condition-pack schema (for R3)

A neutral JSON that a diagnosis engine on either side can load. Signals are referenced by
canonical key so Beast can bind them to its StateRegistry and the plugin to its collectors.

```json
{
  "id": "storage.root_readonly",
  "severity": "critical",
  "confidence": "high",
  "signals": ["storage.root.readonly"],
  "detect": {"all": [{"key": "storage.root.readonly", "is": true}]},
  "symptom": "root filesystem is mounted read-only",
  "cause": "the SD card hit an error and Linux remounted / read-only; writes fail silently",
  "fix": {
    "action": "storage.remount_rw",
    "tier": "risky",
    "reversible": true,
    "verify": {"key": "storage.root.readonly", "is": false}
  },
  "howto": [
    "Back up now — a read-only remount usually means the SD is failing.",
    "sudo mount -o remount,rw /",
    "Reflash to a fresh, reputable SD card soon."
  ],
  "causal_chain": ["storage.sd_errors"]
}
```

Notes:
- `detect` is a tiny boolean tree over canonical keys (`all` / `any`, comparators `is`, `>=`,
  `<`, `contains`). It stays pure and testable; no code ships in a pack.
- `fix.tier` (`safe | risky`) + top-level `confidence` drive the R1/R2 gating: auto-execute only
  `safe` + non-`low`, everything else is explain-only unless the owner escalates.
- `fix.verify` is the probation check (re-read the key after acting).
- `causal_chain` lets the engine collapse related findings into one human sentence
  (the plugin ships a small set: "rfkill-blocked → no monitor → no captures", etc.).
- Beast's `IncidentEngine` conditions (service down, root RO, disk full, thermal, display
  conflict) are already essentially this shape — formalizing them as packs is a small refactor.

---

## 4. Reference implementation (free to lift)

The working plugin is `pwnagotchi-plugins/doctor.py` in `patrickato/test-plugins` (branch
`claude/happy-newton-60zxt8`). Both projects are GPLv3, so patterns/code are freely reusable
with attribution. What's there today:

- **22 conditions** across services, power/throttle (`vcgencmd get_throttled` bits),
  disk + **read-only-root**, `dmesg` signatures (under-voltage, USB resets, OOM, SD I/O errors,
  wifi firmware), `config.toml` validity, bettercap API reach, monitor interface, rfkill, clock
  (year + NTP-sync), memory/swap, route/DNS, temperature, and log signals.
- **Confidence per condition**, with low-confidence findings never auto-fixed (R2).
- **Tiered allow-listed actions** with **circuit breaker**, **snapshot**, and **verify by
  re-detect** (R1/R4).
- **Incident open/resolve lifecycle + black-box snapshot** and **boot uptime-gating** — patterns
  I copied from your `IncidentEngine` (credit to Beast).
- **Causal chains** and the **OK/ATTENTION/DEGRADED/ACTION** field vocabulary (R6/R8).
- ~35 off-Pi unit tests (fake-adapter harness; source/CI evidence only, no physical acceptance).

---

## 5. One-paragraph summary for the other AI

Beast's Doctor is ahead on the part that matters most — truthful causal explanation over a real
dependency graph — and only needs the disciplined *treat* half bolted on, which the Action
Broker / Operator tiers / Governor / IncidentEngine already make possible. The safe path is:
express conditions as data (shared schema), attach an evidence-confidence to each, and let the
Action Broker auto-execute only `safe` + high/medium-confidence + reversible fixes behind the
Explain→Preview→Snapshot→Execute→Probation→Rollback→Record flow you already wrote — using the
dependency graph for blast-radius preview and keeping every health label tied to a real probe.
Build "what changed since known-good?" first; it makes both diagnosis and the safest remediation
("revert this one component") fall out for free.
