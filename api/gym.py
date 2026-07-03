from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random

from models.tables import Character, Event
from core.state import load_character
from core.gym import train
from core.exceptions import DomainError
from api.deps import get_db, get_current_character

router = APIRouter(tags=["gym"])

@router.post("/gym/train/{stat}")
def train_stat(stat: str, char: Character = Depends(get_current_character), db: Session = Depends(get_db)):
    if stat not in ("strength", "speed", "defense", "dexterity"):
        raise HTTPException(status_code=400, detail={"error": "invalid stat", "code": "INVALID_STAT"})
    now = datetime.now(timezone.utc)
    state = load_character(db, char.id, now)
    rng = random.Random()
    try:
        result = train(state, stat, rng, now)
    except DomainError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})
    row = db.query(Character).filter_by(id=char.id).first()
    setattr(row, stat, getattr(row, stat) + result.stat_gain)
    row.energy -= result.energy_cost
    row.bars_updated_at = now
    ev = Event(ts=now, type="train", actor_id=char.id,
               payload_json=f'{{"stat":"{stat}","gain":{result.stat_gain}}}', weight=1)
    db.add(ev)
    db.commit()
    return {"stat": stat, "gain": result.stat_gain, "new_value": getattr(row, stat),
            "energy_remaining": row.energy}

@router.get("/me")
def me(char: Character = Depends(get_current_character), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    state = load_character(db, char.id, now)
    from core.regen import max_bars
    max_e, max_n, max_h = max_bars(state.level)
    row = db.query(Character).filter_by(id=char.id).first()
    row.energy = state.energy
    row.nerve = state.nerve
    row.health = state.health
    row.bars_updated_at = state.bars_updated_at
    db.commit()
    return {
        "id": state.id, "name": state.name, "level": state.level, "xp": state.xp,
        "strength": state.strength, "speed": state.speed, "defense": state.defense, "dexterity": state.dexterity,
        "energy": state.energy, "nerve": state.nerve, "health": state.health,
        "max_energy": max_e, "max_nerve": max_n, "max_health": max_h,
        "bars_updated_at": state.bars_updated_at.isoformat(),
        "cash": state.cash, "bank": state.bank,
        "heat": state.heat, "notoriety": state.notoriety,
        "crime_skill": state.crime_skill,
        "hospital_until": state.hospital_until.isoformat() if state.hospital_until else None,
        "jail_until": state.jail_until.isoformat() if state.jail_until else None,
    }
