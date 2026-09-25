# Beastagotchi v0.19 — Concept Fidelity / Layered Scene Contract

## Why this exists

The 2026-09-24 visual review exposed a product-level mismatch: the actual 480×320 renderer was technically healthy but visually read as a collection of static cards, small image tiles and procedural line effects. Earlier concept work communicated a richer living field-computer/creature experience.

This is not treated as a request for more palette work. It is an architectural presentation correction.

## Rule

A theme may still provide palette, geometry and lightweight background effects, but high-value experience surfaces may use a **layered scene composition**:

1. environment / full-canvas visual layer;
2. creature / identity art layer;
3. ambient motion and lighting;
4. truthful live-data HUD layer;
5. interaction/navigation layer;
6. protected machine-readable and rare/reveal layers.

Telemetry must remain canonical Beast state. Decorative motion must never pretend to be measured data.

## Anti-regression rules

- Do not force concept art into small bordered thumbnail cards merely to fit a generic dashboard grid.
- Do not equate animation with moving scanlines, sweep arms or blinking dots alone.
- Do not make every theme a recolor of the same geometry.
- Do not hide operational truth inside decorative artwork.
- Do not require artwork for correctness: scene assets are optional and procedural fallback remains supported.
- Preserve the 480×320 touch/navigation contract and resource governor.
- Measure target framebuffer/thermal cost before broad rollout.

## v0.19 implementation start

`beastui/scene_compositor.py` adds bounded PIL-native primitives for:
- translucent information planes;
- radial ambient light;
- full-scene asset placement with pulse/tint/edge fade;
- deterministic ambient particles.

`beastui/home_scenes.py` now uses those primitives for the hero scene. The Beast is allowed to visually own the canvas and the live telemetry becomes a compact HUD instead of a three-column card wall.

This is the first migration target, not the final visual design. Home is the proof surface before extending layered composition to Recon, Spectrum, Expedition, progression/reveal moments and other high-value experiences.
