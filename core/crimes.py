from dataclasses import dataclass
from datetime import datetime
import random
from core.state import CharacterState
from core.exceptions import DomainError

@dataclass
class CrimeRow:
    id: str
    tier: int
    name: str
    nerve_cost: int
    base_success: float
    payout_min: int
    payout_max: int

@dataclass
class CrimeResult:
    success: bool
    payout: int
    xp: int
    skill_gain: float
    jailed: bool
    jail_minutes: int
    heat_gain: int
    text_key: str

def attempt_crime(char: CharacterState, crime: CrimeRow, rng: random.Random, now: datetime) -> CrimeResult:
    if char.jail_until and char.jail_until > now:
        raise DomainError("INCAPACITATED", "You are in jail")
    if char.hospital_until and char.hospital_until > now:
        raise DomainError("INCAPACITATED", "You are hospitalized")
    if char.nerve < crime.nerve_cost:
        raise DomainError("NOT_ENOUGH_NERVE", f"Need {crime.nerve_cost} nerve")

    success_p = max(0.05, min(0.95, crime.base_success + char.crime_skill * 0.005))
    success = rng.random() < success_p

    payout = rng.randint(crime.payout_min, crime.payout_max) if success else 0
    xp = crime.tier * 10 if success else crime.tier * 2
    skill_gain = 1.0 if success else 0.2

    jailed = False
    jail_minutes = 0
    if not success and crime.tier >= 3 and rng.random() < 0.35:
        jailed = True
        jail_minutes = rng.randint(10, 45)

    heat_gain = 0
    if success:
        if crime.tier == 4:
            heat_gain = 6
        elif crime.tier == 5:
            heat_gain = 10

    outcome = "jail" if jailed else ("success" if success else "fail")
    text_key = f"crime:{crime.id}:{outcome}"

    return CrimeResult(success=success, payout=payout, xp=xp, skill_gain=skill_gain,
                       jailed=jailed, jail_minutes=jail_minutes, heat_gain=heat_gain,
                       text_key=text_key)
