from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import CharacterState


@dataclass
class UseItemResult:
    health_gained: int
    energy_gained: int
    buff_kind: Optional[str]
    buff_until: Optional[datetime]
    effect_text: str


ITEM_EFFECTS = {
    11: {"health": 40, "energy": 0, "buff": None, "duration_min": 0, "daily_cap": 5},
    12: {"health": 0, "energy": 25, "buff": None, "duration_min": 0, "daily_cap": 2},
    13: {"health": 0, "energy": 0, "buff": "adrenaline", "duration_min": 60, "daily_cap": 1},
}


def use_consumable(char: "CharacterState", item_id: int, now: datetime) -> UseItemResult:
    effect = ITEM_EFFECTS.get(item_id)
    if not effect:
        raise ValueError(f"Unknown consumable item: {item_id}")
    health = min(100, char.health + effect["health"]) - char.health
    energy = min(150, char.energy + effect["energy"]) - char.energy
    buff_until = None
    if effect["buff"]:
        buff_until = now + timedelta(minutes=effect["duration_min"])
    return UseItemResult(
        health_gained=max(0, health),
        energy_gained=max(0, energy),
        buff_kind=effect["buff"],
        buff_until=buff_until,
        effect_text=effect["buff"] or ("heal" if effect["health"] else "energy"),
    )
