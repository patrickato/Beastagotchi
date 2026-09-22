# Beastagotchi Glossary

This vocabulary keeps UI/product conversations consistent as the project expands.

## Beast Core
The privileged/local daemon that gathers canonical state, persists history, exposes read APIs and mediates sensitive actions. UI layers should consume Beast Core rather than independently re-implementing OS/Pwnagotchi control.

## Beast UI
The on-device physical display/touch experience. The 480×320 SPI TFT is the validated reference implementation.

## Beast Studio
The responsive local WebUI/workshop for deep configuration, layouts, visualizers, plugins, packages, logs and management tasks that do not belong on the small field display.

## Page
A high-frequency full-screen Beast UI destination in the swipe/tab carousel, such as Home/Beast, Recon, Networks, Spectrum, Captures, Map or System. Pages are curated; their count is not an architectural limit.

## App
A deeper functional surface launched from Beast UI or Beast Studio. Apps may be built-in or capability-driven and do not need a permanent main-page slot.

## Board
A user-composed live dashboard/canvas made of instruments/widgets bound to canonical Beast data. Boards can appear as apps and eventually on larger displays.

## Widget / Instrument
A visual component bound to one or more canonical data sources. Its data binding should remain separable from renderer, geometry and theme.

## Renderer / Visualizer
A way to present data: line, area, bars, radial, heatmap, waterfall, waveform, timeline, numeric/microtrend, etc. Renderers are not themselves data sources.

## Layout
Geometry/placement of widgets and page elements. Layout is separate from visual theme.

## Theme
A structural visual identity: typography, geometry, background language, graph skin, icon treatment, effects, transitions and color system. Themes are intentionally more than recolors.

## Profile / Presentation
A complete screen presentation mode. Important examples include Beast UI, stock/native Pwnagotchi and Pwnagotchi with Theme Manager.

## Presentation Broker
The planned ownership layer that grants one presentation exclusive framebuffer/touch ownership at a time and coordinates clean handoff/rollback.

## Beast Pack
A downloadable, versioned extension package that can contain themes, face packs, layouts, apps, renderers, hardware adapters, content, missions or other optional capabilities plus a manifest describing compatibility/resources/dependencies.

## Beast Depot
The planned user-facing package/catalog experience for discovering, installing, updating and removing Beast Packs.

## Context Deck
A curated context-sensitive group of apps/boards/actions appropriate to a situation or mode.

## Beast / Personality
The living-character layer: face/expression, energy, curiosity, focus, stress, aura, progression and context-driven reactions. It is derived from real device/activity state rather than arbitrary animation alone.

## Progression
Persistent level/growth/evolution/achievement state. Current design uses finite levels 1–100 plus evolution stages rather than an infinite meaningless counter.

## Rare Moment / Rare Cinematic
Deterministically scheduled or context-triggered uncommon presentation/event layers, with rarity and witness/missed-window behavior. These are part of the long-term experience, not throwaway animations.

## Expedition
A persistent field session capturing route/activity/progression/thermal and discovery context for later review/replay.

## Field Library
Local searchable documents/runbooks/reference material accessible without Internet connectivity.

## Black Box
Persistent incident/event evidence intended to make failures explainable and recoverable.

## Action Broker
Typed/audited privileged mutation interface. UIs request defined actions rather than gaining arbitrary root shell access.

## Resource Governor
Policy layer that protects core services under genuine pressure. It is a safety mechanism, not the normal substitute for efficient architecture.
