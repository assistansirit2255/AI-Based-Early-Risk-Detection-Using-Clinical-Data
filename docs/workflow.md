# Full System Workflow

## Overview

```
Doctor                  Frontend (React)              Backend (Django)              ML Pipeline
  │                          │                              │                            │
  │  Open http://localhost:5173                             │                            │
  │─────────────────────────>│                              │                            │
  │                          │                              │                            │
  │  1. Add Patient          │                              │                            │
  │─────────────────────────>│  POST /api/patients/         │                            │
  │                          │─────────────────────────────>│                            │
  │                          │  201 { Patient }             │                            │
  │                          │<─────────────────────────────│                            │
  │                          │                              │                            │
  │  2. Add Health Record    │                              │                            │
  │─────────────────────────>│  POST /api/patients/{id}/records/                        │
  │                          │─────────────────────────────>│                            │
  │                          │  201 { HealthRecord }        │                            │
  │                          │<─────────────────────────────│                            │
  │  (repeat for each visit) │                              │                            │
  │                          │                              │                            │
  │  3. Run Prediction       │                              │                            │
  │─────────────────────────>│  POST /api/patients/{id}/predict/                        │
  │                          │─────────────────────────────>│                            │
  │                          │                              │  normalize_records()       │
  │                          │                              │─────────────────────────> │
  │                          │                              │  history_collapse()        │
  │                          │                              │─────────────────────────> │
  │                          │                              │  model.predict_proba()     │
  │                          │                              │─────────────────────────> │
  │                          │                              │  SHAP explainer            │
  │                          │                              │─────────────────────────> │
  │                          │                              │  { pred, prob, shap, … }   │
  │                          │                              │<─────────────────────────  │
  │                          │  201 { Prediction }          │                            │
  │                          │<─────────────────────────────│                            │
  │  See risk verdict +      │                              │                            │
  │  SHAP bar chart          │                              │                            │
  │<─────────────────────────│                              │                            │
```

---

## Step-by-Step

### Step 1: Doctor adds a patient

1. Navigate to **Patients → Add Patient**
2. Fill in: Name, Age, Gender, Height, Weight, Lifestyle flags
3. Submit → Patient created in Django `Patient` model
4. Redirected to Patient Detail page

### Step 2: Records stored over time

1. From Patient Detail page, click **+ Add Record**
2. Fill in: Date, Systolic BP, Diastolic BP, Cholesterol level, Glucose level
3. Validation ensures:
   - Systolic BP > Diastolic BP
   - Values within clinically plausible ranges
4. Record stored in `HealthRecord` model linked to patient
5. Repeat at each patient visit

### Step 3: Prediction triggered

1. Doctor clicks **🔮 Run Prediction** on Patient Detail page
2. Frontend calls `POST /api/patients/{id}/predict/`
3. Backend:
   - Loads all `HealthRecord` rows for the patient
   - Builds a payload combining patient demographics + per-record vitals
   - Passes to `predict_from_records(records)`

### Step 4: ML Pipeline executes

1. **`normalize_records(records)`**
   - If `len(records) >= 5` → use as-is → `data_type_used = "real"`
   - If `< 5` → generate synthetic records via linear interpolation → `data_type_used = "hybrid"`
   - No randomness; all values are deterministic interpolations

2. **`history_collapse`** (Strategy A)
   - `ap_hi = 0.7 × latest_bp + 0.3 × avg(last 5 bp values)`
   - `cholesterol, gluc` → smoothed and clamped to 1–3
   - Demographics (age, gender, height, weight, smoke, alco, active) → forward-filled from latest record

3. **Model prediction**
   - Features aligned to `["id","age","gender","height","weight","ap_hi","ap_lo","cholesterol","gluc","smoke","alco","active"]`
   - `model.predict_proba(X)` → probability of CVD = 1
   - `prediction = 1 if probability >= 0.5 else 0`

4. **SHAP computation**
   - Tries `shap.TreeExplainer` (Random Forest / GBM)
   - Falls back to `shap.LinearExplainer` (Logistic Regression)
   - If neither works → `shap_values = null` + `shap_warning` message

5. Result stored in `Prediction` model and returned to frontend

### Step 5: SHAP results shown in frontend

1. Frontend receives `Prediction` object
2. `PredictionResult` component renders:
   - Risk label (🔴 High Risk / 🟢 Low Risk)
   - Probability percentage + progress bar
   - `data_type_used` badge (real / hybrid)
   - SHAP horizontal bar chart — red bars = features increasing risk, green = decreasing
3. Previous predictions listed below for trend tracking

---

## Data Flow Summary

```
Patient demographics  ──┐
                         ├── records_payload ──> normalize_records()
HealthRecord vitals   ──┘                              │
                                                history_collapse()
                                                       │
                                            12-feature snapshot row
                                                       │
                                              cvd_model.predict_proba()
                                                       │
                                              SHAP explainer
                                                       │
                                    { prediction, probability, data_type_used,
                                      shap_values, shap_warning, records_used }
```

---

## Edge Cases Handled

| Scenario | Behaviour |
|----------|-----------|
| No records exist | `POST /predict/` returns **422** with explanation |
| Fewer than 5 records | Synthetic records interpolated; `data_type_used = "hybrid"` |
| Model `.pkl` not found | **503** with `ModelNotAvailableError` message |
| SHAP not computable | `shap_values = null`, `shap_warning` = explanation; prediction still returned |
| Invalid patient id | **404** |
| Invalid form input | **400** with field-level validation errors |
