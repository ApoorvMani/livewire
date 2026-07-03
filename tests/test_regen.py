from datetime import datetime, timezone, timedelta
from core.regen import apply_regen, max_bars, BarsState

def test_no_time_elapsed():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    b = BarsState(energy=50, nerve=10, health=80, updated_at=now)
    result = apply_regen(b, now, 100, 15, 100)
    assert result.energy == 50
    assert result.nerve == 10
    assert result.health == 80
    assert result.updated_at == now

def test_under_interval():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    b = BarsState(energy=50, nerve=10, health=80, updated_at=now - timedelta(minutes=9, seconds=59))
    result = apply_regen(b, now, 100, 15, 100)
    assert result.energy == 50  # not enough time for +5

def test_25_minutes():
    now = datetime(2026, 7, 3, 12, 25, 0, tzinfo=timezone.utc)
    b = BarsState(energy=50, nerve=10, health=80, updated_at=now - timedelta(minutes=25))
    result = apply_regen(b, now, 100, 15, 100)
    # energy: +5*2 = +10, nerve: +1*5 = +5, health: +1*8 = +8
    assert result.energy == 60
    assert result.nerve == 15
    assert result.health == 88

def test_clamped_at_max():
    now = datetime(2026, 7, 3, 14, 0, 0, tzinfo=timezone.utc)
    b = BarsState(energy=95, nerve=14, health=99, updated_at=now - timedelta(hours=2))
    result = apply_regen(b, now, 100, 15, 100)
    assert result.energy == 100
    assert result.nerve == 15
    assert result.health == 100

def test_fractional_carry():
    now = datetime(2026, 7, 3, 12, 15, 0, tzinfo=timezone.utc)
    b = BarsState(energy=50, nerve=10, health=80, updated_at=now - timedelta(minutes=15))
    result = apply_regen(b, now, 100, 15, 100)
    assert result.energy == 55  # 15min = 1*10min interval = +5
    assert result.nerve == 13  # 15min = 3*5min intervals = +3
    assert result.health == 85  # 15min = 5*3min intervals = +5
    # updated_at advances to the max interval consumed (nerve/health: 15min)
    assert result.updated_at == now

def test_max_bars_level_1():
    assert max_bars(1) == (100, 15, 100)

def test_max_bars_level_10():
    assert max_bars(10) == (145, 19, 100)  # energy: 100+45, nerve: 15+4
