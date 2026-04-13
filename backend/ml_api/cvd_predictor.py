"""
cvd_predictor.py
================
Production-ready CVD risk predictor.

Implements Strategy A (smoothed latest) history collapse, minimum-record
normalization, and optional SHAP explanations.

Public API
----------
predict_from_records(records)
    -> dict with keys: prediction, probability, data_type_used,
                       shap_values (or None), shap_warning,
                       records_used

ModelNotAvailableError – raised when the .pkl file cannot be loaded.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from ml_api.record_normalizer import normalize_records, MIN_RECORDS
from ml_api.history_collapse import (
    smoothed_latest_numeric,
    smoothed_latest_level_1_3,
    forward_fill,
)

logger = logging.getLogger(__name__)

# Authoritative feature ordering – must match the training schema
CVD_FEATURE_COLUMNS: List[str] = [
    "id", "age", "gender", "height", "weight",
    "ap_hi", "ap_lo", "cholesterol", "gluc",
    "smoke", "alco", "active",
]


class ModelNotAvailableError(RuntimeError):
    """Raised when the ML model file cannot be found or loaded."""


# ── Model / feature-columns loading (cached) ──────────────────────────────────

def _resolve_path(path_value: str) -> str:
    if not path_value:
        return ""
    expanded = os.path.expanduser(path_value)
    if os.path.isabs(expanded):
        return expanded
    try:
        from django.conf import settings
        base = Path(getattr(settings, "BASE_DIR", Path.cwd())).parent
    except Exception:
        base = Path.cwd()
    return str((base / expanded).resolve())


def _get_model_paths() -> tuple[str, str]:
    """Resolve model paths from Django settings or environment variables."""
    try:
        from django.conf import settings
        model_path = getattr(settings, "CVD_MODEL_PATH", None)
        features_path = getattr(settings, "CVD_FEATURES_PATH", None)
    except Exception:
        model_path = None
        features_path = None

    if not model_path:
        model_path = os.environ.get("CVD_MODEL_PATH", "")
    if not features_path:
        features_path = os.environ.get("CVD_FEATURES_PATH", "")

    return _resolve_path(model_path or ""), _resolve_path(features_path or "")


def _get_shap_background_path() -> str:
    try:
        from django.conf import settings
        bg_path = getattr(settings, "CVD_SHAP_BACKGROUND_PATH", None)
    except Exception:
        bg_path = None

    if not bg_path:
        bg_path = os.environ.get("CVD_SHAP_BACKGROUND_PATH", "")

    # Default to cleaned dataset in repo if present
    if not bg_path:
        bg_path = "cvd/cleaned_cardio_data.csv"

    return _resolve_path(bg_path)


@lru_cache(maxsize=1)
def _load_model():
    model_path, _ = _get_model_paths()
    if not model_path or not os.path.exists(model_path):
        raise ModelNotAvailableError(
            f"CVD model file not found at '{model_path}'. "
            "Set CVD_MODEL_PATH to the correct .pkl path and ensure the file exists."
        )
    try:
        return joblib.load(model_path)
    except Exception as exc:
        raise ModelNotAvailableError(
            f"Failed to load CVD model from '{model_path}': {exc}"
        ) from exc


@lru_cache(maxsize=1)
def _load_feature_columns() -> List[str]:
    _, features_path = _get_model_paths()
    if features_path and os.path.exists(features_path):
        try:
            cols = joblib.load(features_path)
            if isinstance(cols, (list, tuple)) and cols:
                return list(cols)
        except Exception:
            pass
    # Fall back to the authoritative hard-coded list
    return CVD_FEATURE_COLUMNS


@lru_cache(maxsize=1)
def _load_shap_background() -> Optional[pd.DataFrame]:
    path = _get_shap_background_path()
    if not path or not os.path.exists(path):
        return None

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        logger.warning("SHAP background load failed: %s", exc)
        return None

    if "cardio" in df.columns:
        df = df.drop(columns=["cardio"])

    feature_columns = _load_feature_columns()
    missing = [c for c in feature_columns if c not in df.columns]
    if missing:
        logger.warning("SHAP background missing columns: %s", ", ".join(missing))
        return None

    df = df[feature_columns].dropna()
    if df.empty:
        return None

    sample_size = min(100, len(df))
    return df.sample(n=sample_size, random_state=42)


# ── SHAP computation ───────────────────────────────────────────────────────────

def _extract_shap_values(sv: Any, feature_columns: List[str]) -> Optional[Dict[str, float]]:
    values = sv.values if hasattr(sv, "values") else sv
    if isinstance(values, list):
        values = values[1] if len(values) > 1 else values[0]
    if hasattr(values, "ndim"):
        if values.ndim == 3:
            values = values[0, :, 1]
        elif values.ndim == 2:
            values = values[0]
        elif values.ndim == 1:
            values = values
        else:
            return None
    if len(values) != len(feature_columns):
        return None
    return {col: float(v) for col, v in zip(feature_columns, values)}


def _compute_shap(model, X: pd.DataFrame, feature_columns: List[str]) -> tuple[Optional[Dict], str]:
    """
    Attempt to compute SHAP feature attributions.

    Returns
    -------
    (shap_dict, warning_message)
        shap_dict : {feature: shap_value} or None if not available
        warning   : empty string on success, explanation string on failure
    """
    try:
        import shap  # optional dependency

        background = _load_shap_background()
        explainer_background = background if background is not None else X

        # Preferred: unified Explainer (handles many model types and pipelines)
        try:
            explainer = shap.Explainer(model, explainer_background)
            sv = explainer(X)
            shap_dict = _extract_shap_values(sv, feature_columns)
            if shap_dict:
                return shap_dict, ""
        except Exception as exc:
            logger.debug("SHAP Explainer failed: %s", exc)

        # Tree-based models
        try:
            explainer = shap.TreeExplainer(model)
            sv = explainer.shap_values(X)
            shap_dict = _extract_shap_values(sv, feature_columns)
            if shap_dict:
                return shap_dict, ""
        except Exception as exc:
            logger.debug("SHAP TreeExplainer failed: %s", exc)

        # Linear models
        try:
            explainer = shap.LinearExplainer(model, X)
            sv = explainer.shap_values(X)
            shap_dict = _extract_shap_values(sv, feature_columns)
            if shap_dict:
                return shap_dict, ""
        except Exception as exc:
            logger.debug("SHAP LinearExplainer failed: %s", exc)

        # General fallback (slow but broad)
        try:
            predict_fn = model.predict_proba if hasattr(model, "predict_proba") else model.predict
            explainer = shap.KernelExplainer(predict_fn, explainer_background)
            sv = explainer.shap_values(X)
            shap_dict = _extract_shap_values(sv, feature_columns)
            if shap_dict:
                return shap_dict, ""
        except Exception as exc:
            logger.debug("SHAP KernelExplainer failed: %s", exc)

        return None, "SHAP could not be computed for this model type."

    except ImportError:
        return None, "SHAP library is not installed. Run: pip install shap"
    except Exception as exc:
        return None, f"SHAP computation failed: {exc}"


# ── Main predictor ─────────────────────────────────────────────────────────────

def predict_from_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict CVD risk from a list of patient health records.

    Parameters
    ----------
    records : list of dicts
        Each dict must contain clinical measurement keys.
        See record_normalizer.normalize_records for expected keys.

    Returns
    -------
    dict with keys:
        prediction      : int  – 0 (Low Risk) or 1 (High Risk)
        probability     : float – probability of High Risk
        data_type_used  : str  – "real" or "hybrid"
        shap_values     : dict | None
        shap_warning    : str
        records_used    : int
    """
    # 1) Normalize to MIN_RECORDS (interpolate if needed)
    normalized_records, data_type_used = normalize_records(records, min_records=MIN_RECORDS)
    records_used = len(normalized_records)

    # 2) Collapse history to snapshot features (Strategy A: smoothed latest)
    feature_columns = _load_feature_columns()

    ap_hi_series = [r.get("ap_hi") for r in normalized_records]
    ap_lo_series = [r.get("ap_lo") for r in normalized_records]
    chol_series = [r.get("cholesterol") for r in normalized_records]
    gluc_series = [r.get("gluc") for r in normalized_records]

    ap_hi = smoothed_latest_numeric(ap_hi_series, w_latest=0.7, last_k=5)
    ap_lo = smoothed_latest_numeric(ap_lo_series, w_latest=0.7, last_k=5)
    cholesterol = smoothed_latest_level_1_3(chol_series, w_latest=0.7, last_k=5)
    gluc = smoothed_latest_level_1_3(gluc_series, w_latest=0.7, last_k=5)

    feature_row: Dict[str, float] = {
        "id": float(forward_fill(normalized_records, "id", 0) or 0),
        "age": float(forward_fill(normalized_records, "age", 0) or 0),
        "gender": float(forward_fill(normalized_records, "gender", 0) or 0),
        "height": float(forward_fill(normalized_records, "height", 0) or 0),
        "weight": float(forward_fill(normalized_records, "weight", 0) or 0),
        "ap_hi": float(ap_hi),
        "ap_lo": float(ap_lo),
        "cholesterol": float(cholesterol),
        "gluc": float(gluc),
        "smoke": float(forward_fill(normalized_records, "smoke", 0) or 0),
        "alco": float(forward_fill(normalized_records, "alco", 0) or 0),
        "active": float(forward_fill(normalized_records, "active", 0) or 0),
    }

    # Align to exactly the feature columns the model was trained on
    aligned: Dict[str, float] = {col: feature_row.get(col, 0.0) for col in feature_columns}
    X = pd.DataFrame([aligned], columns=feature_columns)

    # 3) Load model and predict
    model = _load_model()

    if hasattr(model, "predict_proba"):
        proba_arr = model.predict_proba(X)
        # For binary classification [prob_class0, prob_class1]
        probability = float(proba_arr[0][1])
    else:
        raw = model.predict(X)
        probability = float(raw[0])

    prediction = int(probability >= 0.5)

    logger.info(
        "CVD predict: data_type_used=%s records_in=%d records_used=%d",
        data_type_used, len(records), records_used,
    )

    # 4) SHAP
    shap_values, shap_warning = _compute_shap(model, X, feature_columns)

    return {
        "prediction": prediction,
        "probability": probability,
        "data_type_used": data_type_used,
        "shap_values": shap_values,
        "shap_warning": shap_warning,
        "records_used": records_used,
    }
