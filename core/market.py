import math


def calculate_fee(price: int, qty: int) -> int:
    return max(1, math.ceil(price * qty * 0.02))
