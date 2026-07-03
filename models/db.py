import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///livewire.db")
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)

def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    from models.tables import Base
    Base.metadata.create_all(bind=engine)
