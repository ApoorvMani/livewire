import random
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.tables import Base

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()

@pytest.fixture
def rng():
    return random.Random(42)

@pytest.fixture
def now():
    return datetime(2026, 7, 3, 12, 0, 0, tzinfo=timezone.utc)
