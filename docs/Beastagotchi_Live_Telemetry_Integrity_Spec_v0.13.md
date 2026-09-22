# Beastagotchi Live Telemetry Integrity Specification v0.13

## Rule
A production chart, gauge, map, number, radar point or animation that implies measurement must be driven by **LIVE**, **DERIVED LIVE**, **PERSISTED**, or **DERIVED PERSISTED** Beast data. Synthetic values are permitted only in an explicitly labeled REPLAY / DEMO / TEST surface.

Unavailable data remains unavailable (`--`, `NO DATA`, or an equivalent theme-native treatment). Visual attractiveness is never a reason to invent a measurement.

## Provenance pipeline

`collector/service/plugin -> canonical state -> semantic/record/history layer -> widget -> renderer -> skin/layout/theme`

The Telemetry Catalog describes canonical key, label, source, quality, update age, unit, category and data kind. Widget authoring must retain that identity even when renderer/theme changes.

## Current corrected examples
- Field Map plots persisted Expedition latitude/longitude points; no decorative pretend route.
- Spectrum history stores actual per-channel observations over time.
- Recon polar renderer uses real RSSI for radius and Wi-Fi channel for angle; it does not claim physical direction.
- CPU (%) and CPU temperature (C) are separately scaled/labeled.
- Live Dashboard binds six user-selected canonical scalar sources and uses real sampled history for microtrend renderers.

## Future requirements
- long-press any widget -> source/provenance/freshness inspector;
- data-aware renderer eligibility;
- Correlation Lab with explicit axes/units;
- replay data clearly labeled and isolated from live records;
- optional confidence/freshness glyphs: LIVE / CACHED / STALE / DERIVED / OFFLINE / UNAVAILABLE.
