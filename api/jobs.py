from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.tables import Character, Event, Job
from core.regen import max_bars
from api.deps import get_db, get_current_character

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs(char: Character = Depends(get_current_character), db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return {
        "jobs": [
            {"id": j.id, "name": j.name, "description": j.description, "pay": j.pay} for j in jobs
        ]
    }


@router.post("/select")
def select_job(
    body: dict, char: Character = Depends(get_current_character), db: Session = Depends(get_db)
):
    job_id = body.get("job_id")
    if not job_id:
        raise HTTPException(
            status_code=400, detail={"error": "job_id required", "code": "MISSING_JOB_ID"}
        )
    job = db.query(Job).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(
            status_code=404, detail={"error": "Job not found", "code": "JOB_NOT_FOUND"}
        )
    now = datetime.now(timezone.utc)
    row = db.query(Character).filter_by(id=char.id).first()
    row.job_id = job_id
    ev = Event(
        ts=now, type="job_select", actor_id=char.id, payload_json=f'{{"job_id":{job_id}}}', weight=1
    )
    db.add(ev)
    db.commit()
    return {"job_id": job_id, "job_name": job.name}


@router.post("/collect")
def collect_job(char: Character = Depends(get_current_character), db: Session = Depends(get_db)):
    if not char.job_id:
        raise HTTPException(status_code=400, detail={"error": "No job selected", "code": "NO_JOB"})
    job = db.query(Job).filter_by(id=char.job_id).first()
    if not job:
        raise HTTPException(
            status_code=400, detail={"error": "Job not found", "code": "JOB_NOT_FOUND"}
        )
    now = datetime.now(timezone.utc)
    last_event = (
        db.query(Event)
        .filter_by(actor_id=char.id, type="job_pay")
        .order_by(Event.ts.desc())
        .first()
    )
    if last_event:
        last_ts = last_event.ts
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
        if (now - last_ts).total_seconds() < 86400:
            remaining = int(86400 - (now - last_ts).total_seconds())
            raise HTTPException(
                status_code=400,
                detail={"error": f"Collect again in {remaining}s", "code": "COOLDOWN"},
            )
    row = db.query(Character).filter_by(id=char.id).first()
    row.cash += job.pay

    if job.name == "Clinic Aide":
        _, _, max_h = max_bars(row.level)
        row.health = min(max_h, row.health + 20)
    elif job.perk_stat in ("speed", "strength", "defense", "dexterity"):
        setattr(row, job.perk_stat, getattr(row, job.perk_stat) + int(job.perk_amount))
    elif job.perk_stat == "crime_skill":
        row.crime_skill += job.perk_amount

    ev = Event(
        ts=now,
        type="job_pay",
        actor_id=char.id,
        payload_json=f'{{"job_id":{job.id},"pay":{job.pay}}}',
        weight=1,
    )
    db.add(ev)
    db.commit()
    return {"pay": job.pay, "cash": row.cash, "job_name": job.name}
