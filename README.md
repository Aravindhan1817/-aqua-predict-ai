# AI-Based Water Quality Prediction and Assessment System

A modern, full-stack, responsive web application for drinking water potability prediction, chemical parameter diagnostic evaluation, and smart purification advisory powered by Machine Learning, FastAPI, SQLite, and React.

---

## 1. Project Overview

Access to safe drinking water is a fundamental human necessity. Traditional laboratory water quality testing can be time-consuming and expensive. The **AI-Based Water Quality Prediction and Assessment System** provides instant, data-driven potability classification and safety diagnostics based on 9 physicochemical water quality parameters.

The application leverages an **Engineered Random Forest Classifier** trained on verified Kaggle water potability records, achieving **68.75% Accuracy**, **70.73% Precision**, **91.00% Specificity**, and **45.91% F1-Score** on an isolated holdout test set with threshold calibration ($\tau = 0.475$). The system cross-references measured values against **World Health Organization (WHO)** and **US Environmental Protection Agency (EPA)** drinking water standards to deliver tailored remediation guidance (e.g., Reverse Osmosis, Activated Carbon Filtration, Calcite Neutralization).

---

## 2. Technology Stack

### Frontend
- **Framework**: React.js 19 with Vite 8
- **Styling**: Modern CSS Design System (Custom palette: Ocean Blue `#0284c7`, Emerald Green `#10b981`, Slate `#0f172a`, and clean card layouts)
- **Icons**: Lucide React (`lucide-react`)
- **Visualizations**: Interactive SVG metric bars, Confusion Matrix heat-grid, and dynamic probability gauges
- **Networking**: REST API Client with Vite reverse proxy configuration

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Server**: Uvicorn ASGI server
- **Validation**: Pydantic schemas with strict boundary validation
- **Middleware**: CORS (`CORSMiddleware`) for seamless frontend connectivity
- **Database**: SQLite with SQLAlchemy ORM for persistent audit trail logging
- **Unified Deployment**: Built-in static files mount serving compiled React frontend from single port

### Machine Learning & Data Science
- **Libraries**: Scikit-learn, Pandas, NumPy, Joblib, Imbalanced-Learn, Matplotlib, Seaborn
- **Algorithms Evaluated**:
  1. Feature-Engineered Random Forest Classifier *(Best Model - Production, $\tau = 0.475$)*
  2. Support Vector Machine (SVM)
  3. Gradient Boosting Classifier
  4. Decision Tree Classifier
  5. Logistic Regression
  6. K-Nearest Neighbors (KNN)
- **Domain Feature Engineering**: 5 physical/chemical ratios:
  - `ph_dev`: pH deviation from neutral ($|pH - 7.0|$)
  - `solids_cond_ratio`: TDS to Electrical Conductivity ratio
  - `hardness_solids_ratio`: Hardness to TDS ratio
  - `chlor_sulfate_ratio`: Chloramines to Sulfate disinfectant ratio
  - `thm_chlor_ratio`: Trihalomethanes to Chloramines byproduct ratio
- **Preprocessing**: Median Imputation (`SimpleImputer`) and Standardization (`StandardScaler`) fitted **strictly on training partitions** to prevent data leakage.
- **Decision Threshold Optimization**: Calibrated to $\tau = 0.475$ to prioritize potable-class precision and non-potable specificity, minimizing hazardous false positives (unsafe water falsely marked safe).

---

## 3. Water Quality Parameters

The system evaluates 9 key physical, chemical, and biological water quality parameters:

| Parameter | Unit | Permissible Standard | Agency | Clinical Health Impact |
|---|---|---|---|---|
| **pH Level** | pH units | `6.5 - 8.5` | WHO / EPA | Low pH (< 6.5) accelerates pipe corrosion, leaching toxic lead/copper. High pH (> 8.5) leaves scale encrustation and degrades chlorine efficacy. |
| **Hardness** | mg/L $CaCO_3$ | `60 - 250 mg/L` | WHO | Caused by dissolved calcium and magnesium. Hard water forms boiler scaling, degrades soap lathering, and accelerates appliance wear. |
| **Solids (TDS)** | ppm (mg/L) | `< 1,000 ppm` | WHO / EPA | Total dissolved inorganic salts and minerals. High TDS creates bitter, salty taste and potential gastrointestinal irritation. |
| **Chloramines** | ppm (mg/L) | `< 4.0 ppm` | US EPA | Residual chemical disinfectant. Concentrations > 4.0 ppm produce mucosal irritation, stomach discomfort, and distinct chemical odor. |
| **Sulfate ($SO_4$)** | mg/L | `< 250 mg/L` | EPA / WHO | Naturally occurring minerals from rock strata. Values > 250 mg/L induce a bitter medicinal taste and acute laxative/dehydration effects. |
| **Electrical Conductivity**| μS/cm | `< 600 μS/cm` | WHO | Measures ionic conductance. High conductivity indicates industrial contamination, fertilizer runoff, or high salinity. |
| **Organic Carbon (TOC)** | ppm (mg/L) | `< 4.0 ppm` | US EPA | Decaying organic matter. Reacts with chlorine disinfectants to produce carcinogenic Disinfection Byproducts (DBPs). |
| **Trihalomethanes (THMs)**| μg/L (ppb) | `< 80 μg/L` | US EPA | Carcinogenic chemical byproducts formed during chlorination. Clinically linked to increased risks of bladder cancer and liver damage. |
| **Turbidity** | NTU | `< 5.0 NTU` | WHO | Optical cloudiness caused by colloidal matter. Protects pathogenic microbes and viruses from chemical and UV disinfection. |

---

## 4. Machine Learning Model Benchmarks

All models were evaluated on an identical **80/20 Stratified Holdout Test Set (656 samples)**. **Zero fabricated or inflated metrics.**

| Model | Test Accuracy | Precision | Recall | F1-Score | Specificity | FPR | ROC-AUC | PR-AUC | Status |
|---|---|---|---|---|---|---|---|---|---|
| **Engineered Random Forest ($\tau=0.475$)** | **68.75%** | **70.73%** | **33.98%** | **45.91%** | **91.00%** | **9.00%** | **0.6744** | **0.6129** | **Production Best** |
| Baseline Random Forest ($\tau=0.500$) | 67.53% | 70.09% | 29.30% | 41.32% | 92.00% | 8.00% | 0.6614 | 0.5890 | Baseline Backup |
| Support Vector Machine (SVM) | 67.38% | 69.44% | 29.30% | 41.21% | 91.50% | 8.50% | 0.6467 | 0.5620 | Candidate |
| Gradient Boosting | 65.85% | 64.55% | 27.73% | 38.80% | 90.25% | 9.75% | 0.6511 | 0.5740 | Candidate |
| Decision Tree | 63.11% | 55.83% | 26.17% | 35.64% | 87.25% | 12.75% | 0.6011 | 0.4910 | Candidate |
| Logistic Regression | 60.98% | 0.00% | 0.00% | 0.00% | 100.0% | 0.00% | 0.5481 | 0.4320 | Baseline |
| K-Nearest Neighbors (KNN) | 59.15% | 46.15% | 28.12% | 34.95% | 79.25% | 20.75% | 0.5988 | 0.4750 | Candidate |

### Production Random Forest Holdout Confusion Matrix ($N = 656$):
- **True Negatives ($TN$)**: 364 (Non-potable correctly identified)
- **False Positives ($FP$)**: 36 (Non-potable falsely called safe - minimized to 9.00%)
- **False Negatives ($FN$)**: 169 (Potable water flagged for cautionary re-test)
- **True Positives ($TP$)**: 87 (Potable water correctly identified)

---

## 5. Project Folder Structure

```
water quality prediction/
├── Dockerfile                          # Multi-stage production container build
├── docker-compose.yml                  # Container orchestration service definition
├── render.yaml                         # Cloud platform auto-deploy configuration
├── Procfile                            # Cloud platform process launcher
├── requirements.txt                    # Root Python dependencies
├── dataset/
│   └── water_potability.csv            # Kaggle 3,276 sample water benchmark
├── ml/
│   ├── train.py                        # Full ML pipeline (split, CV, tuning, export)
│   ├── evaluate.py                     # Standalone verification and classification report
│   ├── eda.py                          # Exploratory data analysis & statistical summaries
│   └── experiment_improvements.py      # Feature engineering & threshold optimization
├── models/
│   ├── best_model.joblib               # Production Engineered Random Forest classifier
│   ├── preprocessor.joblib             # Imputer, Scaler, and Feature Transformer
│   ├── model_metrics.json              # Benchmarks, confusion matrix, ROC points
│   └── backup_baseline/                # Verified backup of baseline model
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI REST API endpoints & static mount
│   │   ├── config.py                   # Configuration & path constants
│   │   ├── database.py                 # SQLite database & SQLAlchemy session
│   │   ├── models.py                   # PredictionHistory ORM entity
│   │   ├── schemas.py                  # Pydantic input/output schemas
│   │   ├── predictor.py                # Safe inference engine with feature alignment
│   │   └── recommendations.py          # Standards evaluator & smart treatment rules
│   ├── water_quality.db                # SQLite database storing predictions
│   └── requirements.txt                # Backend dependencies
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx             # Navigation sidebar with status pill
│   │   │   └── Header.jsx              # Header with breadcrumb and active model badge
│   │   ├── pages/
│   │   │   ├── OverviewPage.jsx        # Dashboard overview, stats, and parameter guide
│   │   │   ├── PredictPage.jsx         # Interactive prediction form, presets, and result card
│   │   │   ├── PerformancePage.jsx     # Model comparison table, confusion matrix, charts
│   │   │   ├── HistoryPage.jsx         # Audit log, search, filter, sort, detail modal, CSV export
│   │   │   └── StandardsPage.jsx       # WHO & EPA regulatory standards encyclopedia
│   │   ├── services/
│   │   │   └── api.js                  # Unified API client
│   │   ├── App.jsx                     # Root router and state controller
│   │   ├── index.css                   # Custom Blue/Emerald design system
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js                  # Vite dev server with proxy to backend
├── tests/
│   ├── run_full_qa.py                  # Complete 19-point automated test suite
│   └── test_phase4_security_reliability.py # Security & boundary condition validation
└── README.md                           # Documentation & execution instructions
```

---

## 6. REST API Endpoints

The backend provides comprehensive REST endpoints with interactive Swagger UI available at `http://127.0.0.1:8000/docs`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | System identification and route directory (or serves Frontend in unified mode) |
| `GET` | `/health` | Live backend health check with ISO timestamp |
| `POST` | `/api/predict` | Predicts water potability, assigns risk, and stores record in SQLite |
| `GET` | `/api/history` | Retrieves list of past prediction records (supports `limit`) |
| `GET` | `/api/history/{id}` | Retrieves a single prediction record by ID |
| `DELETE`| `/api/history/{id}` | Deletes a specific prediction audit record |
| `DELETE`| `/api/history` | Clears all historical records |
| `GET` | `/api/model-performance`| Returns real benchmark metrics, confusion matrices, and feature importances |
| `GET` | `/api/presets` | Returns realistic preset samples for rapid testing |
| `GET` | `/api/standards` | Returns WHO/EPA parameter thresholds and health risks |

---

## 7. Installation and Local Execution

### Prerequisites
- **Python**: Version 3.10+
- **Node.js**: Version 18+
- **Package Managers**: `pip` and `npm`

---

### Option A: Unified Full-Stack Single-Port Execution (Recommended)
You can run both the frontend and backend together on a single port (`http://127.0.0.1:8000`):

1. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Build frontend assets:**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```
3. **Start the unified server:**
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```
4. Open `http://127.0.0.1:8000/` in your browser.

---

### Option B: Development Mode (Hot-Reloading)

1. **Start Backend (Terminal 1):**
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Start Frontend (Terminal 2):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Open `http://127.0.0.1:5173/` in your browser.

---

## 8. Docker Deployment

### Run with Docker Compose:
```bash
docker-compose up --build -d
```
The application will be live at `http://localhost:8000`.

### Build & Run Manually with Docker:
```bash
docker build -t water-quality-ai .
docker run -p 8000:8000 --name water-ai-app water-quality-ai
```

---

## 9. Automated Testing & Verification

Run the full end-to-end automated test suite:
```bash
python tests/run_full_qa.py
```
Run security and edge-case reliability tests:
```bash
python tests/test_phase4_security_reliability.py
```

---

## 10. License & Attribution

- **Dataset**: Kaggle Water Potability Dataset (`water_potability.csv`).
- **Standards**: World Health Organization (WHO) Guidelines for Drinking-water Quality (4th ed.) and US EPA National Primary & Secondary Drinking Water Regulations.
