# ADR 0002 — Canonical state flows through Beast Core

**Status:** accepted

Multiple UIs/modules should consume canonical state/history from Beast Core instead of independently polling and interpreting the same OS/Pwnagotchi/Bettercap sources.

Rationale: one source of truth improves consistency, reduces duplicated CPU/heat, and makes WebUI/TFT/external displays agree.
