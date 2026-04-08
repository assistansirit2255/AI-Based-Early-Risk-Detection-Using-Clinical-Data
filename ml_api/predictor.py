import joblib
import numpy as np
import pandas as pd
from datetime import datetime

class Predictor:
    def __init__(self):
        self.model = joblib.load('cvd/cvd_model.pkl')
        self.feature_columns = joblib.load('cvd/feature_columns.pkl')

    def aggregate_history(self, records):
        df = pd.DataFrame(records)
        if df.empty:
            return {}
        aggregated = {
            'latest': df.iloc[-1].to_dict(),
            'mean': df.mean().to_dict(),
            'min': df.min().to_dict(),
            'max': df.max().to_dict(),
            'std': df.std().to_dict() if len(df) >= 2 else {},
            'trend_slope': self.compute_trend_slope(df)
        }
        return aggregated

    def compute_trend_slope(self, df):
        # Simple linear regression for trend slope
        x = np.arange(len(df))
        slope = np.polyfit(x, df['bp'], 1)[0]  # example for 'bp'
        return slope

    def predict_from_records(self, records):
        aggregated_features = self.aggregate_history(records)
        aligned_features = self.align_features(aggregated_features)
        if isinstance(self.model, joblib.Pipeline):
            probabilities = self.model.predict_proba(pd.DataFrame([aligned_features]))
        else:
            probabilities = self.model.predict_proba([aligned_features])
        return {
            'prediction': np.argmax(probabilities),
            'probability': probabilities,
            'shap_values': self.compute_shap_values(aligned_features)
        }

    def align_features(self, features):
        return {col: features.get(col, 0) for col in self.feature_columns}

    def compute_shap_values(self, features):
        try:
            if hasattr(self.model, 'tree_'):
                explainer = shap.TreeExplainer(self.model)
                shap_values = explainer.shap_values(features)
                return dict(zip(self.feature_columns, shap_values))
            else:
                # For linear models
                if hasattr(self.model, 'coef_'):
                    return {col: coef * features[col] for col, coef in zip(self.feature_columns, self.model.coef_)}
                else:
                    return 'SHAP values not available.'
        except Exception as e:
            return str(e)
