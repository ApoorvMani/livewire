from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    LargeBinary,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False, index=True)
    pw_hash = Column(String(128), nullable=False)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    flags = Column(Integer, default=0)

    characters = relationship("Character", back_populates="user")


class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_ai = Column(Boolean, default=False)
    name = Column(String(30), nullable=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    strength = Column(Integer, default=10)
    speed = Column(Integer, default=10)
    defense = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    energy = Column(Integer, default=100)
    nerve = Column(Integer, default=15)
    health = Column(Integer, default=100)
    bars_updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    cash = Column(Integer, default=500)
    bank = Column(Integer, default=0)
    heat = Column(Integer, default=0)
    heat_updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notoriety = Column(Integer, default=0)
    job_id = Column(Integer, nullable=True)
    faction_id = Column(Integer, nullable=True)
    hospital_until = Column(DateTime, nullable=True)
    jail_until = Column(DateTime, nullable=True)
    crime_skill = Column(Float, default=0.0)
    persona_json = Column(Text, nullable=True)
    next_tick_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="characters")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    slot = Column(String(20), nullable=False)
    bonus = Column(Integer, nullable=False)
    base_price = Column(Integer, nullable=False)
    daily_cap = Column(Integer, nullable=True)


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    char_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    qty = Column(Integer, default=1)
    equipped = Column(Boolean, default=False)


class MarketListing(Base):
    __tablename__ = "market_listings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    price = Column(Integer, nullable=False)
    qty = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class MarketBand(Base):
    __tablename__ = "market_bands"
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    floor = Column(Integer, nullable=False)
    ceiling = Column(Integer, nullable=False)
    mm_daily_cap = Column(Integer, nullable=False)


class Crime(Base):
    __tablename__ = "crimes"
    id = Column(String(20), primary_key=True)
    tier = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    nerve_cost = Column(Integer, nullable=False)
    base_success = Column(Float, nullable=False)
    payout_min = Column(Integer, nullable=False)
    payout_max = Column(Integer, nullable=False)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False)
    type = Column(String(30), nullable=False)
    actor_id = Column(Integer, nullable=False)
    target_id = Column(Integer, nullable=True)
    payload_json = Column(Text, nullable=True)
    weight = Column(Integer, nullable=False)
    seen_by_target = Column(Boolean, default=False)


class Nemesis(Base):
    __tablename__ = "nemeses"
    char_id = Column(Integer, ForeignKey("characters.id"), primary_key=True)
    ai_id = Column(Integer, nullable=False)
    stage = Column(Integer, default=0)
    assigned_at = Column(DateTime, nullable=False)
    defeats = Column(Integer, default=0)


class Faction(Base):
    __tablename__ = "factions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    boss_id = Column(Integer, nullable=True)
    is_ai_led = Column(Boolean, nullable=False)
    points = Column(Integer, default=0)


class FactionMember(Base):
    __tablename__ = "faction_members"
    id = Column(Integer, primary_key=True, autoincrement=True)
    faction_id = Column(Integer, ForeignKey("factions.id"), nullable=False)
    char_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    rank = Column(String(20), nullable=False)


class NewspaperIssue(Base):
    __tablename__ = "newspaper_issues"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, unique=True, nullable=False)
    content_md = Column(Text, nullable=False)


class DigestsCache(Base):
    __tablename__ = "digests_cache"
    char_id = Column(Integer, ForeignKey("characters.id"), primary_key=True)
    last_event_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    ts = Column(DateTime, nullable=False)


class LlmCache(Base):
    __tablename__ = "llm_cache"
    purpose = Column(String(50), nullable=False)
    key_hash = Column(String(64), nullable=False)
    output = Column(Text, nullable=True)
    ts = Column(DateTime, nullable=False)
    __table_args__ = (PrimaryKeyConstraint("purpose", "key_hash"),)


class LlmLog(Base):
    __tablename__ = "llm_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False)
    purpose = Column(String(50), nullable=False)
    tier = Column(String(5), nullable=False)
    tokens_in = Column(Integer, nullable=False)
    tokens_out = Column(Integer, nullable=False)
    cost_est = Column(Float, nullable=False)


class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    name = Column(String(50), primary_key=True)
    enabled = Column(Boolean, nullable=False)
    config_json = Column(Text, default="{}")


class MetricsEvent(Base):
    __tablename__ = "metrics_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False)
    char_id = Column(Integer, nullable=True)
    name = Column(String(50), nullable=False)
    props_json = Column(Text, nullable=True)


class Buff(Base):
    __tablename__ = "buffs"
    char_id = Column(Integer, ForeignKey("characters.id"), primary_key=True)
    kind = Column(String(30), primary_key=True)
    until = Column(DateTime, nullable=False)


class ContentLine(Base):
    __tablename__ = "content_lines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    kind = Column(String(30), nullable=False)
    key = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=True)
