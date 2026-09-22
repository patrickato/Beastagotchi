# Beastagotchi Native Pwnagotchi Bridge — v0.9.3

## Goal

Preserve the **actual live Jayofelony Pwnagotchi UI**, including its stock face selection, mood/action changes, status text, plugin UI elements, layout and voice-driven state, while Beastagotchi remains the display owner and Beast Core continues running.

## Why this works

Jayofelony's Pwnagotchi `View.update()` composes the real Pwnagotchi canvas and sends it to `pwnagotchi.ui.web.update_frame()` on each UI update. The web helper saves that canvas to:

```text
/var/tmp/pwnagotchi/pwnagotchi.png
```

This happens independently of whether the physical Pwnagotchi display renderer is enabled. Beastagotchi therefore does **not** need to recreate the face/mood logic. It can consume the frame Pwnagotchi itself just rendered while keeping `ui.display.enabled = false` so two programs never fight over `/dev/fb1`.

## Built-in native profiles

- `pwn_native_raw` — the live Jayofelony canvas itself, plus the configured hardware rotation, with no recoloring.
- `pwn_native_dark` — exact native foreground/layout, normalized to white ink on black.
- `pwn_native_light` — exact native foreground/layout, normalized to black ink on white.
- `pwn_native_chroma` — exact native foreground/layout used as the mask for mood-aware Beast color/glow treatment.

The older `pwn_dark`, `pwn_light`, and `pwn_chroma` profiles remain as **Beast-rendered replicas/fallbacks** and are labeled as such.

## Fidelity rules

For Native RAW, Native Dark and Native Light, Beastagotchi intentionally does **not** paint its normal header, footer, page chrome, event reaction, scanline, or reconstructed face over the frame. The native Pwnagotchi composition is the screen.

A long press opens Beast Control Center. Ordinary taps and horizontal swipes are ignored while the native profile is idle because the stock Pwnagotchi UI is not a touch UI. A downward swipe may also open Beast controls.

Rare omens/moments remain a final Beast-wide overlay by design. They are intentionally allowed to appear over Native Pwnagotchi because rare-event presentation is part of the Beast wrapper experience.

## Safety and failure behavior

The source PNG is read into memory before Pillow decodes it. If Beast catches the file during a Pwnagotchi write and decoding fails, it keeps the last known-good frame. If no native frame has ever been available, the Native profile displays an explicit `NATIVE FRAME UNAVAILABLE` diagnostic rather than silently falling back to a replica.

## Diagnostic command

```bash
beast-pwn-native
```

Reports source availability, dimensions, frame age, and whether the native frame is exactly 480×320.

## Why this is better than reproducing the stock face

The Native Bridge follows Pwnagotchi's own live `View` output. That means future face choices, random face variants, status changes and plugin elements produced by the installed Jayofelony build appear automatically. Beastagotchi does not need to guess which stock expression Pwnagotchi should be showing.
