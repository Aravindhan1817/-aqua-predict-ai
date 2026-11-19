"""
Systematic Machine Learning Performance Improvement Experiments for Water Potability.
Strict adherence to:
- Stratified 5-Fold Cross-Validation on training set ONLY.
- Holdout test set (656 samples) completely isolated until final validation.
- In-fold preprocessing and in-fold SMOTE via imbalanced-learn Pipeline.
- Out-of-fold probability collection for threshold tuning and PR-AUC.
- Safety-oriented metrics: Potable Precision/Recall, Specificity, FPR (Unsafe->Potable).
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# Path setup
sys.path.insert(0, os.path.abspath("."))

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

# ----------------- DOMAIN FEATURE ENGINEERING TRANSFORMER -----------------
class WaterFeatureEngineering(BaseEstimator, TransformerMixin):
    """
    Computes domain-specific chemical and physical ratios:
    - ph_dev: Absolute deviation from neutral pH (7.0)
    - solids_cond_ratio: TDS to conductivity ratio (ion density index)
    - hardness_solids_ratio: Proportion of mineral hardness relative to total solids
    - chlor_sulfate_ratio: Disinfectant to mineral sulfate balance
    - thm_chlor_ratio: Disinfection byproduct conversion ratio
    """
    def __init__(self, add_features=True):
        self.add_features = add_features
        self.feature_names_out_ = None

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if not self.add_features:
            return X

        # X is numpy array with 9 base features:
        # 0:ph, 1:Hardness, 2:Solids, 3:Chloramines, 4:Sulfate,
        # 5:Conductivity, 6:Organic_carbon, 7:Trihalomethanes, 8:Turbidity
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

        new_features = np.hstack([
            X, ph_dev, solids_cond_ratio, hardness_solids_ratio,
            chlor_sulfate_ratio, thm_chlor_ratio
        ])
        return new_features

# ----------------- EXPERIMENT EVALUATION HELPER -----------------
def evaluate_cv_pipeline(pipeline, X_train, y_train, cv, has_decision_function=False):
    """
    Runs Stratified 5-Fold Cross Validation collecting out-of-fold (OOF) probabilities.
    Returns comprehensive metrics calculated on OOF predictions.
    """
    oof_probs = np.zeros(len(y_train))
    fold_accuracies = []

    for fold, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train)):
        X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
        X_val, y_val = X_train.iloc[val_idx], y_train.iloc[val_idx]

        pipeline.fit(X_tr, y_tr)

        if hasattr(pipeline, "predict_proba"):
            probs = pipeline.predict_proba(X_val)[:, 1]
        elif hasattr(pipeline, "decision_function"):
            df_vals = pipeline.decision_function(X_val)
            # sigmoid calibration
            probs = 1.0 / (1.0 + np.exp(-df_vals))
        else:
            probs = pipeline.predict(X_val).astype(float)

        oof_probs[val_idx] = probs
        fold_acc = accuracy_score(y_val, (probs >= 0.5).astype(int))
        fold_accuracies.append(fold_acc)

    # Standard metrics at default tau = 0.50
    preds_50 = (oof_probs >= 0.50).astype(int)
    cm = confusion_matrix(y_train, preds_50)
    tn, fp, fn, tp = cm.ravel()

    acc = float(accuracy_score(y_train, preds_50)) * 100.0
    prec = float(precision_score(y_train, preds_50, zero_division=0)) * 100.0
    rec = float(recall_score(y_train, preds_50, zero_division=0)) * 100.0
    f1 = float(f1_score(y_train, preds_50, zero_division=0)) * 100.0
    roc_auc = float(roc_auc_score(y_train, oof_probs))
    pr_auc = float(average_precision_score(y_train, oof_probs))
    specificity = float(tn / (tn + fp)) * 100.0
    fpr = float(fp / (tn + fp)) * 100.0

    return {
        "oof_probs": oof_probs,
        "cv_accuracy_mean": round(float(np.mean(fold_accuracies)) * 100.0, 2),
        "cv_accuracy_std": round(float(np.std(fold_accuracies)) * 100.0, 2),
        "accuracy": round(acc, 2),
        "precision": round(prec, 2),
        "recall": round(rec, 2),
        "f1_score": round(f1, 2),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "specificity": round(specificity, 2),
        "fpr": round(fpr, 2),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
    }

def optimize_decision_threshold(y_true, oof_probs, max_fpr=15.0):
    """
    Searches optimal threshold tau in [0.30, 0.60] on Out-Of-Fold predictions.
    Safety constraint: False Positive Rate (FPR) must be <= max_fpr (default 15%).
    Selects tau that maximizes F1 score subject to the safety constraint.
    """
    thresholds = np.linspace(0.30, 0.60, 61)
    best_tau = 0.50
    best_f1 = -1.0
    best_metrics = None

    for tau in thresholds:
        preds = (oof_probs >= tau).astype(int)
        cm = confusion_matrix(y_true, preds)
        tn, fp, fn, tp = cm.ravel()
        fpr = (fp / (tn + fp)) * 100.0 if (tn + fp) > 0 else 100.0

        if fpr <= max_fpr:
            f1 = f1_score(y_true, preds, zero_division=0) * 100.0
            if f1 > best_f1:
                best_f1 = f1
                best_tau = float(tau)
                prec = precision_score(y_true, preds, zero_division=0) * 100.0
                rec = recall_score(y_true, preds, zero_division=0) * 100.0
                acc = accuracy_score(y_true, preds) * 100.0
                best_metrics = {
                    "threshold": round(best_tau, 3),
                    "f1_score": round(f1, 2),
                    "precision": round(prec, 2),
                    "recall": round(rec, 2),
                    "accuracy": round(acc, 2),
                    "specificity": round((tn / (tn + fp)) * 100.0, 2),
                    "fpr": round(fpr, 2),
                    "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
                }

    return best_metrics or {
        "threshold": 0.50, "f1_score": 0.0, "precision": 0.0,
        "recall": 0.0, "accuracy": 0.0, "specificity": 0.0, "fpr": 0.0,
        "confusion_matrix": {}
    }

# ----------------- MAIN EXPERIMENTS RUNNER -----------------
def run_all_experiments():
    data_path = os.path.join("dataset", "water_potability.csv")
    df = pd.read_csv(data_path)

    features = [
        'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
        'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity'
    ]
    target = 'Potability'

    X = df[features]
    y = df[target]

    # Isolated Holdout Split (Strictly Held Out)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    print("=" * 80)
    print("PHASE 2: EXECUTING MODEL IMPROVEMENT EXPERIMENTS (5-FOLD STRATIFIED CV)")
    print(f"Training Pool: {len(X_train)} samples | Holdout Test Pool: {len(X_test)} samples (ISOLATED)")
    print("=" * 80)

    experiments = {}

    # --- Experiment 1: Baseline Random Forest (Unweighted, Default tau=0.50) ---
    print("\n[Running Experiment 1: Baseline Random Forest]...")
    exp1_pipe = ImbPipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_split=5, random_state=42))
    ])
    exp1_res = evaluate_cv_pipeline(exp1_pipe, X_train, y_train, cv)
    experiments["Exp 1: Baseline RF (Unweighted)"] = exp1_res
    print(f"  -> CV Acc: {exp1_res['accuracy']}% | Prec: {exp1_res['precision']}% | Rec: {exp1_res['recall']}% | F1: {exp1_res['f1_score']}% | Spec: {exp1_res['specificity']}% | FPR: {exp1_res['fpr']}%")

    # --- Experiment 2: Class-Weighted Random Forest (balanced_subsample) ---
    print("\n[Running Experiment 2: Balanced Subsample Random Forest]...")
    exp2_pipe = ImbPipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=5,
            class_weight='balanced_subsample', random_state=42
        ))
    ])
    exp2_res = evaluate_cv_pipeline(exp2_pipe, X_train, y_train, cv)
    experiments["Exp 2: Balanced-Subsample RF"] = exp2_res
    print(f"  -> CV Acc: {exp2_res['accuracy']}% | Prec: {exp2_res['precision']}% | Rec: {exp2_res['recall']}% | F1: {exp2_res['f1_score']}% | Spec: {exp2_res['specificity']}% | FPR: {exp2_res['fpr']}%")

    # --- Experiment 3: In-Fold SMOTE Oversampling + Random Forest ---
    print("\n[Running Experiment 3: In-Fold SMOTE + Random Forest]...")
    exp3_pipe = ImbPipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('smote', SMOTE(random_state=42, sampling_strategy=0.85)),
        ('clf', RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_split=5, random_state=42))
    ])
    exp3_res = evaluate_cv_pipeline(exp3_pipe, X_train, y_train, cv)
    experiments["Exp 3: In-Fold SMOTE + RF"] = exp3_res
    print(f"  -> CV Acc: {exp3_res['accuracy']}% | Prec: {exp3_res['precision']}% | Rec: {exp3_res['recall']}% | F1: {exp3_res['f1_score']}% | Spec: {exp3_res['specificity']}% | FPR: {exp3_res['fpr']}%")

    # --- Experiment 4: Feature Engineering Pipeline + Random Forest ---
    print("\n[Running Experiment 4: Feature Engineering (5 Domain Ratios) + RF]...")
    exp4_pipe = ImbPipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('engineer', WaterFeatureEngineering(add_features=True)),
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_split=5, random_state=42))
    ])
    exp4_res = evaluate_cv_pipeline(exp4_pipe, X_train, y_train, cv)
    experiments["Exp 4: Engineered Features + RF"] = exp4_res
    print(f"  -> CV Acc: {exp4_res['accuracy']}% | Prec: {exp4_res['precision']}% | Rec: {exp4_res['recall']}% | F1: {exp4_res['f1_score']}% | Spec: {exp4_res['specificity']}% | FPR: {exp4_res['fpr']}%")

    # --- Experiment 5: Tuned HistGradientBoosting (Early Stopping + L2) ---
    print("\n[Running Experiment 5: HistGradientBoosting (Native NaNs + L2 Regularization)]...")
    exp5_pipe = ImbPipeline([
        # HistGradientBoosting handles NaNs natively without imputation
        ('scaler', StandardScaler()),
        ('clf', HistGradientBoostingClassifier(
            max_iter=150, learning_rate=0.06, max_leaf_nodes=31,
            min_samples_leaf=20, l2_regularization=1.5,
            early_stopping=True, random_state=42
        ))
    ])
    exp5_res = evaluate_cv_pipeline(exp5_pipe, X_train, y_train, cv)
    experiments["Exp 5: Tuned HistGradientBoosting"] = exp5_res
    print(f"  -> CV Acc: {exp5_res['accuracy']}% | Prec: {exp5_res['precision']}% | Rec: {exp5_res['recall']}% | F1: {exp5_res['f1_score']}% | Spec: {exp5_res['specificity']}% | FPR: {exp5_res['fpr']}%")

    # --- Experiment 6: Tuned Support Vector Machine (RBF, Class-Weighted) ---
    print("\n[Running Experiment 6: Tuned SVM (RBF + Class-Weighted)]...")
    exp6_pipe = ImbPipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('clf', SVC(C=1.5, gamma='scale', class_weight='balanced', probability=True, random_state=42))
    ])
    exp6_res = evaluate_cv_pipeline(exp6_pipe, X_train, y_train, cv)
    experiments["Exp 6: Tuned SVM (Balanced)"] = exp6_res
    print(f"  -> CV Acc: {exp6_res['accuracy']}% | Prec: {exp6_res['precision']}% | Rec: {exp6_res['recall']}% | F1: {exp6_res['f1_score']}% | Spec: {exp6_res['specificity']}% | FPR: {exp6_res['fpr']}%")

    # --- Experiment 7: Decision Threshold Optimization on Best Probability Model ---
    print("\n[Running Experiment 7: Decision Threshold Optimization on OOF Probabilities]...")
    # Evaluate threshold tuning across models
    threshold_results = {}
    for exp_name, res in experiments.items():
        opt = optimize_decision_threshold(y_train, res["oof_probs"], max_fpr=12.0)
        threshold_results[exp_name] = opt

    # ----------------- SUMMARY COMPARISON TABLE -----------------
    print("\n" + "=" * 95)
    print("SUMMARY COMPARISON TABLE: 5-FOLD STRATIFIED CROSS-VALIDATION ON TRAINING DATA")
    print(f"{'Experiment Model':<35} | {'Acc':<6} | {'Prec':<6} | {'Recall':<6} | {'F1':<6} | {'ROC-AUC':<7} | {'PR-AUC':<6} | {'Spec':<6} | {'FPR':<6}")
    print("-" * 95)
    for exp_name, m in experiments.items():
        print(f"{exp_name:<35} | {m['accuracy']:>5.2f}% | {m['precision']:>5.2f}% | {m['recall']:>5.2f}% | {m['f1_score']:>5.2f}% | {m['roc_auc']:>7.4f} | {m['pr_auc']:>6.4f} | {m['specificity']:>5.2f}% | {m['fpr']:>5.2f}%")

    print("\n" + "=" * 95)
    print("THRESHOLD-OPTIMIZED RESULTS (SAFETY CONSTRAINT: FPR <= 12% on Out-Of-Fold Data)")
    print(f"{'Experiment Model':<35} | {'Tau':<5} | {'Acc':<6} | {'Prec':<6} | {'Recall':<6} | {'F1':<6} | {'Spec':<6} | {'FPR':<6}")
    print("-" * 95)
    for exp_name, t in threshold_results.items():
        if t["threshold"] != 0.50:
            print(f"{exp_name:<35} | {t['threshold']:>5.3f} | {t['accuracy']:>5.2f}% | {t['precision']:>5.2f}% | {t['recall']:>5.2f}% | {t['f1_score']:>5.2f}% | {t['specificity']:>5.2f}% | {t['fpr']:>5.2f}%")
        else:
            print(f"{exp_name:<35} | {t['threshold']:>5.3f} | (No threshold found with FPR <= 12% that beats tau=0.50)")

    # ----------------- SELECTION DECISION -----------------
    # Identify best candidate based on CV Safety Profile:
    # High Specificity (>= 88%), Low FPR (<= 12%), Highest F1 & PR-AUC
    print("\n" + "=" * 80)
    print("PHASE 4: FINAL MODEL SELECTION & VERIFICATION ON HOLDOUT TEST SET")
    print("=" * 80)

    # Let's benchmark the top 2 candidate pipelines on the untouched Holdout Test Set (656 samples)
    # Candidate A: Baseline RF
    exp1_pipe.fit(X_train, y_train)
    holdout_prob_1 = exp1_pipe.predict_proba(X_test)[:, 1]
    holdout_pred_1 = (holdout_prob_1 >= 0.50).astype(int)
    cm1 = confusion_matrix(y_test, holdout_pred_1)
    tn1, fp1, fn1, tp1 = cm1.ravel()

    # Candidate B: Feature Engineering RF
    exp4_pipe.fit(X_train, y_train)
    holdout_prob_4 = exp4_pipe.predict_proba(X_test)[:, 1]
    holdout_pred_4 = (holdout_prob_4 >= 0.50).astype(int)
    cm4 = confusion_matrix(y_test, holdout_pred_4)
    tn4, fp4, fn4, tp4 = cm4.ravel()

    # Candidate C: Tuned HistGradientBoosting
    exp5_pipe.fit(X_train, y_train)
    holdout_prob_5 = exp5_pipe.predict_proba(X_test)[:, 1]
    holdout_pred_5 = (holdout_prob_5 >= 0.50).astype(int)
    cm5 = confusion_matrix(y_test, holdout_pred_5)
    tn5, fp5, fn5, tp5 = cm5.ravel()

    print("\nHOLDOUT TEST SET EVALUATION (656 Unseen Samples):")
    print(f"  [Baseline RF]:")
    print(f"    - Accuracy   : {accuracy_score(y_test, holdout_pred_1)*100:.2f}%")
    print(f"    - Precision  : {precision_score(y_test, holdout_pred_1, zero_division=0)*100:.2f}%")
    print(f"    - Recall     : {recall_score(y_test, holdout_pred_1, zero_division=0)*100:.2f}%")
    print(f"    - F1-Score   : {f1_score(y_test, holdout_pred_1, zero_division=0)*100:.2f}%")
    print(f"    - Specificity: {(tn1 / (tn1 + fp1))*100:.2f}%")
    print(f"    - FPR (Unsafe->Potable): {(fp1 / (tn1 + fp1))*100:.2f}% (FP={fp1})")
    print(f"    - ROC-AUC    : {roc_auc_score(y_test, holdout_prob_1):.4f}")
    print(f"    - PR-AUC     : {average_precision_score(y_test, holdout_prob_1):.4f}")

    print(f"\n  [Candidate: Feature Engineering RF]:")
    print(f"    - Accuracy   : {accuracy_score(y_test, holdout_pred_4)*100:.2f}%")
    print(f"    - Precision  : {precision_score(y_test, holdout_pred_4, zero_division=0)*100:.2f}%")
    print(f"    - Recall     : {recall_score(y_test, holdout_pred_4, zero_division=0)*100:.2f}%")
    print(f"    - F1-Score   : {f1_score(y_test, holdout_pred_4, zero_division=0)*100:.2f}%")
    print(f"    - Specificity: {(tn4 / (tn4 + fp4))*100:.2f}%")
    print(f"    - FPR (Unsafe->Potable): {(fp4 / (tn4 + fp4))*100:.2f}% (FP={fp4})")
    print(f"    - ROC-AUC    : {roc_auc_score(y_test, holdout_prob_4):.4f}")
    print(f"    - PR-AUC     : {average_precision_score(y_test, holdout_prob_4):.4f}")

    print(f"\n  [Candidate: HistGradientBoosting]:")
    print(f"    - Accuracy   : {accuracy_score(y_test, holdout_pred_5)*100:.2f}%")
    print(f"    - Precision  : {precision_score(y_test, holdout_pred_5, zero_division=0)*100:.2f}%")
    print(f"    - Recall     : {recall_score(y_test, holdout_pred_5, zero_division=0)*100:.2f}%")
    print(f"    - F1-Score   : {f1_score(y_test, holdout_pred_5, zero_division=0)*100:.2f}%")
    print(f"    - Specificity: {(tn5 / (tn5 + fp5))*100:.2f}%")
    print(f"    - FPR (Unsafe->Potable): {(fp5 / (tn5 + fp5))*100:.2f}% (FP={fp5})")
    print(f"    - ROC-AUC    : {roc_auc_score(y_test, holdout_prob_5):.4f}")
    print(f"    - PR-AUC     : {average_precision_score(y_test, holdout_prob_5):.4f}")

    # Serialize experiments report
    clean_exp_log = {}
    for k, v in experiments.items():
        clean_exp_log[k] = {
            "cv_accuracy_mean": v["cv_accuracy_mean"],
            "accuracy": v["accuracy"],
            "precision": v["precision"],
            "recall": v["recall"],
            "f1_score": v["f1_score"],
            "roc_auc": v["roc_auc"],
            "pr_auc": v["pr_auc"],
            "specificity": v["specificity"],
            "fpr": v["fpr"],
            "confusion_matrix": v["confusion_matrix"]
        }

    log_payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cv_folds": 5,
        "experiments": clean_exp_log,
        "threshold_tuning": threshold_results
    }
    with open("models/experiments_log.json", "w") as f:
        json.dump(log_payload, f, indent=2)
    print("\nSaved full experimental logs to models/experiments_log.json")

if __name__ == "__main__":
    run_all_experiments()
