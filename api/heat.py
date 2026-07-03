from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.tables import Character, Event
from core.state import load_character
from core.heat import bribe_cost
from api.deps import get_db, get_current_character

router = APIRouter(prefix="/heat", tags=["heat"])


@router.post("/bribe")
def bribe(char: Character = Depends(get_current_character), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    state = load_character(db, char.id, now)
    cost = bribe_cost(state.heat)
    if state.cash < cost:
        raise HTTPException(
            status_code=400,
            detail={"error": f"Need ${cost}, have ${state.cash}", "code": "INSUFFICIENT_CASH"},
        )
    new_heat = max(0, state.heat - 30)
    row = db.query(Character).filter_by(id=char.id).first()
    row.cash -= cost
    row.heat = new_heat
    row.heat_updated_at = now
    ev = Event(
        ts=now,
        type="bribe",
        actor_id=char.id,
        payload_json=f'{{"heat_before":{state.heat},"heat_after":{new_heat},"cost":{cost}}}',
        weight=2,
    )
    db.add(ev)
    db.commit()
    return {"heat": new_heat, "cash": row.cash, "cost": cost}
