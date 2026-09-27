# Beastagotchi Cross-Layer Jam — Batch 02

Status: candidate brainstorm only. Nothing here is canon merely because it appears in this file.

Goal: deliberately search for less-obvious, cross-layer combinations that only become possible because Beastagotchi joins Pwnagotchi, Bettercap, Linux, Doctor, Search, Abilities, Device Passport, Home Base, phone companion, distributed knowledge, transactions, history, Sandbox, and provider architecture into one platform.

## Candidate combinations

1. Contextual Capability Deck — current hardware, software, location/context, task, health and connectivity determine which abilities/actions are surfaced most prominently without hiding the rest.
2. Observed-to-Procedure Promotion — repeated owner workflows can be recognized from history and offered as a saveable Procedure, without silently automating them.
3. Near-Miss Memory — failed starts, recovered devices, almost-full storage, transient undervoltage, recovered services and other near-failures become useful warning context before the next incident.
4. Session Preflight — before a substantial Pwnagotchi/Beast session, verify radios, storage, time, capture path, power, regulatory state, GPS/location source if relevant, required services and any session-specific dependencies.
5. Before/After Session Delta — compare meaningful machine and environment state before and after a session to answer what changed.
6. Hardware Trust Memory — Device Passport remembers specific USB/radio/storage hardware identities, prior roles, stability history and preferred mappings.
7. Smart Hardware Replacement — when an equivalent device replaces a failed/missing one, Beast can offer to inherit the old role/configuration rather than forcing full setup from scratch.
8. Capability Fallback Chain — one ability can have multiple Providers, such as dedicated GPS -> phone GPS -> last-known location, or speaker -> phone output -> visual notification.
9. Evidence Pinning — while Doctor or another task is running, owner can mark evidence as important so cleanup/retention policies cannot discard it.
10. Incident Capsule — one local object containing timeline, relevant logs, config diffs, screenshots, hardware state, Doctor reasoning and owner notes; rich locally, sanitizable for sharing.
11. Causal Bookmark — owner taps “it happened now” when a symptom appears, creating a high-value timestamp that Doctor aligns against logs and telemetry.
12. Temporary Deep Watch — Doctor can temporarily raise telemetry/detail for one subsystem for a bounded window, then automatically return to normal collection.
13. Heavy-Work Offload — when Home Base/PC is available, optional heavy jobs such as large indexing, conversion or map processing can execute there while remaining visible as one Beast task.
14. Hot Knowledge Cache — small frequently useful manuals/docs/fixes can be automatically retained locally based on actual use while larger source libraries remain on phone/Home Base/Internet.
15. Contextual Documentation — Help for a screen can include the exact hardware/software/current-state context instead of generic documentation.
16. Record/Replay as a First-Class Runtime Provider — recorded real sessions can feed Doctor, WebUI, Studio, UI testing and training exactly like a live machine while clearly labeled replay.
17. What Changed Since Last Known-Good — combine snapshots, System Graph, package/config/device changes and event history into a direct comparison.
18. Freshness/Confidence Decay — location, satellite data, manuals, Doctor cases, cached metadata and other provider data expose age/freshness so stale truth cannot masquerade as current truth.
19. Opportunity Detection — rules detect new capability combinations and surface one-time “you can now do X” opportunities after hardware/software/provider changes.
20. Session-Scoped Profiles — temporary bundles for a lab, authorized assessment, travel day, bench session or radio task can activate relevant settings/resources and restore afterwards.
21. Companion Rescue QR — when networking/pairing/setup goes wrong, TFT can display a QR/code that lets phone/WebUI reopen the exact failed step or Doctor case.
22. Emergency Management Path — if normal Wi-Fi/network setup breaks, provide a deliberately limited fallback management path through a supported local AP, USB gadget or Bluetooth channel where feasible.
23. Incident Short Code — TFT can show a short non-secret incident identifier; opening it on phone/WebUI jumps directly into the same Doctor/task context.
24. Recovery Island — a tiny independent recovery/control surface remains available even if the normal Beast presentation layer fails, so core status, Doctor, restore and rollback remain reachable.
25. Upgrade Rehearsal — use Beast Sandbox/Shadow Beast plus recorded patient state to rehearse risky updates/config changes before touching the physical Beast.
26. Fleet-Aware Upgrade Warning — Global Doctor can warn that a specific update/version combination has poor verified outcomes on closely matching hardware before the owner installs it.
27. Ability Provenance — every Ability can explain exactly which hardware, software, provider, config and permissions make it possible and what removing each dependency would affect.
28. Config Time Machine — managed configs can expose meaningful version history, diffs and selective rollback without hiding the raw files.
29. Procedure Receipt — after a Guided Procedure succeeds, Beast can retain a compact receipt: steps, versions, changed resources, verification and rollback point.
30. Device Notes + Passport + Doctor — owner notes such as “this Alfa hates this cable” or “screen only works with overlay X” become attached to the exact device/cohort and appear during future diagnosis.
31. Current-State Timeline Drilldown — from a present error/state, jump backward through the exact service/device/config transitions that led there.
32. Install Impact Preview — before installing/removing/updating software, System Graph can show expected abilities gained/lost, conflicts, disk cost and affected services.
33. Operational Density View — Pwnagotchi observations, radio environment, location history and session data can generate a density/context layer useful for deciding where/when a Beast session was productive without becoming a generic demographic map.
34. Adaptive TFT Action Strip — a very small contextual strip can surface the 2–4 actions most relevant to the current task/state while every other function remains reachable normally.
35. Cross-Device Continuity Token — a running task/session can be handed to phone/WebUI/Desktop by opening the same task identity, not by restarting/recreating it.
36. Failure-to-Knowledge Promotion — once Doctor verifies a local fix, the resolved case can become searchable local knowledge and optionally a sanitized Global Doctor contribution.
37. Negative Knowledge — failed fixes are retained as evidence too, so Doctor knows “this was already tried on this exact patient and made no improvement.”
38. Environment-Aware Resource Arbitration — arbitration can consider task urgency/context, not only first-come-first-served; e.g. active capture/session work outranks background indexing.
39. Owner Override with Receipt — owner can override a managed warning/resource conflict, but Beast records exactly what was overridden and the resulting outcome for later Doctor reasoning.
40. Recovery-Backed Experiment Mode — owner can intentionally try an experimental driver/plugin/config with snapshot, bounded observation and one-tap rollback rather than treating experimentation as an unsupported side activity.

## Early synthesis

The strongest new theme in Batch 02 is not another feature family. It is a platform behavior:

**Beast should remember context, preserve causality, rehearse risk, recover cleanly, and turn successful real-world use into reusable local knowledge.**

This strengthens Beastagotchi as a situationally composable machine rather than an app collection.
