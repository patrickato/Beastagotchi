# Beastagotchi Reference-Build Software / Service BOM Strategy — v0.1

**Date:** 2026-09-24  
**Purpose:** seed the versioned superset Bill of Materials for the user's Pi 4 Beastagotchi reference build  
**Important:** this document catalogs; it does not instruct Beast to bulk-install the superset.

## Governing rule

Maintain two different sets:

1. **KNOWN UNIVERSE / SUPERSET BOM** — everything the currently approved Beastagotchi feature universe may require.
2. **ACTIVE INSTALL SET** — only the dependency closure needed by the selected build/features/hardware.

The superset may be large. The active install set should remain intentionally smaller.

## Current Jayofelony image baseline

Reference source:
- repository: `jayofelony/pwnagotchi`
- branch: `noai`
- reviewed commit: `93dda381ef11538e4ec03fd130abad3ceeea7a4c`

These dependencies belong to the upstream image/runtime baseline. Beast should
detect them before attempting to install equivalents.

### Upstream Python project dependencies

Jayofelony's current `pyproject.toml` declares:

- PyYAML
- dbus-python
- file-read-backwards
- flask
- flask-cors
- flask-wtf
- gpiozero
- inky
- pycryptodome
- python-dateutil
- requests
- rpi-lgpio
- rpi_hardware_pwm
- scapy
- setuptools
- smbus
- smbus2
- spidev
- tomlkit
- toml
- tweepy
- websockets
- pisugar

Python requirement: **>= 3.11**

The current upstream file explicitly notes that `numpy`, `gast` and `shimmy`
were removed from the Pwnagotchi dependency set because they belonged to the old
AI-training pipeline.

### Upstream image package seed

The current Jayofelony image build package list includes:

- aircrack-ng
- binutils-gold
- bluez
- bluez-tools
- build-essential
- curl
- dkms
- dphys-swapfile
- g++
- git
- libbluetooth-dev
- libc6-dev
- libcurl4-openssl-dev
- libdbus-1-dev
- libdbus-glib-1-dev
- libfl-dev
- libfreetype6
- libfreetype-dev
- libjpeg-dev
- liblgpio-dev
- libnetfilter-queue-dev
- libopenjp2-7
- libpcap-dev
- libdtovl0
- libssl-dev
- libtiff6
- libusb-1.0-0-dev
- pkg-config
- python3-dev
- python3-luma.lcd
- python3-luma.oled
- python3-pil
- python3-pip
- python3-prctl
- python3-setuptools
- python3-tomlkit
- python3-virtualenv
- rsync
- socat
- swig
- systemd-timesyncd
- tcpdump
- unzip
- wget
- wl
- xxd
- zlib1g-dev

The image build also installs/builds `lgpio`, Pwnagotchi in
`/opt/.pwn` with system-site-packages, Bettercap/pwngrid, Nexmon-related pieces,
hcxtools, systemd services and PwnStore as separate image stages.

These are **baseline facts**, not Beastagotchi requests to reinstall them.

## Current Beastagotchi dependency posture

Beastagotchi intentionally relies heavily on the standard library and the already
present host environment.

Current development/test requirements in `requirements-dev.txt` are:

- pytest >= 8
- Pillow >= 10
- numpy >= 1.26
- pypdf >= 5
- PyMuPDF >= 1.24
- qrcode >= 8.0

These must not automatically be treated as production-runtime requirements.

Current special case:
- `qrcode >= 8.0` is used by CI to validate the real Capsule Share QR renderer.
- The physical-acceptance path pins the currently CI-tested runtime package to
  `qrcode==8.2`.
- Beast UI/Studio now include the Beast-owned optional path
  `/opt/beast-python/site-packages` in their PYTHONPATH.
- `beast-v019-accept prepare-qr` explicitly downloads the 8.2 wheel, records
  its SHA-256 and installs it with `pip --target` into that Beast-owned path.
- `beast-v019-accept remove-qr` removes only the Beast-owned qrcode package.
- The normal installer creates the package root but does not silently download
  optional runtime packages.
- This does **not** modify Pwnagotchi's protected `/opt/.pwn` site-packages.

This is a first concrete optional-runtime boundary, not yet the generalized
Dependency & Capability Resolver remediation engine.

The BOM should distinguish:
- runtime-required;
- optional runtime;
- document-format enhancement;
- CI/test/build only.

## Service baseline currently observed by Beast

Beast's current ServicesCollector tracks:

- pwnagotchi.service
- bettercap.service
- gpsd.service
- pwngrid-peer.service
- NetworkManager.service
- systemd-timesyncd.service
- beast-core.service
- beast-ui.service
- beast-studio.service

Tracking a service does **not** mean it must be active on every build.

Future BOM/resolver work should record for each service:

- installed?
- enabled?
- active?
- required by which capability?
- safe to stop when capability inactive?
- restart policy?
- port/socket ownership where relevant?
- resource cost?

## Plugin-specific dependency layer

The stock plugin compatibility class is cataloged separately in:

`docs/Beastagotchi_Dependency_Capability_Resolver_v0.1.md`

Important rule:

A plugin should declare abstract requirements whenever possible rather than force
one implementation.

For example:

`location.position`

may be supplied by:
- USB GPS / current GPS plugin;
- gpsd;
- PwnDroid;
- a later Hardware Pack.

This prevents dependency bloat and allows provider choice.

## BOM tiers for the user's reference build

### Tier A — Foundation / always present
The smallest common Beast + upstream runtime necessary for ordinary operation.

### Tier B — Current physical hardware
Only dependencies required by hardware actually attached to this user's Pi 4.

Examples currently include the 480×320 ILI9486/XPT2046 path and any validated
power/GPS/radio hardware that is actually present.

### Tier C — Stock Pwnagotchi compatibility
Support knowledge for all Jayofelony stock/stock-known plugins.

This does not mean all plugins or all plugin-specific hardware packages are
enabled.

### Tier D — Selected Beast capabilities
Dependencies installed because the user chooses a feature such as:
- SDR;
- ADS-B;
- Meshtastic;
- offline maps;
- local AI;
- voice;
- additional display;
- Home Base integrations.

### Tier E — Developer/build/test
Compilers, headers, pytest, documentation extraction helpers, packaging tools and
other development-only software.

These should not leak into the production runtime simply because CI uses them.

### Tier F — Known future universe
Catalog entries for approved long-term features not selected on the current build.

These exist so the user can ask "What would I need?" without installing anything.

## Why this is better than a kitchen-sink image

A preinstalled "everything image" sounds convenient but makes dependency ownership
less clear.

The preferred Beast model gets the convenience without the bloat:

- complete catalog;
- complete dry-run plan;
- one-tap capability preparation where safe;
- exact user guidance where not;
- verified installation only when selected;
- rollback;
- reproducible provenance.

That gives the user the information advantage of "everything known" without the
runtime cost and conflict risk of "everything installed."

## Future generated artifacts

Once the resolver inventory is mature, Beast should be able to generate:

### `beast-bom-full.json`
Every known current requirement for the reference build universe.

### `beast-bom-installed.json`
What is actually installed/running.

### `beast-bom-missing.json`
Requirements needed by currently selected features but missing.

### `beast-bom-unused.json`
Installed software/services no selected capability currently needs.

### `beast-bom-conflicts.json`
Known conflicts/ownership collisions.

### Human-readable "Build Readiness Report"
A concise explanation suitable for the TFT/Studio.

## Safety boundary

The BOM is informational by default.

Generating or refreshing the BOM must not:
- apt install/remove anything;
- pip install/remove anything;
- enable/disable/start/stop services;
- change kernel modules;
- change Pwnagotchi config;
- change secrets;
- select hardware providers.

Mutation belongs to separately audited, explicit Action Broker transactions.
