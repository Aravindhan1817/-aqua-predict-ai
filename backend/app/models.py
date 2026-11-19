from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from backend.app.database import Base

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sample_name = Column(String(100), default="Water Sample")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 9 Water parameters
    ph = Column(Float, nullable=False)
    hardness = Column(Float, nullable=False)
    solids = Column(Float, nullable=False)
    chloramines = Column(Float, nullable=False)
    sulfate = Column(Float, nullable=False)
    conductivity = Column(Float, nullable=False)
    organic_carbon = Column(Float, nullable=False)
    trihalomethanes = Column(Float, nullable=False)
    turbidity = Column(Float, nullable=False)

    # Prediction outcomes
    prediction = Column(Integer, nullable=False) # 1 = Safe/Potable, 0 = Unsafe/Not Potable
    potability_label = Column(String(20), nullable=False) # "Safe" or "Unsafe"
    probability = Column(Float, nullable=False) # Probability of being potable
    confidence = Column(Float, nullable=False) # Confidence score %
    risk_level = Column(String(50), nullable=False) # e.g. "Low Risk", "High Risk"
    model_used = Column(String(50), default="Random Forest")
