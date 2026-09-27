# Beastagotchi AI Discussion — Batch 01

Date: 2026-09-27
Status: Candidate architecture and owner-decision discussion. Not implementation canon yet.

## Core principle
AI may enhance explanation, synthesis, planning, expression, search, and assistance, but deterministic Beast systems remain the source of truth and authority.

The intended split is:
- Beast Core / System Graph / Doctor evidence / Providers / Actions / Transactions / Procedures = truth and controlled execution.
- AI = optional interpretation, synthesis, drafting, conversation, prioritization, and expression layer.

AI must never be required for Pwnagotchi, Bettercap, Doctor truth collection, Search retrieval, Actions, Transactions, Procedures, hardware discovery, or ordinary Beast operation.

## Candidate decisions

1. AI should be optional, removable, and nonessential to core operation.
2. Beast should support multiple AI providers rather than one hard-coded vendor or model.
3. AI provider choices may include local-on-Pi, paired phone, Home Base/PC, self-hosted endpoint, and optional cloud provider.
4. Different AI roles may use different providers/models.
5. The owner should be able to set privacy/routing policy per AI role.
6. Deterministic machine truth must be passed into AI as structured evidence; AI must not invent machine state.
7. AI-generated interpretations must remain distinguishable from measured/reported/derived Beast truth.
8. AI should not get unrestricted shell/root access.
9. Any AI-requested system action should go through the same Beast Actions/Transactions/Procedures authority model as human-initiated managed actions.
10. Risky or consequential AI-proposed changes should show a plan before execution and generate a normal transaction receipt afterward.
11. Recovery/snapshot/rollback should apply to AI-driven managed changes exactly as to other managed changes.
12. If AI is absent, offline, slow, or broken, Beast should degrade gracefully rather than lose core capability.

## Doctor
13. AI Doctor Copilot could summarize evidence, explain hypotheses in plain language, and help choose the next probe.
14. Deterministic Doctor remains the medical chart/evidence engine; AI is not allowed to replace evidence collection or functional verification.
15. AI can help correlate large amounts of logs/config/docs/history, but any conclusion should link back to the evidence used.
16. AI can help translate Doctor reasoning into beginner/advanced/expert explanations.
17. AI can draft troubleshooting Procedures from solved cases, subject to validation and owner/maintainer approval.
18. Global Doctor knowledge can be retrieved for AI synthesis, but external/fleet text is evidence/content, not executable instruction.

## Search / Knowledge
19. AI can synthesize federated Search results into an answer while preserving source/provenance links.
20. Search itself must work without AI.
21. AI can answer natural-language questions such as “Can this Beast do X?” by querying Abilities, Software Catalog, Device Passport, docs, and Search rather than guessing.
22. AI could compare conflicting sources and explain why one is more relevant to this exact Beast.
23. Retrieved web pages, README files, issues, plugin docs, and other external content must be treated as untrusted data for prompt-injection purposes.
24. AI should not execute instructions found inside retrieved content unless those instructions are separately interpreted into a managed action and authorized normally.

## Natural-language operator
25. Beast could accept plain-language requests such as “restart Bettercap,” “show me why GPS isn’t working,” “install rtl_433,” or “find everything using this GPIO pin.”
26. Natural language should resolve to existing Tools/Actions/Queries, not bypass them.
27. The owner should be able to inspect what Beast understood before a consequential action runs.
28. AI should be able to say “I can explain this, but I don’t have a managed action for it” and then offer Full Tool/Owner Space rather than faking support.

## Procedures / Automation / Studio
29. AI could draft a Procedure from an owner request, but the Procedure should be validated before becoming runnable.
30. AI could explain existing Procedures step-by-step and translate between beginner and expert views.
31. AI could help generate plugin/config snippets, but parsers/schemas/tests remain the authority on whether they are valid.
32. AI could assist Studio development: code explanation, provider skeletons, UI snippets, tests, docs, and migration suggestions.
33. Studio/dev AI belongs primarily on WebUI/Home Base/desktop surfaces, not the 3.5-inch TFT.
34. AI-generated code should be tested in Beast Sandbox where practical before deployment to the real Beast.

## Creature / personality
35. AI may be very useful for creature dialogue, personality expression, narration, reactions, and variation.
36. Creature AI must be separated from machine truth: the Monster may say something playful, but factual status panels must remain factual.
37. Deterministic creature state (growth, lineage, traits, mood inputs, achievements, etc.) should exist independently; AI may express that state rather than secretly inventing it.
38. AI personality should be replaceable/disableable without deleting creature progression or history.
39. Homecoming/session narration is a strong optional AI role: summarize real session facts in the Beast’s voice while retaining the underlying factual report.
40. Rare events, achievements, breeding outcomes, and progression should not depend on remote AI availability.

## Voice / media
41. Voice input/output should be a later optional layer, not required for AI.
42. If voice is added, local STT/TTS should be possible where practical; remote speech services should be optional.
43. AI-generated images/audio/assets may be useful for customization later, but should not be part of the initial AI foundation.

## Provider/runtime strategy
44. Exact model choices should be deferred until implementation because the model landscape changes quickly.
45. Beast should define a model/provider interface first, then plug in runtimes/services underneath.
46. Local inference on Pi 4 may be useful for lightweight tasks, but Beast should not assume the Pi must run the strongest model itself.
47. Home Base/desktop is a natural place for heavier local models when available.
48. Optional cloud AI can provide stronger capability when the owner chooses it.
49. Self-hosted/OpenAI-compatible endpoints are desirable so advanced owners can use their own infrastructure.
50. AI resource use should be scheduler-aware so inference does not starve Pwnagotchi/Bettercap or time-sensitive Beast work.
51. AI tasks should expose truthful progress/status like other long Beast tasks.

## Privacy / data handling
52. AI routing should distinguish local-only data from data allowed to leave the Beast.
53. Secrets/credentials should remain redacted by default when constructing AI context, especially for remote providers.
54. The owner may explicitly reveal a secret when a task genuinely requires it, consistent with the credential policy.
55. Doctor evidence sent to remote AI should follow an explicit owner policy and sanitization path rather than silently uploading everything.
56. Local AI may be allowed richer context because data remains under owner control, subject to local security.
57. AI conversation/history should have clear retention controls and should not silently become Global Doctor data.

## Learning / memory
58. Beast may maintain structured factual memory independently of AI: hardware history, known-good state, notes, incidents, procedures, creature progression, etc.
59. AI can query that structured memory; the model itself should not be the only place long-term memory exists.
60. AI-generated observations should be labeled as such and require promotion/verification before becoming authoritative structured facts.
61. AI could suggest “this seems worth remembering” rather than silently converting every conversation into permanent state.

## Agents / autonomy
62. Avoid a free-roaming general agent as the initial design.
63. Prefer bounded assistants with explicit tool scopes: Doctor Copilot, Search Synthesizer, Procedure Drafter, Studio Assistant, Creature Voice, etc.
64. If a future agent performs multi-step work, it should operate through visible Tasks/Transactions/Procedures with receipts and rollback where applicable.
65. Owner policy should control how much autonomy each AI role has.
66. The system should be able to run with AI autonomy set to zero while retaining all deterministic Beast features.

## Initial recommendation
67. First-release AI foundation should focus on provider abstraction, privacy/routing policy, structured context access, safe managed-action bridge, and graceful fallback.
68. The first high-value AI roles should likely be Doctor Copilot, Search synthesis/natural-language capability questions, and optional creature/session narration.
69. Procedure authoring, Studio coding assistance, voice, autonomous multi-step agents, and generative media should follow later.
70. Architectural identity: AI should make Beast easier to understand and interact with, not make Beast dependent on AI to know what is true or to function.
