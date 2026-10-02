# Beastagotchi Beast Packs / Depot Specification v0.1

## Purpose
Keep the base platform stable while allowing themes, layouts, apps, integrations and optional hardware capabilities to grow without making every installation carry every feature.

## Candidate package classes
- theme / visual identity pack;
- face / animation / audio pack;
- layout / Board / Context Deck pack;
- app / tool pack;
- hardware adapter pack;
- Mission Pack;
- offline map/data/library pack;
- optional renderer/visualizer pack;
- integration pack (for example Theme Manager interoperability);
- experimental/developer pack.

## Manifest concepts
Every pack should be able to declare identity/version, compatible Beast/Pwnagotchi versions, dependencies/conflicts, required capabilities/hardware, disk footprint, background services, permissions/privilege needs, restart requirements, supported displays, and an approximate resource/thermal class.

## Lifecycle
`AVAILABLE -> DOWNLOADED/STAGED -> VERIFIED -> INSTALLED -> ENABLED` with disable/remove/update/rollback paths.

Install/update should be transactional where practical and integrated with Beast backups, config snapshots, Action Broker, Task Center, health observation and Update Center.

Inactive packs must not consume continuous compute merely because they are installed.

## Extension role metadata

Pack type remains a broad technical category. Do not create a new `pack_type`
for every product idea.

v0.19 manifests now also support:

- `extension_class`: `pack` or `companion`;
- `content_roles`: e.g. achievement catalog, trophy art, widget bundle,
  challenge catalog, capsule schema;
- `signals_provides`;
- `signals_consumes`;
- `offline_transports`;
- `capsule_types`;
- `companion.pwnagotchi_plugins`;
- `companion.beast_apps`;
- `companion.beast_packs`.

A **Companion Expansion** may therefore describe one coherent user-facing feature
whose pieces legitimately live in several subsystems without forcing all logic
into one giant plugin or Pack.

This metadata is descriptive until a dedicated activation adapter exists. It does
not cause Pwnagotchi plugin installation, service changes or code execution by
itself.

