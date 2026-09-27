# Beastagotchi Capability Expansion — Audio / Visual / Camera / Media / I/O

**Date:** 2026-09-27
**Status:** capability-expansion brainstorm; many items intentionally deferred for later development

## Standing rule

Prefer mature existing tools/frameworks and integrate them. Build Beast-native code primarily where integration, orchestration, capability discovery, lifecycle, presentation, policy, or cross-layer behavior is missing.

Current mature building blocks worth reusing:
- Raspberry Pi `libcamera` / `rpicam-*` / Picamera2 for camera capture and camera APIs.
- PipeWire for Linux audio/video routing and device graph management.
- FFmpeg for capture, conversion, filtering, inspection, and transcoding.
- mpv for flexible lightweight media playback and scriptable control.

## Release-priority framing

Use explicit statuses:
- **NOW** — belongs in first serious release path.
- **LATER** — preserve, but do not spend release effort yet.
- **MAYBE** — interesting; needs a concrete use case.
- **REUSE** — integrate a mature existing engine/tool instead of reimplementing it.

## Candidate capability directions

1. **NOW / REUSE — Device discovery and capability registration.** Detect microphones, speakers, USB audio, Bluetooth audio, cameras, displays, LEDs, haptics, and relevant USB/CSI devices. Register what they can do without pretending unsupported hardware is known.

2. **NOW — Shared output routing.** A common Output/Expression capability model should know available display/audio/haptic/LED targets. This is infrastructure for alerts, Doctor, future Monster expression, and accessibility.

3. **NOW / REUSE — Audio device routing through PipeWire where appropriate.** Expose simple default source/sink selection and clear device naming; advanced users retain full underlying tools.

4. **NOW — Basic sound playback capability.** Alerts, UI sounds, optional notification tones, and future creature audio should reuse one audio output path rather than each feature inventing its own.

5. **NOW — Volume/mute/output selection.** Small but necessary operational capability, with per-output awareness where possible.

6. **NOW — Display/output inventory.** Enumerate the TFT, HDMI/DRM/framebuffer outputs, orientation, resolution, touch mapping, and availability. Reuse the same truth for UI, Doctor, screenshots, and future multi-display work.

7. **NOW — Screenshot/export current display state.** Useful for support, visual testing, Doctor evidence, Studio, and sharing. Must preserve provenance of what surface/version was captured.

8. **LATER — Screen recording.** Useful for bug reports/tutorials/demos, but not essential to first release.

9. **NOW / REUSE — Camera detection and health.** If a Pi camera/USB camera exists, identify it, report basic capabilities, and make it available through a Provider. Reuse libcamera/rpicam/Picamera2 rather than writing a camera stack.

10. **LATER — Guided still-photo capture.** Simple photo capture and preview from supported camera devices.

11. **LATER — Guided video capture.** Simple recording with sensible defaults, delegating encoding to existing camera/FFmpeg tooling.

12. **LATER — Camera as temporary Beast sense.** Camera presence can expand Abilities and later perception/Monster systems without making camera hardware a requirement.

13. **LATER — Phone camera as temporary Provider.** If paired phone integration eventually supports it, the phone can lend camera/QR/document capture capability to Beast.

14. **LATER — QR/barcode scanning.** Strong practical candidate for pairing, URLs, package/project identifiers, hardware labels, Wi-Fi credentials, or future workflows. Prefer mature decoder libraries.

15. **MAYBE — OCR/document capture.** Could help manuals/labels/serial numbers, but only if a real use case justifies the complexity.

16. **LATER — Computer vision/object detection.** Raspberry Pi's modern camera stack supports post-processing possibilities, but this should not become early-release scope without a concrete Beast use case.

17. **NOW / REUSE — Media inspection.** ffprobe/FFmpeg can expose codec, duration, resolution, bitrate, channels, metadata, etc. Useful whenever users import media/assets.

18. **LATER / REUSE — Media conversion toolbox.** Guided wrappers around FFmpeg for common conversions; full FFmpeg remains accessible.

19. **LATER / REUSE — Lightweight playback.** mpv is a strong existing engine for audio/video playback instead of a custom Beast player engine.

20. **LATER — Media/asset preview inside WebUI/Studio.** Especially useful for themes, animations, sounds, creature assets, screenshots, and content packs.

21. **LATER — Theme/animation preview pipeline.** Use the real rendering/assets where possible so users can preview what will actually appear on TFT/WebUI before deploying.

22. **NOW — Orientation as a first-class display property.** Manual landscape/portrait selection, persisted per surface where useful.

23. **LATER — Automatic orientation from IMU.** A later hardware expansion can auto-rotate UI and touch mapping; Experiences may optionally declare preferred orientation while owner retains lock/override.

24. **LATER — Multi-display support.** Useful eventually for larger companion displays, HDMI dashboards, development, kiosks, etc.; not a release blocker for the reference TFT.

25. **NOW — Brightness/backlight control where hardware supports it.** Simple manual control first; ambient-light automation later.

26. **LATER — Ambient-light-driven brightness.** Requires optional sensor hardware and should remain a later enhancement.

27. **LATER — LED/RGB output Provider.** Addressable LEDs or simple RGB indicators can become generic expression/notification outputs if hardware exists.

28. **LATER — Haptic/vibration output Provider.** Useful with supported external hardware or phone; later expression/accessibility capability.

29. **LATER — Buzzer/speaker notification profiles.** User-selectable alert styles rather than hard-coded sounds.

30. **LATER — Audio input/microphone Provider.** Record/inspect audio where hardware exists. Voice/AI semantics explicitly deferred to the separate AI discussion.

31. **LATER — Basic audio recorder.** Could support notes, debugging, signal capture, or future voice features. Reuse existing Linux audio stack.

32. **LATER — Audio waveform/level visualization.** Potentially useful in Radio/Workshop/diagnostics; not needed early.

33. **LATER — Spectrum/audio analysis tools.** Reuse mature DSP/audio utilities where useful; do not duplicate SDR tooling.

34. **MAYBE — Local sound-event detection.** Only if a concrete owner/security/automation use case emerges.

35. **NOW — Unified notification presentation targets.** The same event can choose TFT banner, WebUI, phone, sound, LED, haptic, etc. according to capability and owner policy. No separate notification systems per subsystem.

36. **NOW — Presentation fallback.** If an Experience asks for audio/LED/haptic/camera and hardware is absent, degrade gracefully rather than erroring or faking a capability.

37. **NOW — Resource arbitration.** Shared/exclusive hardware must be claimed through the same resource model: camera device, microphone, speaker, display, SPI, GPIO, etc. Explain conflicts instead of allowing hidden contention.

38. **NOW — Doctor evidence hooks.** Doctor should be able to inspect device enumeration, PipeWire/audio state, camera/libcamera status, display/touch mapping, rendering/output failures, and relevant logs/configuration without creating separate diagnostic products.

39. **LATER — Visual/audio self-test Procedures.** Examples: play test tone, display color/test pattern, verify touch corners, capture camera frame, check speaker/mic. Useful later for Doctor and onboarding.

40. **LATER — Accessibility options.** Larger text, higher contrast, alternate alert modes, haptic/audio substitution, reduced motion, etc. Worth preserving but needs a separate careful pass.

41. **LATER — Choreography system for expression.** One semantic event can fan out to available outputs: face/animation, LED, sound, haptic. The underlying fact/event remains separate from presentation.

42. **LATER — Creature expression bindings.** Explicitly defer detailed personality/emotion/creature responses to the Monster / perception / expression jam. This cluster only ensures the output capabilities exist.

43. **LATER — Camera-driven perception bindings.** Likewise defer what the creature *interprets* from camera input. Camera remains a neutral Provider first.

44. **LATER — Media asset library.** User sounds/images/animations/themes may eventually be catalogued, previewed, tagged, and assigned to Experiences; not required for core release.

45. **LATER — Content capture to Chronicle/Homecoming.** Selective screenshots/media or generated summaries may attach to history when owner explicitly chooses; avoid default accumulation of bulky media.

46. **NOW — Privacy/secret handling applies to media too.** Local owner media/evidence can be richly retained when needed, but sharing/export/global upload follows explicit policy and sanitization where appropriate.

47. **NOW — Owner control.** Cameras/microphones are never silently treated as always-on simply because detected. Capability presence is not consent to capture.

48. **NOW — Full-tool escape.** Owners can still launch/use normal Linux multimedia/camera/audio tools where installed. Beast does not lock the device into Beast-only media workflows.

## Current takeaway

The core release need is intentionally small:
- discover and register I/O hardware;
- basic audio/display controls;
- common output/notification routing;
- screenshot/export;
- orientation and display truth;
- camera/audio device health if present;
- resource arbitration;
- Doctor inspection hooks;
- full-tool access.

Most richer camera, recording, media, LED, haptic, computer-vision, accessibility, choreography, and creature-expression work is preserved as **LATER** rather than expanded into first-release scope.
