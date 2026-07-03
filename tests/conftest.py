import random
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from models.tables import Base


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
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


@pytest.fixture
def app(db):
    from api.main import create_app

    app = create_app()
    app.state.test_db = db
    return app


@pytest.fixture
async def client(app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
