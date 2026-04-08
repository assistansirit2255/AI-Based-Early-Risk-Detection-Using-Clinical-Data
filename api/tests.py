"""
Basic tests for the clinical API endpoints.
"""
import json

from django.test import TestCase
from django.urls import reverse

from .models import HealthRecord, Patient


class PatientCreateTestCase(TestCase):
    def _post_patient(self, payload=None):
        payload = payload or {
            'name': 'Alice Smith',
            'date_of_birth': '1985-03-20',
            'gender': 0,
            'height': 165.0,
            'weight': 62.5,
        }
        return self.client.post(
            reverse('patient-create'),
            json.dumps(payload),
            content_type='application/json',
        )

    def test_create_patient_returns_201(self):
        resp = self._post_patient()
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['name'], 'Alice Smith')
        self.assertIn('id', data)

    def test_create_patient_missing_name_returns_400(self):
        resp = self._post_patient({'date_of_birth': '1985-03-20', 'gender': 0, 'height': 165.0, 'weight': 62.5})
        self.assertEqual(resp.status_code, 400)


class HealthRecordCreateTestCase(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            name='Bob Jones',
            date_of_birth='1970-07-15',
            gender=1,
            height=178.0,
            weight=82.0,
        )

    def _post_record(self, payload=None):
        payload = payload or {
            'patient': self.patient.pk,
            'recorded_on': '2024-06-01',
            'age': 53,
            'ap_hi': 130,
            'ap_lo': 85,
            'cholesterol': 2,
            'gluc': 1,
            'smoke': False,
            'alco': False,
            'active': True,
        }
        return self.client.post(
            reverse('healthrecord-create'),
            json.dumps(payload),
            content_type='application/json',
        )

    def test_create_health_record_returns_201(self):
        resp = self._post_record()
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['patient'], self.patient.pk)

    def test_ap_hi_less_than_ap_lo_returns_400(self):
        resp = self._post_record({
            'patient': self.patient.pk,
            'recorded_on': '2024-06-01',
            'age': 53,
            'ap_hi': 80,
            'ap_lo': 90,
            'cholesterol': 1,
            'gluc': 1,
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('non_field_errors', resp.json())


class PatientHistoryTestCase(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            name='Carol White',
            date_of_birth='1990-01-10',
            gender=0,
            height=160.0,
            weight=58.0,
        )
        HealthRecord.objects.create(
            patient=self.patient,
            recorded_on='2024-01-01',
            age=34,
            ap_hi=120,
            ap_lo=80,
            cholesterol=1,
            gluc=1,
        )
        HealthRecord.objects.create(
            patient=self.patient,
            recorded_on='2024-06-01',
            age=34,
            ap_hi=125,
            ap_lo=82,
            cholesterol=1,
            gluc=1,
        )

    def test_history_returns_records_for_patient(self):
        resp = self.client.get(reverse('patient-history', kwargs={'pk': self.patient.pk}))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 2)

    def test_history_for_nonexistent_patient_returns_404(self):
        resp = self.client.get(reverse('patient-history', kwargs={'pk': 9999}))
        self.assertEqual(resp.status_code, 404)

    def test_history_ordered_by_date(self):
        resp = self.client.get(reverse('patient-history', kwargs={'pk': self.patient.pk}))
        results = resp.json()['results']
        dates = [r['recorded_on'] for r in results]
        self.assertEqual(dates, sorted(dates))


class CVDPredictTestCase(TestCase):
    """
    These tests validate the predict endpoint's error handling.
    Full prediction is only available when cvd_model.pkl is present.
    """

    def setUp(self):
        self.patient = Patient.objects.create(
            name='Dan Brown',
            date_of_birth='1975-05-20',
            gender=1,
            height=175.0,
            weight=80.0,
        )

    def test_predict_with_no_records_returns_400(self):
        resp = self.client.post(
            reverse('patient-predict', kwargs={'pk': self.patient.pk}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.json())

    def test_predict_for_nonexistent_patient_returns_404(self):
        resp = self.client.post(
            reverse('patient-predict', kwargs={'pk': 9999}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 404)
        self.assertIn('error', resp.json())
