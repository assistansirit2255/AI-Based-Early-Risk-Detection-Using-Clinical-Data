import joblib
import pandas as pd
from typing import List, Dict, Any


def predict_from_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predicts health risk based on clinical records provided.

    Args:
        records (List[Dict[str, Any]]): A list of dictionaries containing
        clinical measurements (e.g., blood pressure, cholesterol, sugar).

    Returns:
        Dict[str, Any]: A dictionary containing prediction label and probability.
    """
    # Parse and validate records
    # ... (parsing and validation logic)
    
    # Sort records by date
    records.sort(key=lambda x: x['date'])
    
    # Compute aggregated features (latest, mean, min, max, std, trend)
    # ... (feature computation logic)
    
    # Load the model and feature columns
    model_path = 'cvd/cvd_model.pkl'
    feature_columns_path = 'cvd/feature_columns.pkl'
    model = joblib.load(model_path)

    if os.path.exists(feature_columns_path):
        with open(feature_columns_path, 'rb') as f:
            feature_columns = joblib.load(f)
    else:
        feature_columns = []  # handle missing feature columns
    
    # Build DataFrame with required columns
    df = pd.DataFrame(records)
    df = df.reindex(columns=feature_columns, fill_value=0)
    
    # Predict using the model
    if hasattr(model, 'predict_proba'):
        prediction = model.predict_proba(df)
    else:
        prediction = model.predict(df)
    
    # Prepare and return the result
    return {'label': prediction[0], 'probability': prediction[1]}
