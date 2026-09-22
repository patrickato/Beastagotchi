# Beastagotchi v0.6.1 Physical Visual Validation Report — 2026-09-20

## Result
PASS.

The six-theme physical visual-system gate is complete.

## User-observed results
- All six structural themes were readable.
- Theme switching worked reliably.
- Motion was generally smooth with only minor visible jitter.
- Matrix Beast has enough apparent headroom to support denser/faster rain.
- The single slowly descending horizontal scanline was positively received and should remain as an intentional visual effect.
- No meaningful clipping, tearing or theme-specific usability failure was reported.

## Validation archive observations
- Beast Core health: healthy.
- Canonical state: 226 live keys, 0 stale, 0 unavailable at collection time.
- Touch calibration remained the validated 480×320 ADS7846 transform.
- Gesture logs contain clean horizontal and vertical gestures plus reliable footer taps.
- Final saved theme preference in the archive was `blackice`.
- The archive was collected after the reversible test state had ended/restored: Pwnagotchi and Beast Core were active and Beast UI was inactive. This is expected for a timed test/rollback state and does not invalidate the physical UI test.

## Follow-up applied in v0.7
- Matrix rain density increased.
- Matrix rain speed increased.
- Moving scanline preserved and made theme-configurable.
- High-motion FPS budget increased when CPU headroom permits.
- Framebuffer file descriptor is retained across frames to remove unnecessary open/close overhead and reduce minor jitter.
