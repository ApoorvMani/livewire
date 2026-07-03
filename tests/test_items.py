from datetime import datetime, timezone
from models.tables import Character, Event, Buff


async def test_shop_items(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.get("/api/shop")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 13
    assert data[0]["name"] == "Knuckles"
    assert data[0]["slot"] == "weapon"
    assert data[0]["base_price"] == 500


async def test_buy_item(db, client):
    from jobs.seed import seed_items
    from models.tables import Character

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "buyer", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="buyer").first()
    char.cash = 5000
    db.commit()
    resp = await client.post("/api/shop/buy", json={"item_id": 1, "qty": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["cash"] == 5000 - 500 * 2  # 4000


async def test_buy_not_enough_cash(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "poor", "password": "password123"}
    )
    assert resp.status_code == 200
    from models.tables import Character

    char = db.query(Character).filter_by(name="poor").first()
    char.cash = 10
    db.commit()
    resp = await client.post("/api/shop/buy", json={"item_id": 5, "qty": 1})
    assert resp.status_code == 400
    data = resp.json()
    assert "NOT_ENOUGH_CASH" in str(data)


async def test_buy_invalid_item(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "buyer2", "password": "password123"}
    )
    assert resp.status_code == 200
    resp = await client.post("/api/shop/buy", json={"item_id": 999, "qty": 1})
    assert resp.status_code == 404


async def test_buy_invalid_request(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "buyer3", "password": "password123"}
    )
    assert resp.status_code == 200
    resp = await client.post("/api/shop/buy", json={"item_id": None, "qty": 1})
    assert resp.status_code == 400
    resp = await client.post("/api/shop/buy", json={"item_id": 1, "qty": 0})
    assert resp.status_code == 400


async def test_inventory_after_buy(db, client):
    from jobs.seed import seed_items
    from models.tables import Character

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "invuser", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="invuser").first()
    char.cash = 5000
    db.commit()
    resp = await client.get("/api/inventory")
    assert resp.status_code == 200
    assert resp.json() == []
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 2})
    resp = await client.get("/api/inventory")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["item_id"] == 1
    assert data[0]["qty"] == 2
    assert not data[0]["equipped"]


async def test_equip_item(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "equipper", "password": "password123"}
    )
    assert resp.status_code == 200
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    resp = await client.post(f"/api/inventory/{inv_id}/equip")
    assert resp.status_code == 200
    assert resp.json()["equipped"]
    inv2 = (await client.get("/api/inventory")).json()
    assert inv2[0]["equipped"]


async def test_unequip_item(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "unequipper", "password": "password123"}
    )
    assert resp.status_code == 200
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    await client.post(f"/api/inventory/{inv_id}/equip")
    resp = await client.post(f"/api/inventory/{inv_id}/unequip")
    assert resp.status_code == 200
    assert not resp.json()["equipped"]
    inv2 = (await client.get("/api/inventory")).json()
    assert not inv2[0]["equipped"]


async def test_equip_same_slot_unequips_old(db, client):
    from jobs.seed import seed_items
    from models.tables import Character

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "dualwield", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="dualwield").first()
    char.cash = 5000
    db.commit()
    # Buy 2 of item 1 and 1 of item 2
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 2})
    await client.post("/api/shop/buy", json={"item_id": 2, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    assert len(inv) == 2
    weapon1 = [i for i in inv if i["item_id"] == 1][0]
    weapon2 = [i for i in inv if i["item_id"] == 2][0]
    await client.post(f"/api/inventory/{weapon1['id']}/equip")
    resp = await client.post(f"/api/inventory/{weapon2['id']}/equip")
    assert resp.status_code == 200
    inv_after = (await client.get("/api/inventory")).json()
    e1 = [i for i in inv_after if i["id"] == weapon1["id"]][0]
    e2 = [i for i in inv_after if i["id"] == weapon2["id"]][0]
    assert not e1["equipped"]
    assert e2["equipped"]


async def test_equip_consumable_fails(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "consuser", "password": "password123"}
    )
    assert resp.status_code == 200
    await client.post("/api/shop/buy", json={"item_id": 11, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    resp = await client.post(f"/api/inventory/{inv_id}/equip")
    assert resp.status_code == 400
    assert "INVALID_SLOT" in str(resp.json())


async def test_equip_not_found(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "lost", "password": "password123"}
    )
    assert resp.status_code == 200
    resp = await client.post("/api/inventory/9999/equip")
    assert resp.status_code == 404


async def test_use_medkit_heals(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "healer", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="healer").first()
    char.health = 50
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 11, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    resp = await client.post(f"/api/inventory/{inv_id}/use")
    assert resp.status_code == 200
    assert resp.json()["used"]
    char = db.query(Character).filter_by(name="healer").first()
    assert char.health == 90  # 50 + 40


async def test_use_medkit_caps_at_100(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "healer2", "password": "password123"}
    )
    assert resp.status_code == 200
    await client.post("/api/shop/buy", json={"item_id": 11, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    resp = await client.post(f"/api/inventory/{inv_id}/use")
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="healer2").first()
    assert char.health == 100  # capped


async def test_use_energy_drink(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "energizer", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="energizer").first()
    char.energy = 30
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 12, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    resp = await client.post(f"/api/inventory/{inv_id}/use")
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="energizer").first()
    assert char.energy == 55  # 30 + 25


async def test_use_adrenaline_creates_buff(db, client):
    from jobs.seed import seed_items
    from models.tables import Character

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "adrena", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="adrena").first()
    char.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 13, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    resp = await client.post(f"/api/inventory/{inv_id}/use")
    assert resp.status_code == 200
    buff = db.query(Buff).filter_by(char_id=1, kind="adrenaline").first()
    assert buff is not None
    assert buff.until > datetime.now(timezone.utc).replace(tzinfo=None)


async def test_use_adrenaline_hits_daily_cap(db, client):
    from jobs.seed import seed_items
    from models.tables import Character

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "adrena2", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="adrena2").first()
    char.cash = 5000
    db.commit()
    # Buy 2 adrenaline (daily cap is 1)
    await client.post("/api/shop/buy", json={"item_id": 13, "qty": 2})
    inv = (await client.get("/api/inventory")).json()
    id1 = inv[0]["id"]
    resp = await client.post(f"/api/inventory/{id1}/use")
    assert resp.status_code == 200
    buff = db.query(Buff).filter_by(char_id=1, kind="adrenaline").first()
    assert buff is not None
    # Second use should hit daily cap
    resp = await client.post(f"/api/inventory/{id1}/use")
    assert resp.status_code == 400
    assert "DAILY_CAP" in str(resp.json())


async def test_use_non_consumable_fails(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "noncon", "password": "password123"}
    )
    assert resp.status_code == 200
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    resp = await client.post(f"/api/inventory/{inv_id}/use")
    assert resp.status_code == 400
    assert "NOT_CONSUMABLE" in str(resp.json())


async def test_use_daily_cap(db, client):
    from jobs.seed import seed_items
    from models.tables import Character

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "capuser", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="capuser").first()
    char.cash = 50000
    db.commit()
    # Buy 10 medkits (daily cap is 5)
    await client.post("/api/shop/buy", json={"item_id": 11, "qty": 10})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    # Use 5 times - should work
    for _ in range(5):
        resp = await client.post(f"/api/inventory/{inv_id}/use")
        assert resp.status_code == 200
    # 6th time - should hit daily cap
    resp = await client.post(f"/api/inventory/{inv_id}/use")
    assert resp.status_code == 400
    assert "DAILY_CAP" in str(resp.json())


async def test_use_not_found(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "nouser", "password": "password123"}
    )
    assert resp.status_code == 200
    resp = await client.post("/api/inventory/9999/use")
    assert resp.status_code == 404


async def test_use_event_created(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "eventuser", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="eventuser").first()
    char.health = 50
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 11, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    await client.post(f"/api/inventory/{inv_id}/use")
    events = db.query(Event).filter_by(type="use_item", actor_id=1).all()
    assert len(events) == 1
    assert '"item_id":11' in events[0].payload_json


async def test_equip_event_created(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "eqevent", "password": "password123"}
    )
    assert resp.status_code == 200
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    inv = (await client.get("/api/inventory")).json()
    inv_id = inv[0]["id"]
    await client.post(f"/api/inventory/{inv_id}/equip")
    events = db.query(Event).filter_by(type="equip_item", actor_id=1).all()
    assert len(events) == 1


async def test_buy_event_created(db, client):
    from jobs.seed import seed_items
    from models.tables import Character

    seed_items(db)
    db.commit()
    resp = await client.post(
        "/api/auth/register", json={"username": "buyevent", "password": "password123"}
    )
    assert resp.status_code == 200
    char = db.query(Character).filter_by(name="buyevent").first()
    char.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 2})
    events = db.query(Event).filter_by(type="buy_item", actor_id=1).all()
    assert len(events) == 1
    assert '"item_id":1' in events[0].payload_json
    assert '"qty":2' in events[0].payload_json
