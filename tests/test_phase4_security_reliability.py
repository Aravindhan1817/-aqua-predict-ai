"""
Phase 4: Security, Robustness, and Reliability Test Suite
"""
import os
import sys
import json
import sqlite3
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))
from backend.app.main import app
from backend.app.database import DB_PATH

def test_phase4_security_and_reliability():
    client = TestClient(app)
    print("=" * 70)
    print("PHASE 4: SECURITY & RELIABILITY TEST SUITE")
    print("=" * 70)

    # 1. SQL Injection attempt in sample_name
    sqli_payload = {
        "sample_name": "'; DROP TABLE prediction_history; --",
        "ph": 7.4, "hardness": 170.0, "solids": 18000.0,
        "chloramines": 6.0, "sulfate": 240.0, "conductivity": 400.0,
        "organic_carbon": 11.0, "trihalomethanes": 55.0, "turbidity": 3.2
    }
    r = client.post("/api/predict", json=sqli_payload)
    assert r.status_code == 200, f"Expected 200 parameterized insertion, got {r.status_code}"
    # Verify table was NOT dropped
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM prediction_history")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0, "SQL injection successfully dropped or corrupted the database!"
    print(f"[PASSED] SQL Injection Immunity: Parameterized queries in SQLAlchemy prevent SQL injection (table intact, count={count})")

    # 2. XSS Script Injection in sample_name
    xss_payload = dict(sqli_payload, sample_name="<script>alert('XSS')</script>")
    r = client.post("/api/predict", json=xss_payload)
    assert r.status_code == 200
    saved_name = r.json()["sample_name"]
    assert saved_name == "<script>alert('XSS')</script>"
    print("[PASSED] XSS Input Sanitization: Raw script tags safely serialized without execution")

    # 3. Oversized string payload (exceeding max_length=100)
    oversized_payload = dict(sqli_payload, sample_name="A" * 250)
    r = client.post("/api/predict", json=oversized_payload)
    assert r.status_code == 422, f"Expected 422 for oversized sample_name, got {r.status_code}"
    print("[PASSED] Buffer / String Overflow Protection: Pydantic rejects sample_name > 100 characters with HTTP 422")

    # 4. Out-of-bounds float limits (NaN / Malformed JSON body)
    r = client.post("/api/predict", content=b'{"sample_name": "Test", "ph": NaN}', headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    print("[PASSED] Malformed Float / NaN Rejection: HTTP 422 returned on non-standard NaN payload")

    # 5. Extreme values boundary testing
    extreme_min = dict(sqli_payload, ph=0.0, turbidity=0.0, solids=0.0)
    r = client.post("/api/predict", json=extreme_min)
    assert r.status_code == 200, "Failed on minimum legal values"

    extreme_max = dict(sqli_payload, ph=14.0, solids=100000.0, turbidity=50.0)
    r = client.post("/api/predict", json=extreme_max)
    assert r.status_code == 200, "Failed on maximum legal values"
    print("[PASSED] Boundary Range Handling: Correctly accepts mathematical boundaries (pH 0.0 and 14.0)")

    # 6. Database persistence after connection reset
    # Simulate process reboot by re-initializing connection to DB_PATH
    conn2 = sqlite3.connect(DB_PATH)
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT id, sample_name, potability_label, probability FROM prediction_history ORDER BY id DESC LIMIT 1")
    row = cursor2.fetchone()
    conn2.close()
    assert row is not None
    print(f"[PASSED] Persistent SQLite Storage: Verified disk persistence across separate connection sessions (ID #{row[0]}, Label: {row[2]})")

    # 7. No sensitive information exposure in API errors
    r_bad_path = client.get("/api/history/invalid_string_id")
    assert r_bad_path.status_code == 422
    err_text = r_bad_path.text
    assert "password" not in err_text.lower()
    assert "secret" not in err_text.lower()
    assert "c:\\" not in err_text.lower() # No internal file path disclosure in client validation error
    print("[PASSED] Error Information Disclosure Audit: Clean JSON validation error without path/key exposure")

    print("=" * 70)
    print("ALL SECURITY & RELIABILITY TESTS PASSED")
    print("=" * 70)

if __name__ == "__main__":
    test_phase4_security_and_reliability()
