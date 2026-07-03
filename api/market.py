import math
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.tables import MarketListing, Inventory, Event, Character
from api.deps import get_db, get_current_character

router = APIRouter(prefix="/market", tags=["market"])


@router.post("/list")
def list_item(
    body: dict, char: Character = Depends(get_current_character), db: Session = Depends(get_db)
):
    item_id = body.get("item_id")
    price = body.get("price")
    qty = body.get("qty", 1)
    if not item_id or not price or qty <= 0 or price < 1 or price > 10_000_000:
        raise HTTPException(
            status_code=400, detail={"error": "Invalid listing", "code": "INVALID_LISTING"}
        )
    inv = db.query(Inventory).filter_by(char_id=char.id, item_id=item_id).first()
    if not inv or inv.qty < qty:
        raise HTTPException(
            status_code=400, detail={"error": "Not enough items", "code": "NOT_ENOUGH_ITEMS"}
        )
    fee = max(1, math.ceil(price * qty * 0.02))
    row = db.query(Character).filter_by(id=char.id).first()
    if row.cash < fee:
        raise HTTPException(
            status_code=400, detail={"error": "Not enough cash for fee", "code": "NOT_ENOUGH_CASH"}
        )
    row.cash -= fee
    inv.qty -= qty
    if inv.qty <= 0:
        db.delete(inv)
    listing = MarketListing(seller_id=char.id, item_id=item_id, price=price, qty=qty)
    db.add(listing)
    db.commit()
    return {"id": listing.id, "fee": fee}


@router.get("/my")
def my_listings(char: Character = Depends(get_current_character), db: Session = Depends(get_db)):
    listings = (
        db.query(MarketListing)
        .filter_by(seller_id=char.id)
        .order_by(MarketListing.created_at.desc())
        .all()
    )
    return [
        {"id": row.id, "item_id": row.item_id, "price": row.price, "qty": row.qty}
        for row in listings
    ]


@router.get("/{item_id}")
def order_book(item_id: int, db: Session = Depends(get_db)):
    listings = (
        db.query(MarketListing).filter_by(item_id=item_id).order_by(MarketListing.price).all()
    )
    return [
        {"id": row.id, "seller_id": row.seller_id, "price": row.price, "qty": row.qty}
        for row in listings
    ]


@router.post("/buy/{listing_id}")
def buy_listing(
    listing_id: int,
    body: dict,
    char: Character = Depends(get_current_character),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    qty = body.get("qty", 1)
    listing = db.query(MarketListing).filter_by(id=listing_id).first()
    if not listing or listing.qty < qty:
        raise HTTPException(
            status_code=404,
            detail={"error": "Listing not found or insufficient qty", "code": "NOT_FOUND"},
        )
    cost = listing.price * qty
    row = db.query(Character).filter_by(id=char.id).first()
    if row.cash < cost:
        raise HTTPException(
            status_code=400, detail={"error": "Not enough cash", "code": "NOT_ENOUGH_CASH"}
        )
    result = db.execute(
        text("UPDATE market_listings SET qty = qty - :qty WHERE id = :id AND qty >= :qty"),
        {"qty": qty, "id": listing_id},
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(
            status_code=409, detail={"error": "Listing changed", "code": "CONCURRENT_BUY"}
        )
    seller = db.query(Character).filter_by(id=listing.seller_id).first()
    seller.cash += cost
    row.cash -= cost
    inv = db.query(Inventory).filter_by(char_id=char.id, item_id=listing.item_id).first()
    if inv:
        inv.qty += qty
    else:
        db.add(Inventory(char_id=char.id, item_id=listing.item_id, qty=qty, equipped=False))
    db.query(MarketListing).filter(MarketListing.id == listing_id, MarketListing.qty <= 0).delete()
    ev = Event(
        ts=now,
        type="trade",
        actor_id=char.id,
        target_id=listing.seller_id,
        payload_json=f'{{"item_id":{listing.item_id},"qty":{qty},"price":{listing.price}}}',
        weight=2,
    )
    db.add(ev)
    db.commit()
    return {"bought": True, "qty": qty, "total": cost}


@router.post("/cancel/{listing_id}")
def cancel_listing(
    listing_id: int, char: Character = Depends(get_current_character), db: Session = Depends(get_db)
):
    listing = db.query(MarketListing).filter_by(id=listing_id, seller_id=char.id).first()
    if not listing:
        raise HTTPException(
            status_code=404, detail={"error": "Listing not found", "code": "NOT_FOUND"}
        )
    item_id = listing.item_id
    qty = listing.qty
    db.delete(listing)
    inv = db.query(Inventory).filter_by(char_id=char.id, item_id=item_id).first()
    if inv:
        inv.qty += qty
    else:
        db.add(Inventory(char_id=char.id, item_id=item_id, qty=qty, equipped=False))
    db.commit()
    return {"cancelled": True, "qty_returned": qty}
