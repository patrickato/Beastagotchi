# Beastagotchi Cross-Layer X + Y = Z Jam — Batch 01

**Date:** 2026-09-27
**Status:** active creative jam; candidate combinations, not final approved canon

This pass intentionally combines already-preserved capabilities to discover higher-order Beastagotchi behaviors.

1. **Hardware discovery + Software Catalog + Abilities + Guided Software -> Instant Ability Onboarding**
   Plug in hardware. Beast identifies it, shows what it can enable, identifies required software/dependencies, offers Install/Queue/Open, verifies function, and updates Abilities.

2. **Phone Provider + Beast Core + WebUI + shared state -> Seamless multi-surface Beast**
   TFT, phone and WebUI are not separate products. They are different surfaces on the same canonical state/task/session.

3. **Home Base + Acquisition Queue + NAS/phone/PC + external power + software/content catalogs -> Field-to-home logistics**
   Beast can defer heavy downloads, sync, backup, indexing, map/library updates and staged acquisition until trusted connectivity/power are available.

4. **Doctor + Known-Good + Global Doctor + trusted acquisition + Transaction/Procedure engine -> Closed-loop repair**
   Diagnose, compare, acquire missing helper/fix, snapshot, repair, verify, rollback if necessary, learn.

5. **Power/thermal evidence + USB/kernel events + radio/device health + Doctor -> Root-cause correlation**
   Distinguish power failure, driver failure, thermal issue, resource contention and hardware instability rather than treating all symptoms alike.

6. **Location + Pwnagotchi/Bettercap observations + Maps + Chronicle/Expedition -> Operational spatial history**
   Dense-area operation can be visualized geographically: route, AP/network observations, radio activity and session context.

7. **Pwnagotchi session truth + GPS/location + map + Homecoming -> Real visual debrief**
   Turn session/epoch/peer/capture/location data into a truthful post-session map and summary without accumulating rendered reports by default.

8. **SDR + trusted time + GPS + SKY + satellite data + Guided Software -> Pass-aware radio workflow**
   Beast knows a relevant satellite pass is approaching, sees compatible SDR hardware, offers the appropriate receiver/profile/tool, and can queue missing data/software.

9. **SDR + tuner arbitration + Abilities + Guided Software -> One dongle, many coherent roles**
   FM, ADS-B, AIS, rtl_433, spectrum and satellites appear as abilities backed by the same primitive tuner, with explicit conflict/scheduling rules.

10. **Search + Abilities + Software Catalog + Knowledge Library -> “Can my Beast do X?”**
    Search can answer whether an ability is ready, available to install, needs hardware, has a Guided route, or requires a Full Tool.

11. **Federated Search + local/phone/Home Base/web storage + Acquisition Queue -> Information availability instead of file location**
    Beast asks where useful information can be obtained now, not only whether it exists on the Pi SD card.

12. **Owner scripts + Tool registration + Search + Automation + WebUI -> User-created first-class capabilities**
    Owner scripts can be registered with metadata, inputs, permissions and outputs so Beast can discover/invoke them without pretending Beast authored them.

13. **Bench Project + Hardware Bench + dependencies + docs + validation -> Reproducible physical-computing project**
    A saved project can eventually capture hardware, wiring, firmware, software, config, docs and verification in one owner-controlled project artifact.

14. **Multiple Beasts + Pwnagotchi peer concepts + local discovery + shared canonical protocols -> Beast pack awareness**
    Preserve peer identity/presence, optional shared observations, Doctor cohort/local assistance and cooperative context without requiring centralized control.

15. **Unified notifications + display/audio/LED/haptic outputs + later Monster expression -> Semantic choreography**
    One event (success, warning, rare event, Doctor attention) can fan out across whatever outputs exist, with graceful fallback.

16. **IMU/orientation + Presentation platform + Experience preferences -> Adaptive portrait/landscape UI**
    UI and touch mapping rotate together; Experiences may prefer orientation; owner can lock orientation.

17. **Terrain/elevation + maps + RF/session observations + 2.5D/3D presentation -> Spatially dynamic RF/debrief views**
    Actual terrain and elevation can make field/session visualization materially more informative rather than decorative.

18. **Network context + Home Base + Tailscale + phone pairing + policy -> Context-aware connectivity**
    Beast can behave differently on trusted Home Base, tethered, remote-owner, or untrusted networks without inventing giant hard-coded modes.

19. **Smart Inbox + artifact identification + Catalog + Doctor + Full Tool -> Intelligent intake**
    Incoming PCAP/config/firmware/map/manual/archive/etc. can be identified and routed to the relevant Guided or Full Tool without dumping everything into an opaque Downloads folder.

20. **Credential catalog + Doctor + Guided SSH + service dependencies -> Guided credential lifecycle**
    Beast can show where a credential lives, what uses it, help replace/rotate/test it, and keep secrets redacted from ordinary views while owner-reveal remains available.

21. **Live WebUI preview + Sandbox + record/replay + physical Pi validation -> Visual fidelity pipeline**
    Browser preview remains live, Sandbox accelerates testing, record/replay supports deterministic states, and physical TFT remains final visual truth.

22. **Dependency isolation + Software Catalog + Git Workspace + Sandbox -> Safer plugin/tool development**
    Clone/test/install plugins and tools in isolated environments before touching the protected Pwnagotchi runtime.

23. **Rich local evidence + privacy boundary + support-bundle sanitizer -> Useful local truth, safe sharing**
    Keep complete owner-local evidence where justified; sanitize only when data crosses a sharing/upload boundary.

24. **Trusted time + event correlation + Doctor + Chronicle -> Cross-system causal reasoning**
    Accurate timestamps and correlation IDs let Doctor connect power, USB, radio, service and Pwnagotchi events into one incident timeline.

25. **Location page + regulatory domain + Wi-Fi/radio state + maps + local density/session context -> Operational “Where Am I?”**
    Location information becomes relevant to Beast operation rather than generic tourism facts.

26. **Pwnagotchi second-adapter behavior + radio role assignment + resource arbitration -> Predictable multi-Wi-Fi operation**
    Beast must respect how Pwnagotchi actually handles secondary Wi-Fi hardware while making connectivity/monitor/lab roles explicit and non-conflicting.

27. **Phone camera/QR + Software/Hardware Catalog + Smart Inbox -> Scan-to-capability**
    Scan a supported hardware label/QR/project reference and jump directly into identification, docs, required software or a relevant project/package flow.

28. **Global Doctor + healthy baselines + hardware cohorts + Device Passport -> Rare-hardware intelligence**
    Doctor can prioritize evidence from systems matching this exact hardware/kernel/config cohort rather than generic popularity.

29. **Task contextual progress + Task Center + unified notifications -> Seamless foreground/background work**
    Progress stays where the task started; leaving the page backgrounds it; Task Center and notifications preserve continuity.

30. **Power/resource pressure + Scheduler + Home Base policy -> Intelligent heavy-work timing**
    Indexing, backups, downloads and other Beast-managed heavy jobs can wait for suitable power/network conditions without degrading live operation.

31. **Offline Library + phone cache + Home Base library + federated Search -> Distributed knowledge mesh**
    Useful knowledge may live across Pi, phone, browser cache, NAS or Internet while remaining searchable as one system.

32. **Pwnagotchi/plugin configs + Config Toolbox + docs/Search + Doctor -> Guided plugin integration**
    Validate syntax, known keys, examples and dependencies while keeping raw config editing and full docs available.

33. **System Graph + Software Catalog + dependency provenance -> “What breaks if I remove this?”**
    Before uninstall/removal, Beast can explain which abilities, tools, plugins or services depend on the target.

34. **System Graph + resource claims + radios/displays/GPIO/Hardware Bench -> Conflict planner**
    Beast can explain why two requested capabilities cannot currently coexist and offer safe reassignment/sequencing options.

35. **PCAP/import + Guided analysis + Wireshark Full Tool + Doctor -> From capture to diagnosis**
    Beginner gets summaries and relevant findings; expert gets full capture tooling; Doctor can use resulting evidence when troubleshooting owner-authorized systems.

## Jam principle
These are intentionally cross-layer candidate behaviors. Do not automatically promote each into a standalone feature or app. Prefer reuse of existing substrates and the full-not-cluttered rule.
