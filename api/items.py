from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.tables import Item, Inventory, Character, Event, Buff
from api.deps import get_db, get_current_character
from core.items import use_consumable, ITEM_EFFECTS
from core.state import CharacterState

router = APIRouter(tags=["items"])


@router.get("/shop")
def shop(db: Session = Depends(get_db)):
    items = db.query(Item).order_by(Item.id).all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "slot": i.slot,
            "bonus": i.bonus,
            "base_price": i.base_price,
            "daily_cap": i.daily_cap,
        }
        for i in items
    ]


@router.post("/shop/buy")
def buy_item(
    body: dict,
    char: Character = Depends(get_current_character),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    item_id = body.get("item_id")
    qty = body.get("qty", 1)
    if not item_id or qty <= 0:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid request", "code": "INVALID_REQUEST"},
        )
    item = db.query(Item).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail={"error": "Item not found", "code": "NOT_FOUND"},
        )
    cost = item.base_price * qty
    row = db.query(Character).filter_by(id=char.id).first()
    if row.cash < cost:
        raise HTTPException(
            status_code=400,
            detail={"error": "Not enough cash", "code": "NOT_ENOUGH_CASH"},
        )
    row.cash -= cost
    inv = db.query(Inventory).filter_by(char_id=char.id, item_id=item_id).first()
    if inv:
        inv.qty += qty
    else:
        db.add(Inventory(char_id=char.id, item_id=item_id, qty=qty, equipped=False))
    ev = Event(
        ts=now,
        type="buy_item",
        actor_id=char.id,
        payload_json=f'{{"item_id":{item_id},"qty":{qty},"cost":{cost}}}',
        weight=1,
    )
    db.add(ev)
    db.commit()
    return {"cash": row.cash}


@router.get("/inventory")
def inventory(
    char: Character = Depends(get_current_character),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Inventory, Item)
        .join(Item, Inventory.item_id == Item.id)
        .filter(Inventory.char_id == char.id)
        .all()
    )
    result = []
    for inv, item in rows:
        result.append(
            {
                "id": inv.id,
                "item_id": item.id,
                "name": item.name,
                "slot": item.slot,
                "bonus": item.bonus,
                "qty": inv.qty,
                "equipped": inv.equipped,
            }
        )
    return result


@router.post("/inventory/{inv_id}/equip")
def equip_item(
    inv_id: int,
    char: Character = Depends(get_current_character),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    inv = db.query(Inventory).filter_by(id=inv_id, char_id=char.id).first()
    if not inv:
        raise HTTPException(
            status_code=404,
            detail={"error": "Item not found", "code": "NOT_FOUND"},
        )
    item = db.query(Item).filter_by(id=inv.item_id).first()
    if item.slot == "consumable":
        raise HTTPException(
            status_code=400,
            detail={"error": "Cannot equip consumable", "code": "INVALID_SLOT"},
        )
    if inv.qty < 1:
        raise HTTPException(
            status_code=400,
            detail={"error": "No items left", "code": "NO_ITEMS"},
        )
    # Unequip same slot
    existing = (
        db.query(Inventory)
        .join(Item)
        .filter(
            Inventory.char_id == char.id,
            Inventory.equipped,
            Item.slot == item.slot,
        )
        .all()
    )
    for e in existing:
        e.equipped = False
    inv.equipped = True
    ev = Event(
        ts=now,
        type="equip_item",
        actor_id=char.id,
        payload_json=f'{{"item_id":{item.id}}}',
        weight=1,
    )
    db.add(ev)
    db.commit()
    return {"equipped": True}


@router.post("/inventory/{inv_id}/unequip")
def unequip_item(
    inv_id: int,
    char: Character = Depends(get_current_character),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    inv = db.query(Inventory).filter_by(id=inv_id, char_id=char.id).first()
    if not inv:
        raise HTTPException(
            status_code=404,
            detail={"error": "Item not found", "code": "NOT_FOUND"},
        )
    inv.equipped = False
    ev = Event(
        ts=now,
        type="unequip_item",
        actor_id=char.id,
        payload_json=f'{{"item_id":{inv.item_id}}}',
        weight=1,
    )
    db.add(ev)
    db.commit()
    return {"equipped": False}


@router.post("/inventory/{inv_id}/use")
def use_item(
    inv_id: int,
    char: Character = Depends(get_current_character),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    inv = db.query(Inventory).filter_by(id=inv_id, char_id=char.id).first()
    if not inv or inv.qty < 1:
        raise HTTPException(
            status_code=404,
            detail={"error": "Item not found", "code": "NOT_FOUND"},
        )
    item = db.query(Item).filter_by(id=inv.item_id).first()
    if item.slot != "consumable":
        raise HTTPException(
            status_code=400,
            detail={"error": "Not a consumable", "code": "NOT_CONSUMABLE"},
        )
    effect = ITEM_EFFECTS.get(item.id)
    if not effect:
        raise HTTPException(
            status_code=400,
            detail={"error": "Unknown item", "code": "UNKNOWN_ITEM"},
        )
    cap = effect.get("daily_cap", 0)
    if cap:
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        used_today = (
            db.query(Event)
            .filter(
                Event.type == "use_item",
                Event.actor_id == char.id,
                Event.ts >= today_start,
                Event.payload_json.like(f'%"item_id":{item.id}%'),
            )
            .count()
        )
        if used_today >= cap:
            raise HTTPException(
                status_code=400,
                detail={"error": "Daily cap reached", "code": "DAILY_CAP"},
            )
    row = db.query(Character).filter_by(id=char.id).first()
    state = CharacterState(
        id=row.id,
        name=row.name,
        level=row.level,
        xp=row.xp,
        strength=row.strength,
        speed=row.speed,
        defense=row.defense,
        dexterity=row.dexterity,
        energy=row.energy,
        nerve=row.nerve,
        health=row.health,
        bars_updated_at=row.bars_updated_at,
        cash=row.cash,
        bank=row.bank,
        heat=row.heat,
        heat_updated_at=row.heat_updated_at,
        notoriety=row.notoriety,
        crime_skill=row.crime_skill,
        hospital_until=row.hospital_until,
        jail_until=row.jail_until,
        job_id=row.job_id,
        faction_id=row.faction_id,
        weapon_bonus=0,
        armor_bonus=0,
        buff_until=None,
    )
    result = use_consumable(state, item.id, now)
    row.health += result.health_gained
    row.energy += result.energy_gained
    row.bars_updated_at = now
    if result.buff_kind:
        existing = db.query(Buff).filter_by(char_id=char.id, kind=result.buff_kind).first()
        if existing:
            existing.until = result.buff_until
        else:
            db.add(
                Buff(
                    char_id=char.id,
                    kind=result.buff_kind,
                    until=result.buff_until,
                )
            )
    inv.qty -= 1
    if inv.qty <= 0:
        db.delete(inv)
    ev = Event(
        ts=now,
        type="use_item",
        actor_id=char.id,
        payload_json=f'{{"item_id":{item.id}}}',
        weight=1,
    )
    db.add(ev)
    db.commit()
    return {"used": True, "item": item.name}
