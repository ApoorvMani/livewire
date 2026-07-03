from datetime import datetime, timezone, timedelta
from models.tables import Character
from core.state import load_character
from core.exceptions import DomainError

def test_load_character_applies_regen(db):
    now = datetime(2026, 7, 3, 12, 30, 0, tzinfo=timezone.utc)
    char = Character(name="Test", energy=50, nerve=5, health=50,
                     bars_updated_at=now - timedelta(minutes=30),
                     cash=500, bank=0, heat=0, heat_updated_at=now,
                     crime_skill=0.0, level=1, xp=0,
                     strength=10, speed=10, defense=10, dexterity=10)
    db.add(char)
    db.commit()
    state = load_character(db, char.id, now)
    # 30 min = +15 energy, +6 nerve, +10 health
    assert state.energy == 65
    assert state.nerve == 11
    assert state.health == 60

def test_not_found(db):
    now = datetime.now(timezone.utc)
    try:
        load_character(db, 999, now)
        assert False
    except DomainError as e:
        assert e.code == "NOT_FOUND"
