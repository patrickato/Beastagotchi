# Beastagotchi Canonical Template Token Registry — v0.19

## Purpose

The Template Token Registry is a neutral presentation contract between Beast Core
and renderers/configuration surfaces.

It exists so Beast UI, Beast Studio, Boards, Packs and future interoperability
adapters can request values such as:

- `{system.temp}`
- `{system.cpu}`
- `{gps.fix}`
- `{beast.name}`
- `{beast.level}`
- `{expedition.distance}`
- `{peers.total}`

without creating another telemetry collector.

## Core rule

**Tokens never poll hardware and never become a second source of truth.**

Every token resolves through the canonical `StateRegistry`. State metadata is
preserved with the result, including source, quality, timestamp, age and error
state. Missing canonical data renders as unavailable (`--`) rather than a fake
or approximate value.

## Architecture

Implementation:

- `beastcore/template_tokens.py`
- `TemplateTokenRegistry`
- declarative `TokenSpec` allow-list

Each token records:

- canonical state key;
- formatting class;
- unit;
- privacy class;
- publication policy metadata;
- update class;
- optional compatibility aliases.

The registry supports:

- token catalog discovery;
- one-token resolution;
- bounded multi-token snapshots;
- bounded text-template rendering;
- compatibility aliases such as `temp`, `cpu`, `battery`, `gps`, `level`
  and `peers`.

Unknown tokens and unavailable canonical state are explicit rather than guessed.

## Local API

Beast Core exposes a bounded read-only endpoint:

`GET /template-tokens`

Optional query:

`GET /template-tokens?names=system.temp,beast.level,gps.fix`

Catalog metadata can be included with:

`GET /template-tokens?catalog=1`

The normal Beast Core API remains local-first and read-only.

## Privacy / publication

Token metadata is not permission to publish a value.

`publication=policy` means the value may be eligible for a future user-controlled
publication path. Existing Global privacy settings remain authoritative. The
registry does not bypass Global publication scopes, sanitization, consent or
preview rules.

No precise location, SSID, MAC, credential or capture-content token is included
in the initial allow-list.

## Theme Manager interoperability

The current Korrie71 Theme Manager exposes a `STAT_SOURCE` callback seam. The
registry is intentionally suitable for a future small adapter that maps an
allow-listed Theme Manager request to Beast Core state.

That adapter is **not enabled in this milestone**.

The current step creates the neutral contract first. It does not import Theme
Manager, execute Theme Manager code, change its configuration, or enable physical
Presentation Broker handoff.

## Resource behavior

The registry adds no background polling loop.

Resolution cost is bounded dictionary/state lookup plus formatting. Template
rendering is bounded to 1024 input characters and 64 token substitutions by
default.

## Validation boundary

Automated tests cover:

- canonical-state resolution;
- source/quality metadata preservation;
- aliases;
- formatting;
- truthful unavailable/unknown behavior;
- privacy/publication metadata;
- bounded rendering;
- Local API bundle exposure.

This is source/CI functionality. It does not itself require or claim a new
physical TFT validation result.

## Next uses

The registry is intended to become shared substrate for:

1. Beast Studio no-code text/value widgets;
2. Board/Layout/Theme Pack dynamic labels;
3. Beast Doctor/Explain summaries;
4. Visual Asset Interop;
5. a future read-only Theme Manager `STAT_SOURCE` adapter;
6. future public-profile preview helpers only where Global privacy policy permits.

The implementation should remain canonical-state-backed rather than growing new
provider-specific pollers.
