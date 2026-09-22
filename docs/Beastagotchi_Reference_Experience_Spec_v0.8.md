# Beastagotchi Reference Experience Spec v0.8

## Purpose

v0.8 is the first step from validated framework toward the actual Beastagotchi experience. It deliberately connects live state to identity, progression, reactions and user-selectable visualization without changing Pwnagotchi's RF behavior.

## Progression contract

Level cap: 100.

Stages:
Hatchling -> Cub -> Scout -> Tracker -> Hunter -> Beast -> Alpha -> Apex -> Monstergotchi.

Persistent profile:
`/var/lib/beastagotchi/profile.json`

Primary principle: reward exploration, cataloging and longevity. Avoid creating incentives to repeatedly trigger intrusive behavior.

## Lifetime encounter contract

`wifi_encounters` in `/var/lib/beastagotchi/beast.db` stores one row per observed BSSID. Session-first observations may update that row. Lifetime-first observations are separately identified so repeated sightings do not repeatedly award discovery XP.

## Aura contract

Auras are session-local visual intensity tiers based on session-unique discoveries. Themes may map the same aura name to completely different graphics.

## Reaction contract

Only one dominant reaction owns the main visual reaction layer at a time. Safety/health signals beat cosmetic celebrations.

## Renderer contract

A widget owns data; a renderer owns presentation. v0.8 proves this with Spectrum Bars / Line / Heatmap / Radar using the same channel-occupancy data.

## Render-loop contract

No routine HTTP/history fetch is allowed to block the composition path. Data feed and rendering remain separate.

## Safety contract

Progression, achievements, auras, themes and reactions never alter Pwnagotchi attack/radio policy.
