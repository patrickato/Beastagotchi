# ADR 0003 — Exactly one physical presentation owner

**Status:** planned/accepted direction

Stock Pwnagotchi, Theme Manager and Beast UI may coexist as installed capabilities, but only one owns the physical framebuffer/touch device at a time. Ownership changes should use prepare → release → acquire → health check → commit, with rollback to the previous owner on failure.

Rationale: renderer/touch races are unacceptable and unnecessary.
