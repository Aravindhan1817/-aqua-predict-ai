"""
Predictor engine: Loads preprocessor and trained ML model to run inference.
Supports Domain Feature Engineering and Calibrated Decision Thresholds.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Domain Feature Engineering Transformer (Required for unpickling)
class WaterFeatureEngineering(BaseEstimator, TransformerMixin):
    def __init__(self, add_features=True):
        self.add_features = add_features

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if not self.add_features:
            return X
        ph = X[:, 0]
        hardness = X[:, 1]
        solids = X[:, 2]
        chloramines = X[:, 3]
        sulfate = X[:, 4]
        cond = X[:, 5]
        org_c = X[:, 6]
        thm = X[:, 7]
        turb = X[:, 8]

        ph_dev = np.abs(ph - 7.0).reshape(-1, 1)
        solids_cond_ratio = (solids / (cond + 1.0)).reshape(-1, 1)
        hardness_solids_ratio = (hardness / (solids + 1.0)).reshape(-1, 1)
        chlor_sulfate_ratio = (chloramines / (sulfate + 1.0)).reshape(-1, 1)
        thm_chlor_ratio = (thm / (chloramines + 0.1)).reshape(-1, 1)

        return np.hstack([
            X, ph_dev, solids_cond_ratio, hardness_solids_ratio,
            chlor_sulfate_ratio, thm_chlor_ratio
        ])

# Path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "models")

BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.joblib")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")

_model = None
_preprocessor = None

def get_engine():
    global _model, _preprocessor
    if _model is None or _preprocessor is None:
        if not os.path.exists(BEST_MODEL_PATH) or not os.path.exists(PREPROCESSOR_PATH):
            raise FileNotFoundError("Model or Preprocessor files not found. Run ml/train.py first.")
        _model = joblib.load(BEST_MODEL_PATH)
        _preprocessor = joblib.load(PREPROCESSOR_PATH)
    return _model, _preprocessor

def predict_water_quality(data: dict) -> dict:
    model, preprocessor = get_engine()

    feature_names = preprocessor['feature_names']
    input_df = pd.DataFrame([{feat: data[feat] for feat in feature_names}])

    # 1. Impute and Apply Domain Feature Engineering
    imputed = preprocessor['imputer'].transform(input_df)
    if 'engineer' in preprocessor and preprocessor['engineer'] is not None:
        engineered = preprocessor['engineer'].transform(imputed)
        scaled = preprocessor['scaler'].transform(engineered)
    else:
        scaled = preprocessor['scaler'].transform(imputed)

    # 2. Threshold-Calibrated Probability & Decision
    threshold = preprocessor.get('threshold', 0.475)

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(scaled)[0]
        prob_safe = float(probs[1]) * 100.0
        prediction = 1 if (probs[1] >= threshold) else 0
        confidence = float(np.max(probs)) * 100.0
    else:
        prediction = int(model.predict(scaled)[0])
        prob_safe = 100.0 if prediction == 1 else 0.0
        confidence = 85.0

    # 3. Potability label and Risk categorization
    potability_label = "Safe" if prediction == 1 else "Unsafe"

    if prediction == 1:
        if prob_safe >= 70.0:
            risk_level = "Low Risk (High Potability Assurance)"
        else:
            risk_level = "Acceptable (Moderate Potability Assurance)"
    else:
        if prob_safe < 25.0:
            risk_level = "Critical Risk (Severe Contamination Hazard)"
        else:
            risk_level = "Elevated Risk (Non-Potable Warning)"

    # 4. Feature contribution weights across the 9 primary water factors
    feature_importances = getattr(model, "feature_importances_", None)
    contributions = {}
    if feature_importances is not None:
        # Map primary 9 features from scaled vector
        raw_scaled = np.abs(scaled[0][:len(feature_names)])
        primary_imp = feature_importances[:len(feature_names)]
        weighted = raw_scaled * primary_imp
        total_w = np.sum(weighted) if np.sum(weighted) > 0 else 1.0
        for feat, w in zip(feature_names, weighted):
            contributions[feat] = round(float((w / total_w) * 100), 2)
    else:
        for feat in feature_names:
            contributions[feat] = round(100.0 / len(feature_names), 2)

    return {
        "prediction": prediction,
        "potability_label": potability_label,
        "probability": round(prob_safe, 2),
        "confidence": round(confidence, 2),
        "risk_level": risk_level,
        "model_used": "Feature-Engineered Random Forest",
        "feature_contributions": contributions
    }
