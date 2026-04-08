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

    return model_path or "", features_path or ""


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


# ── SHAP computation ───────────────────────────────────────────────────────────

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

        try:
            explainer = shap.TreeExplainer(model)
            sv = explainer.shap_values(X)
            # sv may be a list (one array per class) or a single 2-D array
            if isinstance(sv, list):
                # Take class-1 SHAP values for binary classification
                values = sv[1][0] if len(sv) > 1 else sv[0][0]
            else:
                values = sv[0]
            shap_dict = {col: float(v) for col, v in zip(feature_columns, values)}
            return shap_dict, ""
        except Exception:
            pass

        # Fall back to LinearExplainer / KernelExplainer for non-tree models
        try:
            explainer = shap.LinearExplainer(model, X)
            sv = explainer.shap_values(X)
            if isinstance(sv, list):
                values = sv[1][0] if len(sv) > 1 else sv[0][0]
            else:
                values = sv[0]
            shap_dict = {col: float(v) for col, v in zip(feature_columns, values)}
            return shap_dict, ""
        except Exception:
            pass

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
