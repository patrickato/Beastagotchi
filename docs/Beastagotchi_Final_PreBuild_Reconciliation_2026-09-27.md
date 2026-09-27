# Beastagotchi Final Pre-Build Reconciliation

**Date:** 2026-09-27  
**Status:** pre-build reconciliation after Doctor, Capability Expansion, X+Y=Z, AI, and Monster/perception/expression jams  
**Purpose:** classify accumulated ideas as APPROVE / MODIFY / RESERVE / REJECT before refreshing architecture, roadmap, migration order, and implementation tranches.

---

# 1. Governing product rules — APPROVE

1. Beastagotchi remains a modular local-first platform built around protected Pwnagotchi + Bettercap rather than replacing them.
2. Hard semantic kernel, wild ecosystem.
3. Real/live data over fake/demo telemetry.
4. Unknown stays unknown; simulated stays labeled simulated.
5. Owner sovereignty: managed defaults without turning the Pi into a locked appliance.
6. Unsupported is not forbidden; Owner Space remains real.
7. Guided experiences never remove the full underlying tool.
8. Reuse mature software where it already solves the problem; Beast-native code should add integration, presentation, orchestration, lifecycle, safety, discovery, or Guided experience.
9. One conceptual execution spine: Truth -> Capability -> Action -> Transaction -> Procedure -> Doctor -> History -> Presentation.
10. Full-but-not-cluttered: top-level identity only for distinct user jobs; everything else becomes a view, Instrument, Tool, Procedure, condition pack, Workspace component, Surface, or query.
11. Huge capability universe, small active runtime working set.
12. Efficiency before degradation; thermal/load shedding is protection, not the normal operating strategy.
13. Collect richly where justified locally; share minimally and intentionally.
14. Catalog everything important, including secrets metadata; securely store secret payloads, redact ordinary views/logs, reveal/export to the owner only on explicit request.
15. Situational composability is a core platform characteristic: hardware, software, phone/Home Base, location, connectivity, health, and context can change current Abilities without changing Beast identity.

---

# 2. Core architecture systems — APPROVE

1. One Doctor.
2. One System Graph.
3. One Action / Transaction / Procedure model.
4. One capability/provider lifecycle.
5. One presentation platform across TFT/WebUI/phone/Studio-capable surfaces.
6. One content/storage model spanning local Pi, phone, Home Base/NAS/PC, cache, Internet, and owner-configured remote storage.
7. One owner customization/provenance history.
8. Shared Signals/Events/Actions primitives.
9. Shared truthful live-operation progress primitive.
10. Shared resource ownership/arbitration model for radios, SDR, GPIO, SPI, I2C, displays, cameras, audio, and other scarce resources.
11. Device Passport / patient hardware identity as shared truth.
12. Known-Good and What Changed? as first-class historical capabilities.

---

# 3. Doctor — APPROVE

1. Doctor is the one-stop diagnostic/repair capability for board/hardware, Linux, Pwnagotchi/Bettercap, Beast, and attached managed ecosystem.
2. Machine Census -> symptom -> dependency path -> competing hypotheses -> targeted probes -> evidence/confidence -> repair plan -> snapshot/rollback -> repair -> functional verification -> cleanup -> learn.
3. Running != working; functional verification matters more than service state.
4. Machine Census + cheap vital signs + fault-family Probe Blocks + open-ended escalation.
5. Confidence ladder: Possible / Supported / Likely / Strongly Supported / Confirmed / Contradicted.
6. Quiet caretaker by default; visibly communicative when owner opens Doctor, significant trouble appears, input/approval is needed, or verbose mode is selected.
7. Doctor investigates aggressively, repairs conservatively, and asks intelligently.
8. Doctor finds it -> uses it -> puts it back.
9. Acquisition Queue is shared beyond Doctor.
10. Global/Collective Doctor Knowledge Network remains a strong platform direction: sanitized cases, negative outcomes, healthy baselines, cohort similarity, provenance, freshness, outcome strength, recovery readiness.
11. Failures teach what breaks; healthy systems teach what normal looks like.
12. Doctor capability is independent of visual skin; TFT function-first, richer WebUI/phone presentation.
13. Doctor can expose full raw evidence/commands/config/diffs/System Graph/Transaction detail for expert use.
14. Power/thermal/storage/radio/display/etc. are Doctor evidence domains, not separate Doctors.

---

# 4. AI + Doctor — MODIFY / APPROVE NEW DIRECTION

Previous framing of a separate Beast AI/chat feature is superseded.

Approved direction:

1. To the user, Doctor may serve as the primary conversational AI companion/front door.
2. Underneath, Doctor's factual engine remains deterministic and fully useful with zero AI.
3. AI is an interchangeable reasoning/conversation provider that Doctor/Beast can borrow; it is not the source of machine truth.
4. Beast without AI must still diagnose known failure patterns, search, operate Actions/Transactions/Procedures, compare Known-Good, show evidence, and repair through managed workflows.
5. AI enhances natural-language intent interpretation, synthesis, explanation, hypothesis ranking, Procedure/config/code drafting, and optional creature narration/expression.
6. AI never gets a separate authority universe or magical unrestricted root shell. It requests existing Beast Actions/Transactions/Procedures.
7. If no managed action exists, AI may explain, draft commands/code, or offer Full Tool / Owner Space, but must not pretend the unmanaged path is equivalent to a verified Beast Action.
8. AI Provider abstraction is required before provider-specific integrations.
9. Provider locations may include Pi-local, paired phone, Home Base/PC, self-hosted server, and optional cloud providers.
10. Ordinary users should be able to use an Automatic routing mode rather than choose a model per prompt.
11. Privacy/context routing policy controls what may leave the Beast.
12. Remote AI receives only policy-allowed context; secrets are redacted by default unless the owner explicitly authorizes required use.
13. AI conversation/history is not automatically Global Doctor contribution.
14. AI is not Beast's database. Structured Beast state remains authoritative.
15. Pi Zero 2 W must remain a supported architecture target for AI integration by using deterministic Doctor + external AI provider client; no local LLM requirement.
16. Pi 4 likewise must not depend on local LLM capability.
17. Pi 5 may support more useful local models, but the architecture remains provider-neutral.
18. Stronger Home Base/desktop GPUs may provide heavy local reasoning while the Pi remains the instrumented physical endpoint.
19. Self-hosted owner-chosen models, including models with different alignment/restriction profiles, may be supported as providers; model behavior does not expand Beast machine permissions.
20. Specialized/fine-tuned Doctor models are RESERVE for later, after Beast has earned a quality verified-case dataset.
21. Voice is RESERVE for later.
22. Do not build a giant autonomous Beast Agent initially; prefer bounded roles/infrastructure with visible Tasks/Transactions/Procedures.

---

# 5. Guided Software / Linux / Tooling — APPROVE

1. Guided -> Advanced Guided -> Full Tool pattern.
2. Broad Software Catalog / Abilities catalog with Installed / Available / Missing Dependency / Update / Incompatible / Experimental / Full Tool / Guided Available / Queued style states.
3. Use apt/pipx/release packages/project installers/etc. rather than inventing a Beast package ecosystem unnecessarily.
4. Real Bash underneath the terminal; optional enhancement such as ble.sh or equivalent mature tooling; do not invent Beast shell syntax.
5. Full SSH/SFTP plus Guided SSH/tutorial support.
6. Config Toolbox focused on real formats and common Beast/Pwnagotchi/plugin/service use; raw editing remains.
7. Start/stop/restart/enable/disable relevant services; no need for a full bespoke process-manager clone.
8. Task Center for background work, but work remains visible in context on the page that started it.
9. Existing Signals/Events/Actions feed Automation Builder; do not create separate geofence/cron-style automation products.
10. Owner Bash/Python scripting and optional Tool registration are first-class extension paths.
11. Dependency isolation is strongly preferred over polluting the Pwnagotchi environment.
12. Git Workspace / plugin development / browser code editor are accepted.
13. Structured Data Toolbox and Document Toolbox are accepted.
14. Mature media tooling should be wrapped/reused later rather than reimplemented.

---

# 6. Search / knowledge / content — APPROVE

1. One federated Search, not many disconnected searches.
2. Source labels/provenance remain visible: LIVE BEAST / LOCAL FILE / OFFLINE LIBRARY / DOCTOR / GLOBAL DOCTOR / OWNER NOTE / HOME BASE / WEB / GITHUB, etc.
3. Mature engines underneath where appropriate: SQLite FTS, Recoll/Xapian-style document search, ripgrep, exact registries, map/geocoder provider, Doctor matcher, Kiwix/ZIM, MapLibre/PMTiles, optional SearXNG or other providers.
4. Knowledge Catalog mirrors Software Catalog semantics for large manuals/maps/reference content.
5. Distributed knowledge across Pi, phone, Home Base/NAS/PC, browser cache, Internet.
6. Search can truthfully return 'available on paired phone/Home Base' and offer Queue/Keep Offline when appropriate.
7. AI is optional above Search for synthesis; exact Search remains useful without AI.

---

# 7. Capability / hardware discovery — APPROVE

1. Abilities dynamically reflect actual hardware/software/context.
2. Typical states: READY / AVAILABLE / FULL TOOL / OWNER SPACE / NEEDS HARDWARE / NEEDS SOFTWARE / context/compatibility/licensing-required states where applicable.
3. Plugging in hardware should visibly expand what Beast can do.
4. Device -> primitive capabilities -> Experiences.
5. Capability fallback chains are architecturally allowed, but sophisticated automatic fallback policy may be deferred.
6. Full expert programs remain accessible.

---

# 8. RF / SDR / GPS / Sensor World — APPROVE

1. SDR treated as capability family rather than one app.
2. Broadcast/weather/rtl_433/ADS-B/AIS/satellite/spectrum/amateur lawful receive-focused experiences may share the same receiver.
3. Tuner arbitration required.
4. GPS is a shared sense across Pwnagotchi, maps, SKY, SDR context, Homecoming, etc.
5. Sensor onboarding creates Providers + Signals/Events.
6. SKY / What’s Above Me? and What’s Around Me? remain approved conceptual Experiences.
7. Beginner teach-while-doing SDR workflow remains approved.
8. Real celestial/aircraft/satellite context may drive truthful creature reactions later.

---

# 9. Hardware Bench — APPROVE / RESERVE SPLIT

APPROVE:
1. One Hardware Bench family for GPIO/I2C/SPI/UART/1-Wire/PWM/USB serial/sensors/measurement/logic analysis.
2. Pin/bus ownership and conflict handling.
3. Sensor/device onboarding and calibration.
4. Guided wiring/help plus full expert access.
5. Bench Projects as a future reproducible-project concept.
6. Logic-analyzer/measurement evidence may feed Doctor.
7. RS-232/RS-485/Modbus/CAN/instrument interfaces as owner-controlled diagnostics/learning/full-tool integrations where hardware exists.

RESERVE:
8. Repurposable Pico/ESP32 role cartridges.
9. Remote/distributed microcontroller senses.
10. Deep reusable/shareable Bench Project ecosystem implementation until later release work.

---

# 10. Connectivity / Companion / Home Base — APPROVE

1. Phone is a real Beast companion surface, not just a remote webpage.
2. Accountless local pairing.
3. TFT <-> phone/WebUI context/session handoff.
4. Local discovery, Tailscale, MQTT, LocalSend/Syncthing-style mature integrations where useful.
5. Phone may temporarily provide GPS/camera/mic/speaker/storage/Internet/etc. through Providers where technically practical.
6. Home Base handles field->home logistics, queued work, heavy resources, archives, backups, and optional heavy compute.
7. Networking changes must respect Pwnagotchi/Jayofelony multi-adapter behavior and radio arbitration.
8. Unknown/untrusted networks use quieter defaults unless owner authorizes otherwise.
9. Multiple Beasts may cooperate where Pwnagotchi peer concepts permit; richer pack/fleet features are later.

RESERVE:
10. Generic Home Base service catalog.
11. KDE Connect-style integration investigation.
12. Broad local-network inventory and beginner packet-analysis UI until later.

---

# 11. Physical world / location / field — MODIFY / APPROVE

1. Reject wilderness/camping framing as Beast's primary identity.
2. Natural operating contexts include dense AP/RF environments, cities, campuses, events, hotels, neighborhoods, travel corridors, labs, and authorized assessment environments.
3. Offline capability is resilience/preparation, not a wilderness identity.
4. Location is a shared sense, not a standalone GPS app.
5. gpsd or another mature multi-client base should be reused where appropriate.
6. Source/freshness/trust are explicit: GNSS, phone, network, last-known, Sandbox, unknown.
7. Route/session recording and GPX/KML/GeoJSON import/export accepted.
8. Dedicated Where Am I? Experience remains optional but promising if it shows Beast-relevant operational context rather than tourism trivia.
9. Weather/environment are contextual inputs, not dashboard clutter.
10. IMU-based auto-rotation is later but now considered a strong useful candidate; rotate UI and touch coordinates together.
11. Terrain/elevation remains useful for later dynamic maps/RF/sky/session views.
12. Homecoming should include truthful Pwnagotchi/session data and only persist derived pretty reports if saved/snapshotted/exported/highlighted.

---

# 12. Audio / visual / camera / I/O — APPROVE / RESERVE SPLIT

APPROVE NOW/FOUNDATION:
1. I/O discovery and capability exposure.
2. Shared semantic output model across TFT/phone/WebUI/audio/LED/haptic destinations.
3. Reuse PipeWire/ALSA/etc. rather than custom audio plumbing.
4. Basic audio control and test path where hardware exists.
5. Full display inventory/truth.
6. Screenshot capability.
7. Camera detection as Provider via mature Pi/UVC stacks.
8. Manual orientation as first-class.
9. Brightness/backlight control where supported.
10. Unified notifications.
11. Graceful output fallback.
12. Hardware arbitration.
13. Doctor integration.
14. Camera/mic detection does not imply always-recording.
15. Full Linux tools remain available.
16. WebUI/Studio live preview is already part of the direction; fidelity is the requirement. Physical TFT remains final visual truth.

RESERVE:
17. Screen recording.
18. Photo/video workflows beyond basic provider support.
19. Phone camera/mic/speaker as temporary providers beyond minimal architecture support.
20. QR/barcode workflows.
21. OCR/computer vision.
22. Media conversion/playback/asset library beyond mature-tool integration.
23. IMU auto-rotation implementation.
24. Multi-display experiences.
25. LED/RGB/haptic expression hardware.
26. Audio recording/spectrum/waveform experiences.
27. Rich accessibility work beyond foundational non-color-only signaling.
28. Chronicle media attachment workflows.

---

# 13. Power / thermal / performance / hardware health — APPROVE

1. Shared health truth source for Doctor, Power Detective, and compact System Health.
2. No invented power/battery telemetry.
3. Battery/UPS/power-monitor devices become Providers when present.
4. Runtime estimates only when justified and labeled Estimated.
5. Power/thermal/USB/storage history is correlated evidence.
6. Distinguish heat from actual throttling.
7. Resource pressure informs Beast-owned scheduling without making degradation the normal solution.
8. Attribute Beast-managed heavy tasks where possible.
9. Power Detective answers causal questions rather than being graph-only.
10. Meaningful alerts only.
11. Managed shutdown may use truthful supported UPS/battery state.
12. Measurements should distinguish Measured / Reported by device / Derived / Estimated / Unknown.
13. Reuse Linux/Pi tooling underneath.

RESERVE:
14. Custom fan curves unless reference hardware requires them.
15. True per-process wattage accounting.
16. Predictive failure claims.
17. Sophisticated anomaly detection until enough real data exists.

---

# 14. Cross-layer X+Y=Z — APPROVE / RESERVE

APPROVE as platform-defining:
1. Situational composability.
2. Hardware Discovery + Software Catalog + Abilities.
3. Search/Abilities question: Can my Beast do X?
4. Multi-radio/resource arbitration.
5. Pwnagotchi + location + map + history operational spatial memory.
6. Doctor + power + USB + radio historical causality.
7. Doctor + Known-Good + fleet evidence + Transactions repair loop.
8. Rich local evidence + sanitized sharing derivative.
9. Plugin config + Config Toolbox + Search + Doctor.
10. System Graph dependency impact and conflict planning.
11. Distributed Search/content availability.
12. Task continuity across surfaces.
13. Power/resource-aware scheduling.
14. Unified semantic outputs for later creature expression.
15. Trusted time + Chronicle + Doctor causality.
16. Live preview + Sandbox + Record/Replay + physical TFT validation loop.
17. Software Catalog + Device Passport + Abilities personalization.

FOUNDATION NOW / POLISH LATER:
18. phone/Beast/WebUI shared session state;
19. phone temporary capability Providers;
20. Homecoming/debrief;
21. obscure-hardware cohort expertise;
22. credential lifecycle guidance;
23. safer plugin experimentation;
24. Smart Inbox/actionable files;
25. owner scripts -> Tools -> Automation;
26. Home Base logistics.

RESERVE:
27. Batch 2 cross-layer brainstorm, all 40 items, including It Happened NOW, Record/Replay-as-Provider, Recovery Island, Fleet-Aware Upgrade Intelligence, Recovery-Backed Experiment Mode, Temporary Deep Watch, Incident Capsule, Config Time Machine, etc. Preserve for later consideration; none are current-release commitments.

---

# 15. Monster / breeding / perception / expression — APPROVE FOUNDATION, RESERVE DEPTH

APPROVE FOUNDATION:
1. Beast senses truthfully; creature interprets those senses through traits, memory, lineage/context, then expresses that interpretation through available outputs.
2. Breeding/progression does not gate fundamental machine capability.
3. Perception maps real Beast Signals/Events into creature senses.
4. Traits/affinities change what the creature notices/values/reacts to, not whether hardware/software exists.
5. Expression is semantic before presentation; TFT/audio/LED/haptic/phone/WebUI render what hardware allows.
6. Creature memory is structured Beast data, not AI memory.
7. Relationship/progression should emerge from real shared history, not forced login streaks.
8. Creature and Doctor remain distinct identities, but can interact.
9. Machine health may influence truthful creature expression; tapping through can reveal Doctor evidence.
10. Owner control always wins over creature preference.
11. AI may enrich dialogue/narration but is optional and may not invent factual session data.

RESERVE DEEP SYSTEMS:
12. Detailed breeding genetics.
13. Recessive/combination traits.
14. Morphology/evolution economy.
15. Cross-device breeding mechanics.
16. Large rare mutation chains.
17. AI-rich creature dialogue system.
18. Deep hardware-expression choreography.
19. Exact reward/probability values until implementation/testing makes them meaningful owner decisions.

---

# 16. Explicit MODIFY decisions from prior discussion

1. Live preview is NOW direction; only high-fidelity rendering/physical validation remains the challenge.
2. Secrets are not omitted locally; they are securely cataloged, redacted by default, and owner-revealable/exportable on explicit request.
3. Privacy emphasis is stronger at the boundary where data leaves Beast; rich local evidence is acceptable where justified.
4. Task progress remains in-context; Task Center is background aggregation, not the only place to see work.
5. Location/field is not a wilderness persona.
6. AI is not a separate required chatbot; Doctor is the preferred conversational front door with swappable AI brains.
7. Zero 2 W support means AI integration cannot require local inference.
8. Mature tool reuse is now a standing design rule.

---

# 17. Explicit REJECT decisions

1. Any architecture requiring AI to operate Beast or Doctor.
2. AI as unquestioned source of truth.
3. AI with implicit unrestricted root authority.
4. Separate Doctor products for radio/display/storage/etc.
5. Breeding/progression gating essential machine features.
6. Fake telemetry, fake percentages, or fabricated battery/power/sensor values.
7. Arbitrary fixed-page limits or artificial ecosystem limits unrelated to actual hardware/resources.
8. Generic form-builder UI for every possible config file.
9. A bespoke Beast shell language.
10. Full graphical process manager clone as a core product requirement.
11. Separate generic cron/systemd-timer GUI when terminal/full tools already cover expert use.
12. Wilderness/camping framing as the defining field identity.
13. Universal always-visible clutter or one top-level app per capability.
14. Hidden removal of technically real capabilities merely because Beast does not manage them.
15. Silent always-on camera/mic recording.
16. Automatic permanent capture of every AI conversation or every derived report as canonical Beast memory.
17. Building replacements for mature external software merely because Beast can.

---

# 18. RESERVE shelf — intentionally not current release scope

Preserve without current implementation obligation:
- Batch 2 cross-layer brainstorm (all 40 ideas);
- Pico/ESP32 role cartridges and remote distributed senses;
- advanced Home Base service catalog;
- deep map/terrain/3D experiences;
- QR/OCR/computer vision workflows;
- rich audio/LED/haptic expression systems;
- deep breeding/genetics/morphology economy;
- specialized/fine-tuned Doctor model;
- voice interface;
- giant autonomous multi-step AI agent;
- advanced anomaly detection/predictive hardware failure;
- cross-device breeding;
- richer multi-Beast pack/fleet social mechanics;
- later data-lab/SQLite explorer/container/Node-RED-style development tools;
- additional media/recording/conversion systems where no concrete release use case exists yet.

Reserve means: architect so these are not blocked, preserve ideas/documents, but do not let them expand the immediate release critical path.

---

# 19. Immediate architecture consequences

The architecture refresh after this reconciliation should explicitly encode:

1. deterministic Beast/Doctor core with optional AI Provider layer;
2. board-scalable architecture from Zero 2 W through Pi 4/5 and external compute;
3. capability/provider graph and dynamic Abilities;
4. shared resource arbitration;
5. shared Signals/Events/Actions/Transactions/Procedures;
6. System Graph + Device Passport + Known-Good + What Changed?;
7. Doctor evidence/probe/repair/verification spine;
8. federated Search/Knowledge and Acquisition Queue;
9. distributed storage/phone/Home Base concepts;
10. presentation independence across TFT/WebUI/phone;
11. high-fidelity live preview with physical TFT truth;
12. foundational creature identity/perception/expression substrate without deep breeding economy yet;
13. mature-tool integration boundaries and Owner Space;
14. truthful privacy/secrets/export boundaries;
15. explicit release-now vs reserved capability ledger.

---

# 20. Build-resume rule

After architecture contracts, capability/tool ledgers, roadmap, and migration order are refreshed from this reconciliation, implementation may resume in meaningful test-backed tranches.

Do not reopen settled product questions during every small implementation step. Ask owner input only when a genuine end-state/product decision, value, irreversible contract, reward economy, naming/tone choice, or major visual fork requires it.
