# Beastagotchi Visualization Studio Spec v1.0

## Purpose

Visualization is a first-class customization axis, independent of theme, layout and data source. A widget/page asks for data; a renderer decides how that data is drawn; the theme skins the result.

Canonical separation:

`data source -> widget -> renderer -> layout -> theme -> animation`

## v0.10.0 renderer library

Implemented primitives:

- sparkline
- line
- area
- multi-line
- bars
- stacked bars
- histogram
- heatmap
- waterfall/history strip
- oscilloscope waveform
- radial gauge
- donut
- radar/spider
- polar plot
- signal meter
- event timeline/raster
- numeric + microtrend hybrid

## v0.10.0 page renderer sets

- Recon: radar / polar / bars / signal
- Spectrum: bars / line / heatmap / radar / area / polar / histogram / donut / waveform / waterfall
- Captures: bars / donut / radial / timeline
- System: line / area / waveform / histogram / waterfall

The page can still cycle its primary visualization by tapping the graph. Visualizer Studio adds a central large-target chooser so users do not need to remember hidden graph gestures.

## Future

- renderer eligibility based on data shape
- graph-skin manifests per theme
- stacked area
- RSSI trail
- channel occupancy blocks
- true spectrogram fed by SDR samples
- per-widget renderer choice
- per-renderer options such as smoothing, time window, scale, labels, fill, trail, persistence and animation
- saved visualizer presets independent of theme
