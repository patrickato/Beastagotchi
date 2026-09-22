# ADR 0001 — Protect the Pwnagotchi engine

**Status:** accepted

Beastagotchi treats Pwnagotchi/Bettercap as protected underlying engines. Prefer read-only callback bridges, collectors/adapters and defined control interfaces over repeated patches inside Pwnagotchi internals.

Rationale: upgrades remain possible, failures are easier to isolate, and Beastagotchi can evolve independently.
