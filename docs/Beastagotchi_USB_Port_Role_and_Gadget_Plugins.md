# USB-C port role & USB-gadget plugins (hardware contract)

**Status:** note / hardware contract. Added after a BadHID (USB HID injection)
plugin build surfaced how the Pi's USB-C port role interacts with gadget-style
plugins.

## The contract

A Raspberry Pi's OTG-capable USB port (the **USB-C** port on a Pi 4, the **USB**
micro port on a Pi Zero) can be in one of a few roles, set by the `dwc2`
devicetree overlay in `config.txt`:

- `dr_mode=host` — the port acts as a USB **host** (devices plug *into* it).
- `dr_mode=peripheral` — the port acts as a USB **device/gadget** (the Pi
  presents itself to another computer, e.g. as a keyboard or a network adapter).
- `dr_mode=otg` — **auto**: device when plugged into a host, host with an OTG
  cable. The most flexible, and the recommended default.

**These roles are mutually exclusive at a given moment.** A plugin or layer that
needs the Pi to *be* a USB device (a "gadget") and one that needs the port in
*host* mode cannot both own that port at once.

## What this means for Beastagotchi layers

- **USB-gadget plugins** (e.g. BadHID keystroke injection, USB-ethernet `usb0`,
  serial/console gadgets, mass-storage gadgets) require the port in
  `dr_mode=otg` or `peripheral`. If a future Beastagotchi "USB layer" /
  "Gadget Dock" exposes any of these, it should ensure that role and document
  that it is claiming the port.
- **USB-host uses** on that same port (plugging a USB device *into* the USB-C
  port) require `dr_mode=host`. A layer that needs this should set/restore it and
  document that it is claiming the port for host mode, since doing so disables
  gadget plugins on that port until it's released.
- Treat the USB-C port role like any other **exclusive-control resource**
  (the radio, the display bus): a layer that demands it should announce the
  claim, and two layers that need it in opposite roles can't run at once.

## Stock-image gotcha (why "no device controller" happens)

On current **Raspberry Pi OS (Bookworm)**, the stock `config.txt` ships:

```
[cm4]
otg_mode=1
[cm5]
dtoverlay=dwc2,dr_mode=host
[all]
...
```

The `dwc2` overlay is **scoped to `[cm5]`** (Compute Module 5 only). So on a
**Pi 4 or Pi Zero**, there is *no active `dwc2` overlay at all* — and therefore
no USB device controller (`/sys/class/udc` is empty), and gadget mode silently
doesn't work. The fix is to add an overlay under `[all]` (or the board's own
section), **leaving the `[cm5]` line and any display/other overlays untouched**:

```
[all]
dtoverlay=dwc2,dr_mode=otg
```

(The BadHID suite's `enable_dwc2.sh` does exactly this, section-aware, with a
backup and `--revert`. This note records the underlying contract so any
Beastagotchi USB layer handles the port role deliberately.)

## Not affected by the port role

- **SPI/GPIO displays** (e.g. a 3.5" MPI3501/ILI9486 via `tft35a` + `ads7846`
  touch) are on the SPI bus / GPIO header, **not USB** — the `dwc2` port role
  does not affect them.
- **USB-A ports** on a Pi 4 run on a **separate** controller (VL805) from the
  USB-C `dwc2` port, so devices there (e.g. a u-blox USB GPS) are unaffected by
  the USB-C port's `dr_mode`.
