from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from itsdangerous import URLSafeTimedSerializer
from os import getenv

from models.tables import User, Character
from api.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-z0-9_]+$")
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    username: str
    password: str

def make_session(user_id: int) -> str:
    secret = getenv("SECRET_KEY", "dev-secret-key")
    s = URLSafeTimedSerializer(secret)
    return s.dumps(user_id)

@router.post("/register")
def register(req: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=req.username).first()
    if existing:
        raise HTTPException(status_code=409, detail={"error": "username taken", "code": "USERNAME_TAKEN"})
    pw_hash = bcrypt.hash(req.password)
    now = datetime.now(timezone.utc)
    user = User(username=req.username, pw_hash=pw_hash, created_at=now)
    db.add(user)
    db.flush()
    char = Character(name=req.username, user_id=user.id, bars_updated_at=now, created_at=now)
    db.add(char)
    db.commit()
    token = make_session(user.id)
    response.set_cookie(key="session", value=token, httponly=True, max_age=30*86400, samesite="lax")
    return {"id": user.id, "username": user.username}

@router.post("/login")
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=req.username).first()
    if not user or not bcrypt.verify(req.password, user.pw_hash):
        raise HTTPException(status_code=401, detail={"error": "invalid credentials", "code": "INVALID_CREDENTIALS"})
    token = make_session(user.id)
    response.set_cookie(key="session", value=token, httponly=True, max_age=30*86400, samesite="lax")
    return {"id": user.id, "username": user.username}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session")
    return {"ok": True}
