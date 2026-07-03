import math


def xp_to_level(xp: int) -> int:
    return int(math.floor((xp / 100) ** 0.6)) + 1
