from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random

from models.tables import Character, Event
from core.state import load_character, require_ok
from core.exceptions import DomainError
from api.deps import get_db, get_current_character

router = APIRouter(prefix="/jail", tags=["jail"])


@router.get("/list")
def list_jailed(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    jailed = (
        db.query(Character)
        .filter(
            Character.jail_until.isnot(None),
            Character.jail_until > now,
        )
        .all()
    )
    result = []
    for c in jailed:
        remaining = int((c.jail_until - now).total_seconds() // 60)
        result.append({"id": c.id, "name": c.name, "level": c.level, "minutes_left": remaining})
    return result


@router.post("/{char_id}/bust")
def bust_out(
    char_id: int,
    char: Character = Depends(get_current_character),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    state = load_character(db, char.id, now)
    try:
        require_ok(state, now)
    except DomainError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})
    if state.energy < 10:
        raise HTTPException(
            status_code=400,
            detail={"error": "Need 10 energy", "code": "NOT_ENOUGH_ENERGY"},
        )
    if char.id == char_id:
        raise HTTPException(
            status_code=400,
            detail={"error": "Cannot bust yourself", "code": "SELF_BUST"},
        )
    target = db.query(Character).filter_by(id=char_id).first()
    if not target:
        raise HTTPException(
            status_code=404,
            detail={"error": "Character not found", "code": "NOT_FOUND"},
        )
    target_jail = target.jail_until
    if target_jail is not None and target_jail.tzinfo is None:
        target_jail = target_jail.replace(tzinfo=timezone.utc)
    if not target_jail or target_jail <= now:
        raise HTTPException(
            status_code=400,
            detail={"error": "Target is not jailed", "code": "NOT_JAILED"},
        )
    rng = random.Random()
    success_p = max(0.05, min(0.95, 0.30 + state.crime_skill * 0.004))
    success = rng.random() < success_p
    row = db.query(Character).filter_by(id=char.id).first()
    row.energy -= 10
    row.bars_updated_at = now
    if success:
        target.jail_until = None
        ev = Event(
            ts=now,
            type="bust",
            actor_id=char.id,
            target_id=char_id,
            payload_json='{"success": true}',
            weight=6,
        )
    else:
        target.jail_until = now + timedelta(minutes=rng.randint(5, 15))
        ev = Event(
            ts=now,
            type="bust",
            actor_id=char.id,
            target_id=char_id,
            payload_json='{"success": false}',
            weight=3,
        )
    db.add(ev)
    db.commit()
    return {"success": success}
