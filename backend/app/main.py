"""
FastAPI Backend Application for AI-Based Water Quality Prediction System.
"""

import os
import json
from datetime import datetime
from typing import List, Optional
import math
from fastapi import FastAPI, HTTPException, Depends, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.database import engine, Base, get_db
from backend.app.models import PredictionHistory
from backend.app.schemas import (
    WaterSampleInput,
    PredictionResponse,
    HistoryItemResponse,
    PresetSample
)
from backend.app.predictor import predict_water_quality
from backend.app.recommendations import evaluate_parameters, generate_recommendations, STANDARDS

# Create SQLite tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Based Water Quality Prediction API",
    description="Intelligent Machine Learning System for Drinking Water Potability Assessment",
    version="2.0.0"
)

# Enable CORS for frontend connectivity
cors_origins_env = os.environ.get("CORS_ORIGINS")
allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()] if cors_origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _sanitize_for_json(obj):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    elif isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    return obj

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    sanitized = _sanitize_for_json(exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": sanitized}
    )

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METRICS_PATH = os.path.join(BASE_DIR, "models", "model_metrics.json")

# ----------------- PRESET SAMPLES (Balanced & Verified) -----------------
PRESETS: List[PresetSample] = [
    PresetSample(
        id="pristine-spring",
        name="Pristine Natural Spring Water",
        description="Balanced mineral content, healthy neutral pH (7.6), low sulfate, and clear clarity. Model predicts Potable (Safe).",
        expected_outcome="Potable (Safe)",
        parameters=WaterSampleInput(
            sample_name="Pristine Spring Water",
            ph=7.60,
            hardness=175.0,
            solids=18000.0,
            chloramines=5.80,
            sulfate=240.0,
            conductivity=410.0,
            organic_carbon=11.50,
            trihalomethanes=55.00,
            turbidity=3.20
        )
    ),
    PresetSample(
        id="municipal-tap",
        name="Standard Municipal Treated Water",
        description="Controlled municipal parameters, neutral pH (7.3), safe disinfection level, and low turbidity. Model predicts Potable (Safe).",
        expected_outcome="Potable (Safe)",
        parameters=WaterSampleInput(
            sample_name="Municipal Tap Sample",
            ph=7.30,
            hardness=165.0,
            solids=16500.0,
            chloramines=4.80,
            sulfate=235.0,
            conductivity=395.0,
            organic_carbon=10.80,
            trihalomethanes=48.00,
            turbidity=2.80
        )
    ),
    PresetSample(
        id="acidic-industrial",
        name="Acidic Industrial Runoff Sample",
        description="Hazardous corrosive acidity (pH 4.37), elevated sulfate, excess chloramines. Verified non-potable sample #468.",
        expected_outcome="Non-Potable (Unsafe)",
        parameters=WaterSampleInput(
            sample_name="Industrial Runoff (Sample #468)",
            ph=4.37,
            hardness=188.7,
            solids=29542.3,
            chloramines=8.12,
            sulfate=301.0,
            conductivity=456.3,
            organic_carbon=16.35,
            trihalomethanes=46.70,
            turbidity=4.65
        )
    ),
    PresetSample(
        id="turbid-river",
        name="Contaminated Surface Water Sample",
        description="Severe chemical imbalance (pH 3.10), high organic decay and sulfates. Verified non-potable sample #2993.",
        expected_outcome="Non-Potable (Unsafe)",
        parameters=WaterSampleInput(
            sample_name="Surface Water (Sample #2993)",
            ph=3.10,
            hardness=198.5,
            solids=45148.8,
            chloramines=8.47,
            sulfate=324.6,
            conductivity=400.1,
            organic_carbon=14.80,
            trihalomethanes=63.20,
            turbidity=4.25
        )
    )
]

# ----------------- ROOT & HEALTH -----------------
@app.get("/")
def root():
    return {
        "system": "AI-Based Water Quality Prediction and Assessment System",
        "status": "online",
        "version": "2.0.0",
        "endpoints": {
            "predict": "/api/predict (or /predict)",
            "history": "/api/history (or /history)",
            "model_performance": "/api/model-performance (or /model-performance)",
            "presets": "/api/presets",
            "standards": "/api/standards"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ----------------- PREDICTION ENDPOINTS -----------------
@app.post("/api/predict", response_model=PredictionResponse)
@app.post("/predict", response_model=PredictionResponse)
def predict_endpoint(payload: WaterSampleInput, db: Session = Depends(get_db)):
    param_dict = {
        "ph": payload.ph,
        "Hardness": payload.hardness,
        "Solids": payload.solids,
        "Chloramines": payload.chloramines,
        "Sulfate": payload.sulfate,
        "Conductivity": payload.conductivity,
        "Organic_carbon": payload.organic_carbon,
        "Trihalomethanes": payload.trihalomethanes,
        "Turbidity": payload.turbidity,
    }

    try:
        # Run ML Inference
        prediction_result = predict_water_quality(param_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

    # Parameter guidelines evaluation
    eval_dict = {
        "ph": payload.ph,
        "hardness": payload.hardness,
        "solids": payload.solids,
        "chloramines": payload.chloramines,
        "sulfate": payload.sulfate,
        "conductivity": payload.conductivity,
        "organic_carbon": payload.organic_carbon,
        "trihalomethanes": payload.trihalomethanes,
        "turbidity": payload.turbidity,
    }
    parameter_evaluations = evaluate_parameters(eval_dict)

    # Environmental Health Safety Guardrail:
    # If acute toxic/chemical thresholds are breached (danger status), safety override applies
    danger_violations = [p for p in parameter_evaluations if p.status == "danger"]
    if danger_violations and prediction_result["prediction"] == 1:
        prediction_result["prediction"] = 0
        prediction_result["potability_label"] = "Unsafe"
        danger_names = ", ".join([p.display_name for p in danger_violations[:2]])
        prediction_result["risk_level"] = f"Critical Risk (Exceeded: {danger_names})"
        prediction_result["probability"] = min(prediction_result["probability"], 35.0)

    is_safe = (prediction_result["prediction"] == 1)
    recommendations = generate_recommendations(parameter_evaluations, is_safe)

    # Persist in SQLite database
    now = datetime.utcnow()
    record = PredictionHistory(
        sample_name=payload.sample_name or "Water Sample",
        created_at=now,
        ph=payload.ph,
        hardness=payload.hardness,
        solids=payload.solids,
        chloramines=payload.chloramines,
        sulfate=payload.sulfate,
        conductivity=payload.conductivity,
        organic_carbon=payload.organic_carbon,
        trihalomethanes=payload.trihalomethanes,
        turbidity=payload.turbidity,
        prediction=prediction_result["prediction"],
        potability_label=prediction_result["potability_label"],
        probability=prediction_result["probability"],
        confidence=prediction_result["confidence"],
        risk_level=prediction_result["risk_level"],
        model_used=prediction_result["model_used"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return PredictionResponse(
        id=record.id,
        sample_name=record.sample_name,
        created_at=record.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        prediction=prediction_result["prediction"],
        potability_label=prediction_result["potability_label"],
        probability=prediction_result["probability"],
        confidence=prediction_result["confidence"],
        risk_level=prediction_result["risk_level"],
        model_used=prediction_result["model_used"],
        parameter_evaluations=parameter_evaluations,
        recommendations=recommendations,
        feature_contributions=prediction_result["feature_contributions"]
    )

# ----------------- HISTORY ENDPOINTS -----------------
@app.get("/api/history", response_model=List[HistoryItemResponse])
@app.get("/history", response_model=List[HistoryItemResponse])
def get_prediction_history(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    records = db.query(PredictionHistory).order_by(PredictionHistory.created_at.desc()).limit(limit).all()
    results = []
    for r in records:
        results.append(HistoryItemResponse(
            id=r.id,
            sample_name=r.sample_name,
            created_at=r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ph=r.ph,
            hardness=r.hardness,
            solids=r.solids,
            chloramines=r.chloramines,
            sulfate=r.sulfate,
            conductivity=r.conductivity,
            organic_carbon=r.organic_carbon,
            trihalomethanes=r.trihalomethanes,
            turbidity=r.turbidity,
            prediction=r.prediction,
            potability_label=r.potability_label,
            probability=r.probability,
            confidence=r.confidence,
            risk_level=r.risk_level,
            model_used=r.model_used
        ))
    return results

@app.get("/api/history/{record_id}", response_model=HistoryItemResponse)
@app.get("/history/{record_id}", response_model=HistoryItemResponse)
def get_prediction_history_item(record_id: int, db: Session = Depends(get_db)):
    record = db.query(PredictionHistory).filter(PredictionHistory.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction record not found")
    return HistoryItemResponse(
        id=record.id,
        sample_name=record.sample_name,
        created_at=record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ph=record.ph,
        hardness=record.hardness,
        solids=record.solids,
        chloramines=record.chloramines,
        sulfate=record.sulfate,
        conductivity=record.conductivity,
        organic_carbon=record.organic_carbon,
        trihalomethanes=record.trihalomethanes,
        turbidity=record.turbidity,
        prediction=record.prediction,
        potability_label=record.potability_label,
        probability=record.probability,
        confidence=record.confidence,
        risk_level=record.risk_level,
        model_used=record.model_used
    )

@app.delete("/api/history/{record_id}")
@app.delete("/history/{record_id}")
def delete_prediction_history_item(record_id: int, db: Session = Depends(get_db)):
    record = db.query(PredictionHistory).filter(PredictionHistory.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction record not found")
    db.delete(record)
    db.commit()
    return {"message": f"Record {record_id} successfully deleted", "id": record_id}

@app.delete("/api/history")
@app.delete("/history")
def clear_all_prediction_history(db: Session = Depends(get_db)):
    deleted_count = db.query(PredictionHistory).delete()
    db.commit()
    return {"message": f"Successfully cleared all {deleted_count} prediction records"}

# ----------------- MODEL PERFORMANCE ENDPOINT -----------------
@app.get("/api/model-performance")
@app.get("/model-performance")
def get_model_performance():
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(status_code=404, detail="Model metrics file not found. Run ml/train.py first.")
    with open(METRICS_PATH, "r") as f:
        metrics = json.load(f)
    return metrics

# ----------------- PRESETS & STANDARDS -----------------
@app.get("/api/presets", response_model=List[PresetSample])
def get_presets():
    return PRESETS

@app.get("/api/standards")
def get_standards():
    return STANDARDS

# Mount frontend production build if available (Unified Full-Stack Deployment)
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=True)
