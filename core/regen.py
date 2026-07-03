from dataclasses import dataclass
from datetime import datetime, timedelta

ENERGY_INTERVAL = timedelta(minutes=10)
ENERGY_RATE = 5
NERVE_INTERVAL = timedelta(minutes=5)
NERVE_RATE = 1
HEALTH_INTERVAL = timedelta(minutes=3)
HEALTH_RATE = 1

@dataclass
class BarsState:
    energy: int
    nerve: int
    health: int
    updated_at: datetime

def apply_regen(b: BarsState, now: datetime, max_energy: int, max_nerve: int, max_health: int) -> BarsState:
    energy_intervals = int((now - b.updated_at) / ENERGY_INTERVAL)
    nerve_intervals = int((now - b.updated_at) / NERVE_INTERVAL)
    health_intervals = int((now - b.updated_at) / HEALTH_INTERVAL)

    new_energy = min(max_energy, b.energy + energy_intervals * ENERGY_RATE)
    new_nerve = min(max_nerve, b.nerve + nerve_intervals * NERVE_RATE)
    new_health = min(max_health, b.health + health_intervals * HEALTH_RATE)

    new_updated = b.updated_at
    if energy_intervals > 0:
        new_updated = max(new_updated, b.updated_at + energy_intervals * ENERGY_INTERVAL)
    if nerve_intervals > 0:
        new_updated = max(new_updated, b.updated_at + nerve_intervals * NERVE_INTERVAL)
    if health_intervals > 0:
        new_updated = max(new_updated, b.updated_at + health_intervals * HEALTH_INTERVAL)

    return BarsState(energy=new_energy, nerve=new_nerve, health=new_health, updated_at=new_updated)

def max_bars(level: int):
    energy = min(150, 100 + 5 * (level - 1))
    nerve = min(25, 15 + (level - 1) // 2)
    return (energy, nerve, 100)
