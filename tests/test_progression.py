from core.progression import xp_to_level


def test_level_1_at_0_xp():
    assert xp_to_level(0) == 1


def test_level_2_at_100_xp():
    assert xp_to_level(100) == 2


def test_levels():
    assert xp_to_level(2600) == 8
    assert xp_to_level(3500) == 9
    assert xp_to_level(4000) == 10
    assert xp_to_level(4700) == 11


def test_monotonic():
    for xp in range(0, 50000, 100):
        l1 = xp_to_level(xp)
        l2 = xp_to_level(xp + 1)
        assert l2 >= l1
