# Beastagotchi Local Secrets and Doctor Credential Guidance

**Date:** 2026-09-27
**Status:** Owner correction / accepted design direction

## Core correction

For owner-local/internal use, Beastagotchi should not pretend passwords, credentials, tokens, private keys, certificates, API keys, and related secret material do not exist or make them inaccessible.

Use this principle:

> **Catalog everything important; store secrets securely; redact them from ordinary views/logs; reveal them to the owner on explicit request.**

This refines the prior rule:

> **Collect richly where justified locally; share minimally and intentionally.**

## Local handling

- Secrets and credentials may be cataloged as first-class records with metadata such as type, owner, provider/service, scope, creation/import time, expiration if known, last use/verification, and which Beast capabilities depend on them.
- Routine logs, Doctor summaries, support bundles, screenshots, and general UI should redact or mask secret values by default.
- The secret value itself must remain available to the owner on explicit request through an appropriate owner-controlled reveal/export action.
- Local storage should use appropriate protection/encryption and avoid unnecessary plaintext duplication.
- Beast should distinguish between catalog metadata and the secret payload itself.
- Deleting or rotating a secret should first expose what currently depends on it.

## Doctor role

Doctor should help with credential lifecycle rather than simply saying "authentication failed."

Doctor may guide the owner through:
- locating where a password/token/key/certificate is stored;
- identifying which service/provider/action uses it;
- determining whether a credential is missing, expired, malformed, inaccessible, or rejected;
- safely creating/importing/replacing/rotating credentials;
- validating permissions/ownership and file locations;
- installing SSH keys and explaining fingerprints;
- testing a new credential after replacement;
- rolling back or recovering from a broken authentication change where possible;
- backing up/exporting credentials intentionally;
- explaining the consequences of revocation/rotation;
- showing the owner the actual credential value when explicitly requested and policy permits.

Doctor should preserve useful local evidence around authentication failures while avoiding routine secret-value disclosure.

## Sharing boundary

Local/private owner use is different from external sharing.

- **Local Beast / owner-only evidence:** may be detailed and rich.
- **Owner-requested export:** owner chooses what is included; warn when secret material is present.
- **Global Doctor / fleet knowledge:** secret values must not be uploaded; normalize/sanitize evidence.
- **Public/shared support bundle:** redact secret values by default.
- **External/cloud providers:** send only what the provider actually requires and according to explicit owner policy.

## Product implication

Beastagotchi should eventually have a coherent owner-facing Secrets/Credentials substrate rather than scattering passwords and keys through unrelated config files with no inventory.

This does not require building a full password-manager product for initial release. The immediate architecture requirement is:

1. recognize secrets as first-class sensitive resources;
2. know where they live and what uses them;
3. keep ordinary interfaces/logs redacted;
4. make the actual values available to the owner on explicit request;
5. let Doctor provide clear credential setup/recovery guidance;
6. never silently upload them as diagnostic evidence.

