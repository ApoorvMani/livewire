from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import math

from models.tables import Character, Event
from core.state import load_character, require_ok
from core.combat import resolve_attack
from core.exceptions import DomainError
from api.deps import get_db, get_current_character

router = APIRouter(tags=["combat"])


@router.post("/attack")
def attack_target(
    body: dict, char: Character = Depends(get_current_character), db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    state = load_character(db, char.id, now)
    try:
        require_ok(state, now)
    except DomainError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})
    if state.energy < 25:
        raise HTTPException(
            status_code=400, detail={"error": "Need 25 energy", "code": "NOT_ENOUGH_ENERGY"}
        )
    target_name = body.get("target_name", "")
    if not target_name:
        raise HTTPException(
            status_code=400, detail={"error": "target_name required", "code": "MISSING_TARGET"}
        )
    target_row = db.query(Character).filter_by(name=target_name).first()
    if not target_row:
        raise HTTPException(
            status_code=404, detail={"error": "Target not found", "code": "NOT_FOUND"}
        )
    if char.id == target_row.id:
        raise HTTPException(
            status_code=400, detail={"error": "Cannot attack yourself", "code": "SELF_ATTACK"}
        )
    choice = body.get("choice", "mug")
    if choice not in ("mug", "hospitalize", "leave"):
        raise HTTPException(
            status_code=400, detail={"error": "Invalid choice", "code": "INVALID_CHOICE"}
        )
    target_state = load_character(db, target_row.id, now)
    try:
        require_ok(target_state, now)
    except DomainError:
        raise HTTPException(
            status_code=400,
            detail={"error": "Target is incapacitated", "code": "TARGET_INCAPACITATED"},
        )
    rng = random.Random()
    result = resolve_attack(state, target_state, choice, rng, now)
    row = db.query(Character).filter_by(id=char.id).first()
    row.energy -= 25
    row.heat += result.heat_gain
    row.notoriety += result.notoriety_gain
    row.xp += result.xp
    row.bars_updated_at = now
    if result.hospital_minutes_attacker > 0:
        row.hospital_until = now + timedelta(minutes=result.hospital_minutes_attacker)
    if result.mug_amount > 0:
        row.cash += result.mug_amount
        target_row.cash -= result.mug_amount
    if result.hospital_minutes_target > 0:
        target_row.hospital_until = now + timedelta(minutes=result.hospital_minutes_target)
    ev = Event(
        ts=now,
        type="attack",
        actor_id=char.id,
        target_id=target_row.id,
        payload_json=f'{{"p_win":{result.p_win:.3f},"choice":"{choice}","mug_amount":{result.mug_amount}}}',
        weight=8 if choice == "hospitalize" else (6 if choice == "mug" else 3),
    )
    if not result.won:
        ev.weight = 3
    db.add(ev)
    db.commit()
    return {
        "won": result.won,
        "p_win": round(result.p_win, 3),
        "mug_amount": result.mug_amount,
        "xp": result.xp,
        "heat_gain": result.heat_gain,
        "text_key": result.text_key,
    }


@router.post("/bank/deposit")
def deposit(
    body: dict, char: Character = Depends(get_current_character), db: Session = Depends(get_db)
):
    amount = body.get("amount", 0)
    if amount <= 0:
        raise HTTPException(
            status_code=400, detail={"error": "Invalid amount", "code": "INVALID_AMOUNT"}
        )
    row = db.query(Character).filter_by(id=char.id).first()
    if row.cash < amount:
        raise HTTPException(
            status_code=400, detail={"error": "Not enough cash", "code": "NOT_ENOUGH_CASH"}
        )
    fee = max(1, math.ceil(amount * 0.015))
    row.cash -= amount
    row.bank += amount - fee
    db.commit()
    return {"cash": row.cash, "bank": row.bank, "fee": fee}


@router.post("/bank/withdraw")
def withdraw(
    body: dict, char: Character = Depends(get_current_character), db: Session = Depends(get_db)
):
    amount = body.get("amount", 0)
    if amount <= 0:
        raise HTTPException(
            status_code=400, detail={"error": "Invalid amount", "code": "INVALID_AMOUNT"}
        )
    row = db.query(Character).filter_by(id=char.id).first()
    if row.bank < amount:
        raise HTTPException(
            status_code=400, detail={"error": "Not enough in bank", "code": "NOT_ENOUGH_BANK"}
        )
    row.bank -= amount
    row.cash += amount
    db.commit()
    return {"cash": row.cash, "bank": row.bank}
