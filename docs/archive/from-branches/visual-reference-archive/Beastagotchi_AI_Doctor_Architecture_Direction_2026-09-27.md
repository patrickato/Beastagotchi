# Beastagotchi AI / Doctor Architecture Direction

Date: 2026-09-27
Status: Recommended direction for owner discussion; not yet final implementation contract.

## Core recommendation

The user-facing experience should treat Doctor as the single companion/assistant identity, while the underlying architecture separates deterministic truth from probabilistic AI reasoning.

- Beastagotchi is the body/platform: capabilities, hardware, actions, transactions, procedures, search, history, permissions, providers.
- Doctor Core is the deterministic clinician: evidence collection, system graph, probes, known-good comparison, confidence, repair verification, rollback, local/fleet case matching.
- AI is an interchangeable cognition/provider layer that Doctor may attach to.
- The user should not need to understand which model is being used in ordinary operation.

This allows the owner to experience "Doctor is the AI" without making Doctor depend on AI for truth.

## Why not train a model to replace Doctor

A trained model cannot by itself know the live state of the machine. It still needs tools to read logs, inspect hardware, query services, test interfaces, compare configuration, and perform verified repairs.

Fine-tuning may improve style, triage habits, domain vocabulary, hypothesis ranking, or procedure drafting, but it does not replace live evidence or deterministic verification.

Therefore the initial path should prioritize:

1. structured Doctor evidence and case data;
2. a model/provider-neutral AI interface;
3. tool/function access to Beast capabilities;
4. retrieval over Doctor knowledge, manuals, owner notes, and Global Doctor cases;
5. deterministic action execution through Beast Actions/Transactions/Procedures;
6. optional later fine-tuning on verified Doctor cases if real data proves it worthwhile.

Do not train a bespoke Doctor foundation model first.

## User experience

The user talks to Doctor.

Example:

"My TFT is white again. It worked yesterday. Figure it out."

Doctor Core gathers machine census, current display state, kernel/device-tree evidence, recent changes, known-good state, relevant case history and documentation. The attached AI provider interprets and discusses that evidence, requests additional probes through Doctor where useful, and proposes a repair. Beast executes any approved managed repair through its existing transaction/action authority system and Doctor performs functional verification.

The user sees one continuing Doctor conversation rather than separate "Doctor" and "AI chatbot" products.

If no AI is available, the same Doctor case remains usable through deterministic Guided UI and evidence views.

## External AI is a first-class design, not a fallback

The Beast device should not be required to host the strongest model. An AI package on Beast should primarily provide the integration/client/provider infrastructure. A model may live elsewhere.

Potential providers:

- local lightweight model on Beast where hardware permits;
- paired phone;
- Home Base / desktop / laptop;
- owner self-hosted inference server;
- optional cloud provider;
- future compatible providers.

The ordinary user can choose Automatic routing and simply talk to Doctor.

## Hardware tiers

### Pi Zero 2 W

Deterministic Beast/Doctor functionality remains available. Do not assume a useful general-purpose local LLM. AI package acts mainly as a thin client to an external provider. Keep memory/CPU/network overhead small and allow complete no-AI operation.

### Pi 4

Same architecture. Tiny local language/embedding/classification components may be possible later, but should not compete with Pwnagotchi/Bettercap/Beast workloads merely to claim that AI runs locally. External AI is the preferred route for serious reasoning.

### Pi 5

Optional small local models become more plausible for basic offline conversation, summarization, intent parsing, and creature expression, but must still be optional and resource-managed. Strong external AI remains useful.

### Home Base / capable PC

This is the preferred private high-power local AI tier when available. A GPU-equipped desktop can run substantially stronger models while Beast remains the live sensor/action endpoint.

### Cloud provider

Optional. Useful for strongest general reasoning and coding when owner policy permits. Data routing/redaction rules apply.

## Provider independence

Do not hard-code the product to one vendor or model family. Define an AI Provider interface and advertise provider capabilities such as:

- text reasoning;
- structured tool calling;
- context window;
- vision;
- code ability;
- latency;
- local/remote classification;
- privacy policy chosen by owner;
- cost/availability metadata;
- maximum context accepted.

Doctor chooses an appropriate available provider, or the owner can pin one.

## Model specialization

Initially use prompting, structured context, tool schemas and retrieval rather than bespoke training.

A future specialized Doctor model/adapter is possible after a large corpus of verified cases exists. Potential uses include:

- triage/hypothesis ranking;
- selecting high-information probes;
- translating raw evidence into clear explanations;
- generating candidate Procedures;
- predicting relevant known cases;
- distinguishing likely hardware, software, configuration, power and dependency failures.

Any specialized model remains advisory until deterministic evidence/verification confirms outcomes.

## Tool boundary

AI can request Beast capabilities but does not gain magical root authority.

Examples:

- request Doctor probe;
- query System Graph;
- search local/global knowledge;
- inspect Device Passport;
- invoke registered Action;
- start Transaction;
- execute validated Procedure;
- request software acquisition;
- open Full Tool / Owner Space for the owner.

AI-triggered managed actions use the same permissions, receipts, rollback, history and verification as button-triggered actions.

An owner-configured unrestricted/self-hosted model may be supported as an AI provider. The model's behavioral restrictions do not define Beast's action authority. An unrestricted model does not automatically receive unrestricted machine control. Owner Space remains the explicit path for raw Linux/root operation.

## Secrets and privacy

Local Doctor evidence may remain rich. Remote AI receives only context allowed by owner policy.

Secrets are not casually placed into model context. When a task legitimately requires a credential, Beast should provide the minimum required credential to the relevant operation rather than expose the raw value to conversational context by default. The owner retains explicit reveal/export authority.

Suggested routing policies:

- Local only;
- Home Base/local network allowed;
- Remote allowed after sanitization;
- Remote allowed.

## Doctor memory and AI memory

Doctor/Beast structured state is authoritative memory. AI conversation history is not the database.

Persisted truth includes Device Passport, known-good state, incidents, cases, procedures, owner notes, configuration history, progression, capability state and verified outcomes.

AI may read these. AI may propose new notes or case conclusions. Persistence should be explicit or governed by well-defined Beast rules.

## One Doctor, potentially many brains

The user should not see a collection of independent AI personalities for diagnostics. Doctor remains one coherent identity/session.

Internally different providers can serve different jobs. A cheap/light provider may handle simple conversation while a stronger Home Base or cloud model is invoked for a difficult case. This routing is an implementation detail unless the owner wants to inspect it.

## AI-enhanced Doctor loop

1. Owner states problem naturally.
2. Doctor creates/continues a case.
3. Deterministic machine census and evidence collection occur.
4. Relevant knowledge is retrieved.
5. AI interprets evidence and proposes hypotheses/next probes.
6. Doctor executes approved probes.
7. AI updates reasoning from new evidence.
8. When sufficient confidence exists, AI proposes a managed repair.
9. Beast exposes exact intended changes when appropriate.
10. Action/Transaction/Procedure engine performs repair.
11. Doctor functionally verifies the result.
12. Failed repair can roll back.
13. Case outcome is retained as structured knowledge.
14. AI explains the result at the owner's desired level.

## Product identity

Recommended mental model:

**Beastagotchi is the body. Doctor is the clinician/companion. AI is an interchangeable brain Doctor can borrow.**

To the ordinary user, this can simply feel like "Doctor".

The architecture therefore supports very small boards, powerful local PCs, phones, self-hosted models and cloud models without fragmenting the user experience or making core functionality dependent on AI.
