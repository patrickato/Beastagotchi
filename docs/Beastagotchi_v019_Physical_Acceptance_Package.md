# Beastagotchi v0.19 — Bounded Physical Acceptance Package

Status: **implemented in source; target execution pending**

This package turns the current v0.19 Unified Experience into one bounded, reversible physical session on the 480×320 reference Pi/TFT.

It is intentionally different from source/CI validation.

## What this gate is for

The physical session is intended to answer questions CI cannot:

- Is the 480×320 hierarchy actually readable on the 3.5-inch ILI9486 panel?
- Are the real resistive-touch targets reliable in the enclosure?
- Do swipes, footer controls, Apps and overlays feel coherent?
- Does the Capsule Share QR remain visibly clean on the physical LCD?
- Can a normal phone/camera scan the real QR frame repeatedly?
- Does changed-row framebuffer writing reduce physical writes in real use?
- What are render/compose/framebuffer-write timings while the user actually navigates?
- What temperature/CPU/governor behavior occurs during the same session?
- Are there clipping, stutter, glare, accidental taps or visual-polish problems that an off-screen PNG cannot reveal?

The script does **not** automatically declare these things acceptable. Objective telemetry is summarized separately from user physical judgment.

## Installed command

After the current v0.19 UI package is installed:

    sudo beast-v019-accept start 15

The number is the existing automatic display rollback window in minutes.

The command:

1. creates a timestamped acceptance session;
2. captures pre-handoff Core/display/service/config evidence;
3. records Beast component versions and source fingerprints;
4. probes the optional QR renderer without installing anything;
5. requests a real privacy-curated Lineage Capsule from Beast Core;
6. calls the existing claim_display_test.sh handoff;
7. starts Beast UI in physical-test mode;
8. captures the initial framebuffer;
9. leaves the established rollback timer authoritative.

It does **not** silently confirm permanent Beast display ownership.

## One substantial interaction window

While Beast owns the TFT, use it normally rather than performing isolated micro-tests.

Recommended path:

- swipe through the main page carousel;
- use footer/page navigation;
- open and close Control Center;
- open Apps and move through categories/pages;
- open **Capsules**;
- inspect the QR quiet border/module clarity;
- scan the visible frame with a phone if the QR backend is available;
- change QR frames with both controls and horizontal swipe;
- open at least one dense operational surface;
- open at least one visual/theme surface;
- notice clipping, accidental taps, missed swipes, stutter, glare or visual corruption.

From SSH during that interaction window:

    sudo beast-v019-accept sample 60

The sample command gathers one-second objective evidence while the UI is being used.

## Evidence collected

The session records, when available:

- canonical Core state snapshots;
- Core health;
- platform bundle;
- display ownership/conflict state;
- installed touch calibration;
- component versions;
- selected installed-file SHA-256 fingerprints;
- QR renderer availability/backend;
- real Lineage Capsule export and QR frame count;
- actual physical framebuffer captures;
- UI runtime telemetry;
- render/compose/framebuffer-write timing;
- target/lifetime FPS evidence;
- framebuffer changed rows;
- framebuffer bytes written;
- dirty-span/full-write evidence;
- cumulative framebuffer byte savings;
- CPU temperature;
- CPU utilization;
- governor state/reason;
- touch/gesture records;
- service states;
- relevant journals.

## Runtime sampler

tools/v019_acceptance_report.py produces:

- acceptance-summary.json
- acceptance-summary.txt

The report calculates min/average/max values for CPU temperature, CPU utilization, render time, compose time, framebuffer-write time, changed rows, bytes written, write ratio, target FPS and lifetime FPS.

It also reports framebuffer cumulative deltas, touch-gesture counts, Capsule/QR availability and final UI/Core state.

### Important evidence boundary

The report explicitly states that physical user judgment is required. It does not convert low CPU usage or a successful screenshot into a claim that touch, readability, QR scanning or polish passed.

## Capture a checkpoint during the session

Optional:

    sudo beast-v019-accept capture capsule
    sudo beast-v019-accept capture operations

These capture the framebuffer plus matching Core/runtime/display evidence under the chosen label.

## Finish modes

### Bundle only / make no new ownership decision

    sudo beast-v019-accept finish observe

This creates the evidence bundle but does not confirm or release display ownership. The existing rollback timer remains the safety mechanism.

### Explicitly accept Beast display ownership

Only after the human physical test actually passes:

    sudo beast-v019-accept finish pass

This collects evidence, then invokes the existing confirm_display.sh.

### Explicitly roll back immediately

    sudo beast-v019-accept finish rollback

This collects evidence first, then invokes the existing release_display.sh.

## Output

The bundle is written as:

    /home/pi/beast-v019-physical-acceptance-YYYYMMDD_HHMMSS.tar.gz

The timestamped working session remains under:

    /var/lib/beastagotchi/acceptance/v019/

The bundle is intended to be uploaded back into the Beastagotchi development conversation for analysis.

## QR dependency rule

The Capsule Share UI uses qrcode only when the module is available.

The acceptance harness **does not install it**.

This is intentional. The project has not yet approved silently adding optional Beast dependencies into Pwnagotchi's protected /opt/.pwn environment.

Long-term direction:

- Beast-owned optional Python dependency location;
- capability/BOM awareness;
- explicit install/removal provenance;
- no accidental Pwnagotchi dependency pollution.

Until that packaging boundary is implemented, the physical session truthfully records whether the QR renderer exists.

## Existing safety model retained

This package does not replace display ownership tooling.

It delegates to:

- claim_display_test.sh
- confirm_display.sh
- release_display.sh
- the existing systemd automatic rollback unit

Therefore display mutation/rollback logic remains single-sourced.

## Acceptance status

As of this document:

- source/CI gate: implemented;
- off-screen 480×320 gallery: implemented;
- Capsule QR off-screen decode proof: implemented;
- bounded physical acceptance harness: implemented;
- actual reference Pi/TFT session: **pending**;
- physical QR phone/camera scan: **pending**;
- sustained thermal acceptance: **pending**;
- real Presentation Broker multi-owner switching: still a later separate gate.
