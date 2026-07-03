from dataclasses import dataclass
from datetime import datetime
import random
from core.state import CharacterState
from core.exceptions import DomainError

BASE_GAIN = 5
ENERGY_COST = 5
DIMINISHING_K = 5000

@dataclass
class GymResult:
    stat_gained: str
    stat_gain: int
    energy_cost: int

def train(char: CharacterState, stat: str, rng: random.Random, now: datetime) -> GymResult:
    if char.jail_until and char.jail_until > now:
        raise DomainError("INCAPACITATED", "You are in jail")
    if char.hospital_until and char.hospital_until > now:
        raise DomainError("INCAPACITATED", "You are hospitalized")
    if char.energy < ENERGY_COST:
        raise DomainError("NOT_ENOUGH_ENERGY", f"Need {ENERGY_COST} energy")

    current = getattr(char, stat)
    gain = int(BASE_GAIN / (1 + current / DIMINISHING_K))
    gain = max(1, gain)

    return GymResult(stat_gained=stat, stat_gain=gain, energy_cost=ENERGY_COST)
