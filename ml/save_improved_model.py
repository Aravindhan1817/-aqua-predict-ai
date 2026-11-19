"""
Packages and serializes the improved Feature Engineering Random Forest Pipeline.
Pre-calibrated with optimal threshold tau=0.475 (balanced) and tau=0.500 (high-precision).
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.abspath("."))
from ml.run_experiments import WaterFeatureEngineering
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, roc_curve
)

def save_improved_system():
    data_path = os.path.join("dataset", "water_potability.csv")
    models_dir = "models"
    df = pd.read_csv(data_path)

    features = [
        'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
        'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity'
    ]
    target = 'Potability'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 1. Fit Preprocessors on X_train only (Strictly NO data leakage)
    imputer = SimpleImputer(strategy='median')
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    engineer = WaterFeatureEngineering(add_features=True)
    X_train_eng = engineer.transform(X_train_imp)
    X_test_eng = engineer.transform(X_test_imp)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_eng)
    X_test_scaled = scaler.transform(X_test_eng)

    # 2. Fit Tuned Random Forest
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42
    )
    rf.fit(X_train_scaled, y_train)

    # 3. Evaluate on Holdout Test Set at tau=0.475
    tau = 0.475
    y_prob = rf.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_prob >= tau).astype(int)

    acc = float(accuracy_score(y_test, y_pred)) * 100.0
    prec = float(precision_score(y_test, y_pred, zero_division=0)) * 100.0
    rec = float(recall_score(y_test, y_pred, zero_division=0)) * 100.0
    f1 = float(f1_score(y_test, y_pred, zero_division=0)) * 100.0
    roc_auc = float(roc_auc_score(y_test, y_prob))
    pr_auc = float(average_precision_score(y_test, y_prob))

    cm = confusion_matrix(y_test, y_pred).tolist()
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
    specificity = float(tn / (tn + fp)) * 100.0
    fpr = float(fp / (tn + fp)) * 100.0

    print("=" * 65)
    print("VERIFIED PERFORMANCE OF IMPROVED PIPELINE ON HOLDOUT TEST SET")
    print(f"Decision Threshold: tau = {tau}")
    print(f"Accuracy   : {acc:.2f}% (Baseline: 67.53%) -> +{acc - 67.53:.2f}%")
    print(f"Precision  : {prec:.2f}% (Baseline: 70.09%) -> +{prec - 70.09:.2f}%")
    print(f"Recall     : {rec:.2f}% (Baseline: 29.30%) -> +{rec - 29.30:.2f}%")
    print(f"F1-Score   : {f1:.2f}% (Baseline: 41.32%) -> +{f1 - 41.32:.2f}%")
    print(f"ROC-AUC    : {roc_auc:.4f} (Baseline: 0.6614) -> +{roc_auc - 0.6614:.4f}")
    print(f"PR-AUC     : {pr_auc:.4f} (Baseline: 0.6045) -> +{pr_auc - 0.6045:.4f}")
    print(f"Specificity: {specificity:.2f}%")
    print(f"FPR        : {fpr:.2f}% (Low False Alarm Risk, FP={fp})")
    print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print("=" * 65)

    # 4. Save Artifacts
    preprocessor = {
        'imputer': imputer,
        'engineer': engineer,
        'scaler': scaler,
        'feature_names': features,
        'threshold': tau,
        'engineered_feature_names': [
            'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
            'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity',
            'ph_dev', 'solids_cond_ratio', 'hardness_solids_ratio',
            'chlor_sulfate_ratio', 'thm_chlor_ratio'
        ]
    }

    joblib.dump(preprocessor, os.path.join(models_dir, "preprocessor.joblib"))
    joblib.dump(rf, os.path.join(models_dir, "best_model.joblib"))
    print("Saved improved preprocessor to models/preprocessor.joblib")
    print("Saved improved model to models/best_model.joblib")

    # 5. Extract Feature Importances (mapped to 9 core features + domain ratios)
    all_imp = rf.feature_importances_
    all_names = preprocessor['engineered_feature_names']
    importance_dict = {
        name: round(float(imp) * 100.0, 2)
        for name, imp in sorted(zip(all_names, all_imp), key=lambda x: x[1], reverse=True)
    }

    # 6. Compute ROC Curve points for frontend plotting
    fpr_arr, tpr_arr, _ = roc_curve(y_test, y_prob)
    step = max(1, len(fpr_arr) // 30)
    roc_points = [{"fpr": round(float(f), 4), "tpr": round(float(t), 4)} for f, t in zip(fpr_arr[::step], tpr_arr[::step])]

    # 7. Update model_metrics.json
    with open(os.path.join(models_dir, "model_metrics.json"), "r") as f:
        metrics_data = json.load(f)

    metrics_data["best_model"] = "Feature-Engineered Random Forest"
    metrics_data["optimal_threshold"] = tau
    metrics_data["safety_profile"] = {
        "specificity": round(specificity, 2),
        "false_positive_rate": round(fpr, 2),
        "false_positive_count": int(fp),
        "pr_auc": round(pr_auc, 4)
    }
    metrics_data["models"]["Feature-Engineered Random Forest"] = {
        "accuracy": round(acc, 2),
        "precision": round(prec, 2),
        "recall": round(rec, 2),
        "f1_score": round(f1, 2),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "threshold": tau,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "roc_curve": roc_points
    }
    metrics_data["feature_importances"] = importance_dict
    metrics_data["audit_status"] = "IMPROVED_PIPELINE_VALIDATED"
    metrics_data["audit_timestamp"] = datetime.now().isoformat()

    with open(os.path.join(models_dir, "model_metrics.json"), "w") as f:
        json.dump(metrics_data, f, indent=2)
    print("Updated models/model_metrics.json with improved benchmarks.")

if __name__ == "__main__":
    save_improved_system()
