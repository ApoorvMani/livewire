from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Literal
from sqlalchemy.orm import Session
from models.tables import Character, Inventory, Item, Buff as BuffTable
from core.exceptions import DomainError
from core.regen import apply_regen, max_bars, BarsState
from core.heat import apply_heat_decay


@dataclass
class CharacterState:
    id: int
    name: str
    level: int
    xp: int
    strength: int
    speed: int
    defense: int
    dexterity: int
    energy: int
    nerve: int
    health: int
    bars_updated_at: datetime
    cash: int
    bank: int
    heat: int
    heat_updated_at: datetime
    notoriety: int
    crime_skill: float
    hospital_until: Optional[datetime]
    jail_until: Optional[datetime]
    job_id: Optional[int]
    faction_id: Optional[int]
    weapon_bonus: int
    armor_bonus: int
    buff_until: Optional[datetime]


def load_character(session: Session, char_id: int, now: datetime) -> CharacterState:
    row = session.query(Character).filter_by(id=char_id).first()
    if not row:
        raise DomainError("NOT_FOUND", "Character not found")
    max_e, max_n, max_h = max_bars(row.level)
    bars_updated = row.bars_updated_at
    if bars_updated.tzinfo is None:
        bars_updated = bars_updated.replace(tzinfo=timezone.utc)
    bars = apply_regen(
        BarsState(row.energy, row.nerve, row.health, bars_updated), now, max_e, max_n, max_h
    )
    row.energy = bars.energy
    row.nerve = bars.nerve
    row.health = bars.health
    row.bars_updated_at = bars.updated_at
    heat, heat_updated_at = apply_heat_decay(row.heat, row.heat_updated_at, now)
    row.heat = heat
    row.heat_updated_at = heat_updated_at
    jail_until = row.jail_until
    if jail_until is not None and jail_until.tzinfo is None:
        jail_until = jail_until.replace(tzinfo=timezone.utc)
    hospital_until = row.hospital_until
    if hospital_until is not None and hospital_until.tzinfo is None:
        hospital_until = hospital_until.replace(tzinfo=timezone.utc)
    # Load equipped item bonuses
    weapon_bonus = 0
    armor_bonus = 0
    equipped_rows = (
        session.query(Inventory, Item)
        .join(Item, Inventory.item_id == Item.id)
        .filter(Inventory.char_id == char_id, Inventory.equipped)
        .all()
    )
    for inv, itm in equipped_rows:
        if itm.slot == "weapon":
            weapon_bonus += itm.bonus
        elif itm.slot == "armor":
            armor_bonus += itm.bonus
    # Load active buffs
    buff_until = None
    active_buff = (
        session.query(BuffTable)
        .filter_by(char_id=char_id, kind="adrenaline")
        .filter(BuffTable.until > now)
        .first()
    )
    if active_buff:
        b = active_buff.until
        if b.tzinfo is None:
            b = b.replace(tzinfo=timezone.utc)
        buff_until = b
    return CharacterState(
        id=row.id,
        name=row.name,
        level=row.level,
        xp=row.xp,
        strength=row.strength,
        speed=row.speed,
        defense=row.defense,
        dexterity=row.dexterity,
        energy=bars.energy,
        nerve=bars.nerve,
        health=bars.health,
        bars_updated_at=bars.updated_at,
        cash=row.cash,
        bank=row.bank,
        heat=heat,
        heat_updated_at=heat_updated_at,
        notoriety=row.notoriety,
        crime_skill=row.crime_skill,
        hospital_until=hospital_until,
        jail_until=jail_until,
        job_id=row.job_id,
        faction_id=row.faction_id,
        weapon_bonus=weapon_bonus,
        armor_bonus=armor_bonus,
        buff_until=buff_until,
    )


def derive_status(char: CharacterState, now: datetime) -> Literal["ok", "hospital", "jail"]:
    if char.jail_until and char.jail_until > now:
        return "jail"
    if char.hospital_until and char.hospital_until > now:
        return "hospital"
    return "ok"


def require_ok(char: CharacterState, now: datetime) -> None:
    status = derive_status(char, now)
    if status != "ok":
        remaining = 0
        if status == "jail" and char.jail_until:
            remaining = int((char.jail_until - now).total_seconds())
        elif status == "hospital" and char.hospital_until:
            remaining = int((char.hospital_until - now).total_seconds())
        raise DomainError("INCAPACITATED", f"You are in {status} for {remaining}s")
