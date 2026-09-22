# Beastagotchi Thermal Efficiency Strategy v0.13

The Resource Governor is an emergency/safety mechanism, **not the normal way Beastagotchi achieves acceptable temperature**. Full visual quality should be the ordinary state on suitable hardware/cooling.

## Software efficiency before load shedding
- batch state/events and history requests;
- cache facts at the cadence at which they can actually change;
- avoid repeated parsing/stat/process launches;
- write only changed RGB565 framebuffer rows;
- keep hidden apps/pages from doing heavy rendering;
- static pages render when live data/input changes rather than continuously at their maximum FPS budget;
- animated backgrounds request their own lower cadence independently of touch/data responsiveness;
- measure Beast UI/Core/Studio/Pwnagotchi/Bettercap/gpsd CPU/RAM and render/compose/framebuffer-write cost.

## Next physical comparison
v0.13 will be compared to v0.11 on the same Pi for temperature, Beast UI CPU, total CPU, average render/compose time, framebuffer write percentage and user-perceived responsiveness. If the device still approaches the Pi thermal limit during ordinary Full operation, optimization continues before accepting routine REDUCED mode.

## Hardware cooling is a capability
Optional active cooling is legitimate platform hardware, not a software failure. Hardware Studio should eventually expose fan availability, duty/RPM, curves, quiet/performance profiles and failure detection. Beast should exploit cooling intelligently while preserving the silent/passive experience where possible.
