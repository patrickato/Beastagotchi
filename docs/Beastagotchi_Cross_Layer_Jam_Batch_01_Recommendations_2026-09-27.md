# Beastagotchi Cross-Layer X + Y = Z Jam — Batch 01 Recommendations

Date: 2026-09-27

Status: Assistant recommendation pass, with owner explicitly deferring this batch to assistant judgment.

Decision rule:
- KEEP NOW: materially strengthens Beastagotchi identity, reduces user friction, or unlocks several other systems.
- FOUNDATION NOW / EXPERIENCE LATER: architecture should support it now, but polished experience can come later.
- LATER: preserve, but do not spend first-release effort.
- MERGE: idea is valid but should be absorbed into another existing concept rather than become separate product identity.
- DROP: not worth carrying unless a new concrete use case emerges.

## Recommendations

1. Hardware Discovery + Software Catalog + Abilities = KEEP NOW. Signature Beast behavior.
2. Search + Abilities + Software Catalog = KEEP NOW. Strong human-intent-to-capability bridge.
3. Phone + Beast + WebUI shared task/session/state = KEEP NOW as architecture; polished cross-device continuation may phase in.
4. Phone Hardware + Provider Architecture = FOUNDATION NOW / EXPERIENCE LATER.
5. Phone QR/Camera + Hardware Catalog = LATER. Useful but not release-defining.
6. Pwnagotchi + secondary Wi-Fi + Beast resource arbitration = KEEP NOW where second-adapter support is available; must respect Jayofelony/Pwnagotchi behavior exactly.
7. SDR + Abilities + tuner arbitration = KEEP NOW for SDR foundation; individual experiences can phase in.
8. SDR + GPS + Time + SKY = LATER, but architecture must not block it.
9. Pwnagotchi + Location + Map + History = KEEP NOW at data-model/history level; rich visualization can phase in.
10. Operational Spatial Memory + Homecoming debrief = FOUNDATION NOW / EXPERIENCE LATER.
11. Useful 'Where Am I?' operational page = KEEP NOW, avoiding irrelevant civic/tourism trivia.
12. Terrain/elevation + RF + 2.5D/3D = LATER.
13. Doctor + Power + USB + Radio history correlation = KEEP NOW. High diagnostic value.
14. Doctor + Known-Good + Global Doctor + Transactions repair loop = KEEP NOW as core Doctor direction.
15. Global Doctor + Device Passport cohort expertise = KEEP NOW as Global Doctor data model; value grows with fleet size.
16. Rich local logs + sharing sanitizer = KEEP NOW. Strong privacy/evidence model.
17. Credential Catalog + Doctor + Guided SSH = KEEP NOW at catalog/guidance/security semantics; polished UI can phase in.
18. Plugin Config + Config Toolbox + Search + Doctor = KEEP NOW. High-value beginner/expert bridge.
19. Git + dependency isolation + Sandbox + plugin catalog = KEEP NOW for development/testing architecture; user-facing polish can follow.
20. System Graph + dependency catalog = KEEP NOW. Important for safe install/remove/update behavior.
21. System Graph + resource claims = KEEP NOW. Core anti-conflict architecture.
22. Smart Inbox + Search/Catalog = FOUNDATION NOW / EXPERIENCE LATER.
23. PCAP + Guided Analysis + Wireshark = LATER for Guided analysis; full-tool integration remains available sooner.
24. Owner Script + Tool Registration + Automation = KEEP NOW at metadata/registration contract level; UI can phase in.
25. Home Base + queues + phone/NAS/PC + power state = KEEP NOW as architecture/logistics model; advanced automation can phase in.
26. Search + distributed storage = KEEP NOW. Major part of Beast knowledge architecture.
27. Task progress + Task Center + notifications = KEEP NOW. Shared progress semantics already selected.
28. Power/resource awareness + Scheduler = KEEP NOW for Beast-managed tasks.
29. Unified Outputs + later Monster expression = KEEP NOW as output/event substrate; Monster expression later.
30. Multiple Beastagotchi + Pwnagotchi peer concepts = LATER, but do not architect against it.
31. Trusted time + Chronicle + Doctor causality = KEEP NOW.
32. Live WebUI Preview + Sandbox + Record/Replay + Pi verification = KEEP NOW for development workflow and fidelity.
33. Bench Project + Hardware Bench = LATER, already explicitly deferred past release.
34. Software Catalog + Device Passport + Abilities personalized readiness = KEEP NOW.
35. Situationally composable Beastagotchi identity = KEEP as architectural north star.

## Consolidated priority

### Release-defining / core now
1, 2, 6, 7, 9, 11, 13, 14, 16, 18, 20, 21, 26, 27, 28, 29, 31, 32, 34, 35.

### Foundation now, polished experience later
3, 4, 10, 15, 17, 19, 22, 24, 25.

### Later
5, 8, 12, 23, 30, 33.

### Drop
None from Batch 01. Every item either strengthens the architecture or is worth preserving for later; the key is preventing later items from inflating first-release scope.

## Main conclusion

The most important decision from Batch 01 is that Beastagotchi should be designed as a situationally composable platform rather than a collection of monolithic apps. Hardware, software, capabilities, tools, knowledge, context, tasks, history, and presentation should combine dynamically based on what is actually present and available.
