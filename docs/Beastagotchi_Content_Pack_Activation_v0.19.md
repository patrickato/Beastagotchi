# v0.19 Content Pack Activation

The first Beast Pack activation tier is deliberately **data/assets only**.

Supported at this gate:
- theme
- face
- animation
- audio
- layout
- board
- data
- map

Activation changes the Pack's managed registry state. It does not copy Pack
files into `/opt`, execute code, import Python, install dependencies, restart
services, or change presentation ownership.

Content-only activation is blocked if a Pack requests permissions, declares a
background service/service restart, contains code-like executable file types, or
contains executable filesystem permissions.

## Theme Packs

Theme Packs are the first end-to-end consumer of this model.

An enabled installed theme Pack may contain:

```
manifest.json
state.json
themes/
  my_theme.json
  another_theme.json
```

The theme filename must match its internal theme ID. Beast UI and Beast Studio
discover enabled Pack themes directly from the managed installed-Pack registry.
Built-in theme IDs always win collisions, so community content cannot silently
replace a built-in visual identity.

Disabling the Pack removes its themes from the live catalog. If the active theme
disappears, Beast UI falls back to Classic rather than continuing to reference
disabled content.

This proves the Depot architecture without weakening the security boundary.
Code-bearing app, renderer, integration, hardware and experimental Packs still
require dedicated activation adapters.
