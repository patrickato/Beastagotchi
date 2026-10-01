# Beastagotchi Capability Expansion — Content / Knowledge / Search / Maps / Offline Library / Internet Acquisition

**Date:** 2026-09-27
**Status:** active capability-expansion cluster; candidate directions for owner discussion

## Standing design rule

Prefer mature existing engines/tools when they already solve the hard problem well. Build Beast-native code where the missing value is integration, orchestration, discovery, presentation, provenance, caching, lifecycle, policy, or cross-system composition.

## Core concept

Beast should become a portable, selectively synchronized knowledge system that remains useful online and offline and can answer from multiple sources without pretending they are all the same.

Desired model:

**Search request -> Search Broker -> relevant providers -> ranked/provenanced results -> optional acquisition/cache -> open/use in place**

Potential source classes:
- live Beast state/capabilities/settings/hardware;
- Beast/Pwnagotchi/Bettercap docs;
- local owner files and project notes;
- Doctor local knowledge and prior cases;
- Global Doctor/fleet knowledge;
- Kiwix/ZIM offline content;
- local manuals/datasheets/PDF/TXT/Markdown/HTML;
- maps/geodata;
- astronomy/satellite data;
- SDR/radio reference data;
- owner NAS/PC/phone/Home Base stores;
- Internet search/current docs/GitHub/project sites when online.

## Candidate capabilities

1. One federated Search surface rather than many unrelated search boxes.
2. Results must identify source/provenance and freshness; offline/local/global/current web are not interchangeable.
3. Search should be capability-aware and context-aware rather than merely file-text search.
4. Local full-text search should reuse a mature engine such as Recoll/Xapian where appropriate; narrower structured stores may use SQLite FTS and exact code/file lookup may use tools such as ripgrep.
5. Search result types can include settings, files, docs, Doctor cases, Procedures, hardware, software catalog entries, maps/places, Expedition/history data, source code, packages and Internet results.
6. Search filters should support source, type, date/freshness, local/offline/online, capability, project/workspace and provenance.
7. Search should work without Internet and improve when Internet becomes available.
8. Internet results should augment local truth rather than replace it.
9. Search can expose `Search locally`, `Search downloaded knowledge`, `Search Doctor`, `Search web`, and `Search everywhere` as explicit scopes without forcing separate products.
10. SearXNG is a candidate optional online metasearch engine/provider because it exposes an HTTP search API and can be self-hosted, but Beast should not depend on public instances or require local Pi hosting by default.
11. Online providers can instead include project-specific official APIs/docs/search sources where useful, with a common Search Provider contract.
12. Kiwix should be evaluated as the primary offline web-knowledge engine. It already runs on Raspberry Pi, reads compressed ZIM archives and can serve them over the local network.
13. Beast should not reimplement Kiwix; integrate its catalog/files/server/search into the Field Library/Knowledge experience.
14. Kiwix content categories could include Wikipedia, Wiktionary, Project Gutenberg and other freely distributable collections available in its catalog.
15. Content licensing/provenance must be respected; Beast should not assume arbitrary websites may be mirrored. The Kiwix WikiHow removal is a concrete reminder that source permission can change.
16. Offline knowledge should be selectable rather than all-or-nothing. Kiwix already exposes mini/nopic/maxi variants for some large collections; Beast can explain storage tradeoffs.
17. Library items should show size, version/date, source, license/provenance where available, installed location, update availability and whether currently searchable.
18. One-click `Download`, `Queue`, `Remove`, `Open`, `Search`, `Move` should parallel the Software Catalog interaction model.
19. Large knowledge files can live on Pi storage, phone, NAS/Home Base, PC/laptop, removable storage, owner cloud, or another configured provider. The logical Library should not assume one physical storage location.
20. Beast should support storage-provider awareness: content can be `local now`, `available nearby`, `available at Home Base`, `online only`, or `queued`.
21. Phone can be a content cache/provider for selected maps/manuals/ZIMs rather than merely a UI client.
22. Browser/PWA storage can be used as an opportunistic cache but never the sole durable copy.
23. Home Base can refresh indexes, download large datasets, sync library selections and stage updates according to owner policy.
24. Acquisition Queue should be reused for content: map region, manual, ZIM, astronomy data, firmware, package, dataset, etc.
25. Search results should be able to offer `Get this for offline use` when a source supports lawful local caching/download.
26. Downloads should remain distinct from install/apply. Acquiring a manual or package does not imply changing the system.
27. Beast should avoid silently retaining large transient downloads forever; content policy should distinguish cache vs intentionally saved library item.
28. Maps should be a shared geospatial capability, not a single app owned by Expeditions.
29. MapLibre is a strong rendering candidate; local PMTiles files can be read directly by MapLibre Native, making single-file offline vector-map regions practical.
30. Beast should support user-selected offline map regions rather than requiring an entire country/world dataset on the Pi.
31. Offline map packages should show estimated size before download and allow deletion/move to another storage provider.
32. Maps can serve Expeditions, Homecoming, GPS, ADS-B, AIS, Meshtastic, RF observations, celestial context, owner POIs and future tools.
33. Base map truth and overlay truth should remain separate: route, aircraft, vessel, RF/sensor observation and Pwnagotchi discovery layers should not be baked into tiles.
34. Map data freshness should be visible where relevant.
35. A map-location acquisition action such as `Download this area` could use current viewport/route/region selection.
36. Field Library should include owner-added PDFs, manuals, datasheets, Markdown/TXT, READMEs and other reference files.
37. Beast should extract/index searchable text where technically possible, preserving original files rather than replacing them with conversions.
38. Search snippets should link back to exact source document/page/section where possible.
39. Hardware discovery can connect directly to relevant local manuals/datasheets if present; otherwise Search/Acquisition can locate them.
40. Doctor can query the same Library/Search system rather than maintaining a separate giant documentation silo.
41. Doctor search ranking should favor exact patient compatibility, provenance, current versions and verified fleet evidence.
42. Guided Software can query the same knowledge layer for tutorials/reference material.
43. Workshop Projects can later attach selected manuals, notes and source references without duplicating the whole Library.
44. Astronomy data should be handled as datasets/providers rather than hand-authored static content. Current satellite orbital data can come from sources such as CelesTrak and be cached with explicit age/freshness.
45. Satellite identifiers/data formats should be future-tolerant; CelesTrak moved beyond 5-digit catalog-number assumptions in 2026, illustrating why Beast should not hardcode old TLE-only assumptions.
46. Celestial calculations should prefer local computation from downloaded datasets/time/GPS where practical, preserving offline operation.
47. SDR/radio reference data should follow the same provider model: local cached datasets where licensing allows, owner-added references, current online sources where permitted.
48. Search should distinguish factual data sources from owner notes and community guidance.
49. Owner notes should be first-class searchable content but clearly labeled as owner-authored.
50. Search history is optional and should be privacy-governed; federated search itself should not require global query logging.
51. Public/global Beast services should receive only the minimum query/context required for the selected provider.
52. A result can be useful without being imported into Beast. Open external source in phone/WebUI/full browser when appropriate.
53. `Save for offline` should preserve provenance/source URL/version/date where available.
54. Knowledge updates should be incremental where the underlying format supports it; where it does not (e.g. Kiwix ZIM currently lacks general incremental updates), Beast should tell the owner the replacement download size before acting.
55. Duplicate datasets/content should be detected where practical by hashes/identity rather than silently consuming storage twice.
56. Search and Library should expose storage impact so the owner can decide how much knowledge lives locally.
57. Field-use defaults should favor compact, relevant knowledge rather than enormous archives merely because storage can be filled.
58. Home Base/NAS/phone can hold larger master libraries while the Beast carries a selected working set.
59. A `Keep Nearby` or equivalent policy could express that selected content should be available either on Beast or a paired nearby provider; exact UX remains open.
60. Search Broker should permit future AI-based synthesis without making AI mandatory. Deterministic search/provenance remains usable independently.
61. Search results should never silently blend AI inference with source text; if AI is later added, generated summaries must remain distinct from retrieved evidence.
62. Online acquisition must honor source licensing/terms and avoid treating arbitrary web scraping as a universal mirroring mechanism.
63. Public Beast project resources can use GitHub Releases/Pages and the previously discussed free backend architecture where appropriate.
64. Global Doctor structured knowledge should remain separate from bulk document hosting, allowing a small/free structured backend to serve high-value case metadata.
65. Beast should support a provider-neutral backend interface so public knowledge/catalog services are not permanently locked to one hosting vendor.
66. The user-facing target is not `where is this file stored?` but `do I have this knowledge available right now, and if not, where can I get it?`

## Strong emerging identity

> Beastagotchi can carry a small, relevant working library in the field, borrow larger content from a phone/Home Base when nearby, search the current Internet when available, and always show where an answer came from.

This is a shared platform capability for Doctor, Guided Software, Hardware Bench, Expeditions, SKY/FIELD, Workshop, Search and future AI—not another isolated app.
