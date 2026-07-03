from datetime import datetime, timezone
from core.gym import train
from core.state import CharacterState
from core.exceptions import DomainError

def make_char(**kw):
    defaults = dict(energy=100, nerve=15, health=100, heat=0, cash=500, bank=0,
                    crime_skill=0.0, level=1, xp=0, strength=10, speed=10,
                    defense=10, dexterity=10, hospital_until=None, jail_until=None,
                    notoriety=0, job_id=None, faction_id=None, weapon_bonus=0,
                    armor_bonus=0, buff_until=None, id=1, name="Test",
                    bars_updated_at=datetime.now(timezone.utc),
                    heat_updated_at=datetime.now(timezone.utc))
    defaults.update(kw)
    return CharacterState(**defaults)

def test_train_reduces_energy():
    char = make_char(energy=100)
    now = datetime.now(timezone.utc)
    rng = __import__("random").Random(42)
    result = train(char, "strength", rng, now)
    assert result.energy_cost == 5
    assert result.stat_gain > 0
    assert result.stat_gained == "strength"

def test_not_enough_energy():
    char = make_char(energy=3)
    try:
        train(char, "strength", __import__("random").Random(0), datetime.now(timezone.utc))
        assert False
    except DomainError as e:
        assert e.code == "NOT_ENOUGH_ENERGY"

def test_incapacitated():
    char = make_char(jail_until=datetime(2026, 7, 4, 12, 0, 0, tzinfo=timezone.utc))
    try:
        train(char, "strength", __import__("random").Random(0), datetime.now(timezone.utc))
        assert False
    except DomainError as e:
        assert e.code == "INCAPACITATED"
