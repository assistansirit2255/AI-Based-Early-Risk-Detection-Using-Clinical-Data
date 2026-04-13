# Backend — Django REST API

## Structure

```
backend/
├── backend/          ← Django project (settings, urls, wsgi, asgi)
├── api/              ← DRF app
│   ├── models.py     ← Patient, HealthRecord, Prediction
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── ml_api/           ← ML pipeline
│   ├── record_normalizer.py   ← History normalization (MIN_RECORDS=5)
│   ├── history_collapse.py    ← Strategy A: smoothed-latest collapse
│   └── cvd_predictor.py       ← Main predictor + SHAP
├── requirements.txt
├── .env.example
└── manage.py
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # edit as needed
python manage.py migrate
python manage.py runserver
```

Note: The backend loads backend/.env automatically if python-dotenv is installed.

## Tests

```bash
python manage.py test api
```

## ML Pipeline

1. **`record_normalizer.normalize_records(records)`**  
   Ensures at least `MIN_RECORDS=5` records. Uses linear interpolation for synthetic gap-fill. Returns `(records, "real"|"hybrid")`.

2. **`history_collapse`** — Strategy A helpers  
   `smoothed_latest = 0.7 × latest + 0.3 × avg(last 5)`

3. **`cvd_predictor.predict_from_records(records)`**  
   Full pipeline: normalize → collapse → align features → predict → SHAP.

## Key Design Decisions

- **Graceful model-missing handling**: returns HTTP 503 with a descriptive error if `.pkl` not found.
- **SHAP optional**: tries TreeExplainer → LinearExplainer → returns `null` + warning.
- **Authoritative feature list**: `["id","age","gender","height","weight","ap_hi","ap_lo","cholesterol","gluc","smoke","alco","active"]`
- **Standard response envelope**: `{"status": "success"|"error", "data": {...}}`.

## Diabetes Model Env Vars

Add these to backend/.env to enable diabetes predictions:

DIABETES_MODEL_PATH=diabetes/diabetes_model.pkl
DIABETES_FEATURES_PATH=diabetes/feature_columns.pkl
DIABETES_SHAP_BACKGROUND_PATH=diabetes/diabetes.csv
