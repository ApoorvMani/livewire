from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from models.db import get_session as _get_session

def get_db(request: Request):
    if hasattr(request.app.state, "test_db"):
        yield request.app.state.test_db
    else:
        yield from _get_session()

async def get_current_character(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session")
    if not session_token:
        raise HTTPException(status_code=401, detail={"error": "Not authenticated", "code": "NOT_AUTHENTICATED"})
    from models.tables import User, Character
    from itsdangerous import URLSafeTimedSerializer
    from os import getenv
    secret = getenv("SECRET_KEY", "dev-secret-key")
    s = URLSafeTimedSerializer(secret)
    try:
        user_id = s.loads(session_token, max_age=30*86400)
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid session", "code": "INVALID_SESSION"})
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail={"error": "User not found", "code": "USER_NOT_FOUND"})
    char = db.query(Character).filter_by(user_id=user.id).first()
    if not char:
        raise HTTPException(status_code=401, detail={"error": "Character not found", "code": "CHARACTER_NOT_FOUND"})
    return char
