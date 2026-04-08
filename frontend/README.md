# Frontend — React (Vite) SPA

## Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.js         ← Centralized Axios instance (proxy to /api)
│   │   ├── patients.js       ← Patient CRUD API calls
│   │   ├── records.js        ← Health record API calls
│   │   └── predictions.js    ← Prediction API calls
│   ├── pages/
│   │   ├── PatientListPage.jsx    ← List + search + pagination
│   │   ├── PatientDetailPage.jsx  ← Profile + records + predictions
│   │   ├── AddPatientPage.jsx     ← Create patient form
│   │   ├── AddRecordPage.jsx      ← Add health record form
│   │   └── PredictionPage.jsx     ← Full prediction history view
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── PatientCard.jsx
│   │   ├── RecordTable.jsx
│   │   ├── PredictionResult.jsx   ← Risk verdict + probability bar + SHAP chart
│   │   ├── LoadingSpinner.jsx
│   │   └── ErrorMessage.jsx
│   ├── App.jsx                ← Router setup
│   ├── main.jsx
│   └── index.css
├── vite.config.js             ← Proxy /api → localhost:8000 in dev
├── package.json
└── .env.example
```

## Setup

```bash
npm install
cp .env.example .env   # edit VITE_API_BASE_URL if needed
npm run dev            # http://localhost:5173
```

## Key Features

- **Centralized API client**: all backend calls go through `src/api/client.js`  
- **Loading + error states**: every page shows a spinner while fetching and an error box with retry on failure  
- **SHAP visualization**: horizontal bar chart showing top-10 feature attributions  
- **Inline validation**: client-side form validation before API submission  
- **Dev proxy**: Vite proxies `/api/*` to `localhost:8000` so no CORS issue during development  
