"""
Machine Learning Training and Evaluation Pipeline for Water Quality Prediction.
Strictly avoids data leakage: Imputation and scaling are fit solely on training data.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve
)

def run_training():
    data_path = os.path.join("dataset", "water_potability.csv")
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)

    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)

    feature_columns = [
        'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
        'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity'
    ]
    target_column = 'Potability'

    X = df[feature_columns]
    y = df[target_column]

    print(f"Dataset shape: {X.shape}, Target distribution: {np.bincount(y)}")

    # 1. Stratified Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 2. Fit Imputer ONLY on X_train to avoid data leakage
    imputer = SimpleImputer(strategy='median')
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    # 3. Fit Scaler ONLY on X_train_imp
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_imp)
    X_test_scaled = scaler.transform(X_test_imp)

    # Save preprocessing components together
    preprocessor = {
        'imputer': imputer,
        'scaler': scaler,
        'feature_names': feature_columns,
        'medians': {col: float(val) for col, val in zip(feature_columns, imputer.statistics_)},
        'means': {col: float(val) for col, val in zip(feature_columns, scaler.mean_)},
        'scales': {col: float(val) for col, val in zip(feature_columns, scaler.scale_)}
    }
    joblib.dump(preprocessor, os.path.join(models_dir, "preprocessor.joblib"))
    print("Saved preprocessor to models/preprocessor.joblib")

    # 4. Define candidate models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, min_samples_leaf=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=12, min_samples_split=5, random_state=42),
        "Support Vector Machine (SVM)": SVC(probability=True, kernel='rbf', C=1.5, gamma='scale', random_state=42),
        "K-Nearest Neighbors (KNN)": KNeighborsClassifier(n_neighbors=7, weights='distance'),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
    }

    # 5. Hyperparameter Tuning for Random Forest
    print("Performing hyperparameter optimization for Random Forest...")
    rf_param_grid = {
        'n_estimators': [100, 150, 200],
        'max_depth': [10, 12, 15],
        'min_samples_split': [3, 5, 8]
    }
    rf_grid = GridSearchCV(
        RandomForestClassifier(random_state=42),
        rf_param_grid,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring='accuracy',
        n_jobs=-1
    )
    rf_grid.fit(X_train_scaled, y_train)
    best_rf = rf_grid.best_estimator_
    models["Random Forest"] = best_rf
    print(f"Optimal Random Forest params: {rf_grid.best_params_}")

    # 6. Train, Cross-Validate, and Evaluate all models
    results = {}
    best_name = None
    best_score = -1.0
    best_model_obj = None

    for name, clf in models.items():
        print(f"Training and evaluating {name}...")
        clf.fit(X_train_scaled, y_train)

        # 5-fold Cross-Validation on training set
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(clf, X_train_scaled, y_train, cv=cv, scoring='accuracy')

        # Test set predictions
        y_pred = clf.predict(X_test_scaled)
        if hasattr(clf, "predict_proba"):
            y_prob = clf.predict_proba(X_test_scaled)[:, 1]
        elif hasattr(clf, "decision_function"):
            y_prob = clf.decision_function(X_test_scaled)
        else:
            y_prob = y_pred

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        try:
            auc = float(roc_auc_score(y_test, y_prob))
        except Exception:
            auc = 0.5

        cm = confusion_matrix(y_test, y_pred).tolist()

        # Compute ROC curve points
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        # downsample for JSON storage (30 points)
        step = max(1, len(fpr) // 30)
        roc_points = [{"fpr": round(float(f), 4), "tpr": round(float(t), 4)} for f, t in zip(fpr[::step], tpr[::step])]

        results[name] = {
            "accuracy": round(acc * 100, 2),
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "roc_auc": round(auc, 4),
            "cv_accuracy_mean": round(float(cv_scores.mean()) * 100, 2),
            "cv_accuracy_std": round(float(cv_scores.std()) * 100, 2),
            "confusion_matrix": {
                "tn": int(cm[0][0]),
                "fp": int(cm[0][1]),
                "fn": int(cm[1][0]),
                "tp": int(cm[1][1])
            },
            "roc_curve": roc_points
        }

        # Model selection: combination of accuracy and f1
        combined_score = acc + f1
        if combined_score > best_score:
            best_score = combined_score
            best_name = name
            best_model_obj = clf

    print(f"\nBest performing model: {best_name} with Accuracy {results[best_name]['accuracy']}% and F1 {results[best_name]['f1_score']}%")

    # 7. Extract Feature Importances
    feature_importance_dict = {}
    if hasattr(best_model_obj, "feature_importances_"):
        importances = best_model_obj.feature_importances_
        feature_importance_dict = {
            col: round(float(imp) * 100, 2)
            for col, imp in sorted(zip(feature_columns, importances), key=lambda x: x[1], reverse=True)
        }
    else:
        # Fallback to Random Forest feature importance
        importances = models["Random Forest"].feature_importances_
        feature_importance_dict = {
            col: round(float(imp) * 100, 2)
            for col, imp in sorted(zip(feature_columns, importances), key=lambda x: x[1], reverse=True)
        }

    # 8. Save best model
    joblib.dump(best_model_obj, os.path.join(models_dir, "best_model.joblib"))
    print("Saved best model to models/best_model.joblib")

    # Also save each individual model for comparison & fallback
    for name, clf in models.items():
        slug = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        joblib.dump(clf, os.path.join(models_dir, f"{slug}.joblib"))

    # 9. Save complete metrics metadata
    metrics_payload = {
        "best_model": best_name,
        "dataset_stats": {
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "potable_count": int((df['Potability'] == 1).sum()),
            "non_potable_count": int((df['Potability'] == 0).sum()),
            "features": feature_columns
        },
        "models": results,
        "feature_importances": feature_importance_dict,
        "best_rf_params": rf_grid.best_params_
    }

    metrics_file = os.path.join(models_dir, "model_metrics.json")
    with open(metrics_file, "w") as f:
        json.dump(metrics_payload, f, indent=2)
    print(f"Saved evaluation metrics to {metrics_file}")

if __name__ == "__main__":
    run_training()
