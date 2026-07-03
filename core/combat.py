from dataclasses import dataclass
from datetime import datetime
import math
import random
from core.state import CharacterState


@dataclass
class CombatResult:
    won: bool
    p_win: float
    damage_dealt: int
    hospital_minutes_target: int
    hospital_minutes_attacker: int
    mug_amount: int
    xp: int
    heat_gain: int
    notoriety_gain: int
    text_key: str


def resolve_attack(
    att: CharacterState, dfn: CharacterState, choice: str, rng: random.Random, now: datetime
) -> CombatResult:
    atk = att.strength * 1.0 + att.speed * 0.4 + att.weapon_bonus
    if att.buff_until and att.buff_until > now:
        atk *= 1.1
    dfn_p = dfn.defense * 1.0 + dfn.dexterity * 0.4 + dfn.armor_bonus
    scale = 0.25 * ((atk + dfn_p) / 2)
    p_win = 1.0 / (1.0 + math.exp(-(atk - dfn_p) / max(scale, 1.0)))
    p_win = max(0.10, min(0.90, p_win))
    won = rng.random() < p_win
    if won:
        mug_amt = 0
        target_h = rng.randint(15, 60)
        att_h = 0
        heat = 1
        notoriety = 1
        if choice == "mug":
            mug_amt = int(dfn.cash * rng.uniform(0.03, 0.10))
            heat = 4
        elif choice == "hospitalize":
            heat = 8
            notoriety = 3
        return CombatResult(
            won=True,
            p_win=p_win,
            damage_dealt=0,
            hospital_minutes_target=target_h,
            hospital_minutes_attacker=att_h,
            mug_amount=mug_amt,
            xp=15,
            heat_gain=heat,
            notoriety_gain=notoriety,
            text_key=f"attack:win:{choice}",
        )
    else:
        att_h = rng.randint(10, 30)
        return CombatResult(
            won=False,
            p_win=p_win,
            damage_dealt=0,
            hospital_minutes_target=0,
            hospital_minutes_attacker=att_h,
            mug_amount=0,
            xp=5,
            heat_gain=0,
            notoriety_gain=0,
            text_key=f"attack:loss:{choice}",
        )
