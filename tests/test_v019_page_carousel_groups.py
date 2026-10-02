from beastui.design import PRIMARY_PAGES, PAGE_GROUPS, page_group, page_group_boundaries


def test_every_primary_page_has_exactly_one_semantic_group():
    memberships = {page: [] for page in PRIMARY_PAGES}
    for group, pages in PAGE_GROUPS.items():
        for page in pages:
            if page in memberships:
                memberships[page].append(group)

    assert all(len(groups) == 1 for groups in memberships.values())


def test_expected_page_groups_are_stable():
    assert page_group("home") == "identity"
    assert page_group("beast") == "identity"
    assert page_group("overview") == "awareness"
    assert page_group("recon") == "awareness"
    assert page_group("captures") == "records"
    assert page_group("expedition") == "records"
    assert page_group("dashboard") == "workspace"
    assert page_group("system") == "device"
    assert page_group("not-a-page") == "other"


def test_page_group_boundaries_match_primary_carousel_order():
    boundaries = page_group_boundaries()
    assert boundaries
    for idx in boundaries:
        assert idx > 0
        assert page_group(PRIMARY_PAGES[idx]) != page_group(PRIMARY_PAGES[idx - 1])

    # Every actual transition between adjacent semantic groups must be represented.
    expected = tuple(
        idx for idx in range(1, len(PRIMARY_PAGES))
        if page_group(PRIMARY_PAGES[idx]) != page_group(PRIMARY_PAGES[idx - 1])
    )
    assert boundaries == expected
