# Beastagotchi v0.10.0 — Known-Good Checkpoint Delta

v0.10.0 is still based on the physically working checkpoint lineage. It does not replace the low-level framebuffer, touch reader, Pwnagotchi Native source, display handoff, collectors, bridge, database or core state model.

Primary changed surfaces:

- `beastui/widgets/renderers.py`: expanded renderer library
- `beastui/widgets/__init__.py`: renderer exports
- `beastui/pages.py`: Recon/Spectrum/Captures/System renderer selection
- `beastui/engine.py`: Visualizer Studio, generalized renderer registry, non-Matrix Theme Studio options
- `beastui/backgrounds.py`: runtime customization for Classic/Starcore/Black Ice/Hunter/Minimal
- `beastui/datafeed.py`: broader history cache for future visualizers

The production touch calibration remains the restored/original transform selected during physical A/B testing.
