from core.market import calculate_fee
from models.tables import Character, Event, Inventory, MarketListing


def test_calculate_fee_minimum():
    assert calculate_fee(1, 1) == 1


def test_calculate_fee_exact():
    assert calculate_fee(100, 1) == 2
    assert calculate_fee(50, 2) == 2


def test_calculate_fee_rounds_up():
    assert calculate_fee(99, 1) == 2
    assert calculate_fee(101, 1) == 3
    assert calculate_fee(1000, 1) == 20


def test_calculate_fee_large():
    assert calculate_fee(10_000_000, 1) == 200_000


async def _register(client, username: str, password: str = "password123"):
    resp = await client.post(
        "/api/auth/register", json={"username": username, "password": password}
    )
    assert resp.status_code == 200
    return resp.cookies


async def test_list_item(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    cookies = await _register(client, "seller")
    client.cookies.update(cookies)
    char = db.query(Character).filter_by(name="seller").first()
    char.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 3})
    inv = (await client.get("/api/inventory")).json()
    assert len(inv) == 1
    assert inv[0]["qty"] == 3
    resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["fee"] == calculate_fee(600, 2)
    char = db.query(Character).filter_by(name="seller").first()
    fee = calculate_fee(600, 2)
    assert char.cash == 5000 - 500 * 3 - fee
    inv_after = (await client.get("/api/inventory")).json()
    assert inv_after[0]["qty"] == 1


async def test_list_item_not_enough_items(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    cookies = await _register(client, "seller")
    client.cookies.update(cookies)
    char = db.query(Character).filter_by(name="seller").first()
    char.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 5})
    assert resp.status_code == 400
    assert "NOT_ENOUGH_ITEMS" in str(resp.json())


async def test_list_item_not_enough_cash_for_fee(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    cookies = await _register(client, "broke_seller")
    client.cookies.update(cookies)
    char = db.query(Character).filter_by(name="broke_seller").first()
    char.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    char.cash = 0
    db.commit()
    resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 1})
    assert resp.status_code == 400
    assert "NOT_ENOUGH_CASH" in str(resp.json())


async def test_order_book_sorted_by_price(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    await _register(client, "seller1")
    char1 = db.query(Character).filter_by(name="seller1").first()
    char1.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 5})
    await client.post("/api/market/list", json={"item_id": 1, "price": 700, "qty": 2})
    await _register(client, "seller2")
    char2 = db.query(Character).filter_by(name="seller2").first()
    char2.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 5})
    await client.post("/api/market/list", json={"item_id": 1, "price": 500, "qty": 2})
    await _register(client, "seller3")
    char3 = db.query(Character).filter_by(name="seller3").first()
    char3.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 5})
    await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 2})
    resp = await client.get("/api/market/1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[0]["price"] == 500
    assert data[1]["price"] == 600
    assert data[2]["price"] == 700


async def test_order_book_empty(db, client):
    cookies = await _register(client, "nobody")
    client.cookies.update(cookies)
    resp = await client.get("/api/market/1")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_buy_listing(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    await _register(client, "seller")
    seller = db.query(Character).filter_by(name="seller").first()
    seller.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 3})
    list_resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 2})
    listing_id = list_resp.json()["id"]
    old_seller_cash = db.query(Character).filter_by(name="seller").first().cash
    await _register(client, "buyer")
    buyer = db.query(Character).filter_by(name="buyer").first()
    buyer.cash = 5000
    db.commit()
    buy_resp = await client.post(f"/api/market/buy/{listing_id}", json={"qty": 1})
    assert buy_resp.status_code == 200
    data = buy_resp.json()
    assert data["bought"]
    assert data["qty"] == 1
    assert data["total"] == 600
    seller_after = db.query(Character).filter_by(name="seller").first()
    buyer_after = db.query(Character).filter_by(name="buyer").first()
    assert seller_after.cash == old_seller_cash + 600
    assert buyer_after.cash == 5000 - 600
    inv_buyer = db.query(Inventory).filter_by(char_id=buyer.id, item_id=1).first()
    assert inv_buyer.qty == 1
    listing_after = db.query(MarketListing).filter_by(id=listing_id).first()
    assert listing_after.qty == 1


async def test_buy_listing_full_quantity_cleans_up(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    cookies = await _register(client, "seller")
    client.cookies.update(cookies)
    char = db.query(Character).filter_by(name="seller").first()
    char.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 3})
    list_resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 2})
    listing_id = list_resp.json()["id"]
    await _register(client, "buyer")
    buyer = db.query(Character).filter_by(name="buyer").first()
    buyer.cash = 5000
    db.commit()
    await client.post(f"/api/market/buy/{listing_id}", json={"qty": 2})
    listing_after = db.query(MarketListing).filter_by(id=listing_id).first()
    assert listing_after is None


async def test_buy_not_enough_cash(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    await _register(client, "seller")
    seller = db.query(Character).filter_by(name="seller").first()
    seller.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    list_resp = await client.post("/api/market/list", json={"item_id": 1, "price": 5000, "qty": 1})
    listing_id = list_resp.json()["id"]
    await _register(client, "broke")
    buy_resp = await client.post(f"/api/market/buy/{listing_id}", json={"qty": 1})
    assert buy_resp.status_code == 400
    assert "NOT_ENOUGH_CASH" in str(buy_resp.json())


async def test_buy_listing_not_found(db, client):
    cookies = await _register(client, "nobody")
    client.cookies.update(cookies)
    resp = await client.post("/api/market/buy/9999", json={"qty": 1})
    assert resp.status_code == 404
    assert "NOT_FOUND" in str(resp.json())


async def test_cancel_listing(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    cookies = await _register(client, "seller")
    client.cookies.update(cookies)
    seller = db.query(Character).filter_by(name="seller").first()
    seller.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 3})
    list_resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 2})
    listing_id = list_resp.json()["id"]
    inv_before = db.query(Inventory).filter_by(char_id=seller.id, item_id=1).first()
    assert inv_before.qty == 1
    cancel_resp = await client.post(f"/api/market/cancel/{listing_id}")
    assert cancel_resp.status_code == 200
    data = cancel_resp.json()
    assert data["cancelled"]
    assert data["qty_returned"] == 2
    listing = db.query(MarketListing).filter_by(id=listing_id).first()
    assert listing is None
    inv_after = db.query(Inventory).filter_by(char_id=seller.id, item_id=1).first()
    assert inv_after.qty == 3


async def test_cancel_other_sellers_listing_fails(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    await _register(client, "seller1")
    s1 = db.query(Character).filter_by(name="seller1").first()
    s1.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    list_resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 1})
    listing_id = list_resp.json()["id"]
    await _register(client, "seller2")
    s2 = db.query(Character).filter_by(name="seller2").first()
    s2.cash = 5000
    db.commit()
    resp = await client.post(f"/api/market/cancel/{listing_id}")
    assert resp.status_code == 404
    assert "NOT_FOUND" in str(resp.json())


async def test_concurrent_buy_guard(db, client):
    from jobs.seed import seed_items
    from sqlalchemy import text

    seed_items(db)
    db.commit()
    await _register(client, "seller")
    seller = db.query(Character).filter_by(name="seller").first()
    seller.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 3})
    list_resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 1})
    listing_id = list_resp.json()["id"]
    result = db.execute(
        text("UPDATE market_listings SET qty = qty - :qty WHERE id = :id AND qty >= :qty"),
        {"qty": 1, "id": listing_id},
    )
    assert result.rowcount == 1
    result2 = db.execute(
        text("UPDATE market_listings SET qty = qty - :qty WHERE id = :id AND qty >= :qty"),
        {"qty": 1, "id": listing_id},
    )
    assert result2.rowcount == 0


async def test_buy_creates_trade_event(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    await _register(client, "seller")
    seller = db.query(Character).filter_by(name="seller").first()
    seller.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 2})
    list_resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 1})
    listing_id = list_resp.json()["id"]
    await _register(client, "buyer")
    buyer = db.query(Character).filter_by(name="buyer").first()
    buyer.cash = 5000
    db.commit()
    await client.post(f"/api/market/buy/{listing_id}", json={"qty": 1})
    events = db.query(Event).filter_by(type="trade").all()
    assert len(events) == 1
    assert events[0].actor_id == buyer.id
    assert events[0].target_id == seller.id
    assert events[0].weight == 2
    assert '"item_id":1' in events[0].payload_json
    assert '"qty":1' in events[0].payload_json
    assert '"price":600' in events[0].payload_json


async def test_list_item_invalid_params(db, client):
    from jobs.seed import seed_items

    seed_items(db)
    db.commit()
    cookies = await _register(client, "xchar")
    client.cookies.update(cookies)
    char = db.query(Character).filter_by(name="xchar").first()
    char.cash = 5000
    db.commit()
    await client.post("/api/shop/buy", json={"item_id": 1, "qty": 1})
    resp = await client.post("/api/market/list", json={"item_id": None, "price": 600, "qty": 1})
    assert resp.status_code == 400
    resp = await client.post("/api/market/list", json={"item_id": 1, "price": 0, "qty": 1})
    assert resp.status_code == 400
    resp = await client.post("/api/market/list", json={"item_id": 1, "price": 600, "qty": 0})
    assert resp.status_code == 400
    resp = await client.post("/api/market/list", json={"item_id": 1, "price": 10_000_001, "qty": 1})
    assert resp.status_code == 400
