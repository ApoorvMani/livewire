import pytest
from models.tables import Event


@pytest.mark.asyncio
async def test_event_sequence(db, client):
    from jobs.seed import seed_crimes, seed_jobs

    seed_crimes(db)
    seed_jobs(db)
    db.commit()

    resp = await client.post(
        "/api/auth/register", json={"username": "evtest", "password": "password123"}
    )
    assert resp.status_code == 200

    resp = await client.post("/api/crimes/crime_t1_a/attempt")
    assert resp.status_code == 200
    crime_data = resp.json()

    resp = await client.post("/api/gym/train/strength")
    assert resp.status_code == 200

    resp = await client.post("/api/crimes/crime_t1_a/attempt")
    assert resp.status_code == 200

    resp = await client.post("/api/gym/train/speed")
    assert resp.status_code == 200

    resp = await client.post("/api/crimes/crime_t1_b/attempt")
    assert resp.status_code == 200

    resp = await client.post("/api/gym/train/defense")
    assert resp.status_code == 200

    resp = await client.post("/api/gym/train/dexterity")
    assert resp.status_code == 200

    events = db.query(Event).order_by(Event.id).all()
    assert len(events) == 7

    expected = [
        ("crime", 1 if not crime_data.get("success") else 2),
        ("train", 1),
        ("crime", None),
        ("train", 1),
        ("crime", None),
        ("train", 1),
        ("train", 1),
    ]
    for i, (etype, eweight) in enumerate(expected):
        assert events[i].type == etype, f"event {i}: expected type {etype}, got {events[i].type}"
        if eweight is not None:
            assert events[i].weight == eweight, (
                f"event {i}: expected weight {eweight}, got {events[i].weight}"
            )
        elif events[i].type == "crime":
            assert events[i].weight in (1, 2), (
                f"event {i}: crime weight should be 1 or 2, got {events[i].weight}"
            )
