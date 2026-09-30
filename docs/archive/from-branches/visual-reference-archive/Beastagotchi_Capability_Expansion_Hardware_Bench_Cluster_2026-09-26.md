# Beastagotchi Capability Expansion — Hardware Bench Cluster

**Date:** 2026-09-26  
**Status:** active capability-expansion jam; preserved ideas, not final implementation canon

## Core direction

Treat Pi GPIO/I2C/SPI/UART/1-Wire/PWM, USB-serial devices, Pico/Pico 2, ESP32-family boards, signal-analysis tools, firmware utilities, sensors and attached bench hardware as a coherent **Hardware Bench / physical-computing capability family**.

Do not reduce this to a GPIO toggle page.

Desired outcome:

> Beastagotchi can help the owner identify, connect, test, configure, learn, flash, bridge, monitor and reuse physical hardware while still preserving access to the full underlying expert tools.

Apply the shared rules:

- Guided does not mean restricted.
- Overlapping, not conflicting.
- One provider/capability may support many focused experiences.
- Owner Space remains available.
- Doctor handles diagnosis rather than each hardware tool inventing its own troubleshooting system.
- Resource/acquisition queue can obtain drivers, firmware, docs and packages later when offline.

---

# 1. Hardware Bench Workspace

Candidate deep workspace that composes many primitives without turning each into a top-level app.

Potential panels/tools:

- Raspberry Pi pinout map;
- live GPIO state;
- pin ownership / who is currently using each pin;
- input/output/PWM configuration;
- edge/interrupt observation;
- I2C bus scan and known-device matching;
- I2C register explorer;
- SPI device/profile explorer;
- UART/serial terminal;
- baud/format/profile selection;
- 1-Wire device discovery;
- USB-serial inventory;
- sensor onboarding/calibration;
- firmware flashing/provisioning for supported microcontrollers;
- logic-analyzer/protocol-decoder integration;
- power/current/voltage providers when hardware exists;
- saveable bench profiles/projects;
- guided wiring/help/reference;
- launch full expert tools where installed.

This should be highly visual where useful, but technical/raw paths remain available.

---

# 2. Plug in a sensor -> Beast explains what it can become

Candidate workflow:

1. hardware appears on GPIO/I2C/SPI/UART/USB;
2. Beast identifies bus/address/device ID where possible;
3. Capability Registry matches known profiles;
4. Beast explains what the device can provide;
5. missing driver/library/package is shown;
6. owner may install now / queue for Home Base / open docs / use raw bus explorer;
7. test reading verifies actual function;
8. owner names/claims the sensor if desired;
9. sensor becomes a Provider feeding canonical Signals/Events;
10. the new sense is reusable by Expeditions, creature expression, automation, Doctor, Search, etc.

Example:

> `BME280-compatible environmental sensor detected at I2C 0x76.`
>
> Can provide: temperature, humidity, pressure.  
> Driver/profile: available.  
> [Add Sensor] [Learn] [Raw I2C]

Do not promise automatic identification for every bus device; unknown devices remain unknown and can be explored manually.

---

# 3. Guided bus tools + full tools

## I2C
Guided:
- scan bus;
- identify likely known chips;
- show address conflicts;
- read supported sensor values;
- simple register browser;
- explain pull-ups/address pins where relevant.

Advanced/full:
- raw transaction/register access;
- launch/use standard Linux utilities or owner tools.

## SPI
Guided:
- show enabled controllers/chip-selects;
- known attached profiles;
- clock/mode/config;
- simple test where device contract allows;
- explain contention and pin ownership.

Advanced:
- raw SPI transfer tools / custom scripts / Owner Space.

## UART / serial
Guided:
- detect serial device;
- common baud profiles;
- readable terminal;
- line ending/display modes;
- save known device profile;
- log session if owner chooses.

Advanced:
- complete serial-terminal application or CLI.

## GPIO/PWM
Guided:
- pin map;
- safe pin-state inspection;
- simple LED/button/relay/servo exercises where appropriate;
- PWM controls;
- event counters;
- visual state.

Advanced:
- complete libgpiod/gpio libraries/custom code path.

---

# 4. Pico / Pico 2 / ESP32 as Beast co-processors

Strong capability-expansion candidate:

> Treat inexpensive microcontrollers as attachable physical coprocessors rather than isolated hobby boards.

Possible roles:

- precision timing/PWM;
- extra GPIO;
- ADC/analog acquisition;
- sensor hub;
- remote sensor node;
- LED/lighting controller;
- haptic/output controller;
- serial/I2C/SPI bridge;
- pulse/frequency counter;
- low-power always-on watcher;
- watchdog/helper;
- logic analyzer;
- protocol bridge;
- actuator controller;
- custom owner firmware.

Potential Beast flow:

`USB/serial board appears -> identify chip/family -> inspect firmware role -> show capabilities -> install/flash known role -> verify -> register Providers/Capabilities`

Full expert access remains available.

Relevant real tool families include Raspberry Pi `picotool` for RP2040/RP2350 device/binary interaction and Espressif `esptool` for Espressif inspection/flashing/provisioning.

---

# 5. BenchLink / Role Firmware concept

Candidate evolution of the existing BenchLink idea:

Beast could maintain a small library of known microcontroller **roles** rather than one giant firmware.

Examples:

- `Sensor Hub`;
- `GPIO Expander`;
- `LED/Haptic Controller`;
- `ADC Logger`;
- `Logic Analyzer`;
- `Serial Bridge`;
- `Power Monitor`;
- `Remote Environmental Node`;
- `Experiment Blank`.

A role may declare:

- supported board families;
- required pins/peripherals;
- firmware artifact/version;
- capabilities exported to Beast;
- communication protocol;
- update/rollback support where feasible;
- documentation/tutorial;
- Sandbox/virtual fixture where useful.

Owner can still flash arbitrary firmware manually.

Do not assume firmware can always be backed up/recovered; eFuses/OTP/security settings require special handling and explicit warnings.

---

# 6. Guided firmware flashing

Potential Beast-managed flow for known supported boards:

1. identify exact MCU/board family;
2. inspect current state/version where possible;
3. explain target firmware/role;
4. acquire verified artifact;
5. snapshot/export existing flash only where technically possible and appropriate;
6. enter bootloader/download mode;
7. flash;
8. verify written image;
9. reboot;
10. verify exported capability/function;
11. clean staging files;
12. update Device Passport/Provider inventory.

Beginner UX could say:

> `ESP32 detected. Sensor Hub firmware is available.`
>
> `This will replace the firmware currently on the board.`
>
> [Flash Sensor Hub] [Open esptool/full workflow] [Cancel]

Full Tool paths remain available for PlatformIO/Arduino/ESP-IDF/MicroPython/Pico SDK/etc. as compatible software discovered during the broader pass.

---

# 7. Logic Analyzer / protocol understanding

Very strong combination:

> Hardware Bench + Pico/external logic analyzer + sigrok/PulseView + Doctor.

Possible guided modes:

- `Watch I2C`;
- `Watch SPI`;
- `Watch UART`;
- `Measure PWM`;
- `Find signal activity`;
- `Decode protocol`.

Beast can display a simplified decode while allowing `Open in PulseView` for the complete signal-analysis environment.

This is valuable for both learning and repair.

Example Doctor escalation:

> `The sensor is configured correctly but returns no data.`  
> `I can see I2C clock activity but no ACK from address 0x76.`

That is substantially stronger than only inspecting software state.

---

# 8. Learn-by-doing electronics mode

Guided Software principle extends naturally to physical electronics.

Possible starter labs:

- LED + resistor;
- button/input/pull-up;
- PWM brightness;
- servo control;
- read an I2C sensor;
- UART console;
- SPI display/device basics;
- analog sensing through Pico/ADC;
- logic-analyzer introduction.

Pattern:

> show wiring -> identify pins -> explain why -> run test -> visualize live result -> let owner modify -> verify -> reset/restore baseline.

Potential safety metadata:
- voltage compatibility;
- 3.3V-only warnings;
- current limits;
- external-power warning;
- never imply Pi GPIO is tolerant of arbitrary voltages.

This is education, not just utility.

---

# 9. Capability ownership / arbitration

Physical pins/buses are shared resources.

Beast should know when:

- TFT already consumes SPI pins;
- I2C address conflicts exist;
- UART is already claimed;
- GPIO line is owned by another Provider;
- PWM/timer/resource is busy;
- a device can safely share a bus vs requires exclusive ownership.

User-facing example:

> `SPI0 is already used by the TFT.`  
> `This sensor can share the bus using CE1.`

or:

> `GPIO 18 is currently reserved by Audio PWM.`  
> `Choose another pin or suspend Audio.`

This is a concrete application of **Overlapping, not conflicting**.

---

# 10. Remote / distributed physical senses

ESP32/Pico W or other supported nodes could extend Beast beyond the Pi enclosure.

Possible examples:

- campsite environmental node;
- indoor/outdoor temperature nodes;
- greenhouse/terrarium sensor;
- remote light/motion sensor;
- equipment temperature/power monitor;
- button/remote control surface;
- remote LED/status beacon;
- workshop bench sensor pod.

Transport could vary by implementation/capability: USB serial, Wi-Fi, BLE, MQTT, Meshtastic bridge, etc.

Beast should treat these as Providers with provenance/location/health rather than inventing a bespoke database for every device family.

---

# 11. Practical industrial/vehicle-adjacent interfaces — walk-the-line treatment

Potential compatible hardware domains include:

- USB serial;
- RS-232/RS-485;
- Modbus;
- CAN adapters;
- USB instrument interfaces;
- measurement equipment.

Beast-managed workflows should focus on owner-controlled diagnostics, instrumentation, reading/visualization, learning and explicitly safe supported operations.

Do not pretend broader third-party/full tools do not exist. Owner Space may use complete Linux applications and custom scripts. Beast may recognize/import outputs or expose generic transport capabilities without building purpose-made workflows for harmful or unauthorized control.

---

# 12. Doctor synergy

Hardware Bench should not have its own duplicate troubleshooting engine.

Doctor can use Bench instruments as probes:

- I2C ACK/no-ACK;
- serial enumeration;
- USB connect/disconnect;
- GPIO state;
- signal capture;
- firmware version;
- pin conflict;
- driver/provider health.

Conversely, Hardware Bench can call Doctor when onboarding/test fails.

Example:

> `BME280 onboarding failed.`  
> Doctor sees device absent at expected address, detects no I2C ACK, and guides the owner toward wiring/address/power checks.

---

# 13. Search / acquisition / documentation synergy

When unknown hardware appears:

- identify vendor/product/chip IDs where possible;
- search local Field Library/manuals;
- search Global Doctor hardware population;
- search approved online docs/project sources when permitted;
- find driver/library/profile;
- queue acquisition for later if offline;
- preserve datasheet/reference locally if owner chooses;
- avoid blindly binding arbitrary drivers based on a weak search result.

This can make obscure hardware much easier to use.

---

# 14. Strongest product concepts from this cluster

1. **Hardware Bench as a real physical-computing workspace, not GPIO toggles.**
2. **Plug in hardware -> Beast explains what it can become.**
3. **Pico/ESP32 as attachable Beast coprocessors/sense-expression nodes.**
4. **BenchLink role firmware library.**
5. **Guided firmware flashing with full-tool escape hatch.**
6. **Logic analysis/protocol decoding integrated with Doctor.**
7. **Learn-by-doing electronics/tutorial layer.**
8. **Pin/bus ownership arbitration.**
9. **Remote/distributed physical senses.**
10. **Generic industrial/serial/CAN/Modbus compatibility through managed + full-tool + Owner Space layers.**

## Open jam questions

- Should known microcontroller firmware roles be first-party Packs, a BenchLink catalog, or another presentation over existing Pack/provider contracts?
- How far should Beast go in auto-identifying unknown I2C/SPI hardware before requiring owner confirmation?
- Should hardware projects be saveable as named “Bench Projects” containing wiring/profile/provider/config references?
- Could a user move a Pico/ESP32 role between Beastagotchis and have it identify itself automatically?
- Which remote-node transports deserve first-class support vs generic extension support?

