from beastui.experience_prototype_silhouettes import (
    PROTOTYPE_SILHOUETTES,
    occupancy_signature,
    render_silhouette,
)


def test_prototype_silhouettes_cover_first_five_experiences():
    assert {"atlas", "forge", "observatory", "habitat", "monolith"} <= set(PROTOTYPE_SILHOUETTES)


def test_prototype_silhouette_images_are_structurally_distinct():
    ids = ["atlas", "forge", "observatory", "habitat", "monolith"]
    rendered = [render_silhouette(x) for x in ids]
    payloads = [im.tobytes() for im in rendered]
    assert len(set(payloads)) == len(ids)


def test_prototype_signatures_are_not_identical_dashboard_clones():
    ids = ["atlas", "forge", "observatory", "habitat", "monolith"]
    sigs = {x: occupancy_signature(x) for x in ids}
    assert len(set(sigs.values())) == len(ids)
    # Habitat must materially privilege creature presence over Forge.
    assert sigs["habitat"][1] > sigs["forge"][1]
    # Monolith uses the fewest simultaneous regions by design.
    assert sigs["monolith"][2] < sigs["forge"][2]


def test_silhouette_proof_is_grayscale_structural_not_theme_coloring():
    im = render_silhouette("atlas")
    assert im.size == (480, 320)
    colors = im.getcolors(maxcolors=1024)
    assert colors is not None
    # RGB channels should remain equal because this artifact tests structure only.
    assert all(rgb[0] == rgb[1] == rgb[2] for _, rgb in colors)
