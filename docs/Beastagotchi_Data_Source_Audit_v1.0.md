# Beastagotchi Data Source Audit v1.0

**Status:** Real-hardware audit completed from `beast_source_probe_20260920_022225`  
**Target:** Raspberry Pi 4 Model B Rev 1.5, Debian 13/Trixie, Pwnagotchi 2.9.5.9, Python 3.13.5  
**Purpose:** Replace assumptions in v0.1 with exact sources and implementation decisions for Beast Core.

## Status labels

- **SUPPORTED** — source exists now on this Pi and was directly observed.
- **SUPPORTED/FALLBACK** — source exists and is usable, but Beast Core will prefer a cleaner source when available.
- **DERIVED** — computed by Beast Core from supported state.
- **RUNTIME VERIFY** — collector path is known, but the short probe did not produce a live sample of the specific field.
- **BRIDGE** — best supplied by the Beast Pwnagotchi plugin bridge rather than log scraping.
- **FUTURE** — optional hardware/service.

---

## Verified platform

- Raspberry Pi 4 Model B Rev 1.5, approximately 8 GB RAM.
- Debian GNU/Linux 13 (trixie), aarch64, kernel `6.18.39+rpt-rpi-v8`.
- Pwnagotchi package version `2.9.5.9` from `/opt/.pwn/lib/python3.13/site-packages/pwnagotchi`.
- Pwnagotchi service: `pwnagotchi.service`.
- Bettercap service: `bettercap.service`.
- GPS daemon: `gpsd.service` + `gpsd.socket`, local TCP `127.0.0.1:2947`.
- Pwnagotchi web interface: port 8080.
- Bettercap API: port 8081, authenticated, launched with active caplet `pwnagotchi-auto`.
- Monitor interface: `wlan0mon`; managed parent: `wlan0`; both on `phy0`.
- Display: `/dev/fb1`, `fb_ili9486`, 480×320, RGB565/16-bit.
- Touch: `ADS7846 Touchscreen`, `/dev/input/event0`.
- Existing Beast preview trees are present at `/opt/beastagotchi`, `/opt/beastagotchi-v1`, and `/opt/beastagotchi-v1.2`; the old `beastagotchi.service` is disabled.

---

## System

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `system.cpu.total` | SUPPORTED | Two-sample delta of `/proc/stat` aggregate CPU row. |
| `system.cpu.core0..3` | SUPPORTED | Two-sample delta of `/proc/stat` per-core rows. |
| `system.load.1m/5m/15m` | SUPPORTED | `/proc/loadavg` or `os.getloadavg()`. |
| `system.memory.*` | SUPPORTED | `/proc/meminfo`; prefer `MemAvailable` for usable-free calculation. |
| `system.swap.used_pct` | SUPPORTED | `/proc/meminfo`. Current probe showed no active swap. |
| `system.temp.cpu_c` | SUPPORTED | `/sys/class/thermal/thermal_zone0/temp`; firmware command agrees. |
| `system.throttle.flags` | SUPPORTED | `vcgencmd get_throttled`; sample was `0x0`. |
| `system.uptime_sec` | SUPPORTED | `/proc/uptime`. |
| `system.boot_time` | DERIVED | Wall clock minus uptime. |
| `system.clock.synced` | SUPPORTED | `timedatectl show -p NTPSynchronized --value`. |
| `system.hostname` | SUPPORTED | `socket.gethostname()` / hostname. |
| `system.model` | SUPPORTED | `/proc/device-tree/model`. |
| `system.ram_mb` | SUPPORTED | `/proc/meminfo`. |
| `system.kernel` | SUPPORTED | `uname` / `platform.release()`. |
| `system.beast_version` | SUPPORTED | Beast Core package manifest. |

### Important clock finding

The Pi reports a synchronized clock, but its configured timezone is `Europe/London`. Beast Core should store all database timestamps in UTC and make display timezone an explicit Beast setting rather than embedding OS-local timestamps into persistent records.

---

## Storage

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `storage.root.used_pct` | SUPPORTED | `statvfs('/')`; probe root usage ~8%. |
| `storage.root.free_bytes` | SUPPORTED | `statvfs('/')`. |
| `storage.root.readonly` | SUPPORTED | `/proc/mounts` root mount flags; later add a safe temp write probe in Beast-owned state directory. |
| `storage.mounts[]` | SUPPORTED | `/proc/mounts`, with optional enrichment from `lsblk`. |
| `storage.captures.bytes` | SUPPORTED/FALLBACK | Configured Bettercap handshake directory is `/etc/pwnagotchi/handshakes`; recursive cached size. |
| `storage.logs.bytes` | SUPPORTED | `/etc/pwnagotchi/log` plus Beast logs. Pwnagotchi log path is zram-backed and rsynced by its fs.memory layer. |
| `storage.database.bytes` | SUPPORTED | Beast SQLite file stat. |
| `storage.backup.last_success` | DERIVED | Beast backup metadata. |
| `storage.archive.status` | FUTURE/DERIVED | Beast archive/NAS module. |

### Storage layout finding

The root filesystem is a large ext4 partition on `/dev/mmcblk0p2`, while Pwnagotchi uses zram mounts for `/etc/pwnagotchi/log` and `/var/tmp/pwnagotchi`. Beast should avoid high-frequency writes to the SD card; telemetry history should be batched and SQLite should use WAL with bounded retention.

---

## Radio / Wi-Fi

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `radio.interfaces[]` | SUPPORTED | `iw dev` parser + `/sys/class/net`. |
| `radio.primary.name` | SUPPORTED | Pwnagotchi config `main.iface = wlan0mon`. |
| `radio.primary.mode` | SUPPORTED | `iw dev`; `wlan0mon` is monitor. |
| `radio.primary.mac` | SUPPORTED WITH NOTE | `iw dev`/sysfs. Monitor interface currently reports all-zero MAC, so identity widgets should fall back to parent `wlan0`/phy identity when needed. |
| `radio.primary.channel` | SUPPORTED | `iw dev`. Probe sample: channel 10. |
| `radio.primary.frequency_mhz` | SUPPORTED | `iw dev`. Probe sample: 2457 MHz. |
| `radio.primary.band` | DERIVED | Frequency/channel mapping. |
| `radio.primary.supported_channels[]` | SUPPORTED | Verified via `pwnagotchi.utils.iface_channels('wlan0mon')`. |
| `radio.primary.tx_bytes/rx_bytes` | SUPPORTED | `/sys/class/net/wlan0mon/statistics/*`. |
| `radio.primary.state` | DERIVED | operstate + interface existence + mode + service health. |
| `radio.hop.current` | SUPPORTED | `iw dev`; plugin bridge will provide exact Pwnagotchi hop callback too. |
| `radio.hop.rate` | DERIVED | timestamps of bridge `on_channel_hop` events. |
| `radio.hop.history[]` | DERIVED | bridge event history / Beast time-series. |

### Verified supported channel set

`1–11`, `36`, `40`, `44`, `48`, `52`, `56`, `60`, `64`, `100`, `104`, `108`, `112`, `116`, `120`, `124`, `128`, `132`, `136`, `140`, `144`, `149`, `153`, `157`, `161`, `165`.

The installed site-package `agent.py` contains the earlier Beast troubleshooting patch that refreshes supported channels from the monitor interface and retries when the list is initially empty. Beast Health should audit the presence of this patch instead of blindly reapplying it.

---

## Wi-Fi observations / encounter data

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `wifi.ap_count` | SUPPORTED | Prefer Bettercap `/api/session`; fallback to Pwnagotchi `.apcache` count; plugin bridge provides Pwnagotchi filtered count. |
| `wifi.client_count` | SUPPORTED | Bettercap session or sum of `clients[]` in `.apcache`. |
| `wifi.hidden_count` | DERIVED | AP hostname/SSID state. |
| `wifi.vendor_count` | DERIVED | Unique non-empty vendor names. |
| `wifi.new_ap_rate` | DERIVED | Event/encounter DB time window. |
| `wifi.aps[]` | SUPPORTED/FALLBACK | Bettercap `/api/session` is preferred. Pwnagotchi `/etc/pwnagotchi/handshakes/cache/*.apcache` was directly observed and contains AP + client metadata, RSSI, channel, frequency, encryption, vendor, first/last seen and handshake flag. |
| `wifi.clients[]` | SUPPORTED/FALLBACK | Bettercap API preferred; `.apcache clients[]` fallback. |
| `wifi.channel_activity[]` | DERIVED | Current AP/client observations grouped by channel. |
| `wifi.channel_history[]` | DERIVED | Beast time-series. |
| `wifi.signal_history[]` | DERIVED | Repeated observations in encounter DB. |
| `wifi.encounters.*` | DERIVED | Beast encounter DB. |

The probe confirmed useful AP-cache data without requiring Bettercap API access. This means the Networks page has a robust fallback even if Bettercap's API is temporarily unavailable.

---

## Bettercap

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `bettercap.state` | SUPPORTED | `bettercap.service` + process + API heartbeat. |
| `bettercap.uptime` | DERIVED | `systemctl show bettercap.service` start timestamp. |
| `bettercap.api_latency_ms` | DERIVED | timed authenticated GET. |
| Bettercap live session | RUNTIME VERIFY | Active API is authenticated on port 8081. Probe v1.0 got HTTP 401 because it merged credentials from multiple caplets. Beast Core v0.1 instead detects the **active** caplet from the Bettercap process command line and reads only that caplet's API credentials. |

No design dependency remains blocked by the failed v1.0 schema probe because AP cache provides a fallback. The first on-device Beast Core run will validate the corrected Bettercap collector.

---

## Pwnagotchi

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `pwnagotchi.mode` | BRIDGE | Beast Bridge `on_ready` / future explicit mode state. Avoid HTML scraping. |
| `pwnagotchi.epoch` | BRIDGE | Plugin `on_epoch(agent, epoch, epoch_data)`. |
| `pwnagotchi.mood` | BRIDGE | Plugin callbacks: bored, sad, excited, lonely, sleep, wait, etc. |
| `pwnagotchi.peers` | SUPPORTED/BRIDGE | Session-stats plugin fallback; bridge peer callbacks preferred. |
| `pwnagotchi.bonds` | RUNTIME VERIFY/BRIDGE | Add only if exposed by agent/peer state; not proven by current probe. |
| `pwnagotchi.active/blind/sad/bored` | BRIDGE | `epoch_data` where available. |
| `pwnagotchi.missed` | BRIDGE | `epoch_data` where available. |
| `pwnagotchi.deauths` | SUPPORTED/BRIDGE | Session-stats JSON currently contains `num_deauths`; bridge preferred for exact current epoch/session. |
| `pwnagotchi.assocs` | BRIDGE | `on_association`/epoch data. |
| `pwnagotchi.handshakes` | SUPPORTED/BRIDGE | Session-stats + AP cache handshake flag + bridge event. |

### Architectural decision: Beast Bridge plugin

Do **not** keep parsing Pwnagotchi logs as the primary interface. A tiny read-only custom Pwnagotchi plugin should publish supported callback state into `/run/beastagotchi/pwnagotchi_bridge.json`. This preserves the core while giving Beast exact event-driven channel, mood, epoch, peer, AP/client-count and handshake telemetry. Public Pwnagotchi plugin examples document callbacks including `on_wifi_update`, `on_channel_hop`, `on_handshake`, `on_epoch`, `on_peer_detected`, mood callbacks and others.

---

## GPS

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `gps.fix` | SUPPORTED/RUNTIME VERIFY | gpsd TCP protocol, TPV `mode >= 2`. gpsd itself was directly observed; short probe had no TPV fix. |
| `gps.satellites_visible/used` | RUNTIME VERIFY | gpsd SKY object. |
| `gps.latitude/longitude` | RUNTIME VERIFY | gpsd TPV lat/lon. |
| `gps.altitude_m` | RUNTIME VERIFY | gpsd TPV `altMSL`/`alt`. |
| `gps.speed_mps` | RUNTIME VERIFY | gpsd TPV `speed`. |
| `gps.heading_deg` | RUNTIME VERIFY | gpsd TPV `track`. |
| `gps.hdop` | RUNTIME VERIFY | gpsd SKY `hdop`. |
| `gps.accuracy_m` | RUNTIME VERIFY | gpsd TPV error fields. |
| `gps.trip_distance_m` | DERIVED | accepted-fix track integration. |
| `gps.session_distance_m` | DERIVED | active expedition track integration. |
| `gps.track[]` | DERIVED | Beast session DB. |

### GPS hardware and service

A u-blox 7 GNSS receiver is present as `/dev/ttyACM0` at 9600 baud, with stable `/dev/serial/by-id/...` symlink. `gpsd` is active and listening locally.

### GPS architecture improvement

The current Pwnagotchi GPS plugin is enabled and points directly at the serial device while gpsd is also running. Long-term, use **gpsd as the single serial owner** and have Beast and Pwnagotchi consume gpsd if the plugin supports `localhost:2947`. This avoids two readers competing for one NMEA serial stream. Do not change this until the current GPS behavior is validated outside/with a fix.

---

## Captures

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `captures.total` | SUPPORTED/FALLBACK | AP-cache handshake flags + configured capture-directory file count. |
| `captures.session` | DERIVED | capture events after session start. |
| `captures.valid` | DERIVED/FUTURE | capture validator metadata. |
| `captures.pmkid` | DERIVED/FUTURE | parser/validator metadata. |
| `captures.eapol` | DERIVED/FUTURE | parser/validator metadata. |
| `captures.duplicates` | DERIVED | hash/network/time rules. |
| `captures.storage_bytes` | SUPPORTED | recursive size of `/etc/pwnagotchi/handshakes`. |
| `captures.items[]` | DERIVED | filesystem + AP cache + encounter/session DB enrichment. |

The probe's capture file scan omitted `/etc/pwnagotchi/handshakes`, so actual current `.pcapng` filenames were not inventoried. This is a probe bug, not an architecture blocker. The configured directory is confirmed, and the current Jayofelony branch uses pcapng in recent releases.

---

## Plugins

Pwnagotchi plugin config is readable from `/etc/pwnagotchi/config.toml`. The probe confirmed plugin definitions including auto-backup, GPS, grid, memtemp, pwnstore UI, session-stats, webcfg and multiple disabled optional plugins.

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `platform.plugins[]` | SUPPORTED | TOML config + plugin-file discovery. |
| plugin enabled state | SUPPORTED | `main.plugins.<name>.enabled`. |
| plugin code path/version | PARTIAL | Built-in plugin files verified. Custom directory `/etc/pwnagotchi/custom-plugins` exists, but v1.0 probe failed to enumerate its files. |
| plugin health/errors | DERIVED | Beast event/log adapter + bridge exceptions. |

Plugin configuration UI can therefore be generated from TOML immediately; schema-aware widgets can be added progressively.

---

## Services / health

| Canonical state | Status | Exact source / implementation |
|---|---|---|
| `platform.services[]` | SUPPORTED | `systemctl show` for selected units, later DBus optimization. |
| `platform.notifications[]` | DERIVED | Beast event layer. |
| `platform.events[]` | DERIVED | Beast event bus + SQLite. |
| `platform.incidents[]` | DERIVED | Beast Health Engine. |
| `platform.hardware[]` | SUPPORTED | udev/sysfs/`lsusb`. |

Observed active services include Pwnagotchi, Bettercap, gpsd, pwngrid-peer, NetworkManager, systemd-timesyncd, Bluetooth and SSH. The only failed unit in the probe was `dphys-swapfile.service`; because this image currently has no swap and uses zram for selected Pwnagotchi paths, Beast Health should initially classify this as a **known warning**, not a device-critical failure.

---

## Display / touch

The actual physical target is now fully verified:

- framebuffer `/dev/fb1`
- driver `fb_ili9486`
- 480×320
- 16-bit RGB565
- touch device `/dev/input/event0`
- ADS7846 touchscreen
- current calibrated affine transform already exists under the legacy Beast trees

The production UI can therefore render natively to an RGB565 backbuffer and preserve the existing touch calibration data as an import source.

---

## Security finding from probe v1.0

The broad `grep -R` used for `config/relevant_paths.txt` crossed a private-key file and copied **one line of private key material** into the diagnostic archive. The key is not reproduced here and Beastagotchi will not use it. Probe v1.1 removes recursive config greps across arbitrary files and explicitly excludes keys/secrets. Future diagnostic bundles must follow an allowlist model, not a broad recursive grep model.

---

## Gate B result

### Completed

- real Pi/platform identification
- exact framebuffer/touch target
- Pwnagotchi package/version/service/config locations
- Bettercap service/API location and active-caplet method
- monitor interface + full supported-channel source
- GPS daemon/device/socket
- handshake directory and AP-cache schema
- session-stat source
- plugin config source
- systemd service source
- storage/zram layout
- old Beast installation locations protected from overwrite

### Remaining runtime verifications

These can be completed during the first Beast Core foundation test rather than with another full probe:

1. authenticated Bettercap `/api/session` using active-caplet credentials;
2. GPS TPV/SKY fields while receiver has a real fix;
3. actual capture file extensions/count in `/etc/pwnagotchi/handshakes`;
4. custom-plugin file inventory;
5. exact `epoch_data` keys exposed by Pwnagotchi 2.9.5.9 bridge callbacks.

**Gate B is sufficiently complete to begin Gate C — Beast Core Skeleton.**
