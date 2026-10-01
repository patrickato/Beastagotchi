# Beastagotchi Physical World / Field — Owner Refinements

**Date:** 2026-09-27
**Branch:** openai/v019-visual-reference-archive
**Status:** owner refinement to the Physical World / Environment / Location / Field capability pass

## 1. Correct primary-use assumption

Beastagotchi/Pwnagotchi should **not** be designed primarily around rural/camping/wilderness use.

The more natural operating context is RF/network-dense environments: cities, campuses, events, commercial areas, neighborhoods, travel corridors, authorized security/pentest work, and other busy AP/Internet-heavy areas.

Offline capability remains useful, but mainly as prepared support for where the Beast will operate:
- route/trip preparation;
- “I will be in this area today” prefetching;
- offline maps/reference material;
- cached software/docs/data;
- resilience when connectivity is intermittent;
- planned field/authorized-test sessions.

Do not let the product drift into “camping computer” assumptions.

## 2. Geofence automation — do not create a duplicate subsystem

The proposed geofenced automation concept should not become a separate mechanism.

If location becomes useful as a trigger later, it should feed the existing/general trigger/automation system as another condition/provider, not create a second automation model.

## 3. Dedicated location page is promising if the information is relevant

A dedicated **Where Am I?** / detailed location page is a promising concept, but it must reflect Beastagotchi/Pwnagotchi use rather than generic tourism trivia.

Avoid low-value filler such as founding date, population trivia, generic city-history snippets, etc.

Candidate useful information:
- current coordinates;
- location source (GNSS / phone / network / last-known / simulated);
- fix age and quality/accuracy where available;
- altitude/elevation and terrain context when available;
- heading/course/speed with source semantics preserved;
- local time zone / UTC offset / clock confidence;
- current map position and planned area/route context;
- Wi-Fi regulatory domain / relevant radio-region context;
- cached map/data availability for the current area;
- current nearby Beast/Pwnagotchi operational context where relevant (for example observation density or channel environment from already-authorized/current local observations), without mixing static place trivia into the page;
- relevant weather/severe alert only when useful;
- direct actions such as mark point, start/stop Expedition/session, save/export position, open map, copy coordinates, or open relevant area preparation.

Exact content should be refined later against real owner workflows and the small TFT.

## 4. Ambient light sensor — defer

Ambient-light-based behavior is not a current priority. Preserve for later hardware expansion if useful.

## 5. IMU/orientation — auto-rotate is a strong candidate

An accelerometer/IMU can provide more than generic motion sensing. Strong candidate: **automatic display orientation**.

Potential behavior:
- detect portrait vs landscape;
- rotate TFT UI accordingly;
- transform touch coordinates consistently;
- permit per-Experience preferred orientation where appropriate;
- allow owner lock/override;
- avoid constant rotation jitter with hysteresis/delay.

Some Beast surfaces may genuinely work better in portrait while others work better in landscape. This is more valuable than adding an IMU merely to expose another sensor reading.

## 6. Terrain/elevation can power richer 2.5D/3D presentation

Terrain/elevation data is not only for hiking profiles. It can make map/world presentation dynamic:
- 2.5D terrain;
- 3D map views;
- elevation-aware route/observation rendering;
- RF/coverage context where terrain matters;
- SKY/ground horizon relationships;
- richer Expedition/debrief visuals.

Keep factual elevation/terrain data separate from decorative rendering, but allow multiple presentations over the same spatial truth.

## 7. Internal evidence richness vs outbound privacy

Important owner correction:

> **For local/internal owner use, do not over-minimize diagnostic/scan/event/log evidence merely because it may be sensitive. The bigger risk during diagnosis can be omitting the one fact needed to understand what happened. Privacy minimization should become much stricter when information leaves the owner's Beast.**

Candidate rule:

> **Collect richly where justified locally; share minimally and intentionally.**

Implications:
- Doctor/Incidents/authorized scans/events may retain enough local evidence to diagnose/reconstruct what occurred;
- do not automatically strip useful fields from local evidence just because those fields would be inappropriate to upload globally;
- local retention remains owner-policy/storage-policy governed;
- secrets/credentials/private keys should still receive special handling and should not be casually duplicated into logs just because storage is local;
- export/share/global Doctor upload must pass through explicit sanitization/redaction/provenance rules;
- Global Doctor receives normalized/sanitized case data by default, not raw captures or private location/network identity;
- owner-requested exports may contain more detail when explicitly chosen.

This aligns with the Doctor principle that missing one important fact can make a diagnosis fail, while preserving strong boundaries for egress/sharing.

## 8. Resulting design correction

Physical-world/location capability should support the actual Beast operating model:

**dense-area operation + prepared offline resilience + real contextual location truth + reusable spatial substrate**

rather than assuming wilderness/camping is the primary target.

Location/environment data should feed existing Beast systems (Search, Maps, Expeditions/sessions, Doctor, radio workspaces, triggers, Homecoming/debrief, SKY, etc.) instead of spawning redundant subsystems.
