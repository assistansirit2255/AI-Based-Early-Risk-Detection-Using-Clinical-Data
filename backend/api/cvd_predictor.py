"""
Lightweight CVD predictor for API usage.

Feature columns expected by the trained model (confirmed from feature_columns.pkl):
  ["id", "age", "gender", "height", "weight", "ap_hi", "ap_lo",
   "cholesterol", "gluc", "smoke", "alco", "active"]

cholesterol and gluc are categorical levels 1/2/3.
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np
import pandas as pd
import joblib

try:
    import shap as _shap  # type: ignore
except Exception:  # pragma: no cover
    _shap = None

logger = logging.getLogger(__name__)

CVD_FEATURE_COLUMNS: List[str] = [
    "id",
    "age",
    "gender",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "cholesterol",
    "gluc",
    "smoke",
    "alco",
    "active",
]

# Paths are resolved lazily so settings can override them via env vars.
def _model_path() -> str:
    from django.conf import settings  # type: ignore

    return getattr(settings, "CVD_MODEL_PATH", "cvd/cvd_model.pkl")


def _background_csv_path() -> str:
    from django.conf import settings  # type: ignore

    return getattr(settings, "CVD_BACKGROUND_CSV", "cvd/cleaned_cardio_data.csv")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        s = str(value).strip().rstrip("Z")
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _safe_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        v = float(x)
        return None if np.isnan(v) else v
    except Exception:
        return None


def _clamp_level(v: float) -> float:
    """Clamp a categorical level to {1, 2, 3}."""
    if v <= 1:
        return 1.0
    if v >= 3:
        return 3.0
    return float(round(v))


def _linear_trend(pairs: List[Tuple[datetime, float]]) -> float:
    if len(pairs) < 2:
        return 0.0
    t0 = pairs[0][0]
    t = np.array([(dt - t0).total_seconds() / 86400.0 for dt, _ in pairs], dtype=float)
    y = np.array([v for _, v in pairs], dtype=float)
    denom = np.var(t)
    if denom == 0:
        return 0.0
    return float(np.cov(t, y, bias=True)[0, 1] / denom)


def _series_stats(records_df: pd.DataFrame, col: str) -> Dict[str, float]:
    s = records_df[col].dropna()
    if s.empty:
        return {f"{col}_{k}": 0.0 for k in ["latest", "avg", "min", "max", "std", "trend"]}
    pairs: List[Tuple[datetime, float]] = [
        (row["date_parsed"], float(row[col]))
        for _, row in records_df[["date_parsed", col]].dropna().iterrows()
    ]
    return {
        f"{col}_latest": float(s.iloc[-1]),
        f"{col}_avg": float(s.mean()),
        f"{col}_min": float(s.min()),
        f"{col}_max": float(s.max()),
        f"{col}_std": float(s.std(ddof=0)) if len(s) >= 2 else 0.0,
        f"{col}_trend": _linear_trend(pairs),
    }


# ---------------------------------------------------------------------------
# Cached loaders
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_model():
    path = _model_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"CVD model not found at: {path}")
    return joblib.load(path)


@lru_cache(maxsize=1)
def _load_background() -> pd.DataFrame:
    path = _background_csv_path()
    if not os.path.exists(path):
        logger.warning("Background CSV not found at %s; SHAP explainer will be unavailable.", path)
        return pd.DataFrame(columns=CVD_FEATURE_COLUMNS)
    df = pd.read_csv(path)
    if "gender" in df.columns and df["gender"].dtype == object:
        df["gender"] = df["gender"].map({"Male": 1, "Female": 0}).fillna(0).astype(int)
    df = df.reindex(columns=CVD_FEATURE_COLUMNS, fill_value=0)
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df.sample(n=min(100, len(df)), random_state=42).reset_index(drop=True)


@lru_cache(maxsize=1)
def _get_explainer():
    if _shap is None:
        return None
    model = _load_model()
    background = _load_background()
    if background.empty:
        return None
    try:
        return _shap.TreeExplainer(
            model, data=background, feature_perturbation="tree_path_dependent"
        )
    except Exception:
        pass
    try:
        return _shap.Explainer(model, background)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def predict_from_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert a list of health records into a single prediction.

    Each record dict may contain:
      date, ap_hi (systolic bp), ap_lo (diastolic bp),
      cholesterol (1/2/3), gluc (1/2/3),
      age, gender, height, weight, smoke, alco, active, id

    Returns:
      {
        "prediction": int,
        "probability": float,
        "shap_values": {"top_features": [...], "base_value": float | None},
        "history_summary": {...},
      }
    """
    if not records:
        raise ValueError("records must be a non-empty list")

    rows = []
    for r in records:
        if not isinstance(r, dict):
            continue
        rows.append(
            {
                "date_parsed": _parse_date(r.get("date")),
                "ap_hi": _safe_float(r.get("ap_hi")),
                "ap_lo": _safe_float(r.get("ap_lo")),
                "cholesterol": _safe_float(r.get("cholesterol")),
                "gluc": _safe_float(r.get("gluc")),
                "age": _safe_float(r.get("age")),
                "gender": _safe_float(r.get("gender")),
                "height": _safe_float(r.get("height")),
                "weight": _safe_float(r.get("weight")),
                "smoke": _safe_float(r.get("smoke")),
                "alco": _safe_float(r.get("alco")),
                "active": _safe_float(r.get("active")),
                "id": _safe_float(r.get("id")),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("No valid records found")

    if df["date_parsed"].notna().any():
        df = df.sort_values("date_parsed", ascending=True)
    df = df.reset_index(drop=True)

    bp_stats = _series_stats(df, "ap_hi")
    lo_stats = _series_stats(df, "ap_lo")
    chol_stats = _series_stats(df, "cholesterol")
    gluc_stats = _series_stats(df, "gluc")

    latest = df.iloc[-1]

    def _pick(col: str, fallback: float = 0.0) -> float:
        v = _safe_float(latest.get(col))
        return v if v is not None else fallback

    chol = _clamp_level(_pick("cholesterol", 1.0))
    gluc = _clamp_level(_pick("gluc", 1.0))

    feature_row = {
        "id": _pick("id", 0.0),
        "age": _pick("age", 0.0),
        "gender": _pick("gender", 0.0),
        "height": _pick("height", 0.0),
        "weight": _pick("weight", 0.0),
        "ap_hi": _pick("ap_hi", 0.0),
        "ap_lo": _pick("ap_lo", 0.0),
        "cholesterol": chol,
        "gluc": gluc,
        "smoke": _pick("smoke", 0.0),
        "alco": _pick("alco", 0.0),
        "active": _pick("active", 0.0),
    }

    X = pd.DataFrame([feature_row], columns=CVD_FEATURE_COLUMNS)

    model = _load_model()
    proba = float(model.predict_proba(X)[0][1])
    pred = int(proba >= 0.5)

    # SHAP
    shap_payload: Dict[str, Any] = {"top_features": [], "base_value": None}
    explainer = _get_explainer()
    if explainer is not None:
        try:
            sv = explainer.shap_values(X, check_additivity=False)
            if isinstance(sv, list) and len(sv) >= 2:
                sv_row = np.array(sv[1][0], dtype=float)
                base_value = (
                    explainer.expected_value[1]
                    if isinstance(explainer.expected_value, (list, np.ndarray))
                    else explainer.expected_value
                )
            else:
                sv_row = np.array(sv[0] if sv.ndim == 2 else sv, dtype=float)
                base_value = explainer.expected_value

            contrib = [
                {"feature": fname, "value": float(fval), "shap": float(s)}
                for fname, fval, s in zip(CVD_FEATURE_COLUMNS, X.iloc[0].tolist(), sv_row.tolist())
            ]
            contrib.sort(key=lambda d: abs(d["shap"]), reverse=True)
            shap_payload["top_features"] = contrib[:5]
            shap_payload["base_value"] = float(base_value) if base_value is not None else None
        except Exception as exc:
            logger.warning("SHAP computation failed: %s", exc)

    return {
        "prediction": pred,
        "probability": proba,
        "shap_values": shap_payload,
        "history_summary": {**bp_stats, **lo_stats, **chol_stats, **gluc_stats},
    }
