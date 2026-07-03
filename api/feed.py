from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.tables import Event
from api.deps import get_db, get_current_character

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("")
def feed(since_id: int = 0, char=Depends(get_current_character), db: Session = Depends(get_db)):
    events = (
        db.query(Event)
        .filter(Event.id > since_id, (Event.actor_id == char.id) | (Event.target_id == char.id))
        .order_by(Event.id.desc())
        .limit(50)
        .all()
    )
    result = []
    now = datetime.now(timezone.utc)
    if events:
        event_ids = [e.id for e in events]
        db.query(Event).filter(
            Event.id.in_(event_ids),
            Event.target_id == char.id,
            not Event.seen_by_target,
        ).update({"seen_by_target": True}, synchronize_session=False)
    for e in events:
        mins_ago = int((now - e.ts).total_seconds() / 60)
        result.append(
            {
                "id": e.id,
                "type": e.type,
                "ts": e.ts.isoformat(),
                "actor_id": e.actor_id,
                "target_id": e.target_id,
                "weight": e.weight,
                "mins_ago": mins_ago,
                "payload_json": e.payload_json,
            }
        )
    db.commit()
    return result
