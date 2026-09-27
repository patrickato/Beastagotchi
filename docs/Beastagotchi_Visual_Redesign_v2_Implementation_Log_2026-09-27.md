# Beastagotchi Visual Redesign v2 — Implementation Log

**Date:** 2026-09-27  
**Branch:** `openai/v019-visual-redesign-v2`

## Purpose

Turn the visual reconciliation into a real, testable substrate before asking the owner to approve a visual direction.

## Locked design rule

**Shared Beast shell = fixed semantic contract.**  
**Experience body = creative freedom.**  
**Customization = themes/assets/faces/layout Packs within truth and readability contracts.**

The same underlying truth may be translated differently by Atlas, Forge, Observatory, Habitat and Monolith, but must not change meaning.

## Tranche 1 — shared semantic shell

Implemented:

- `beastui/beast_shell.py`
  - truth-preserving `Reading`
  - explicit quality states: live/captured/stale/estimated/unknown/unavailable/error
  - unknown values do not silently become zero
  - shared attention ladder
  - shared Experience navigation model with >=48 px touch targets
  - legibility-first shell type ramp
  - shared status sentence builder
- `beastui/experience_registry.py`
  - injects one `BeastShellModel` into every Experience render state as `_beast_shell`
  - no visual body is forced to adopt a common layout
- `tests/test_visual_shell_v019.py`
  - unknown-vs-zero regression
  - stale reading provenance/quality
  - radio-stack failure attention
  - critical thermal attention
  - touch-sized navigation geometry
  - truth-safe status sentence

## Next step

Use Monolith as the first semantic consumer because its restrained body makes truth/readability regressions easiest to see. Do not use this as an aesthetic endorsement of Monolith.

Then render a multi-state matrix (healthy / unknown / degraded / radio-offline / critical thermal) and only after that propagate shared shell consumption to the other four Experiences.
