"""
diabetes_predictor.py
====================
Predict diabetes risk from a single clinical record.

Public API
----------
predict_from_record(record)
    -> dict with keys: prediction, probability, shap_values (or None), shap_warning

ModelNotAvailableError – raised when the .pkl file cannot be loaded.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd

logger = logging.getLogger(__name__)

DIABETES_FEATURE_COLUMNS: List[str] = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]


class ModelNotAvailableError(RuntimeError):
    """Raised when the ML model file cannot be found or loaded."""


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
    try:
        from django.conf import settings
        model_path = getattr(settings, "DIABETES_MODEL_PATH", None)
        features_path = getattr(settings, "DIABETES_FEATURES_PATH", None)
    except Exception:
        model_path = None
        features_path = None

    if not model_path:
        model_path = os.environ.get("DIABETES_MODEL_PATH", "")
    if not features_path:
        features_path = os.environ.get("DIABETES_FEATURES_PATH", "")

    return _resolve_path(model_path or ""), _resolve_path(features_path or "")


def _get_shap_background_path() -> str:
    try:
        from django.conf import settings
        bg_path = getattr(settings, "DIABETES_SHAP_BACKGROUND_PATH", None)
    except Exception:
        bg_path = None

    if not bg_path:
        bg_path = os.environ.get("DIABETES_SHAP_BACKGROUND_PATH", "")

    if not bg_path:
        bg_path = "diabetes/diabetes.csv"

    return _resolve_path(bg_path)


@lru_cache(maxsize=1)
def _load_model():
    model_path, _ = _get_model_paths()
    if not model_path or not os.path.exists(model_path):
        raise ModelNotAvailableError(
            f"Diabetes model file not found at '{model_path}'. "
            "Set DIABETES_MODEL_PATH to the correct .pkl path and ensure the file exists."
        )
    try:
        return joblib.load(model_path)
    except Exception as exc:
        raise ModelNotAvailableError(
            f"Failed to load diabetes model from '{model_path}': {exc}"
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
    return DIABETES_FEATURE_COLUMNS


@lru_cache(maxsize=1)
def _load_shap_background() -> Optional[pd.DataFrame]:
    path = _get_shap_background_path()
    if not path or not os.path.exists(path):
        return None

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        logger.warning("Diabetes SHAP background load failed: %s", exc)
        return None

    if "Outcome" in df.columns:
        df = df.drop(columns=["Outcome"])

    feature_columns = _load_feature_columns()
    missing = [c for c in feature_columns if c not in df.columns]
    if missing:
        logger.warning("Diabetes SHAP background missing columns: %s", ", ".join(missing))
        return None

    df = df[feature_columns].dropna()
    if df.empty:
        return None

    sample_size = min(100, len(df))
    return df.sample(n=sample_size, random_state=42)


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
    try:
        import shap

        background = _load_shap_background()
        explainer_background = background if background is not None else X

        try:
            explainer = shap.Explainer(model, explainer_background)
            sv = explainer(X)
            shap_dict = _extract_shap_values(sv, feature_columns)
            if shap_dict:
                return shap_dict, ""
        except Exception as exc:
            logger.debug("Diabetes SHAP Explainer failed: %s", exc)

        try:
            explainer = shap.TreeExplainer(model)
            sv = explainer.shap_values(X)
            shap_dict = _extract_shap_values(sv, feature_columns)
            if shap_dict:
                return shap_dict, ""
        except Exception as exc:
            logger.debug("Diabetes SHAP TreeExplainer failed: %s", exc)

        try:
            explainer = shap.LinearExplainer(model, X)
            sv = explainer.shap_values(X)
            shap_dict = _extract_shap_values(sv, feature_columns)
            if shap_dict:
                return shap_dict, ""
        except Exception as exc:
            logger.debug("Diabetes SHAP LinearExplainer failed: %s", exc)

        try:
            predict_fn = model.predict_proba if hasattr(model, "predict_proba") else model.predict
            explainer = shap.KernelExplainer(predict_fn, explainer_background)
            sv = explainer.shap_values(X)
            shap_dict = _extract_shap_values(sv, feature_columns)
            if shap_dict:
                return shap_dict, ""
        except Exception as exc:
            logger.debug("Diabetes SHAP KernelExplainer failed: %s", exc)

        return None, "SHAP could not be computed for this model type."

    except ImportError:
        return None, "SHAP library is not installed. Run: pip install shap"
    except Exception as exc:
        return None, f"SHAP computation failed: {exc}"


def predict_from_record(record: Dict[str, Any]) -> Dict[str, Any]:
    feature_columns = _load_feature_columns()

    feature_row: Dict[str, float] = {
        "Pregnancies": float(record.get("pregnancies", 0) or 0),
        "Glucose": float(record.get("glucose", 0) or 0),
        "BloodPressure": float(record.get("blood_pressure", 0) or 0),
        "SkinThickness": float(record.get("skin_thickness", 0) or 0),
        "Insulin": float(record.get("insulin", 0) or 0),
        "BMI": float(record.get("bmi", 0) or 0),
        "DiabetesPedigreeFunction": float(record.get("diabetes_pedigree_function", 0) or 0),
        "Age": float(record.get("age", 0) or 0),
    }

    aligned = {col: feature_row.get(col, 0.0) for col in feature_columns}
    X = pd.DataFrame([aligned], columns=feature_columns)

    model = _load_model()

    if hasattr(model, "predict_proba"):
        proba_arr = model.predict_proba(X)
        probability = float(proba_arr[0][1])
    else:
        raw = model.predict(X)
        probability = float(raw[0])

    prediction = int(probability >= 0.5)

    shap_values, shap_warning = _compute_shap(model, X, feature_columns)

    return {
        "prediction": prediction,
        "probability": probability,
        "shap_values": shap_values,
        "shap_warning": shap_warning,
    }
