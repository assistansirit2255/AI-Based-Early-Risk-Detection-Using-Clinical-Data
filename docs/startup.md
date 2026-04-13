# Project Startup Guide (From Scratch)

This guide covers model training/setup, backend startup, and frontend startup in a clean order.

## 1) Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

## 2) Clone and enter the repo

```bash
git clone https://github.com/assistansirit2255/AI-Based-Early-Risk-Detection-Using-Clinical-Data.git
cd AI-Based-Early-Risk-Detection-Using-Clinical-Data
```

## 3) Model setup (required for predictions)

You need the following files:

- cvd/cvd_model.pkl
- cvd/feature_columns.pkl (optional but recommended)
 - diabetes/diabetes_model.pkl
 - diabetes/feature_columns.pkl (optional but recommended)

### Option A: Train using the notebook

Open and run all cells in:

- cvd/machine_learning_CVD.ipynb
 - diabetes/Diabetes_eda and model training.ipynb

This notebook saves the model and feature columns:

- cvd/cvd_model.pkl
- cvd/feature_columns.pkl
 - diabetes/diabetes_model.pkl
 - diabetes/feature_columns.pkl

### Option B: Provide your own model

Place your files at:

- cvd/cvd_model.pkl
- cvd/feature_columns.pkl
 - diabetes/diabetes_model.pkl
 - diabetes/feature_columns.pkl

Expected feature columns (order matters):

```python
["id", "age", "gender", "height", "weight",
 "ap_hi", "ap_lo", "cholesterol", "gluc",
 "smoke", "alco", "active"]
```

Diabetes expected feature columns:

```python
["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
 "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]
```

## 4) Backend setup (Django)

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create and edit environment file (loaded automatically)
cp .env.example .env

# Run migrations
python manage.py migrate

# Start the backend
python manage.py runserver
```

Backend runs at:

- http://localhost:8000/api/

## 5) Frontend setup (React)

Open a second terminal:

```bash
cd frontend

# Install Node dependencies
npm install

# Start the frontend
npm run dev
```

Frontend runs at:

- http://localhost:5173

## 6) Quick validation

- Create a patient
- Add 1+ health records
- Run prediction from the patient detail page

For diabetes:

- Add at least one diabetes record
- Run diabetes prediction from the patient detail page

If the model files are missing, the prediction endpoint returns 503 with a clear message.
