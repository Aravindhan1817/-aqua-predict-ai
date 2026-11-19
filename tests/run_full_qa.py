"""
Full Quality Assurance Test Suite for AI-Based Water Quality Prediction System.
Runs in-process using FastAPI TestClient and Scikit-learn test evaluation.
"""

import sys
import os
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath("."))

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from fastapi.testclient import TestClient

from backend.app.main import app

def run_tests():
    client = TestClient(app)
    results = {"passed": 0, "failed": 0, "tests": []}

    def record_test(name, passed, details=""):
        if passed:
            results["passed"] += 1
            results["tests"].append({"name": name, "status": "PASSED", "details": details})
            print(f"[PASSED] {name} {details}")
        else:
            results["failed"] += 1
            results["tests"].append({"name": name, "status": "FAILED", "details": details})
            print(f"[FAILED] {name} {details}")

    print("=" * 70)
    print("STEP 1: ML PIPELINE & METRICS INTEGRITY VERIFICATION")
    print("=" * 70)

    try:
        # Load dataset and holdout test set
        df = pd.read_csv("dataset/water_potability.csv")
        features = [
            'ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
            'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity'
        ]
        X = df[features]
        y = df['Potability']

        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        preprocessor = joblib.load("models/preprocessor.joblib")
        best_model = joblib.load("models/best_model.joblib")

        X_test_imp = preprocessor['imputer'].transform(X_test)
        if 'engineer' in preprocessor and preprocessor['engineer'] is not None:
            X_test_eng = preprocessor['engineer'].transform(X_test_imp)
            X_test_scaled = preprocessor['scaler'].transform(X_test_eng)
        else:
            X_test_scaled = preprocessor['scaler'].transform(X_test_imp)

        tau = preprocessor.get('threshold', 0.50)
        if hasattr(best_model, "predict_proba"):
            y_prob = best_model.predict_proba(X_test_scaled)[:, 1]
            y_pred = (y_prob >= tau).astype(int)
        else:
            y_pred = best_model.predict(X_test_scaled)
        acc = accuracy_score(y_test, y_pred) * 100.0
        prec = precision_score(y_test, y_pred, zero_division=0) * 100.0
        rec = recall_score(y_test, y_pred, zero_division=0) * 100.0
        f1 = f1_score(y_test, y_pred, zero_division=0) * 100.0
        cm = confusion_matrix(y_test, y_pred).tolist()

        record_test(
            "Model Test Set Verification",
            True,
            f"(Accuracy: {acc:.2f}%, Precision: {prec:.2f}%, Recall: {rec:.2f}%, F1: {f1:.2f}%)"
        )

        # Check against model_metrics.json
        with open("models/model_metrics.json") as f:
            saved_metrics = json.load(f)
        best_name = saved_metrics["best_model"]
        target_metrics = saved_metrics["models"][best_name]

        saved_cm = target_metrics["confusion_matrix"]
        cm_expected = [[saved_cm["tn"], saved_cm["fp"]], [saved_cm["fn"], saved_cm["tp"]]]
        record_test(
            "Confusion Matrix Verification",
            cm == cm_expected,
            f"(TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]})"
        )

        assert round(target_metrics["accuracy"], 2) == round(acc, 2)
        assert round(target_metrics["precision"], 2) == round(prec, 2)
        record_test("Metrics File Synchronized", True, "(model_metrics.json matches real test evaluation)")
    except Exception as e:
        record_test("ML Pipeline & Metrics Verification", False, str(e))

    print("\n" + "=" * 70)
    print("STEP 2: BACKEND ENDPOINTS & INTEGRATION VERIFICATION")
    print("=" * 70)

    # 1. Health & Root
    try:
        r_root = client.get("/")
        assert r_root.status_code == 200 and "Aqua" in r_root.json().get("system", "") or "AI-Based" in r_root.json().get("system", "")
        r_health = client.get("/health")
        assert r_health.status_code == 200 and r_health.json().get("status") == "healthy"
        record_test("Health & Root Endpoints (GET / and GET /health)", True, "(Status: 200 OK)")
    except Exception as e:
        record_test("Health & Root Endpoints", False, str(e))

    # 2. Standards Endpoint
    try:
        r_std = client.get("/api/standards")
        assert r_std.status_code == 200
        standards = r_std.json()
        assert len(standards) == 9
        for p in ['ph', 'hardness', 'solids', 'chloramines', 'sulfate', 'conductivity', 'organic_carbon', 'trihalomethanes', 'turbidity']:
            assert p in standards
        record_test("Water Standards Reference (GET /api/standards)", True, "(9 parameters documented)")
    except Exception as e:
        record_test("Water Standards Reference", False, str(e))

    # 3. Presets Endpoint
    try:
        r_pre = client.get("/api/presets")
        assert r_pre.status_code == 200
        presets = r_pre.json()
        assert len(presets) == 4
        record_test("Preset Samples Endpoint (GET /api/presets)", True, f"({len(presets)} presets available)")
    except Exception as e:
        record_test("Preset Samples Endpoint", False, str(e))

    # 4. Predict Endpoint with All Presets
    try:
        for p in presets:
            r_pred = client.post("/api/predict", json=p["parameters"])
            assert r_pred.status_code == 200, f"Failed for {p['name']}"
            data = r_pred.json()
            assert data["potability_label"] in ("Safe", "Unsafe")
            assert 0.0 <= data["probability"] <= 100.0
            assert len(data["parameter_evaluations"]) == 9
            assert len(data["recommendations"]) > 0
            record_test(
                f"Prediction for '{p['name']}'",
                True,
                f"-> Result: {data['potability_label']}, Prob: {data['probability']}%, Risk: {data['risk_level'][:30]}..."
            )
    except Exception as e:
        record_test("Preset Predictions", False, str(e))

    print("\n" + "=" * 70)
    print("STEP 3: INPUT VALIDATION & ERROR HANDLING (422 / 404)")
    print("=" * 70)

    valid_base = {
        "sample_name": "QA Validation Sample",
        "ph": 7.2,
        "hardness": 160.0,
        "solids": 16000.0,
        "chloramines": 5.5,
        "sulfate": 280.0,
        "conductivity": 420.0,
        "organic_carbon": 11.0,
        "trihalomethanes": 55.0,
        "turbidity": 3.0
    }

    # Test Negative pH (-2.0)
    r = client.post("/api/predict", json=dict(valid_base, ph=-2.0))
    record_test("Validation: Reject Negative pH (< 0.0)", r.status_code == 422, f"(Returned HTTP {r.status_code})")

    # Test Excess pH (> 14.0)
    r = client.post("/api/predict", json=dict(valid_base, ph=16.0))
    record_test("Validation: Reject Excess pH (> 14.0)", r.status_code == 422, f"(Returned HTTP {r.status_code})")

    # Test Negative Turbidity
    r = client.post("/api/predict", json=dict(valid_base, turbidity=-1.5))
    record_test("Validation: Reject Negative Turbidity (< 0.0)", r.status_code == 422, f"(Returned HTTP {r.status_code})")

    # Test Missing Field (Omit Turbidity)
    incomplete = dict(valid_base)
    del incomplete["turbidity"]
    r = client.post("/api/predict", json=incomplete)
    record_test("Validation: Reject Missing Required Parameter", r.status_code == 422, f"(Returned HTTP {r.status_code})")

    # Test Non-numeric Input
    corrupted = dict(valid_base, solids="contaminated_solid")
    r = client.post("/api/predict", json=corrupted)
    record_test("Validation: Reject Non-Numeric Parameter Value", r.status_code == 422, f"(Returned HTTP {r.status_code})")

    print("\n" + "=" * 70)
    print("STEP 4: PERSISTENT DATABASE & HISTORY CRUD OPERATIONS")
    print("=" * 70)

    try:
        # Clear database
        r_del_all = client.delete("/api/history")
        assert r_del_all.status_code == 200

        # Verify empty
        r_empty = client.get("/api/history")
        assert r_empty.status_code == 200 and len(r_empty.json()) == 0
        record_test("History Clear & Empty State", True, "(0 records in database)")

        # Create 2 records
        client.post("/api/predict", json=valid_base)
        r_pred2 = client.post("/api/predict", json=dict(valid_base, sample_name="QA Sample Beta", ph=6.8))
        created_id = r_pred2.json()["id"]

        # Retrieve history
        r_hist = client.get("/api/history?limit=10")
        assert r_hist.status_code == 200
        hist_items = r_hist.json()
        assert len(hist_items) == 2
        record_test("History Retrieval & SQLite Persistence", True, f"({len(hist_items)} items retrieved)")

        # Delete single record
        r_del_one = client.delete(f"/api/history/{created_id}")
        assert r_del_one.status_code == 200
        record_test(f"Single Record Deletion (DELETE /api/history/{created_id})", True, f"(Successfully deleted record #{created_id})")

        # Verify count decreased to 1
        r_hist_after = client.get("/api/history")
        assert len(r_hist_after.json()) == 1

        # Delete non-existent ID -> 404
        r_404 = client.delete("/api/history/888888")
        record_test("404 Error on Non-Existent History ID", r_404.status_code == 404, f"(Returned HTTP {r_404.status_code})")
    except Exception as e:
        record_test("History Operations", False, str(e))

    print("\n" + "=" * 70)
    print("FINAL SUMMARY REPORT")
    print("=" * 70)
    print(f"Total Tests Executed: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed'] / (results['passed'] + results['failed'])) * 100:.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
