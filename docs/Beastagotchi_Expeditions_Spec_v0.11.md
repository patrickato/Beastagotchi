# Beastagotchi Expeditions Specification v0.11

## Purpose

Expeditions make a period of real Beastagotchi use persistent rather than ephemeral. They are the future container for a trip/job/session: GPS route, encounters, captures, hardware, telemetry, notes, achievements and replay.

## v0.11 implemented foundation

- SQLite `expeditions`, `expedition_points` and `expedition_aps` tables.
- automatic Expedition start after collectors have an initial sample.
- clean/unclean restart recovery when the previous active Expedition is recent.
- stale active Expedition interruption if it cannot safely be recovered.
- GPS route points with distance accumulation and basic impossible-jump/accuracy rejection for distance calculations.
- unique AP membership per Expedition.
- captures and XP deltas from the start baseline.
- maximum CPU temperature and CPU utilization.
- minimum observed battery estimate where available.
- periodic durable checkpointing.
- durable checkpoint on Beast Core stop so controlled restarts recover the same Expedition.
- read-only `/expeditions` and `/expedition` API access.
- on-device Expedition page and Map summary integration.

## Deliberately deferred from the full design

The v0.11 page is a foundation, not the final Sessions/Expeditions experience. Still planned:

- explicit user Begin Expedition / End Expedition controls;
- name, purpose, tags and touchscreen notes;
- incidents/errors and attached hardware timeline;
- screenshots/photos/milestone cards;
- vendors, channels, locations, weather/sensor/RF layers;
- end-of-Expedition cinematic/stat recap;
- best/longest/hottest/coldest/rarest records;
- map/playback replay;
- export/share/report formats;
- Memory Vault integration.

## Safety and data integrity

An Expedition records observations and system state; it does not change RF behavior. GPS points rejected from distance because of poor accuracy or impossible speed may still be retained as raw evidence, allowing later diagnostics without corrupting the distance total.
