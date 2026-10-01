# Beastagotchi Linux / Software / Tooling — Owner Decisions

**Date:** 2026-09-27  
**Status:** owner decisions captured during Capability Expansion Pass; implementation still paused until final reconciliation.

## Cross-cutting rule

Do **not** build something merely because we can. If a mature, maintainable existing tool already provides the needed underlying capability and can be safely integrated, launched, wrapped, or orchestrated, prefer using it. Beast-native code should focus on missing integration, orchestration, presentation, capability discovery, policy, lifecycle, provenance, guided workflows, and shared platform contracts.

Guided Software remains a major approved pattern:

> **Guided -> Advanced -> Full Tool**

The real/full program remains available whenever practical.

## Owner decisions by item

1. Software Catalog / Software Abilities — **APPROVE**.
2. Guided -> Advanced -> Full Tool — **APPROVE**.
3. Capability-oriented software acquisition — **APPROVE**, and expand toward a Ninite-like catalog/list of available software/capabilities with simple one-click install/download where technically appropriate.
4. Guided Terminal — **APPROVE/EXPLORE**. Syntax coloring/highlighting is especially desirable because it materially helps readability and learning.
5. Full terminal inside Beastagotchi — **APPROVE / preferred**.
6. Command Explain / Preview — **NEEDS CAREFUL UX**. Must not become annoying or cluttered, and TFT suitability is questionable. Prefer explicit/on-demand invocation, especially on 480x320; richer display belongs on phone/WebUI/Studio.
7. Guided SSH — **APPROVE**.
8. Full SSH/SFTP — **APPROVE**.
9. File Workspace — **APPROVE**.
10. Full file-manager options — **RESERVE for expandability later**, not a priority.
11. Smart Inbox classification — **APPROVE**.
12. Archive Workshop — **ACCEPT**.
13. Guided config editor — **REJECT as a broad/general feature**. Do not build a universal config-form system merely for its own sake. Structured help for common configs may still exist under item 34.
14. Diff before save — **ACCEPT**.
15. Merge/conflict assistance — **ACCEPT**.
16. Strong local/federated search over Linux/files/docs — **APPROVE**.
17. Find every reference/usages — **STRONGLY APPROVE**.
18. Process/Service Workspace — **PARTIAL APPROVAL**: start/stop/restart service controls are approved; broader process-manager/dashboard scope is not currently compelling.
19. Task Center — **APPROVE**, but live progress must remain visible in the active context (e.g. Doctor page) without requiring navigation to Task Center. Task Center is for background/left-behind jobs and overall queue/history.
20. Guided scheduler — **APPROVE**.
21. Full cron/systemd timer access — owner sees no current need as a special feature. Full terminal already permits it. Do not build dedicated UI unless later justified.
22. Automation Builder (When X -> if Y -> do Z) — **APPROVE**.
23. Full scripting / owner scripts — **APPROVE**.
24. Python Workspace — **APPROVE**.
25. pipx/isolated Python app installs where suitable — **APPROVE**.
26. Optional discoverable development runtimes — **APPROVE**.
27. Dependency isolation as platform strength — **STRONGLY APPROVE**.
28. Git Workspace — **STRONGLY APPROVE**.
29. Plugin-development workflow — **APPROVE**.
30. Browser-based code editing — **APPROVE**.
31. Runtime containers on the physical Beast — **RESERVE for later development**.
32. Guided containers — **RESERVE for later development**.
33. Visual flow engine / Node-RED-like integration — **RESERVE for later development**.
34. Structured data/config tooling — **STRONGLY APPROVE**, especially tools that help beginners correctly modify common Pwnagotchi/Beast/plugin configs and understand JSON/YAML/TOML/etc.
35. SQLite/Data Explorer — **RESERVE for later development**.
36. DuckDB/Data Lab — **RESERVE for later development**.
37. Document Toolbox — **APPROVE**.
38. Document conversion / Pandoc-style integration — **ACCEPT** where an existing tool is useful; do not overbuild.
39. Media Toolbox / FFmpeg guided workflows — **APPROVE**.
40. Image Toolbox — **APPROVE**.
41. Audio Toolbox — **APPROVE but not immediate priority**.
42. Screenshot/screen-recording/support capture — **APPROVE**.
43. Checksum/Integrity Toolbox — **ONLY IF NEEDED EARLY**, otherwise reserve for later; underlying integrity functions may still be used internally by Packs/Doctor/acquisition/backups.
44. Signing/provenance UI/support — **RESERVE for later**, though underlying verification should be used where available.
45. Personal encrypted storage — **RESERVE for later development**.
46. Mature backup engines beneath Beast recovery semantics — **APPROVE**.
47. Removable-media guided workflow — **APPROVE**.
48. External/removable storage for field data — concept accepted, but remember users may not carry external media. Continue exploring local/offline/phone/Home Base/NAS/library/cache options that avoid requiring Beast-hosted cloud infrastructure or paid server hosting.
49. Temporary local file server / QR share — **INTERESTING / KEEP**.
50. Static/local web hosting for owner projects — **NEEDS USE-CASE JUSTIFICATION** before promotion.
51. Guided package management — **MAYBE**, not yet a strong priority.
52. Full package manager via Linux/terminal — **APPROVE / already inherent**.
53. Cleanup must be ownership-aware — **APPROVE**.
54. Home Base software maintenance — **APPROVE**.
55. Offline package/resource cache — **STRONGLY APPROVE**, including staging resources in advance so users can quickly adapt when needs/situations change while offline.
56. Software-aware Rebuild Manifest — **APPROVE only if accuracy can be high**; must derive from explicit package/provenance/capability metadata and verification, not guesses.
57. `What installed this?` provenance — **ACCEPT**.
58. `What uses this?` dependency visibility — **APPROVE**.
59. Portable Software Profiles — **STRONGLY APPROVE**.
60. Bench Projects with software/docs/config/verification — **APPROVE**.
61. Bench Project interpretation — treat as a potential archive/catalog of owner-created side projects with reproducible hardware + wiring + firmware + software + docs + config + validation; explore further before final product design.
62. Learning Mode reusable toggle — **APPROVE**.
63. Tutorial progress memory — **ACCEPT**.
64. Tap/hold contextual-help pattern — **REJECT / owner not fond of this interaction**. Find less intrusive/helpful alternatives later.
65. Complete authoritative manuals remain available — **APPROVE**.
66. Capability-aware Tool Launcher — **ACCEPT**.
67. Search + Abilities merged question-answer behavior — **RESERVE for later**.
68. User scripts/programs registered as first-class Tools — **APPROVE / owner likes this**.
69. Managed Tools bounded; full root shell remains Owner Space — **APPROVE**.
70. Beast as translator between human intent and Linux ecosystem — **STRONGLY APPROVE / core platform identity candidate**.

## Clarifications to carry forward

### Ninite-like software/capability catalog
Desired candidate UX:
- searchable/browsable list of useful available software/capabilities;
- status: installed / available / missing dependency / incompatible / queued;
- concise description of what it enables;
- one-click `Install`, `Queue`, or `Open Full Tool` where appropriate;
- category filters rather than raw package names;
- source/provenance and disk/resource impact available in Details;
- can include Beast-managed integrations and recognized full external tools;
- do not turn this into a custom package manager if existing apt/pipx/etc. can do the actual installation underneath.

### Command Explain / Preview
Should be explicit/on-demand rather than intercepting every command. Candidate flow:
- user selects/pastes command and taps `Explain`;
- syntax-colored shell display;
- concise explanation of command/options/pipes/redirection/sudo/affected paths;
- optional expanded view on phone/WebUI/Studio;
- TFT shows only short summary + obvious risk/mutation indicator;
- no pop-up before every terminal command by default.

### Live progress
The shared progress/status system must be embeddable in the current page/workspace. Examples:
- Doctor continues showing current diagnostic/repair progress;
- package install page shows install progress;
- sync page shows sync progress.
Task Center is a secondary place to revisit/inspect background jobs, not the only place progress exists.

### Storage / server-cost philosophy
Do not assume a paid Beast cloud/server is required. Prefer, where appropriate:
- device-local storage/cache;
- phone-provided storage/companion transfer;
- owner NAS/Home Base storage;
- removable storage when available;
- peer/local transfer;
- GitHub/project release hosting for public project artifacts where suitable;
- owner-configured third-party destinations;
- selective caching/indexing instead of mirroring entire knowledge universes locally.
Global Doctor/online ecosystem hosting remains a separate architecture/business question for later.

### Accurate Rebuild Manifest
Only promise reproducibility for managed/observable state. Accuracy can be improved through:
- package database + explicitly managed packages;
- runtime/environment manifests;
- Pack/plugin manifests;
- file/config provenance;
- Capability/Provider dependencies;
- repository/source metadata;
- hardware inventory;
- validation after reconstruction.
Owner Space/untracked manual changes should be identified as such rather than falsely reconstructed.

### Bench Projects
Potential concept:
- user-created project archive/catalog;
- name/description/photos/notes;
- BOM;
- wiring/pin map;
- required hardware;
- firmware/artifacts;
- software/packages/libraries;
- provider/config snippets;
- documentation/tutorial;
- verification/test Procedure;
- portable/exportable project bundle later.
This may eventually become a strong Workshop/Create feature, but final format is not yet frozen.
