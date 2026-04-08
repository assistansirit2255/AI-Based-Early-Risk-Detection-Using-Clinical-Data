"""
CVD risk predictor module.

Loads the trained scikit-learn model and feature columns from the cvd/ directory
once (module-level cache) and exposes ``predict_from_records(records)`` for use
inside the Django API.

The function accepts a list of HealthRecord-like dicts (as returned by Django ORM /
serializer), aggregates them into a fixed-length feature vector, runs inference,
and returns prediction + probability + lightweight SHAP explanation.

Expected feature columns (from cvd/feature_columns.pkl):
    id, age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active
"""

import logging
import os
from typing import Any

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths — anchored to this file's location so they work regardless of the
# working directory (important for WSGI).
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
_MODEL_PATH = os.path.join(_REPO_ROOT, 'cvd', 'cvd_model.pkl')
_FEATURE_COLS_PATH = os.path.join(_REPO_ROOT, 'cvd', 'feature_columns.pkl')
_BACKGROUND_CSV = os.path.join(_REPO_ROOT, 'cvd', 'cleaned_cardio_data.csv')

# ---------------------------------------------------------------------------
# Module-level cache — loaded once, reused across all requests.
# ---------------------------------------------------------------------------
_model = None
_feature_columns: list = []
_shap_explainer = None
_background_df = None


def _load_artifacts() -> None:
    """Load model and feature columns into the module cache (idempotent)."""
    global _model, _feature_columns, _shap_explainer, _background_df

    if _model is not None:
        return

    if not os.path.exists(_MODEL_PATH):
        raise FileNotFoundError(
            f'CVD model not found at {_MODEL_PATH}. '
            'Please add cvd/cvd_model.pkl to the repository.'
        )

    _model = joblib.load(_MODEL_PATH)
    logger.info('CVD model loaded from %s', _MODEL_PATH)

    if os.path.exists(_FEATURE_COLS_PATH):
        _feature_columns = joblib.load(_FEATURE_COLS_PATH)
        logger.info('Feature columns loaded: %s', _feature_columns)
    else:
        # Fallback to the known schema from the problem statement
        _feature_columns = [
            'id', 'age', 'gender', 'height', 'weight',
            'ap_hi', 'ap_lo', 'cholesterol', 'gluc',
            'smoke', 'alco', 'active',
        ]
        logger.warning('feature_columns.pkl not found — using hardcoded fallback schema.')

    # Build a small background dataset for SHAP (max 200 rows)
    if os.path.exists(_BACKGROUND_CSV):
        try:
            raw = pd.read_csv(_BACKGROUND_CSV)
            available_cols = [c for c in _feature_columns if c in raw.columns]
            bg = raw[available_cols].dropna().head(200)
            # Ensure all expected columns exist (fill missing with 0)
            for col in _feature_columns:
                if col not in bg.columns:
                    bg[col] = 0
            _background_df = bg[_feature_columns].reset_index(drop=True)
            logger.info('SHAP background dataset built with %d rows.', len(_background_df))
        except Exception as exc:
            logger.warning('Could not build SHAP background from CSV: %s', exc)

    # Build SHAP explainer
    try:
        import shap  # imported lazily to keep startup fast when shap is absent

        base_estimator = _model
        # Unwrap a sklearn Pipeline to get the final estimator for tree explainers
        if hasattr(_model, 'steps'):
            base_estimator = _model.steps[-1][1]

        if hasattr(base_estimator, 'estimators_'):
            # Tree-based ensemble (RandomForest, GradientBoosting, etc.)
            if _background_df is not None:
                _shap_explainer = shap.TreeExplainer(_model, _background_df)
            else:
                _shap_explainer = shap.TreeExplainer(_model)
            logger.info('SHAP TreeExplainer initialised.')
        elif hasattr(base_estimator, 'coef_'):
            # Linear model
            if _background_df is not None:
                _shap_explainer = shap.LinearExplainer(_model, _background_df)
            else:
                _shap_explainer = shap.LinearExplainer(
                    _model,
                    np.zeros((1, len(_feature_columns)))
                )
            logger.info('SHAP LinearExplainer initialised.')
        else:
            logger.warning(
                'Unknown model type %s — SHAP explainer will be skipped.',
                type(base_estimator).__name__,
            )
    except Exception as exc:
        logger.warning('SHAP explainer could not be initialised: %s', exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_from_records(records: list) -> dict:
    """
    Predict CVD risk from one or more health records for a single patient.

    Parameters
    ----------
    records : list of dict
        Each dict should contain the clinical feature keys that match the
        trained model's expected columns.  At minimum:
            age, gender, height, weight, ap_hi, ap_lo,
            cholesterol, gluc, smoke, alco, active
        An optional ``recorded_on`` / ``date`` key is used for time-ordering.

    Returns
    -------
    dict with keys:
        prediction   : int  (0 = Low Risk, 1 = High Risk)
        probability  : float  (probability of class 1)
        shap_values  : dict
            base_value      : float
            top_features    : list of {feature, value, shap} dicts
    """
    _load_artifacts()

    if not records:
        raise ValueError('records list must not be empty.')

    # -----------------------------------------------------------------------
    # Step 1 — Sort records by date (if present)
    # -----------------------------------------------------------------------
    date_key = next((k for k in ('recorded_on', 'date') if k in records[0]), None)
    if date_key:
        records = sorted(records, key=lambda r: str(r.get(date_key, '')))

    # -----------------------------------------------------------------------
    # Step 2 — Build a DataFrame from the records
    # -----------------------------------------------------------------------
    df = pd.DataFrame(records)

    # -----------------------------------------------------------------------
    # Step 3 — Aggregate multiple visits into a single feature vector.
    #   Static features (gender, height): take the latest value.
    #   Dynamic numeric features: take the latest value as the primary
    #   signal (the model is cross-sectional by design).
    # -----------------------------------------------------------------------
    static_cols = {'gender', 'height'}
    row: dict[str, Any] = {}

    for col in _feature_columns:
        if col == 'id':
            row['id'] = 0  # dummy; the model was trained with this column
            continue
        if col not in df.columns:
            row[col] = 0
            continue

        series = pd.to_numeric(df[col], errors='coerce').dropna()
        if series.empty:
            row[col] = 0
        else:
            row[col] = series.iloc[-1]

    # -----------------------------------------------------------------------
    # Step 4 — Predict
    # -----------------------------------------------------------------------
    X = pd.DataFrame([row])[_feature_columns]

    if hasattr(_model, 'predict_proba'):
        proba = _model.predict_proba(X)[0]
        probability = float(proba[1])
    else:
        probability = float(_model.predict(X)[0])

    prediction = int(probability >= 0.5)

    # -----------------------------------------------------------------------
    # Step 5 — SHAP explanation
    # -----------------------------------------------------------------------
    shap_result: dict[str, Any] = {'base_value': None, 'top_features': []}

    if _shap_explainer is not None:
        try:
            import shap as _shap  # noqa: F811

            shap_output = _shap_explainer(X)

            # shap >= 0.41 returns an Explanation object
            if hasattr(shap_output, 'values'):
                sv_array = shap_output.values
                base_val = shap_output.base_values
            else:
                sv_array = _shap_explainer.shap_values(X)
                base_val = getattr(_shap_explainer, 'expected_value', None)

            # Binary classifiers may return a list [class0, class1] — take class 1
            if isinstance(sv_array, list):
                sv = sv_array[1][0] if len(sv_array) > 1 else sv_array[0][0]
                bv = (
                    base_val[1]
                    if isinstance(base_val, (list, np.ndarray)) and len(base_val) > 1
                    else base_val
                )
            else:
                sv = sv_array[0] if sv_array.ndim > 1 else sv_array
                bv = base_val[0] if isinstance(base_val, (list, np.ndarray)) else base_val

            # Build top-contributors list sorted by absolute SHAP magnitude
            shap_dict = dict(zip(_feature_columns, sv))
            top = sorted(shap_dict.items(), key=lambda kv: abs(kv[1]), reverse=True)[:5]
            shap_result['base_value'] = float(bv) if bv is not None else None
            shap_result['top_features'] = [
                {'feature': k, 'value': float(row.get(k, 0)), 'shap': float(v)}
                for k, v in top
            ]
        except Exception as exc:
            logger.warning('SHAP computation failed: %s', exc)
            shap_result['error'] = str(exc)

    return {
        'prediction': prediction,
        'probability': round(probability, 4),
        'shap_values': shap_result,
    }
