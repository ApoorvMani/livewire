from datetime import datetime, timezone
from core.state import CharacterState, derive_status, require_ok
from core.exceptions import DomainError


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


def test_derive_status_ok():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    char = make_char()
    assert derive_status(char, now) == "ok"


def test_derive_status_jail():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    char = make_char(jail_until=datetime(2026, 7, 3, 13, 0, 0, tzinfo=timezone.utc))
    assert derive_status(char, now) == "jail"


def test_derive_status_hospital():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    char = make_char(hospital_until=datetime(2026, 7, 3, 13, 0, 0, tzinfo=timezone.utc))
    assert derive_status(char, now) == "hospital"


def test_require_ok_raises():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    char = make_char(jail_until=datetime(2026, 7, 3, 13, 0, 0, tzinfo=timezone.utc))
    try:
        require_ok(char, now)
        assert False
    except DomainError as e:
        assert e.code == "INCAPACITATED"


def test_require_ok_passes():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    char = make_char()
    require_ok(char, now)


async def test_list_jail_empty(client):
    resp = await client.get("/api/jail/list")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_jail_with_jailed(client, db):
    from models.tables import Character
    from datetime import timedelta

    future = datetime.now(timezone.utc) + timedelta(hours=2)
    c = Character(
        id=2,
        name="JailedGuy",
        jail_until=future,
    )
    db.add(c)
    db.commit()

    resp = await client.get("/api/jail/list")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "JailedGuy"
    assert data[0]["minutes_left"] > 0


async def test_bust_not_authenticated(client):
    resp = await client.post("/api/jail/1/bust")
    assert resp.status_code == 401


async def test_bust_self(client):
    resp = await client.post(
        "/api/auth/register", json={"username": "selftest", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post("/api/jail/1/bust")
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["code"] == "SELF_BUST"


async def test_bust_not_found(client):
    resp = await client.post(
        "/api/auth/register", json={"username": "busttest", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post("/api/jail/999/bust")
    assert resp.status_code == 404


async def test_bust_not_jailed(client, db):
    from models.tables import Character

    c = Character(id=100, name="NotJailed")
    db.add(c)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "busttest2", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post("/api/jail/100/bust")
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "NOT_JAILED"
