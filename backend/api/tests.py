"""
Unit tests for the API endpoints and ML pipeline.

Run with:
  cd backend
  python manage.py test api
"""

from unittest.mock import MagicMock, patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from api.models import Patient, HealthRecord, Prediction


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_patient(**kwargs):
    defaults = dict(
        name="Test Patient",
        age=45,
        gender=1,
        height=170.0,
        weight=75.0,
        smoke=False,
        alco=False,
        active=True,
    )
    defaults.update(kwargs)
    return Patient.objects.create(**defaults)


def make_record(patient, **kwargs):
    from datetime import date
    defaults = dict(
        patient=patient,
        date=kwargs.pop("date", date.today()),
        ap_hi=120.0,
        ap_lo=80.0,
        cholesterol=1,
        gluc=1,
    )
    defaults.update(kwargs)
    return HealthRecord.objects.create(**defaults)


# ── Health Check ──────────────────────────────────────────────────────────────

class HealthCheckTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check_returns_200(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")


# ── Patient CRUD ──────────────────────────────────────────────────────────────

class PatientListTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_empty_list(self):
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["data"]["count"], 0)

    def test_create_patient_valid(self):
        payload = {
            "name": "Alice",
            "age": 35,
            "gender": 2,
            "height": 165.0,
            "weight": 60.0,
            "smoke": False,
            "alco": False,
            "active": True,
        }
        response = self.client.post("/api/patients/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"]["name"], "Alice")

    def test_create_patient_invalid_age(self):
        payload = {
            "name": "Bob", "age": 200, "gender": 1,
            "height": 180.0, "weight": 80.0,
        }
        response = self.client.post("/api/patients/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "error")

    def test_search_by_name(self):
        make_patient(name="Alice Smith")
        make_patient(name="Bob Jones")
        response = self.client.get("/api/patients/?search=alice")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["count"], 1)

    def test_retrieve_nonexistent_patient(self):
        response = self.client.get("/api/patients/9999/")
        self.assertEqual(response.status_code, 404)

    def test_update_patient(self):
        patient = make_patient()
        response = self.client.put(
            f"/api/patients/{patient.pk}/",
            {"name": "Updated Name", "age": 50, "gender": 1, "height": 175.0, "weight": 80.0},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["name"], "Updated Name")

    def test_delete_patient(self):
        patient = make_patient()
        response = self.client.delete(f"/api/patients/{patient.pk}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Patient.objects.filter(pk=patient.pk).exists())


# ── Health Records ─────────────────────────────────────────────────────────────

class HealthRecordTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = make_patient()

    def test_add_record_valid(self):
        payload = {
            "date": "2024-01-15",
            "ap_hi": 125.0,
            "ap_lo": 82.0,
            "cholesterol": 2,
            "gluc": 1,
        }
        response = self.client.post(
            f"/api/patients/{self.patient.pk}/records/", payload, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"]["ap_hi"], 125.0)

    def test_add_record_invalid_bp(self):
        payload = {
            "date": "2024-01-15",
            "ap_hi": 80.0,
            "ap_lo": 90.0,  # ap_lo >= ap_hi → invalid
            "cholesterol": 1,
            "gluc": 1,
        }
        response = self.client.post(
            f"/api/patients/{self.patient.pk}/records/", payload, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_list_records(self):
        make_record(self.patient)
        make_record(self.patient)
        response = self.client.get(f"/api/patients/{self.patient.pk}/records/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 2)

    def test_delete_record(self):
        record = make_record(self.patient)
        response = self.client.delete(
            f"/api/patients/{self.patient.pk}/records/{record.pk}/"
        )
        self.assertEqual(response.status_code, 204)


# ── Prediction ─────────────────────────────────────────────────────────────────

class PredictionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = make_patient()

    def test_predict_no_records_returns_422(self):
        response = self.client.post(f"/api/patients/{self.patient.pk}/predict/")
        self.assertEqual(response.status_code, 422)

    @patch("api.views.predict_from_records")
    def test_predict_success(self, mock_predict):
        mock_predict.return_value = {
            "prediction": 0,
            "probability": 0.25,
            "data_type_used": "real",
            "shap_values": {"age": 0.1, "ap_hi": -0.05},
            "shap_warning": "",
            "records_used": 5,
        }
        from datetime import date, timedelta
        for i in range(5):
            make_record(self.patient, date=date(2024, 1, i + 1))

        response = self.client.post(f"/api/patients/{self.patient.pk}/predict/")
        self.assertEqual(response.status_code, 201)
        data = response.data["data"]
        self.assertEqual(data["prediction"], 0)
        self.assertAlmostEqual(data["probability"], 0.25)
        self.assertEqual(data["data_type_used"], "real")

    @patch("api.views.predict_from_records")
    def test_predict_model_not_available(self, mock_predict):
        from ml_api.cvd_predictor import ModelNotAvailableError
        mock_predict.side_effect = ModelNotAvailableError("Model file missing")
        from datetime import date
        make_record(self.patient)
        response = self.client.post(f"/api/patients/{self.patient.pk}/predict/")
        self.assertEqual(response.status_code, 503)

    def test_list_predictions_empty(self):
        response = self.client.get(f"/api/patients/{self.patient.pk}/predictions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"], [])


# ── ML: record_normalizer ──────────────────────────────────────────────────────

class RecordNormalizerTest(TestCase):
    def test_enough_records_returns_real(self):
        from ml_api.record_normalizer import normalize_records
        records = [
            {"date": f"2024-01-0{i}", "ap_hi": 120 + i, "ap_lo": 80, "cholesterol": 1, "gluc": 1}
            for i in range(1, 6)
        ]
        normalized, dtype = normalize_records(records, min_records=5)
        self.assertEqual(len(normalized), 5)
        self.assertEqual(dtype, "real")

    def test_fewer_records_returns_hybrid(self):
        from ml_api.record_normalizer import normalize_records
        records = [
            {"date": "2024-01-01", "ap_hi": 120, "ap_lo": 80, "cholesterol": 1, "gluc": 1},
            {"date": "2024-01-05", "ap_hi": 128, "ap_lo": 84, "cholesterol": 2, "gluc": 1},
        ]
        normalized, dtype = normalize_records(records, min_records=5)
        self.assertEqual(len(normalized), 5)
        self.assertEqual(dtype, "hybrid")
        # Check smoothness: ap_hi should interpolate from 120 → 128
        ap_hi_values = [r["ap_hi"] for r in normalized]
        self.assertAlmostEqual(ap_hi_values[0], 120.0, places=1)
        self.assertAlmostEqual(ap_hi_values[-1], 128.0, places=1)
        for i in range(len(ap_hi_values) - 1):
            self.assertLessEqual(ap_hi_values[i], ap_hi_values[i + 1])

    def test_single_record_constant_fill(self):
        from ml_api.record_normalizer import normalize_records
        records = [{"date": "2024-01-01", "ap_hi": 130, "ap_lo": 85, "cholesterol": 1, "gluc": 1}]
        normalized, dtype = normalize_records(records, min_records=5)
        self.assertEqual(len(normalized), 5)
        self.assertEqual(dtype, "hybrid")
        for r in normalized:
            self.assertAlmostEqual(r["ap_hi"], 130.0)

    def test_empty_records_raises(self):
        from ml_api.record_normalizer import normalize_records
        with self.assertRaises(ValueError):
            normalize_records([], min_records=5)


# ── ML: history_collapse ──────────────────────────────────────────────────────

class HistoryCollapseTest(TestCase):
    def test_smoothed_latest_numeric(self):
        from ml_api.history_collapse import smoothed_latest_numeric
        values = [100, 110, 120, 130, 140]
        result = smoothed_latest_numeric(values, w_latest=0.7, last_k=5)
        # expected: 0.7 * 140 + 0.3 * avg([100,110,120,130,140]) = 98 + 0.3*120 = 134
        self.assertAlmostEqual(result, 134.0)

    def test_smoothed_latest_level_clamps(self):
        from ml_api.history_collapse import smoothed_latest_level_1_3
        self.assertEqual(smoothed_latest_level_1_3([3, 3, 3]), 3)
        self.assertEqual(smoothed_latest_level_1_3([1, 1, 1]), 1)

    def test_forward_fill(self):
        from ml_api.history_collapse import forward_fill
        records = [{"age": 40}, {"age": None}, {"age": 45}]
        self.assertEqual(forward_fill(records, "age", 0), 45)
