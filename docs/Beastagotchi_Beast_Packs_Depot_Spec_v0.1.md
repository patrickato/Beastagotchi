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
