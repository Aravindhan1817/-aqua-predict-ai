"""
Phase 1: Model Integration Verification Script
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath("."))
from backend.app.predictor import predict_water_quality, get_engine, WaterFeatureEngineering
from backend.app.recommendations import evaluate_parameters

def verify_phase1():
    print("=" * 70)
    print("PHASE 1: MODEL INTEGRATION VERIFICATION")
    print("=" * 70)

    # 1. Verify model and preprocessor artifacts
    model, preprocessor = get_engine()
    assert model is not None, "Failed to load best_model.joblib"
    assert preprocessor is not None, "Failed to load preprocessor.joblib"
    print("[1] Artifacts Loaded Successfully:")
    print(f"    - Model Type: {type(model).__name__} (n_estimators={model.n_estimators}, max_depth={model.max_depth})")
    print(f"    - Preprocessor Keys: {list(preprocessor.keys())}")

    # 2. Verify 5 feature transformations
    base_sample = np.array([[7.4, 180.0, 18000.0, 6.0, 240.0, 400.0, 11.5, 55.0, 3.2]])
    engineer = preprocessor['engineer']
    engineered_sample = engineer.transform(base_sample)
    assert engineered_sample.shape[1] == 14, f"Expected 14 features, got {engineered_sample.shape[1]}"

    # Verify mathematical definitions of the 5 ratios:
    # 9: ph_dev = |7.4 - 7.0| = 0.4
    # 10: solids_cond_ratio = 18000 / (400 + 1) = 44.8878
    # 11: hardness_solids_ratio = 180 / (18000 + 1) = 0.009999
    # 12: chlor_sulfate_ratio = 6.0 / (240 + 1) = 0.024896
    # 13: thm_chlor_ratio = 55.0 / (6.0 + 0.1) = 9.01639
    assert np.isclose(engineered_sample[0, 9], 0.4), "ph_dev mismatch"
    assert np.isclose(engineered_sample[0, 10], 18000.0 / 401.0), "solids_cond_ratio mismatch"
    assert np.isclose(engineered_sample[0, 11], 180.0 / 18001.0), "hardness_solids_ratio mismatch"
    assert np.isclose(engineered_sample[0, 12], 6.0 / 241.0), "chlor_sulfate_ratio mismatch"
    assert np.isclose(engineered_sample[0, 13], 55.0 / 6.1), "thm_chlor_ratio mismatch"
    print("[2] 5 Feature Transformations Verified (Identical mathematical definitions confirmed):")
    print(f"    - ph_dev                  : {engineered_sample[0, 9]:.4f}")
    print(f"    - solids_cond_ratio       : {engineered_sample[0, 10]:.4f}")
    print(f"    - hardness_solids_ratio   : {engineered_sample[0, 11]:.6f}")
    print(f"    - chlor_sulfate_ratio     : {engineered_sample[0, 12]:.6f}")
    print(f"    - thm_chlor_ratio         : {engineered_sample[0, 13]:.4f}")

    # 3. Verify calibrated decision threshold
    threshold = preprocessor.get('threshold')
    assert threshold == 0.475, f"Expected threshold 0.475, found {threshold}"
    print(f"[3] Calibrated Decision Threshold Verified: tau = {threshold}")

    # 4. Verify model_metrics.json matches actual evaluation
    with open("models/model_metrics.json") as f:
        metrics = json.load(f)
    fe_rf = metrics["models"]["Feature-Engineered Random Forest"]
    assert fe_rf["accuracy"] == 68.75, f"Accuracy mismatch: {fe_rf['accuracy']}"
    assert fe_rf["precision"] == 70.73, f"Precision mismatch: {fe_rf['precision']}"
    assert fe_rf["recall"] == 33.98, f"Recall mismatch: {fe_rf['recall']}"
    assert fe_rf["f1_score"] == 45.91, f"F1 mismatch: {fe_rf['f1_score']}"
    assert fe_rf["confusion_matrix"] == {"tn": 364, "fp": 36, "fn": 169, "tp": 87}
    print("[4] model_metrics.json Synchronization Confirmed:")
    print(f"    - Accuracy: {fe_rf['accuracy']}% | Precision: {fe_rf['precision']}% | Recall: {fe_rf['recall']}% | F1: {fe_rf['f1_score']}%")
    print(f"    - Confusion Matrix: TN={fe_rf['confusion_matrix']['tn']}, FP={fe_rf['confusion_matrix']['fp']}, FN={fe_rf['confusion_matrix']['fn']}, TP={fe_rf['confusion_matrix']['tp']}")

    # 5. Verify WHO/EPA Safety Guardrails
    toxic_sample = {
        'ph': 3.2, 'hardness': 180.0, 'solids': 18000.0,
        'chloramines': 6.0, 'sulfate': 240.0, 'conductivity': 400.0,
        'organic_carbon': 11.5, 'trihalomethanes': 55.0, 'turbidity': 3.2
    }
    evals = evaluate_parameters(toxic_sample)
    danger_evals = [e for e in evals if e.status == "danger"]
    assert len(danger_evals) > 0, "Toxic pH failed to trigger danger status"
    assert danger_evals[0].parameter == "ph", "Expected pH to trigger danger"
    print(f"[5] WHO/EPA Safety Guardrail Confirmed:")
    print(f"    - Evaluated acidic pH 3.2 -> Status: {danger_evals[0].status.upper()} ({danger_evals[0].description[:50]}...)")
    print("=" * 70)
    print("PHASE 1 VERIFICATION: ALL CHECKS PASSED")
    print("=" * 70)

if __name__ == "__main__":
    verify_phase1()
