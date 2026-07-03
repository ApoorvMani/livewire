from datetime import datetime, timezone
import random
from core.combat import resolve_attack
from core.state import CharacterState


def make_char(**kw):
    defaults = dict(
        energy=100,
        nerve=15,
        health=100,
        heat=0,
        cash=500,
        bank=1000,
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


def test_p_win_clamps():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=999, speed=999)
    dfn = make_char(strength=1, speed=1, defense=1, dexterity=1)
    rng = random.Random(42)
    result = resolve_attack(att, dfn, "mug", rng, now)
    assert result.p_win >= 0.90


def test_p_win_near_50():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=10, speed=10, defense=10, dexterity=10)
    dfn = make_char(strength=10, speed=10, defense=10, dexterity=10)
    rng = random.Random(42)
    result = resolve_attack(att, dfn, "mug", rng, now)
    assert 0.48 <= result.p_win <= 0.52


def test_mug_steals_cash_only():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=999, id=1)
    dfn = make_char(strength=1, cash=500, bank=1000, id=2)
    rng = random.Random(42)
    result = resolve_attack(att, dfn, "mug", rng, now)
    assert result.won
    pct = result.mug_amount / 500
    assert 0.03 <= pct <= 0.10


def test_mug_does_not_touch_bank():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=999, id=1)
    dfn = make_char(strength=1, cash=500, bank=1000, id=2)
    rng = random.Random(42)
    resolve_attack(att, dfn, "mug", rng, now)
    assert dfn.bank == 1000


def test_attack_loss():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=1, speed=1, defense=1, dexterity=1)
    dfn = make_char(strength=999, speed=999, id=2)
    rng = random.Random(42)
    result = resolve_attack(att, dfn, "mug", rng, now)
    assert not result.won
    assert result.mug_amount == 0
    assert result.hospital_minutes_attacker > 0


def test_hospitalize_gains_notoriety():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=999, speed=999)
    dfn = make_char(strength=1, speed=1, defense=1, dexterity=1, id=2)
    rng = random.Random(42)
    result = resolve_attack(att, dfn, "hospitalize", rng, now)
    assert result.won
    assert result.heat_gain == 8
    assert result.notoriety_gain == 3
    assert result.mug_amount == 0


def test_leave_attack():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=999, speed=999)
    dfn = make_char(strength=1, speed=1, defense=1, dexterity=1, id=2)
    rng = random.Random(42)
    result = resolve_attack(att, dfn, "leave", rng, now)
    assert result.won
    assert result.mug_amount == 0
    assert result.heat_gain == 1


def test_buff_bonus_applied():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    future = datetime(2026, 7, 3, 13, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=10, speed=10, buff_until=future)
    dfn = make_char(strength=10, speed=10, defense=10, dexterity=10, id=2)
    rng = random.Random(42)
    result_buffed = resolve_attack(att, dfn, "mug", rng, now)
    assert result_buffed.p_win > 0.5  # buff gives +10% atk advantage


def test_buff_expired():
    now = datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
    past = datetime(2026, 7, 3, 11, 0, 0, tzinfo=timezone.utc)
    att = make_char(strength=10, speed=10, buff_until=past)
    dfn = make_char(strength=10, speed=10, defense=10, dexterity=10, id=2)
    rng = random.Random(42)
    result = resolve_attack(att, dfn, "mug", rng, now)
    assert 0.48 <= result.p_win <= 0.52


async def test_attack_endpoint(db, client):
    from jobs.seed import seed_crimes
    from models.tables import Character, Event

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "attacker", "password": "password123"}
    )
    assert resp.status_code == 200

    defender = Character(
        name="defender",
        user_id=None,
        is_ai=True,
        bars_updated_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db.add(defender)
    db.commit()

    resp = await client.post(
        "/api/attack",
        json={"target_name": "defender", "choice": "mug"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "won" in data
    assert "p_win" in data
    assert "xp" in data
    assert "text_key" in data

    events = db.query(Event).filter_by(type="attack").all()
    assert len(events) == 1


async def test_attack_not_enough_energy(db, client):
    from jobs.seed import seed_crimes
    from models.tables import Character

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "lowenergy", "password": "password123"}
    )
    assert resp.status_code == 200

    char = db.query(Character).filter_by(name="lowenergy").first()
    char.energy = 10
    db.commit()

    defender = Character(
        name="victim",
        user_id=None,
        is_ai=True,
        bars_updated_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db.add(defender)
    db.commit()

    resp = await client.post(
        "/api/attack",
        json={"target_name": "victim", "choice": "mug"},
    )
    assert resp.status_code == 400


async def test_attack_self_not_allowed(db, client):
    from jobs.seed import seed_crimes

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "selfish", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/api/attack",
        json={"target_name": "selfish", "choice": "mug"},
    )
    assert resp.status_code == 400


async def test_attack_target_not_found(db, client):
    from jobs.seed import seed_crimes

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "finder", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/api/attack",
        json={"target_name": "nonexistent", "choice": "mug"},
    )
    assert resp.status_code == 404


async def test_invalid_choice(db, client):
    from jobs.seed import seed_crimes
    from models.tables import Character

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "chooser", "password": "password123"}
    )
    assert resp.status_code == 200

    defender = Character(
        name="targetch",
        user_id=None,
        is_ai=True,
        bars_updated_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db.add(defender)
    db.commit()

    resp = await client.post(
        "/api/attack",
        json={"target_name": "targetch", "choice": "invalid"},
    )
    assert resp.status_code == 400


async def test_bank_deposit(db, client):
    from jobs.seed import seed_crimes

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "banker", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/api/bank/deposit",
        json={"amount": 100},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["fee"] >= 1
    assert data["cash"] < 500
    assert data["bank"] > 0


async def test_bank_deposit_not_enough_cash(db, client):
    from jobs.seed import seed_crimes

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "poor", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/api/bank/deposit",
        json={"amount": 99999},
    )
    assert resp.status_code == 400


async def test_bank_withdraw(db, client):
    from jobs.seed import seed_crimes

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "withdrawer", "password": "password123"}
    )
    assert resp.status_code == 200

    from models.tables import Character

    char = db.query(Character).filter_by(name="withdrawer").first()
    char.bank = 1000
    db.commit()

    resp = await client.post(
        "/api/bank/withdraw",
        json={"amount": 200},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["bank"] == 800


async def test_bank_withdraw_not_enough(db, client):
    from jobs.seed import seed_crimes

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "poorbank", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/api/bank/withdraw",
        json={"amount": 99999},
    )
    assert resp.status_code == 400


async def test_bank_invalid_amount(db, client):
    from jobs.seed import seed_crimes

    seed_crimes(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "invalid", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/api/bank/deposit",
        json={"amount": 0},
    )
    assert resp.status_code == 400
