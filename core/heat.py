from datetime import datetime, timezone


def apply_heat_decay(heat: int, updated_at: datetime, now: datetime) -> tuple[int, datetime]:
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    hours = int((now - updated_at).total_seconds() / 3600)
    if hours > 0:
        heat = max(0, heat - hours)
        updated_at = now
    return heat, updated_at


def check_threshold(old_heat: int, new_heat: int) -> list[dict]:
    events = []
    if old_heat < 40 <= new_heat:
        events.append({"type": "shakedown", "weight": 5, "fine_pct": 0.05, "fine_max": 500})
    if old_heat < 70 <= new_heat:
        events.append({"type": "raid", "weight": 9, "cash_loss_pct": 0.10, "jail_min": 10})
    return events


def bribe_cost(heat: int) -> int:
    return heat * 100
