from datetime import datetime, timezone, timedelta
from core.heat import apply_heat_decay, check_threshold, bribe_cost


def test_decay():
    now = datetime(2026, 7, 3, 14, 0, 0, tzinfo=timezone.utc)
    heat, updated = apply_heat_decay(50, now - timedelta(hours=3), now)
    assert heat == 47  # 3 hours = -3
    assert updated == now


def test_no_decay_when_zero_hours():
    now = datetime(2026, 7, 3, 14, 0, 0, tzinfo=timezone.utc)
    heat, updated = apply_heat_decay(50, now, now)
    assert heat == 50
    assert updated == now


def test_decay_to_zero():
    now = datetime(2026, 7, 3, 14, 0, 0, tzinfo=timezone.utc)
    heat, updated = apply_heat_decay(5, now - timedelta(hours=10), now)
    assert heat == 0
    assert updated == now


def test_already_zero():
    now = datetime(2026, 7, 3, 14, 0, 0, tzinfo=timezone.utc)
    heat, updated = apply_heat_decay(0, now - timedelta(hours=10), now)
    assert heat == 0
    assert updated == now


def test_bribe_cost():
    assert bribe_cost(50) == 5000


def test_bribe_cost_zero():
    assert bribe_cost(0) == 0


def test_threshold_crossing_40():
    events = check_threshold(30, 50)
    assert len(events) == 1
    assert events[0]["type"] == "shakedown"


def test_threshold_crossing_70():
    events = check_threshold(50, 80)
    assert len(events) == 1
    assert events[0]["type"] == "raid"


def test_threshold_crossing_both():
    events = check_threshold(30, 80)
    assert len(events) == 2
    assert events[0]["type"] == "shakedown"
    assert events[1]["type"] == "raid"


def test_no_crossing():
    assert check_threshold(50, 60) == []
    assert check_threshold(80, 90) == []
    assert check_threshold(50, 30) == []


def test_exact_boundary():
    assert len(check_threshold(39, 40)) == 1
    assert len(check_threshold(40, 40)) == 0
    assert len(check_threshold(69, 70)) == 1
