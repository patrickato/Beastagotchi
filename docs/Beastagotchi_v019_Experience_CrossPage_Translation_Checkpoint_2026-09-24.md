# Beastagotchi v0.19 — Experience Cross-Page Translation Checkpoint
## 2026-09-24

Status: off-screen architecture/visual evidence only. Not owner visual acceptance and not physical TFT acceptance.

## What this proves

Experience DNA now changes page language beyond Home.

The same sanitized real target state is rendered through two different Experience families across two pages each:

- Atlas Home -> Atlas Recon / Field Survey
- Observatory Home -> Observatory Spectrum Lab

The pair stays structurally and semantically different rather than falling back to a generic shared dashboard.

## Atlas translation

Atlas Recon is a field survey rather than a target/radar fantasy.

- AP channel/RSSI observations drive a relative RF diagram;
- the diagram is explicitly labelled `NOT RANGE OR POSITION`;
- GPS remains `SEARCHING` because the fixture has no fix;
- no location, bearing or range is fabricated;
- field session, bands, handshake/hidden counts and position truth remain compact supporting facts.

Atlas therefore preserves its field/spatial identity while moving from Home to Recon.

## Observatory translation

Observatory Spectrum is a measurement lab rather than a field-survey page.

- current AP observations produce channel occupancy bars;
- current tuned channel is marked from the real radio signal;
- strongest observed AP and handshake-AP count are derived from the same captured state;
- source quality/provenance remains visible;
- the footer explicitly states `NO INVENTED TIME SERIES`.

Observatory therefore preserves a scientific/evidence-first identity while translating into Spectrum.

## Registry / Studio integration

Added `beastui/experience_registry.py` as the central renderer registry.

Current renderer coverage:

- Atlas: Home, Recon
- Forge: Home
- Observatory: Home, Spectrum
- Habitat: Home
- Monolith: Home

Missing page renderers fail explicitly rather than silently falling back to a generic page.

Beast Studio schema now exposes renderer coverage, and a paired-token `/api/experience-preview` endpoint can render a registered Experience page from live canonical state without treating the Experience as a Theme.

## CI evidence

Artifact `v019-experience-page-translations` contains:

- `atlas_home.png`
- `atlas_recon.png`
- `observatory_home.png`
- `observatory_spectrum.png`
- `comparison.png`
- semantic SceneRuntime manifest.

## Next

1. Preserve these proofs as architecture references, not final art.
2. Improve Atlas edge-instrument integration and Observatory visual polish without converging their geometry.
3. Translate Habitat into progression/memory/Expedition next to prove a non-instrument-heavy cross-page Experience.
4. Build the Experience Compiler/runtime selection path before production TFT ownership.
5. Keep physical Gate 1 staging blocked until actual off-screen Experience direction is accepted.