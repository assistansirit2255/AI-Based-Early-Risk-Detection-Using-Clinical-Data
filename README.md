# 🧠 AI-Based Early Risk Detection Using Clinical Data

> **Production-ready** end-to-end system: Django REST backend + React frontend + ML CVD risk model.

---

## 📌 Project Overview

This project predicts early cardiovascular disease (CVD) risk using machine learning models trained on clinical datasets. It exposes a **REST API** (Django) consumed by a **React SPA** that lets doctors manage patients, record vitals over time, and trigger risk predictions with SHAP explainability.

### Disease modules
| Module | Location | Status |
|--------|----------|--------|
| **CVD (Cardiovascular Disease)** | `backend/ml_api/` | ✅ Production-ready REST API |
| Diabetes | `diabetes/` | Streamlit prototype |
| Hypertension | `Hypertension/` | Streamlit prototype |

---

## 🏗 Repository Layout (Option B — Monorepo)

```
AI-Based-Early-Risk-Detection-Using-Clinical-Data/
├── backend/                 ← Django REST API
│   ├── backend/             ← Django project settings, urls, wsgi
│   ├── api/                 ← DRF app: models, serializers, views, tests
│   ├── ml_api/              ← ML pipeline (predictor, normalizer, SHAP)
│   ├── requirements.txt
│   ├── .env.example
│   └── manage.py
├── frontend/                ← React (Vite) SPA
│   ├── src/
│   │   ├── api/             ← Centralized Axios client + API modules
│   │   ├── pages/           ← PatientList, PatientDetail, AddPatient, AddRecord, Prediction
│   │   └── components/      ← Navbar, PatientCard, RecordTable, PredictionResult, …
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── cvd/                     ← CVD dataset + trained model (.pkl excluded from git)
├── diabetes/                ← Diabetes dataset
├── Hypertension/            ← Hypertension dataset
├── modules/                 ← Shared Streamlit utilities
├── docs/                    ← Additional documentation
└── README.md                ← This file
```

---

## 🚀 Complete Startup Guide

### Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

---

### 1️⃣ Clone the repository

```bash
git clone https://github.com/assistansirit2255/AI-Based-Early-Risk-Detection-Using-Clinical-Data.git
cd AI-Based-Early-Risk-Detection-Using-Clinical-Data
```

---

### 2️⃣ Model setup (required before backend will run predictions)

The trained `.pkl` files are excluded from git due to file size limits.

#### Option A — Retrain the CVD model

```bash
# Open and run all cells in:
cvd/machine_learning_CVD.ipynb
# This generates: cvd/cvd_model.pkl  and  cvd/feature_columns.pkl
```

#### Option B — Provide your own model

Place your files at:
```
cvd/cvd_model.pkl          ← sklearn-compatible model with predict_proba()
cvd/feature_columns.pkl    ← list of feature column names (optional)
```

Expected feature columns (in order):
```python
["id", "age", "gender", "height", "weight",
 "ap_hi", "ap_lo", "cholesterol", "gluc",
 "smoke", "alco", "active"]
```

> **Note:** If `cvd_model.pkl` is absent the backend will still start and run; the
> `/api/patients/{id}/predict/` endpoint will return **503** with a clear error message.

---

### 3️⃣ Backend setup (Django)

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env if you need to change SECRET_KEY, database path, or model paths

# Run database migrations
python manage.py migrate

# (Optional) Create admin user
python manage.py createsuperuser

# Start development server on port 8000
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`.

---

### 4️⃣ Frontend setup (React)

```bash
cd frontend

# Install Node dependencies
npm install

# Configure environment (optional – dev proxy handles /api/* automatically)
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000   (only needed for production builds)

# Start Vite dev server on port 5173
npm run dev
```

Open `http://localhost:5173` in your browser.

---

### 5️⃣ Running both services together

Open **two terminals**:

```bash
# Terminal 1 – Backend
cd backend && python manage.py runserver

# Terminal 2 – Frontend
cd frontend && npm run dev
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | Health check |
| GET | `/api/patients/` | List patients (supports `?search=name&page=N`) |
| POST | `/api/patients/` | Create patient |
| GET | `/api/patients/{id}/` | Get patient |
| PUT | `/api/patients/{id}/` | Update patient (partial) |
| DELETE | `/api/patients/{id}/` | Delete patient |
| GET | `/api/patients/{id}/records/` | List health records |
| POST | `/api/patients/{id}/records/` | Add health record |
| DELETE | `/api/patients/{id}/records/{rid}/` | Delete record |
| POST | `/api/patients/{id}/predict/` | Run CVD prediction |
| GET | `/api/patients/{id}/predictions/` | List past predictions |

All responses use the envelope:
```json
{ "status": "success", "data": { ... } }
{ "status": "error",   "message": "…", "details": { … } }
```

---

## 📊 Prediction Response

```json
{
  "id": 1,
  "patient_id": 42,
  "prediction": 1,
  "risk_label": "High Risk",
  "probability": 0.78,
  "data_type_used": "hybrid",
  "shap_values": { "ap_hi": 0.12, "age": 0.08, "cholesterol": 0.05 },
  "shap_warning": "",
  "records_used": 5,
  "records_provided": 3,
  "created_at": "2024-03-15T10:23:45Z"
}
```

- `data_type_used = "real"` — all 5+ real records were used.
- `data_type_used = "hybrid"` — fewer than 5 records; synthetic gap-fill was applied via linear interpolation.
- `shap_values = null` + non-empty `shap_warning` — SHAP could not be computed for this model type.

---

## 🔄 Full Workflow

See [`docs/workflow.md`](docs/workflow.md) for the complete step-by-step workflow.

## ✅ Project Startup Guide

See [`docs/startup.md`](docs/startup.md) for a clean from-scratch setup guide.

---

## 🧪 Running Backend Tests

```bash
cd backend
python manage.py test api
```

---

## 🛠 Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | insecure dev key | Django secret key (change in production) |
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |
| `CVD_MODEL_PATH` | `../cvd/cvd_model.pkl` | Path to model file |
| `CVD_FEATURES_PATH` | `../cvd/feature_columns.pkl` | Path to feature columns file |
| `CVD_SHAP_BACKGROUND_PATH` | `cvd/cleaned_cardio_data.csv` | Background data for SHAP |
| `DIABETES_MODEL_PATH` | `diabetes/diabetes_model.pkl` | Diabetes model file |
| `DIABETES_FEATURES_PATH` | `diabetes/feature_columns.pkl` | Diabetes feature columns file |
| `DIABETES_SHAP_BACKGROUND_PATH` | `diabetes/diabetes.csv` | Background data for diabetes SHAP |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend URL (for production builds) |

---

## 👩‍💻 Author

Garima Sharma — BCA, Artificial Intelligence & Data Science, K.R. Mangalam University
