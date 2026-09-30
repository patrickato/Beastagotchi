# Beastagotchi Capability Expansion — Physical World / Environment / Location / Field Cluster

**Date:** 2026-09-27
**Status:** active capability-expansion discussion record; candidate directions pending owner reconciliation

## Core principle

> Location is not a page. It is a shared sense. Weather is not a widget. It is environmental context. Maps are not decoration. They are the common spatial substrate.

Reuse mature engines and public/open data sources first. Beast should supply integration, orchestration, caching, offline behavior, provenance, Guided presentation, and cross-capability context rather than rebuilding mature GPS/map/weather/astronomy systems.

## Candidate capability directions

1. Shared Location Provider: GPS/GNSS from gpsd or other providers feeds every interested Beast subsystem rather than belonging to one app.
2. Position confidence and source provenance: distinguish dedicated GNSS, phone-provided location, network-derived location, stale last-known location, simulated Sandbox position, or unknown.
3. Location health: fix quality, satellites used/seen, HDOP/VDOP where available, age of fix, altitude source, update rate, and hardware status.
4. Guided GPS onboarding and diagnostics using mature gpsd tooling rather than writing a GPS daemon.
5. GPX/KML/GeoJSON import/export for routes, points, Expeditions, owner POIs, and interoperability with existing mapping software.
6. Expedition recording: route, time, distance, stops, relevant observations, system conditions, and owner-selected provider data.
7. One map substrate with overlay providers: Expedition routes, Pwnagotchi observations, ADS-B, AIS, Meshtastic, sensors, owner POIs, Doctor incidents, satellite/sky projections where appropriate.
8. Offline map packages selectable by region/area, with local-first use and clear storage estimates.
9. "Download this area" as a Guided operation above an appropriate open map packaging/rendering stack.
10. Routing as a provider, not hard-coded into the UI. Reuse open routing engines/services such as Valhalla where sensible; regional/offline routing may be optional due storage/CPU cost.
11. Driving/walking/bicycle route modes when a configured routing provider supports them.
12. Route corridor download/preparation: optionally stage map/reference material for a planned trip or field area.
13. Owner POI collection: campsites, fishing spots, repeat test locations, hardware sites, Home Base, etc., with import/export and no mandatory cloud.
14. Geofenced owner automations: trigger owner-approved Beast behaviors on entering/leaving named regions, with obvious privacy controls and easy disable.
15. Home Base can be partly location-aware, but trusted-network/power identity remains stronger than GPS alone.
16. "Where am I?" field card: coordinates, approximate place name if a geocoder is available, altitude, heading/speed if meaningful, and data provenance.
17. Offline reverse-geocoding/place-name support should use packaged regional data or owner-configured provider rather than abusing public geocoding endpoints.
18. Public Nominatim is not a generic backend for Beast at scale; its published use limits require light, cached, identified use and forbid heavy/systematic usage. Treat geocoding as a replaceable provider.
19. Weather as environmental context: current conditions, forecast, alerts, sunrise/sunset-related context, and historical/provider observations where useful.
20. In the U.S., NWS API can provide free forecasts, observations, and alerts; it should be one provider, not a globally hard-coded dependency.
21. Weather provider abstraction should allow regional/international alternatives and offline last-known data.
22. Severe-weather awareness: active warnings/watches/advisories relevant to current or planned location; notify according to owner policy without becoming noisy.
23. NOAA Weather Radio receive path can complement Internet weather when SDR/radio hardware is available, keeping receive-side behavior distinct from API data.
24. Local environmental sensors can override/complement remote weather: BME280-type temperature/humidity/pressure, light, air quality, etc., always labeled by source.
25. Compare local sensor vs forecast/provider values rather than silently mixing them.
26. Barometric trend as a useful field signal when pressure hardware exists; do not pretend forecast certainty from one cheap sensor.
27. Temperature/humidity/pressure trends can feed Expeditions, Homecoming, alerts, creature expression, and Doctor hardware health where relevant.
28. Environmental sensor calibration metadata belongs with the sensor/provider rather than in arbitrary UI code.
29. Compass/heading support should distinguish GNSS course-over-ground from actual magnetometer heading.
30. Magnetic declination correction can use a standard model such as NOAA/NGA/BGS World Magnetic Model data; model/version should remain replaceable and updateable.
31. Orientation/IMU support can become another sense when hardware exists: acceleration, orientation, motion, tilt, vibration; do not assume every Beast has it.
32. Light sensing can drive truthful ambient UI choices, field observations, or automation when an actual sensor is present.
33. Sound-level sensing may be possible with microphone/hardware, but recording/privacy are separate explicit capabilities and policies.
34. Time is a field capability too: system time quality, GNSS time if available, timezone derived from configured/location provider, sunrise/sunset/twilight, and reliable event timestamps.
35. Chrony/NTP/GNSS/PPS can be integrated for accurate time without Beast inventing a time daemon.
36. SKY remains a strong shared field experience: real Sun, Moon, planets, stars/constellations, satellites/ISS passes, and actual location/time context.
37. Astronomy calculations should work offline where practical using local libraries/catalogs; network is mainly for data refresh (e.g., orbital elements), not every computation.
38. Satellite-pass preparation can connect to SDR/SatDump later: pass time, elevation, azimuth, frequency/doppler context, required hardware/profile, and optional reminder.
39. "What's Above Me?" can combine celestial bodies, satellites, ADS-B aircraft, and perhaps weather layers without conflating their source types.
40. "What's Around Me?" can combine map, Expedition, Pwnagotchi observations, Meshtastic nodes, environmental sensors, owner POIs, and other authorized nearby information.
41. Nearby-data categories should be individually toggled and source-labeled; no giant permanent cluttered radar view is required.
42. Terrain/elevation can be a map/data provider: elevation at current point, route profile, climb/descent, and useful field context when datasets are present.
43. Water/coastal data can be provider-based. In the U.S., NOAA CO-OPS exposes tides, water levels, currents and related station data through public APIs.
44. Tide/current data should only surface where geographically relevant; inland users should not see irrelevant marine clutter.
45. Field reference data can be location-sensitive: nearby repeaters/frequency references, weather stations, trail/park data, owner POIs, astronomy, maps, and hardware/radio reference sets where lawful/licensed.
46. Do not create one monolithic "Field database". Use content/search providers and shared geospatial IDs so datasets can be added/replaced independently.
47. Cached field data should expose age/freshness. A 6-month-old forecast is not a forecast; a 6-month-old topo map may still be useful.
48. Connectivity-aware refresh: update volatile data (weather/alerts/orbital elements) opportunistically; static datasets (maps/manuals) follow separate update policy.
49. Acquisition Queue ties directly into Field: missing maps, forecast data, orbital data, reference packages, manuals, or regional datasets can queue for Internet/Home Base.
50. Paired phone may provide temporary GPS, Internet, camera, compass/IMU or richer map interaction when available, but Beast must still operate without it.
51. Phone-provided sensors should be explicit providers and disappear gracefully when disconnected.
52. Location privacy must be owner-controlled per destination/use; local display and local logging are not equivalent to uploading coordinates.
53. Global Doctor/case uploads should never include location by default merely because GPS exists.
54. Expedition/route retention should have clear policies: live only, short-term, saved Expedition, exported, or discarded.
55. Search should understand spatial queries eventually: manuals/data relevant to current hardware/location, owner POIs, past Expeditions, maps, nearby provider content.
56. Guided field presentation should stay compact on TFT; phone/WebUI can show full maps, timelines, route profiles and overlays.
57. Field capabilities should remain useful with every decorative/creature layer disabled.
58. Creature expression can react to truthful environmental context later (night, storm warning, cold, sunrise, satellite pass, etc.), but factual systems remain independent.
59. Weather/alerts/location should never become fake telemetry; unknown/offline/stale states must be visibly distinct.
60. Overall identity: Beast can become a local-first field computer that understands its physical context and shares that truth with every relevant capability instead of maintaining disconnected weather/GPS/map apps.

## Reuse-first candidates

- gpsd for shared GPS/GNSS access and related CLI tooling.
- chrony/NTP/GNSS/PPS for time discipline where appropriate.
- MapLibre/local PMTiles for map rendering/data already discussed.
- Valhalla or another open routing provider where routing is worth the storage/runtime cost.
- National Weather Service API as a U.S. provider for forecasts/observations/alerts.
- NOAA/NCEI World Magnetic Model for magnetic declination/model-based heading correction.
- NOAA CO-OPS APIs for U.S. tide/current/water-level data when relevant.
- Mature astronomy libraries/catalog providers for offline sky calculations and replaceable orbital data.

## Walk-the-line / open-platform note

Physical-world capabilities should be broadly available. Managed Beast workflows should be truthful, privacy-aware and owner-controlled. Full external map/GIS/navigation/radio tools may coexist. Owner Space remains open; Beast does not artificially block owner-installed software merely because Beast does not manage or guarantee it.
