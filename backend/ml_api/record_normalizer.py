"""
record_normalizer.py
====================
Ensures a minimum number of health records for robust CVD prediction.

If fewer than MIN_RECORDS are available, synthetic records are generated
using **smooth linear interpolation** between the earliest and latest
known values – no randomness, no sudden jumps.

Public API
----------
normalize_records(records, min_records=MIN_RECORDS)
    -> (normalized_records: list[dict], data_type_used: str)
    data_type_used = "real" | "hybrid"
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import math

MIN_RECORDS = 5


# ── Internal helpers ───────────────────────────────────────────────────────────

def _parse_date(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        s = str(value).strip()
        if s.endswith("Z"):
            s = s[:-1]
        return datetime.fromisoformat(s)
    except Exception:
        return None


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


def _clamp_round_level_1_3(v: float) -> int:
    """Round and clamp to ordinal level 1–3 (cholesterol / gluc)."""
    r = int(round(v))
    return max(1, min(3, r))


def _linspace(a: float, b: float, n: int) -> List[float]:
    """n points including both endpoints. n==1 returns [b]."""
    if n <= 1:
        return [b]
    step = (b - a) / (n - 1)
    return [a + i * step for i in range(n)]


def _date_linspace(d0: datetime, d1: datetime, n: int) -> List[datetime]:
    if n <= 1:
        return [d1]
    total_seconds = (d1 - d0).total_seconds()
    step = total_seconds / (n - 1)
    return [d0 + timedelta(seconds=i * step) for i in range(n)]


# ── Public API ─────────────────────────────────────────────────────────────────

def normalize_records(
    records: List[Dict[str, Any]],
    min_records: int = MIN_RECORDS,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Ensure at least `min_records` records.

    Parameters
    ----------
    records : list of dicts
        Each dict must have at least one of the clinical measurement keys.
        Expected keys: date, ap_hi (or bp), ap_lo, cholesterol, gluc,
        id, age, gender, height, weight, smoke, alco, active.
    min_records : int
        Minimum required record count (default: MIN_RECORDS = 5).

    Returns
    -------
    (normalized_records, data_type_used)
        normalized_records : list of dicts, len >= min_records
        data_type_used     : "real" if len(records) >= min_records,
                             "hybrid" otherwise
    """
    if not records:
        raise ValueError("records must be a non-empty list")

    # ── Clean and sort by date ──────────────────────────────────────────────
    cleaned: List[Dict[str, Any]] = []
    for r in records:
        if not isinstance(r, dict):
            continue
        rr = dict(r)
        rr["_dt"] = _parse_date(r.get("date"))
        cleaned.append(rr)

    if not cleaned:
        raise ValueError("No valid record dicts found")

    if any(r["_dt"] is not None for r in cleaned):
        cleaned.sort(key=lambda x: x["_dt"] or datetime.min)

    if len(cleaned) >= min_records:
        for r in cleaned:
            r.pop("_dt", None)
        return cleaned, "real"

    # ── Generate synthetic records via interpolation ────────────────────────
    first = cleaned[0]
    last = cleaned[-1]

    d0, d1 = first["_dt"], last["_dt"]
    if d0 and d1 and d1 >= d0:
        dates = _date_linspace(d0, d1, min_records)
    else:
        anchor = d1 or d0 or datetime.utcnow()
        dates = [anchor - timedelta(days=(min_records - 1 - i)) for i in range(min_records)]

    def last_known(key: str) -> Optional[float]:
        for rr in reversed(cleaned):
            v = _to_float(rr.get(key))
            if v is not None:
                return v
        return None

    def first_known(key: str) -> Optional[float]:
        for rr in cleaned:
            v = _to_float(rr.get(key))
            if v is not None:
                return v
        return None

    # Support both "ap_hi" (backend format) and "bp" (legacy format)
    bp0 = first_known("ap_hi") or first_known("bp") or 120.0
    bp1 = last_known("ap_hi") or last_known("bp") or bp0

    apl0 = first_known("ap_lo") or 80.0
    apl1 = last_known("ap_lo") or apl0

    ch0 = first_known("cholesterol") or 1.0
    ch1 = last_known("cholesterol") or ch0

    su0 = first_known("gluc") or first_known("sugar") or 1.0
    su1 = last_known("gluc") or last_known("sugar") or su0

    bp_seq = _linspace(float(bp0), float(bp1), min_records)
    apl_seq = _linspace(float(apl0), float(apl1), min_records)
    ch_seq = _linspace(float(ch0), float(ch1), min_records)
    su_seq = _linspace(float(su0), float(su1), min_records)

    # Forward-fill static / demographic keys from most recent real record
    static_keys = ["id", "age", "gender", "height", "weight", "smoke", "alco", "active"]
    static_vals: Dict[str, Any] = {}
    for k in static_keys:
        for rr in reversed(cleaned):
            if rr.get(k) is not None:
                static_vals[k] = rr[k]
                break

    normalized: List[Dict[str, Any]] = []
    for i in range(min_records):
        rec: Dict[str, Any] = {
            "date": dates[i].date().isoformat(),
            "ap_hi": round(bp_seq[i], 2),
            "ap_lo": round(apl_seq[i], 2),
            "cholesterol": _clamp_round_level_1_3(ch_seq[i]),
            "gluc": _clamp_round_level_1_3(su_seq[i]),
        }
        rec.update(static_vals)
        normalized.append(rec)

    return normalized, "hybrid"
