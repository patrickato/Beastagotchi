# Beastagotchi Connectivity Cluster — Owner Decisions

**Date:** 2026-09-26  
**Status:** preserved owner feedback for later reconciliation/build planning

This record captures the owner's numbered response to the Connectivity / Companion / Home Base capability cluster so later implementation does not have to reconstruct intent from chat.

## Approved / strong go

1. Phone as a real Beast companion surface — **strong yes**.
2. Accountless local pairing — **strong yes**.
4. Phone/desktop -> Beast handoff — **approved / enthusiastic**.
5. Local service discovery to eliminate IP-address friction — **approved**.
7. Guided network-health capability tied to Doctor — **strong yes**.
8. Packet capture and analysis for legitimate owner/authorized use — **add it**.
11. Wi-Fi roles/arbitration — **approved**, but must directly align with how Pwnagotchi handles a second Wi-Fi adapter and must not fight the protected Pwnagotchi radio model.
12. Dynamic radio arbitration — **strong yes**.
13. Bluetooth/BLE capability family — **approved; remain open to additional useful additions**.
14. LocalSend-style one-off local transfer — **do not pass it up**.
15. Selected-folder synchronization / Syncthing-style capability — **strong yes**.
16. Home Base as field->home logistics context — **direction trusted/approved**.
17. Temporary phone tether/other connectivity may satisfy Acquisition Queue — **strong yes**.
18. Optional Tailscale integration — **strong yes**; owner explicitly notes many users install Tailscale everywhere and Beast should not fight that usage.
19. Guided Tailscale view + Full Tool handoff — **approved / interesting**.
21. MQTT bridge — **approved**.
22. One shared notification system — **yes**.
24. Clipboard/link/text handoff — **strong yes**.
25. Universal local Inbox/intake classification — **strong yes**.
27. Contextual presentation destination based on phone/desktop/TFT availability — owner considered this effectively the expected model already; preserve as normal direction.
28. Phone temporarily provides capabilities (camera/GPS/Internet/audio/etc.) — **approved / cool concept**.
29. Abilities changes dynamically when phone-provided capabilities appear/disappear — **yes**.
30. Multiple Beastagotchis should be able to cooperate if multiple Pwnagotchis can cooperate — **approved principle**.
32. Global services enhance rather than own the platform — **agreed**.
33. WebUI as a portal rather than configuration-only — **approved**.
34. Integrate/launch mature full programs rather than poorly cloning them — **approved**.
35. Abilities may visibly label managed/integrated/Owner Space/context-required/etc. — **interesting / likely useful**.
37. Recovery-backed networking experimentation — **must have**.
39. Composable network/context profiles — **approved, with quality expectation: make it genuinely useful rather than a weak mode list**.
40. Unknown/untrusted networks should make Beast quieter unless owner authorizes otherwise — **approved**.
41. Guided networking education — **approved if easily toggled on/off**.
42. Guided SSH + full SSH tool/tutorial — **strong yes**, especially beginner instructions/tutorials.
43. Portable field/home systems-companion philosophy — **approved**.
44. Managed coding/safety boundary — **owner accepts**; maximize allowed first-party functionality, preserve open Owner Space and give users as much useful information/interoperability as possible where a managed workflow cannot be supplied.
45. Strongest connectivity takeaways — owner response indicates these should carry forward.

## Approved with clarification / needs refinement

3. TFT -> phone/Studio handoff — owner likes the idea but notes Pi/Pwnagotchi/Beast, phone and WebUI may already be connected in some form. During architecture, treat handoff as **deep-link/context transfer across already-connected surfaces**, not necessarily a separate connection mechanism.
26. Acquisition Queue <-> Inbox symmetry — owner is uncertain (`maybe`). Preserve as design observation, not a user-facing concept yet.
31. Offline-local WebUI independence — owner needs pros/cons explained before final decision. Keep as an open architectural item; likely goal is full local administration without Internet while still supporting optional global services.
38. Remote-session-loss verifier — owner is skeptical because Internet drops routinely and constant warnings/notifications could be intrusive. Do not implement noisy connection-drop behavior. If preserved, constrain it to **transaction-aware protection**: only watch connectivity when Beast itself is making a networking change that could strand the current management path, with debounce/grace and no ordinary-drop nagging.

## Later / defer

6. Guided `What's on my network?` inventory — **not yet; maybe later**.
9. Guided packet-analysis beginner UI — **not yet** (packet capture/analysis itself remains approved).
20. Generic Home Base service-capability catalog (NAS/local Git/package mirror/printer/etc.) — **later releases maybe**.
23. KDE Connect investigation — **background/future research**, not mission critical; circle back later.

## Safety/open-platform owner expectation

The owner explicitly trusts the project to code the maximum functionality that can be responsibly provided as first-party Beast capability without unnecessary friction, while:

- marking/structuring safe authorized workflows clearly;
- preserving full-program access where applicable;
- preserving Owner Space and generic integration paths;
- documenting capabilities/gaps instead of pretending unavailable managed facilitation is technical impossibility;
- using recovery/snapshot/rollback/cleanup to make owner-authorized experimentation safer;
- avoiding designs that later cause implementation to stall merely because a capability category is dual-use.

This does **not** override safety boundaries; it is a product-design instruction to maximize legitimate, owner-controlled, defensive, educational, diagnostic and open-platform capability inside them.
