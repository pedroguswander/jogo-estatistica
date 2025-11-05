"""Simple in-memory collector for empirical runs (X values).

X is defined as: number of enemies defeated before the player loses (a non-defeated enemy reaches the deadline).

This module exposes a small API used by the stats screen and the game to record and read runs.
"""
from collections import Counter
from typing import List, Dict

_runs: List[int] = []

def record_run(x: int) -> None:
    """Record one run value (X). Coerces to int and clamps to >= 0."""
    try:
        xi = int(x)
    except Exception:
        xi = 0
    if xi < 0:
        xi = 0
    _runs.append(xi)

def get_runs() -> List[int]:
    return list(_runs)

def reset() -> None:
    _runs.clear()

def get_total_runs() -> int:
    return len(_runs)

def get_counts() -> Dict[int, int]:
    return dict(Counter(_runs))

def get_mean() -> float | None:
    if not _runs:
        return None
    return sum(_runs) / len(_runs)
