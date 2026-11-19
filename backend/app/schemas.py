from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class WaterSampleInput(BaseModel):
    sample_name: Optional[str] = Field(default="Water Sample", max_length=100)
    ph: float = Field(..., ge=0.0, le=14.0, description="pH level (0 - 14)")
    hardness: float = Field(..., ge=0.0, description="Hardness in mg/L (CaCO3 equivalent)")
    solids: float = Field(..., ge=0.0, description="Total Dissolved Solids (TDS) in ppm / mg/L")
    chloramines: float = Field(..., ge=0.0, description="Chloramines concentration in ppm / mg/L")
    sulfate: float = Field(..., ge=0.0, description="Sulfate concentration in mg/L")
    conductivity: float = Field(..., ge=0.0, description="Electrical Conductivity in μS/cm")
    organic_carbon: float = Field(..., ge=0.0, description="Total Organic Carbon (TOC) in ppm / mg/L")
    trihalomethanes: float = Field(..., ge=0.0, description="Trihalomethanes (THMs) in μg/L (ppb)")
    turbidity: float = Field(..., ge=0.0, description="Turbidity in Nephelometric Turbidity Units (NTU)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sample_name": "Municipal Tap Sample",
                "ph": 7.3,
                "hardness": 190.5,
                "solids": 18500.0,
                "chloramines": 6.8,
                "sulfate": 330.0,
                "conductivity": 420.0,
                "organic_carbon": 12.5,
                "trihalomethanes": 65.0,
                "turbidity": 3.8
            }
        }
    }

class ParameterEvaluation(BaseModel):
    parameter: str
    display_name: str
    value: float
    unit: str
    safe_range: str
    status: str  # "safe", "warning", "danger"
    description: str

class Recommendation(BaseModel):
    category: str
    title: str
    description: str
    priority: str  # "high", "medium", "low"

class PredictionResponse(BaseModel):
    id: Optional[int] = None
    sample_name: str
    created_at: str
    prediction: int  # 1 or 0
    potability_label: str  # "Safe" or "Unsafe"
    probability: float  # 0.0 - 100.0 %
    confidence: float  # 0.0 - 100.0 %
    risk_level: str
    model_used: str
    parameter_evaluations: List[ParameterEvaluation]
    recommendations: List[Recommendation]
    feature_contributions: Dict[str, float]

class HistoryItemResponse(BaseModel):
    id: int
    sample_name: str
    created_at: str
    ph: float
    hardness: float
    solids: float
    chloramines: float
    sulfate: float
    conductivity: float
    organic_carbon: float
    trihalomethanes: float
    turbidity: float
    prediction: int
    potability_label: str
    probability: float
    confidence: float
    risk_level: str
    model_used: str

class PresetSample(BaseModel):
    id: str
    name: str
    description: str
    expected_outcome: str
    parameters: WaterSampleInput
