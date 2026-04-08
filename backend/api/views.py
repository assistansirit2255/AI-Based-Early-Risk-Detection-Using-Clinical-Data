from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Patient, HealthRecord
from .serializers import PatientSerializer, HealthRecordSerializer
from .cvd_predictor import predict_from_records


class PatientListCreateView(generics.ListCreateAPIView):
    """GET /api/patients/  →  list all patients
    POST /api/patients/  →  create a patient"""

    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer


class HealthRecordListCreateView(generics.ListCreateAPIView):
    """GET  /api/patients/{id}/records/  →  list records for a patient
    POST /api/patients/{id}/records/  →  add a record"""

    serializer_class = HealthRecordSerializer

    def get_queryset(self):
        patient = get_object_or_404(Patient, pk=self.kwargs["patient_id"])
        return HealthRecord.objects.filter(patient=patient).order_by("date")

    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, pk=self.kwargs["patient_id"])
        serializer.save(patient=patient)


@api_view(["POST"])
def predict_view(request, patient_id):
    """POST /api/patients/{id}/predict/

    Fetches the patient's health records and runs the CVD predictor.
    Returns prediction, probability, and SHAP explanation.
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    qs = HealthRecord.objects.filter(patient=patient).order_by("date")

    if not qs.exists():
        return Response(
            {"error": "No health records found for this patient."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    records = [
        {
            "id": patient.pk,
            "age": patient.age,
            "gender": patient.gender,
            "height": patient.height,
            "weight": patient.weight,
            "smoke": patient.smoke,
            "alco": patient.alco,
            "active": patient.active,
            "date": str(rec.date),
            "ap_hi": rec.ap_hi,
            "ap_lo": rec.ap_lo,
            "cholesterol": rec.cholesterol,
            "gluc": rec.gluc,
        }
        for rec in qs
    ]

    try:
        result = predict_from_records(records)
    except FileNotFoundError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(result)
