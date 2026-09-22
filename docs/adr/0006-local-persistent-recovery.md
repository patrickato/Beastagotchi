# ADR 0006 — Recovery evidence persists locally

**Status:** accepted

Backups, incident evidence, action/job history, configuration snapshots and critical recovery material must have on-device persistence. WebUI views are interfaces to this state, not the only place it exists.

Rationale: recovery must still work when the browser/network/GUI is unavailable.
