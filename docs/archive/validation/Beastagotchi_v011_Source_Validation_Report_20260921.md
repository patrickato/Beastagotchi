# Beastagotchi v0.11.0 — Source / Clean-Package Validation Report

**Date:** 2026-09-21  
**Gate:** source/off-screen release candidate  
**Physical Pi gate:** NOT YET RUN

## Result

PASS for the source and clean-package gate.

The v0.11.0 release tree was packaged, extracted into a fresh directory and validated from the extracted copy rather than only from the development tree.

## Checks passed

- Python compile/import gate for Beast Core, Beast UI, tests and tools.
- `beastcore.__version__ == 0.11.0`.
- `beastui.__version__ == 0.11.0`.
- Shell syntax gate for top-level, display-handoff and tool shell scripts.
- Complete automated suite: **99 passed**.
- v0.11 validation gallery: **23 frames**, all 480×320 and nonblank.
- Structural-theme/page regression is included in the automated suite.
- Package excludes development caches (`.pytest_cache`, `__pycache__`, `*.pyc`).
- `validate_v011.sh` asserts the v0.11.0 runtime versions.

## Pre-release defects caught and corrected

### Historical throttle flag handling

Raspberry Pi `get_throttled` historical bits were separated from current bits. A past undervoltage/thermal event can remain visible as history without falsely pinning the live UI in SURVIVAL.

### Controlled Expedition restart semantics

The first draft finalized the active Expedition on a normal Beast Core service stop, which contradicted the physical gate requirement that a controlled service restart recover the same Expedition. Beast Core now checkpoints the active Expedition without ending it. A restart inside the recovery window resumes the same Expedition ID; explicit end controls remain future work.

### v0.11 target validator version assertion

The first v0.11 validator draft still asserted module version 0.10.0. The validator now correctly requires Beast Core and Beast UI 0.11.0.

## Physical gate still required

Source validation cannot prove TFT appearance, resistive-touch behavior, real thermal recovery, actual GPS route growth, live Pwnagotchi/Bettercap coexistence or physical display handoff. Those remain the purpose of `Beastagotchi_v011_Experience_Gate.md` and the physical validation bundle.

Do not treat this report as physical sign-off.
