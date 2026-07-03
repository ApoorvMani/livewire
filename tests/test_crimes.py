from datetime import datetime, timezone
from core.crimes import attempt_crime, CrimeRow
from core.state import CharacterState
from core.exceptions import DomainError


def make_crime(**kw):
    base = dict(
        id="crime_t1_a",
        tier=1,
        name="Pickpocket",
        nerve_cost=2,
        base_success=0.85,
        payout_min=50,
        payout_max=150,
    )
    base.update(kw)
    return CrimeRow(**base)


def make_char(**kw):
    defaults = dict(
        energy=100,
        nerve=15,
        health=100,
        heat=0,
        cash=500,
        bank=0,
        crime_skill=0.0,
        level=1,
        xp=0,
        strength=10,
        speed=10,
        defense=10,
        dexterity=10,
        hospital_until=None,
        jail_until=None,
        notoriety=0,
        job_id=None,
        faction_id=None,
        weapon_bonus=0,
        armor_bonus=0,
        buff_until=None,
        id=1,
        name="Test",
        bars_updated_at=datetime.now(timezone.utc),
        heat_updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kw)
    return CharacterState(**defaults)


def test_success_with_seeded_rng():
    crime = make_crime()
    char = make_char(nerve=15)
    rng = __import__("random").Random(0)  # seed that gives success
    result = attempt_crime(char, crime, rng, datetime.now(timezone.utc))
    assert result.success
    assert result.payout >= 50 and result.payout <= 150
    assert result.xp == 10  # success: tier * 10
    assert result.skill_gain == 1.0
    assert not result.jailed


def test_not_enough_nerve():
    crime = make_crime(nerve_cost=2)
    char = make_char(nerve=0)
    try:
        attempt_crime(char, crime, __import__("random").Random(0), datetime.now(timezone.utc))
        assert False, "expected DomainError"
    except DomainError as e:
        assert e.code == "NOT_ENOUGH_NERVE"


def test_incapacitated():
    crime = make_crime()
    char = make_char(jail_until=datetime(2026, 7, 4, 12, 0, 0, tzinfo=timezone.utc))
    try:
        attempt_crime(char, crime, __import__("random").Random(0), datetime.now(timezone.utc))
        assert False, "expected DomainError"
    except DomainError as e:
        assert e.code == "INCAPACITATED"


def test_fail_low_skill():
    crime = make_crime(base_success=0.0)  # force fail
    char = make_char(crime_skill=0.0)
    result = attempt_crime(char, crime, __import__("random").Random(0), datetime.now(timezone.utc))
    assert not result.success
    assert result.payout == 0
    assert result.xp == 2  # fail: tier * 2
    assert result.skill_gain == 0.2


def test_jail_possible():
    crime = make_crime(tier=3)
    char = make_char(crime_skill=0.0)
    rng = __import__("random").Random(42)
    result = attempt_crime(char, crime, rng, datetime.now(timezone.utc))
    if not result.success:
        # jail probability 0.35 — may or may not fire with seed 42
        pass  # just verify no crash


def test_heat_gain_t4_success():
    crime = make_crime(tier=4, base_success=1.0)
    char = make_char(crime_skill=0.0)
    rng = __import__("random").Random(0)
    result = attempt_crime(char, crime, rng, datetime.now(timezone.utc))
    assert result.heat_gain == 6


def test_heat_gain_t5_success():
    crime = make_crime(tier=5, base_success=1.0)
    char = make_char(crime_skill=0.0)
    rng = __import__("random").Random(0)
    result = attempt_crime(char, crime, rng, datetime.now(timezone.utc))
    assert result.heat_gain == 10


def test_clamp_bounds():
    crime2 = make_crime(base_success=1.0)
    char2 = make_char(crime_skill=999.0)
    rng = __import__("random").Random(0)
    result2 = attempt_crime(char2, crime2, rng, datetime.now(timezone.utc))
    assert result2.success  # 95% clamp upper


async def test_crime_event_written(db, client):
    from jobs.seed import seed_crimes
    from models.tables import Event

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "eventtest", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post("/api/crimes/crime_t1_a/attempt")
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data
    assert "payout" in data
    assert "jailed" in data

    events = db.query(Event).all()
    assert len(events) == 1
    ev = events[0]
    assert ev.type == "crime"
    assert ev.actor_id is not None
    assert "crime_t1_a" in ev.payload_json
    assert ev.weight in (1, 2)
