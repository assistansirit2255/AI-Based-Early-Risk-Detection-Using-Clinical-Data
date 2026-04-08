"""
history_collapse.py
===================
Strategy A helpers: collapse a time-series of health records into a
single snapshot row for the CVD model.

Strategy A = "latest + smoothing"
  smoothed_latest = 0.7 * latest_value + 0.3 * avg(last_k values)

This keeps predictions close to the training-time semantics (snapshot)
while reducing sensitivity to single noisy readings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import math


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        v = float(x)
        if math.isnan(v):
            return None
        return v
    except Exception:
        return None


def _avg(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def smoothed_latest_numeric(
    values: List[Any],
    w_latest: float = 0.7,
    last_k: int = 5,
) -> float:
    """
    Strategy A collapse for continuous features (e.g. ap_hi, ap_lo).

    Parameters
    ----------
    values  : ordered list of raw values (oldest → newest)
    w_latest: weight given to the most recent observation
    last_k  : window size for the tail average

    Returns
    -------
    float – smoothed estimate
    """
    vals = [v for v in (_to_float(x) for x in values) if v is not None]
    if not vals:
        return 0.0
    latest = vals[-1]
    tail = vals[-last_k:]
    avg_tail = _avg(tail)
    return float(w_latest * latest + (1.0 - w_latest) * avg_tail)


def smoothed_latest_level_1_3(
    values: List[Any],
    w_latest: float = 0.7,
    last_k: int = 5,
) -> int:
    """
    Strategy A collapse for ordinal categorical levels 1/2/3
    (cholesterol, gluc).
    """
    v = smoothed_latest_numeric(values, w_latest=w_latest, last_k=last_k)
    r = int(round(v))
    return max(1, min(3, r))


def forward_fill(records: List[Dict[str, Any]], key: str, default: Any = 0) -> Any:
    """Return the most recent non-None value for `key` across records."""
    for r in reversed(records):
        if r.get(key) is not None:
            return r[key]
    return default
