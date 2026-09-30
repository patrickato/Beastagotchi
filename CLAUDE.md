# CLAUDE.md — Beastagotchi

Guidance for any AI (or human) working in this repo. Read it before making changes.
Keep it current when conventions change.

## What this is

Beastagotchi is a pre-1.0 Raspberry Pi field-computer environment built **around** a
protected Pwnagotchi/Bettercap engine — not a fork of it. Target hardware: **Pi 4 +
3.5" MPI3501 TFT (480×320, ILI9486 / ADS7846 touch)** on the **jayofelony 64-bit
pwnagotchi image**, plus a Waveshare UPS 3S and USB GPS. Runtime baseline: **v0.18.1**;
active development line: **v0.19 (Unified Experience)** on branch `integration/v0.19`.

## Golden rules (violating these is how the project gets hurt)

1. **Pwnagotchi stays protected (ADR-0001).** Beast Core *consumes/adapts* Pwnagotchi,
   Bettercap, Linux and hardware state. It does not patch the engine, issue Bettercap
   commands, change radio behavior, or alter Pwnagotchi. `pwnagotchi_plugin/beast_bridge.py`
   is **read-only** telemetry only.
2. **No silent scope loss (ADR-0007).** Approved ideas are implemented, deferred,
   experimental, or explicitly retired *with a reason* — never quietly dropped. This
   applies to data too: never auto-delete durable records (expeditions, GPS coverage
   points, captures, BeastDex, progression). Retention prunes only churny operational
   logs (see `Store.prune_operational`).
3. **One active development line.** Do **not** create long-lived parallel branches that
   never merge back. (v0.19 once fragmented into 14 divergent branches with half the code
   stranded; every branch head is preserved as an `archive/<name>` tag if you need history.)
   Work on `integration/v0.19`, merge to `main` when validated.
4. **Live data first.** Production views represent real, persisted, or explicitly
   "unavailable" data — never decorative fake telemetry.
5. **TFT is the cockpit; WebUI is the workshop (ADR-0004).** Fast/readable on the device;
   deep configuration/editing belongs in Beast Studio (the browser surface).

## Architecture

- **`beastcore/`** — the engine-adjacent runtime. Single asyncio event loop orchestrates
  ~19 collectors (offloaded to threads via `asyncio.to_thread`) and ~18 engine loops.
  - `state.py` — `StateRegistry`: flat `key -> StateValue` map with **source-priority
    arbitration** and freshness (`live`/`stale`/`unavailable`). This is the spine.
  - `events.py` — `EventBus` pub/sub (bounded history + asyncio.Queue subscribers).
  - `db.py` — SQLite (WAL) durable store: events, samples, wifi_encounters, expeditions,
    captures, incidents, jobs, library+FTS5, beast progression/BeastDex.
  - `collectors/` — uniform `Collector.collect() -> dict`, per-class poll intervals.
  - `actions.py` + `action_server.py` — the audited **Action Broker** (privileged ops:
    plugin toggle, service restart, container control, backups) over a **Unix socket**.
  - `governor.py` — thermal governor (sheds optional work at 70/76/80 °C, before the Pi's
    own throttle; hysteresis on recovery).
- **`beastui/`** — the physical UI. Composes on a fixed **480×320 logical canvas**, then
  `DisplayTransform.to_physical()` letterboxes/scales to the real panel. `framebuffer.py`
  does a dirty-row RGB565 diff over SPI. `engine.py` is the compositor + touch router +
  ~20 overlays (large file). 20 JSON themes in `beastui/themes/`.
- **`beaststudio/`** — responsive local WebUI + action client. Talks to the Action Broker
  over the Unix socket; the web layer itself never execs commands.
- **`pwnagotchi_plugin/beast_bridge.py`** — the small read-only bridge that writes
  Pwnagotchi telemetry/events to `/run/beastagotchi/pwnagotchi_bridge.json`;
  `beastcore/collectors/bridge.py` reads it.

## Gotchas specific to this stack

- **This fork's plugin loader does NOT merge `__defaults__`.** Any pwnagotchi plugin (incl.
  beast_bridge) must read every option defensively; do not rely on `__defaults__` fallback.
- **Config section name = the plugin file's exact basename** (case-sensitive), under
  `[main.plugins.<basename>]`.
- **`StateRegistry` deep-copies values on every read and write** (`get`/`snapshot`/
  `update_many`). `wifi.aps` (the full AP list) lives in state, so this is a known
  CPU/thermal hot spot — a fix must be an opt-in shallow path, not a global removal
  (200+ call sites rely on receiving private mutable copies).
- **Operator privilege tiers are defined but not yet enforced** in `ActionBroker.perform`
  (a known hardening item). Authorization currently reduces to Unix-socket group perms.

## Running the tests

No `conftest.py`; the import root is the repo root. From the repo root:

```bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
python -m compileall -q beastcore beastui beaststudio
bash -n install.sh install_ui.sh install_bridge.sh uninstall.sh validate_v018.sh
```

~117 test files. **3 tests need the optional `qrcode` package** (`test_v019_capsule_*`); if
`qrcode` isn't installed they fail with "QR renderer dependency is not installed" — that's
environmental, not a regression.

## Validation model (docs/TESTING.md)

Three tiers, kept distinct: **(1) source/CI** (imports, deterministic logic, parsers,
render generation — this is what pytest covers); **(2) target off-screen** on the real Pi
via `validate_v*.sh` without touching the live display owner; **(3) physical interaction
gate** — readability/touch on the real screen, which automated tests can't prove. Never
claim hardware behavior from a sandbox pass; label what's sandbox-verified vs
needs-hardware.

## Docs & source of truth

`docs/` keeps versioned specs (many superseded versions retained because installers
reference exact names — see `docs/REPOSITORY_MAP.md` before reorganizing). Current pointers
live in `ROADMAP.md`; superseded branch-only design docs are archived under
`docs/archive/from-branches/`. The completion matrix + continuity ledger are the
anti-forgetting record.

## Sibling repos

- `patrickato/plugins-wip` — rebuilt custom plugins staged before graduation (has its own CLAUDE.md).
- `patrickato/test-plugins` — the third-party plugin audit (has its own CLAUDE.md).
- `patrickato/complete-plugins` — graduation target for finished plugins.

## Commits

Branch off `integration/v0.19` (or `main` only for hotfixes). Keep commits focused with a
clear message. AI-authored commits carry a `Co-Authored-By:` trailer for the model that
made them. Don't rewrite published history; don't force-push shared branches.
