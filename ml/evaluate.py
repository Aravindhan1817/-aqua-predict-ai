"""
Model Evaluation and Verification Script.
Loads serialized models and preprocessor, runs inference on test data, and verifies metrics.
"""

import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def evaluate_models():
    data_path = os.path.join("dataset", "water_potability.csv")
    models_dir = "models"

    if not os.path.exists(os.path.join(models_dir, "best_model.joblib")):
        print("Trained model not found. Please run ml/train.py first.")
        return

    df = pd.read_csv(data_path)
    features = [
        'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
        'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity'
    ]
    X = df[features]
    y = df['Potability']

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = joblib.load(os.path.join(models_dir, "preprocessor.joblib"))
    best_model = joblib.load(os.path.join(models_dir, "best_model.joblib"))

    X_test_imp = preprocessor['imputer'].transform(X_test)
    X_test_scaled = preprocessor['scaler'].transform(X_test_imp)

    y_pred = best_model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)

    print("=" * 60)
    print("VERIFYING BEST MODEL PERFORMANCE ON TEST SET")
    print("=" * 60)
    print(f"Test Accuracy: {acc * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Not Potable (0)", "Potable (1)"]))
    print("=" * 60)

if __name__ == "__main__":
    evaluate_models()
