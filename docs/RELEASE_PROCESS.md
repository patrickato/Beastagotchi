# Release Process (Pre-1.0)

This is the intended release discipline while Beastagotchi is pre-1.0.

1. Freeze runtime changes for the milestone.
2. Run source tests/compile/shell validation.
3. Run reference-audit/privacy checks.
4. Build the release archive from a clean tree (no caches/runtime state).
5. Generate SHA-256 checksum.
6. Install on the target Pi using the release archive, not a developer working tree.
7. Run target off-screen validator and review the returned archive.
8. Perform a physical gate only when the milestone touches presentation/input/hardware behavior.
9. Update changelog, current roadmap/matrix and compatibility spec.
10. Tag/release from the validated commit.

A future CI workflow should automate archive creation/checksum/release artifacts after the installer/upgrader format stabilizes.
