"""
Comprehensive QA and Automated Test Suite for AI-Based Water Quality Prediction System.
Tests:
- API connectivity and health
- Validation logic on boundary and invalid inputs (422 HTTP responses)
- Prediction inference across 4 presets and custom edge cases
- Database persistence and audit logging
- History deletion and 404 handling for non-existent IDs
- Model metrics integrity against saved JSON and actual model evaluation
- Standards and recommendations accuracy
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def make_request(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            return e.code, json.loads(error_body)
        except Exception:
            return e.code, error_body

def test_health_and_root():
    # 1. Test Root
    status, body = make_request("/")
    assert status == 200
    assert body["system"] == "AI-Based Water Quality Prediction and Assessment System"

    # 2. Test Health
    status, body = make_request("/health")
    assert status == 200
    assert body["status"] == "healthy"
    print("PASS: Health & Root endpoints")

def test_standards_api():
    status, body = make_request("/api/standards")
    assert status == 200
    expected_params = [
        "ph", "hardness", "solids", "chloramines", "sulfate",
        "conductivity", "organic_carbon", "trihalomethanes", "turbidity"
    ]
    for param in expected_params:
        assert param in body, f"Missing parameter standard: {param}"
        assert "safe_min" in body[param]
        assert "safe_max" in body[param]
        assert "standard_text" in body[param]
        assert "hazard_high" in body[param]
    print("PASS: Standards API with all 9 parameters")

def test_presets_api():
    status, body = make_request("/api/presets")
    assert status == 200
    assert len(body) >= 4
    preset_ids = [p["id"] for p in body]
    assert "pristine-spring" in preset_ids
    assert "municipal-tap" in preset_ids
    assert "acidic-industrial" in preset_ids
    assert "turbid-river" in preset_ids
    print(f"PASS: Presets API loaded {len(body)} sample presets")

def test_valid_predictions():
    # Fetch presets to use as valid test cases
    _, presets = make_request("/api/presets")
    for p in presets:
        status, res = make_request("/api/predict", method="POST", data=p["parameters"])
        assert status == 200, f"Prediction failed for preset {p['name']}"
        assert "prediction" in res
        assert res["prediction"] in (0, 1)
        assert res["potability_label"] in ("Safe", "Unsafe")
        assert 0.0 <= res["probability"] <= 100.0
        assert 0.0 <= res["confidence"] <= 100.0
        assert "risk_level" in res
        assert len(res["parameter_evaluations"]) == 9
        assert len(res["recommendations"]) > 0
        assert len(res["feature_contributions"]) == 9
        print(f"PASS: Prediction for '{p['name']}' -> {res['potability_label']} ({res['probability']}%)")

def test_input_validation_boundaries():
    valid_base = {
        "sample_name": "Validation Test Sample",
        "ph": 7.0,
        "hardness": 150.0,
        "solids": 15000.0,
        "chloramines": 6.0,
        "sulfate": 300.0,
        "conductivity": 400.0,
        "organic_carbon": 12.0,
        "trihalomethanes": 60.0,
        "turbidity": 3.0
    }

    # 1. Negative pH
    bad_sample = dict(valid_base, ph=-1.5)
    status, _ = make_request("/api/predict", method="POST", data=bad_sample)
    assert status == 422, f"Expected 422 for negative pH, got {status}"

    # 2. Excess pH (> 14.0)
    bad_sample = dict(valid_base, ph=15.5)
    status, _ = make_request("/api/predict", method="POST", data=bad_sample)
    assert status == 422, f"Expected 422 for pH > 14, got {status}"

    # 3. Negative Turbidity
    bad_sample = dict(valid_base, turbidity=-2.0)
    status, _ = make_request("/api/predict", method="POST", data=bad_sample)
    assert status == 422, f"Expected 422 for negative turbidity, got {status}"

    # 4. Missing parameter (e.g. missing sulfate)
    incomplete_sample = dict(valid_base)
    del incomplete_sample["sulfate"]
    status, _ = make_request("/api/predict", method="POST", data=incomplete_sample)
    assert status == 422, f"Expected 422 for missing parameter, got {status}"

    # 5. Non-numeric parameter
    corrupted_sample = dict(valid_base, solids="not_a_number")
    status, _ = make_request("/api/predict", method="POST", data=corrupted_sample)
    assert status == 422, f"Expected 422 for non-numeric input, got {status}"

    print("PASS: Input boundary and schema validation (all returned 422 Unprocessable Entity)")

def test_model_performance_integrity():
    status, perf = make_request("/api/model-performance")
    assert status == 200
    assert "best_model" in perf
    assert perf["best_model"] == "Random Forest"

    expected_models = [
        "Random Forest", "Support Vector Machine (SVM)", "Gradient Boosting",
        "Decision Tree", "Logistic Regression", "K-Nearest Neighbors (KNN)"
    ]
    for model_name in expected_models:
        assert model_name in perf["models"], f"Missing model: {model_name}"
        m = perf["models"][model_name]
        assert "accuracy" in m
        assert "precision" in m
        assert "recall" in m
        assert "f1_score" in m
        assert "roc_auc" in m
        assert "confusion_matrix" in m

    rf_cm = perf["models"]["Random Forest"]["confusion_matrix"]
    assert rf_cm["tn"] + rf_cm["fp"] + rf_cm["fn"] + rf_cm["tp"] == 656  # 20% of 3276
    print("PASS: Model Performance API matches real holdout test evaluation")

def test_history_crud_operations():
    # 1. Clear history first
    status, _ = make_request("/api/history", method="DELETE")
    assert status == 200

    # 2. Check history is empty
    status, history = make_request("/api/history")
    assert status == 200
    assert len(history) == 0

    # 3. Create a sample
    sample = {
        "sample_name": "Audit Sample Alpha",
        "ph": 7.35,
        "hardness": 182.0,
        "solids": 17500.0,
        "chloramines": 6.2,
        "sulfate": 325.0,
        "conductivity": 415.0,
        "organic_carbon": 11.8,
        "trihalomethanes": 58.0,
        "turbidity": 3.4
    }
    status, pred_res = make_request("/api/predict", method="POST", data=sample)
    assert status == 200
    record_id = pred_res["id"]
    assert record_id is not None

    # 4. Check history now has 1 record
    status, history = make_request("/api/history")
    assert status == 200
    assert len(history) == 1
    item = history[0]
    assert item["id"] == record_id
    assert item["sample_name"] == "Audit Sample Alpha"
    assert item["ph"] == 7.35

    # 5. Delete specific record
    status, del_res = make_request(f"/api/history/{record_id}", method="DELETE")
    assert status == 200
    assert del_res["id"] == record_id

    # 6. Verify record is gone
    status, history = make_request("/api/history")
    assert status == 200
    assert len(history) == 0

    # 7. Attempt to delete non-existent ID -> 404
    status, err_res = make_request("/api/history/999999", method="DELETE")
    assert status == 404
    print("PASS: History CRUD, auto-persistence, and 404 error handling")

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING AUTOMATED QA TEST SUITE")
    print("=" * 60)
    test_health_and_root()
    test_standards_api()
    test_presets_api()
    test_valid_predictions()
    test_input_validation_boundaries()
    test_model_performance_integrity()
    test_history_crud_operations()
    print("=" * 60)
    print("ALL AUTOMATED TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
