# Beastagotchi Capability Expansion — Power / Thermal / Performance / Hardware Health

**Date:** 2026-09-27  
**Status:** capability-expansion discussion record; preserve for later reconciliation

## Core split

- **Power Detective** = owner-facing observation/analysis instrument for power/thermal/performance behavior.
- **Doctor** = diagnosis/repair when power/thermal/performance/hardware-health behavior is wrong.
- **System Health** = compact quick-glance status using the same underlying truth.

Do not build three separate truth systems.

Standing owner principle remains:

> **Efficiency before degradation. Thermal throttling/load shedding should be protection/fallback, not the normal answer to resource pressure.**

## Candidate directions

1. **NOW — shared health telemetry substrate.** CPU temperature, clocks/frequencies, load, memory, swap, storage pressure, throttling/undervoltage indicators, uptime, relevant USB/device faults, and other machine health truth should be collected once and reused by System Health, Power Detective, Doctor, history and notifications.

2. **NOW — truthful availability.** If attached hardware does not expose voltage/current/charge state, Beast must say **Unknown** rather than inventing watts, battery percentage or runtime.

3. **NOW — power-source identity where detectable.** Beast should know whether it is on ordinary external power, a UPS/battery HAT/provider, USB power source with telemetry, etc., when the hardware actually exposes that information.

4. **NOW — power telemetry as Providers.** UPS HATs, INA219/INA226-style monitors, smart battery boards, USB power monitors and other supported hardware should expose standardized signals such as voltage/current/power/state-of-charge where available.

5. **NOW — battery percentage only from actual provider truth.** No fake battery meter for a generic Pi powered from an ordinary USB-C supply.

6. **NOW — runtime estimate may exist only when inputs justify it.** If battery capacity/state-of-charge and current draw are actually known, Power Detective may estimate remaining runtime and must label it as an estimate. If not, do not fabricate one.

7. **NOW — undervoltage/throttling history matters.** Power-related flags/events should be timestamped/correlated with crashes, USB resets, radio issues, display instability, storage errors and performance drops so Doctor can distinguish symptoms from causes.

8. **NOW — thermal history.** Current temperature is useful; trend and peak context are more useful. Doctor should be able to answer whether a fault coincided with sustained or transient thermal stress.

9. **NOW — thermal state needs context.** One raw temperature number is not enough. Show current state, whether any throttling/protection is active, relevant trend and what component/sensor the value represents.

10. **NOW — fan awareness where applicable.** Detect supported controllable fans/tach feedback if present. Show requested vs observed behavior where hardware supports it.

11. **LATER — guided fan curves.** Owner-adjustable policy can come later; do not spend first-release effort building a fan-control product unless the reference hardware needs it.

12. **NOW — no routine performance degradation policy.** Beast should optimize scheduling/resource usage first. Automatic throttling, disabling capabilities or load shedding should be reserved for protection/failure conditions or explicit owner policy.

13. **NOW — resource-pressure awareness.** CPU, memory, swap, I/O pressure and storage pressure should feed the scheduler/runtime so Beast can avoid self-inflicted stalls without pretending load itself is a fault.

14. **NOW — heavy jobs should be identifiable.** Downloads, indexing, map processing, media conversion, backups, Doctor probes and other Beast-managed work should expose which task is consuming resources.

15. **LATER — detailed per-process power attribution.** Interesting where hardware/data support it, but not required for release.

16. **NOW — Power Detective should answer practical questions.** Examples: Why did performance drop? Was the Pi undervolting? Is this USB device causing instability? Did temperature spike before the service failed? Is the system power-limited? Is battery telemetry real or estimated?

17. **NOW — Doctor uses the same evidence.** If the system is unstable, Doctor may correlate PSU/undervoltage, USB resets, kernel logs, thermal state, clock throttling, storage and radio symptoms rather than running a separate isolated diagnostic path.

18. **NOW — compact System Health view.** A quick glance should show only meaningful status: healthy / attention / problem, current temperature, major power warning if any, storage pressure, memory pressure and any active protection/throttling state. Detailed data lives deeper.

19. **NOW — no permanent dashboard clutter.** Detailed graphs belong in Power Detective / WebUI when requested, not permanently occupying the TFT.

20. **NOW — alerts should be event-based, not noisy.** Meaningful new undervoltage, overheating/protection, battery critical, storage critical, fan failure, etc. may notify; ordinary transient load changes should not nag.

21. **NOW — graceful low-power shutdown where real battery hardware supports it.** A UPS/battery provider may expose critical state and request safe shutdown through managed Actions/Transactions.

22. **LATER — wake/resume/power-button integrations.** Hardware-dependent; preserve, do not prioritize without a concrete target.

23. **NOW — external power can remain a trigger input.** Home Base/queued work may use `external_power=true` as one condition through the existing trigger system rather than inventing a separate power automation engine.

24. **NOW — USB/hardware-health correlation.** Repeated disconnect/reconnect, over-current-like symptoms, storage resets or radio disappearance should be visible to Doctor and correlated with power/thermal state when evidence exists.

25. **NOW — storage health belongs in hardware health, not a separate truth model.** Filesystem errors, SMART/NVMe health where supported, free space, I/O errors and mount state can feed System Health/Doctor/Storage Workspace.

26. **LATER — deeper predictive storage failure models.** Potentially useful but not first-release scope.

27. **NOW — Device Passport can retain health-relevant hardware identity.** Board revision, storage devices, power/UPS providers, cooling hardware and attached USB devices should be known so Doctor compares the right baselines/cohorts.

28. **NOW — Known-Good baselines should include health state.** After a stable period, Beast can know the normal temperature/load/device/power envelope for this specific machine without confusing normal variation with a fault.

29. **LATER — adaptive anomaly detection.** Useful eventually, but deterministic thresholds/history and owner-visible evidence are sufficient first.

30. **NOW — truthful estimated vs measured labels.** `Measured`, `Reported by device`, `Derived`, `Estimated`, `Unknown` should remain distinguishable where power/performance values can otherwise look more authoritative than they are.

31. **NOW — full Linux tools remain available.** sysfs, vcgencmd where applicable, lm-sensors, smartctl/nvme tools, journal/dmesg, top/htop and other mature tools remain accessible. Beast wraps/integrates rather than replaces them.

32. **NOW — reuse-first principle.** Use mature Linux/Raspberry Pi telemetry and hardware-specific utilities; Beast-native work should focus on normalization, correlation, history, presentation, policy, alerts and Doctor integration.

## Release cut

Strong first-release/core candidates:
- shared health telemetry;
- truthful measured/derived/unknown semantics;
- temperature/throttling/undervoltage history;
- compact System Health;
- Power Detective for meaningful correlation;
- Doctor integration;
- resource-pressure awareness for Beast-managed work;
- external-power trigger input;
- UPS/battery-provider abstraction;
- safe low-battery shutdown when real hardware supports it;
- storage/device health correlation;
- full-tool access.

Mostly later:
- custom fan curves;
- per-process power attribution;
- advanced wake/power hardware integration;
- predictive storage failure modeling;
- adaptive anomaly detection.

## Overall principle

> Beast should understand **whether the machine is healthy, why it is under pressure, and whether power/thermal conditions are contributing**, without fabricating telemetry and without solving ordinary workload problems by simply crippling performance.
