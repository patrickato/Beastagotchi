# Beastagotchi Hardware / Power / Dock Specification v0.1

## Hardware philosophy

Beastagotchi treats attached hardware as capabilities rather than hard-coded one-off peripherals. A device may advertise one or more candidate roles, but Beast verifies what the current Linux driver and hardware revision actually support before assigning an operational role.

The capability pipeline is:

`physical device -> identity -> capability profile -> runtime verification -> role -> apps/widgets`

Unknown USB hardware is retained as an unclassified device so a future adapter can claim it without changing the base USB collector.

## Known hardware seed profiles

### ALFA AWUS036ACM

Seed profile: MediaTek MT7612U, dual-band Wi-Fi. Candidate Beast roles are Scout, management radio, monitor radio and Kismet source. These remain candidate roles until the actual adapter is connected to this Pi and its runtime PHY/driver capabilities are verified.

### Edimax EW-7811Un

Seed profile: 2.4 GHz Wi-Fi. Candidate roles begin with management/Scout and are runtime-verified before use.

### TP-Link Archer T2U Nano AC600

Hardware revisions vary. Beast deliberately does not assign a chipset/role solely from the retail name. USB VID/PID, driver, PHY, bands and supported interface modes will be captured when the exact unit is enrolled.

### RTL-SDR

Beast will treat a detected RTL-SDR as an RF capability that can expose receive-only apps such as Spectrum, Sky/ADS-B, compatible sensor observations and radio exploration. Decoders remain separate services managed by Beast Core.

## Waveshare UPS Module 3S

The pictured board is a Waveshare UPS Module 3S with onboard INA219 voltage/current monitor and an I2C expansion header. Beast Core v0.6 contains an optional INA219 collector that probes 0x41 first, then 0x40 and 0x42 for known Waveshare INA219 variants. If the board is not connected over I2C, the collector reports `not_detected` without degrading Beast Core.

Canonical keys include:

- `power.ups.state`
- `power.telemetry.available`
- `power.battery.voltage_v`
- `power.battery.percent_estimate`
- `power.current_ma`
- `power.power_w`
- `power.charging`
- `power.discharging`
- `power.external_present`
- `power.source`

Battery percentage is initially an estimate derived from the 3S pack voltage window. Later calibration can learn the user's actual cells/load behavior and provide a better runtime estimate.

## Dock definition

The requested definition is intentionally simple:

**DOCKED = external wired power AND Ethernet connected to the enrolled home network.**

Storage is not required. USB devices are not required.

To avoid treating a random Ethernet network as Home, Beast stores a local home-dock fingerprint. The enrollment command is intended to be run once while Ethernet is connected to the user's home network:

`sudo beast-enroll-home`

The fingerprint records the Ethernet default gateway and, when available, its MAC address. Dock mode is then derived locally from external-power state, Ethernet carrier and the enrolled home-network fingerprint.

## Resource governor direction

Modules will eventually declare resource needs (CPU, memory, radio, USB bandwidth, power, foreground/background priority). Hidden pages do not receive heavy rendering. Expensive optional services can be started/stopped according to foreground app, Dock/Field state, thermals and power budget.
