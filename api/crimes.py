from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random

from models.tables import Crime as CrimeTable, Character, Event
from core.crimes import attempt_crime, CrimeRow
from core.state import load_character
from core.exceptions import DomainError
from core.heat import check_threshold
from core.progression import xp_to_level
from api.deps import get_db, get_current_character

router = APIRouter(prefix="/crimes", tags=["crimes"])


@router.get("")
def list_crimes(char: Character = Depends(get_current_character), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    state = load_character(db, char.id, now)
    crimes = db.query(CrimeTable).order_by(CrimeTable.tier, CrimeTable.id).all()
    result = []
    for c in crimes:
        success_p = max(0.05, min(0.95, c.base_success + state.crime_skill * 0.005))
        result.append(
            {
                "id": c.id,
                "tier": c.tier,
                "name": c.name,
                "nerve_cost": c.nerve_cost,
                "success_p": round(success_p, 3),
                "payout_min": c.payout_min,
                "payout_max": c.payout_max,
            }
        )
    return result


@router.post("/{crime_id}/attempt")
def attempt(
    crime_id: str, char: Character = Depends(get_current_character), db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    state = load_character(db, char.id, now)
    crime_row = db.query(CrimeTable).filter_by(id=crime_id).first()
    if not crime_row:
        raise HTTPException(
            status_code=404, detail={"error": "crime not found", "code": "NOT_FOUND"}
        )
    crime = CrimeRow(
        id=crime_row.id,
        tier=crime_row.tier,
        name=crime_row.name,
        nerve_cost=crime_row.nerve_cost,
        base_success=crime_row.base_success,
        payout_min=crime_row.payout_min,
        payout_max=crime_row.payout_max,
    )
    rng = random.Random()
    try:
        result = attempt_crime(state, crime, rng, now)
    except DomainError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})
    row = db.query(Character).filter_by(id=char.id).first()
    row.energy = state.energy
    row.nerve = state.nerve - crime.nerve_cost
    row.health = state.health
    row.cash += result.payout
    row.xp += result.xp
    row.crime_skill += result.skill_gain
    old_heat = row.heat
    row.heat += result.heat_gain
    row.bars_updated_at = now
    if result.jailed:
        row.jail_until = now + timedelta(minutes=result.jail_minutes)
    new_level = xp_to_level(row.xp)
    if new_level > row.level:
        row.level = new_level
        lev_ev = Event(
            ts=now,
            type="level_up",
            actor_id=char.id,
            payload_json=f'{{"level":{new_level}}}',
            weight=2,
        )
        db.add(lev_ev)
    for te in check_threshold(old_heat, row.heat):
        if te["type"] == "shakedown":
            fine = min(int(row.cash * te["fine_pct"]), te["fine_max"])
            row.cash -= fine
            db.add(
                Event(
                    ts=now,
                    type="shakedown",
                    actor_id=char.id,
                    payload_json=f'{{"fine":{fine}}}',
                    weight=te["weight"],
                )
            )
        elif te["type"] == "raid":
            loss = int(row.cash * te["cash_loss_pct"])
            row.cash -= loss
            row.jail_until = now + timedelta(minutes=te["jail_min"])
            db.add(
                Event(
                    ts=now,
                    type="raid",
                    actor_id=char.id,
                    payload_json=f'{{"cash_loss":{loss},"jail_min":{te["jail_min"]}}}',
                    weight=te["weight"],
                )
            )
    ev = Event(
        ts=now,
        type="crime",
        actor_id=char.id,
        payload_json=f'{{"crime_id":"{crime_id}","success":{str(result.success).lower()},"payout":{result.payout}}}',
        weight=crime.tier * (2 if result.success else 1),
    )
    db.add(ev)
    db.commit()
    return {
        "success": result.success,
        "payout": result.payout,
        "xp": result.xp,
        "jailed": result.jailed,
        "heat_gain": result.heat_gain,
        "text_key": result.text_key,
    }
