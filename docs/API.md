# API Documentation

This document describes the Django REST Framework backend for the
AI-Based Early Risk Detection system.

---

## Base URL

```
http://localhost:8000/api/
```

---

## Endpoints

### 1. Add a Patient

**POST** `/api/patients/`

Registers a new patient in the system.

#### Request body

| Field           | Type    | Required | Description                        |
|-----------------|---------|----------|------------------------------------|
| `name`          | string  | Yes      | Full name of the patient           |
| `date_of_birth` | date    | Yes      | ISO 8601 date, e.g. `"1985-03-20"` |
| `gender`        | integer | Yes      | `0` = Female, `1` = Male           |
| `height`        | float   | Yes      | Height in centimetres              |
| `weight`        | float   | Yes      | Weight in kilograms                |

#### Example request

```bash
curl -s -X POST http://localhost:8000/api/patients/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Smith",
    "date_of_birth": "1985-03-20",
    "gender": 0,
    "height": 165.0,
    "weight": 62.5
  }'
```

#### Example response (`201 Created`)

```json
{
  "id": 1,
  "name": "Alice Smith",
  "date_of_birth": "1985-03-20",
  "gender": 0,
  "height": 165.0,
  "weight": 62.5,
  "created_at": "2024-06-01T10:00:00Z"
}
```

---

### 2. Add a Health Record

**POST** `/api/health-records/`

Adds a clinical measurement snapshot for an existing patient.

#### Request body

| Field         | Type    | Required | Description                                 |
|---------------|---------|----------|---------------------------------------------|
| `patient`     | integer | Yes      | Patient ID                                  |
| `recorded_on` | date    | Yes      | ISO 8601 date of the measurement            |
| `age`         | integer | Yes      | Patient age at time of measurement (years)  |
| `ap_hi`       | integer | Yes      | Systolic blood pressure (mmHg)              |
| `ap_lo`       | integer | Yes      | Diastolic blood pressure (mmHg)             |
| `cholesterol` | integer | Yes      | `1` = Normal, `2` = Above normal, `3` = Well above normal |
| `gluc`        | integer | Yes      | `1` = Normal, `2` = Above normal, `3` = Well above normal |
| `smoke`       | boolean | No       | Smoker? Default `false`                     |
| `alco`        | boolean | No       | Alcohol intake? Default `false`             |
| `active`      | boolean | No       | Physically active? Default `true`           |

#### Example request

```bash
curl -s -X POST http://localhost:8000/api/health-records/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient": 1,
    "recorded_on": "2024-06-01",
    "age": 39,
    "ap_hi": 130,
    "ap_lo": 85,
    "cholesterol": 2,
    "gluc": 1,
    "smoke": false,
    "alco": false,
    "active": true
  }'
```

#### Example response (`201 Created`)

```json
{
  "id": 1,
  "patient": 1,
  "recorded_on": "2024-06-01",
  "age": 39,
  "ap_hi": 130,
  "ap_lo": 85,
  "cholesterol": 2,
  "gluc": 1,
  "smoke": false,
  "alco": false,
  "active": true,
  "created_at": "2024-06-01T10:05:00Z"
}
```

---

### 3. Get Patient History

**GET** `/api/patients/<id>/history/`

Returns a paginated list of all health records for a patient, ordered by date.

#### Path parameter

| Parameter | Description |
|-----------|-------------|
| `id`      | Patient ID  |

#### Query parameters (pagination)

| Parameter | Default | Description           |
|-----------|---------|-----------------------|
| `page`    | `1`     | Page number           |

#### Example request

```bash
curl -s http://localhost:8000/api/patients/1/history/
```

#### Example response (`200 OK`)

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "patient": 1,
      "recorded_on": "2024-06-01",
      "age": 39,
      "ap_hi": 130,
      "ap_lo": 85,
      "cholesterol": 2,
      "gluc": 1,
      "smoke": false,
      "alco": false,
      "active": true,
      "created_at": "2024-06-01T10:05:00Z"
    },
    {
      "id": 2,
      "patient": 1,
      "recorded_on": "2024-09-15",
      "age": 39,
      "ap_hi": 135,
      "ap_lo": 88,
      "cholesterol": 2,
      "gluc": 1,
      "smoke": false,
      "alco": false,
      "active": true,
      "created_at": "2024-09-15T09:00:00Z"
    }
  ]
}
```

---

### 4. Predict CVD Risk

**POST** `/api/patients/<id>/predict/`

Runs CVD risk prediction using all stored health records for the patient.
Returns prediction label, probability, and SHAP feature importance.

#### Path parameter

| Parameter | Description |
|-----------|-------------|
| `id`      | Patient ID  |

#### Example request

```bash
curl -s -X POST http://localhost:8000/api/patients/1/predict/ \
  -H "Content-Type: application/json"
```

#### Example response (`200 OK`)

```json
{
  "patient_id": 1,
  "patient_name": "Alice Smith",
  "prediction": 0,
  "prediction_label": "Low Risk",
  "probability": 0.1823,
  "shap_values": {
    "base_value": 0.3412,
    "top_features": [
      { "feature": "ap_hi",       "value": 135.0, "shap":  0.0921 },
      { "feature": "age",         "value": 39.0,  "shap":  0.0614 },
      { "feature": "cholesterol", "value": 2.0,   "shap":  0.0312 },
      { "feature": "active",      "value": 1.0,   "shap": -0.0201 },
      { "feature": "smoke",       "value": 0.0,   "shap": -0.0088 }
    ]
  }
}
```

#### Notes
- `prediction` is `0` (Low Risk) or `1` (High Risk).
- `probability` is the model's estimated probability of CVD being present (0–1).
- `shap_values.top_features` lists the 5 features with the largest absolute SHAP
  contributions for this prediction. Positive SHAP values push towards High Risk;
  negative values push towards Low Risk.
- If the CVD model `.pkl` files are not present the endpoint returns `503`.

---

## Running the Backend

```bash
# Install dependencies
pip install -r requirement.txt

# Apply database migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`.

---

## Project Structure

```
.
├── backend/               # Django project package
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── api/                   # Django app
│   ├── models.py          # Patient, HealthRecord
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API endpoints
│   ├── urls.py            # URL routing
│   └── migrations/
├── ml_api/                # ML integration package
│   └── cvd_predictor.py   # predict_from_records() + SHAP
├── cvd/                   # CVD model artifacts
│   ├── cvd_model.pkl      # Trained sklearn model
│   ├── feature_columns.pkl
│   └── cleaned_cardio_data.csv  # SHAP background data
├── manage.py
└── requirement.txt
```
