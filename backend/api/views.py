"""
API views for the clinical risk detection system.

Endpoints
---------
GET  /api/health/                           health check
GET  /api/patients/                         list patients (paginated, with search)
POST /api/patients/                         create patient
GET  /api/patients/{id}/                    retrieve patient
PUT  /api/patients/{id}/                    update patient
DELETE /api/patients/{id}/                  delete patient
GET  /api/patients/{id}/records/            list records for patient
POST /api/patients/{id}/records/            add record for patient
DELETE /api/patients/{id}/records/{rid}/    delete a record
POST /api/patients/{id}/predict/            trigger CVD prediction
GET  /api/patients/{id}/predictions/        list past predictions
"""

import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import HealthRecord, Patient, Prediction
from .serializers import HealthRecordSerializer, PatientSerializer, PredictionSerializer
from ml_api.cvd_predictor import predict_from_records, ModelNotAvailableError

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ok(data, status_code=status.HTTP_200_OK):
    """Wrap data in a standard success envelope."""
    return Response({"status": "success", "data": data}, status=status_code)


def _err(message, status_code=status.HTTP_400_BAD_REQUEST, details=None):
    """Wrap error in a standard error envelope."""
    payload = {"status": "error", "message": message}
    if details:
        payload["details"] = details
    return Response(payload, status=status_code)


# ── Health Check ──────────────────────────────────────────────────────────────

@api_view(["GET"])
def health_check(request):
    return _ok({"service": "AI Clinical Risk API", "version": "1.0.0"})


# ── Patients ──────────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
def patient_list(request):
    if request.method == "GET":
        qs = Patient.objects.all()
        # Simple search by name
        name = request.query_params.get("search", "").strip()
        if name:
            qs = qs.filter(name__icontains=name)

        # Manual pagination
        page_size = 20
        try:
            page = max(1, int(request.query_params.get("page", 1)))
        except (ValueError, TypeError):
            page = 1
        start = (page - 1) * page_size
        end = start + page_size
        total = qs.count()
        serializer = PatientSerializer(qs[start:end], many=True)
        return _ok({
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": serializer.data,
        })

    # POST
    serializer = PatientSerializer(data=request.data)
    if serializer.is_valid():
        patient = serializer.save()
        return _ok(PatientSerializer(patient).data, status.HTTP_201_CREATED)
    return _err("Validation failed", details=serializer.errors)


@api_view(["GET", "PUT", "DELETE"])
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == "GET":
        return _ok(PatientSerializer(patient).data)

    if request.method == "PUT":
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return _ok(serializer.data)
        return _err("Validation failed", details=serializer.errors)

    # DELETE
    patient.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Health Records ─────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
def record_list(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == "GET":
        records = patient.health_records.all()
        serializer = HealthRecordSerializer(records, many=True)
        return _ok(serializer.data)

    # POST
    serializer = HealthRecordSerializer(data=request.data)
    if serializer.is_valid():
        record = serializer.save(patient=patient)
        return _ok(HealthRecordSerializer(record).data, status.HTTP_201_CREATED)
    return _err("Validation failed", details=serializer.errors)


@api_view(["DELETE"])
def record_detail(request, pk, rid):
    patient = get_object_or_404(Patient, pk=pk)
    record = get_object_or_404(HealthRecord, pk=rid, patient=patient)
    record.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Prediction ─────────────────────────────────────────────────────────────────

@api_view(["POST"])
def predict(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    # Build records list from the patient's HealthRecord history
    health_records = list(patient.health_records.order_by("date"))

    if not health_records:
        return _err(
            "No health records found for this patient. "
            "Add at least one record before requesting a prediction.",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # Serialise records into the format expected by the ML pipeline
    records_payload = []
    for r in health_records:
        records_payload.append({
            "date": r.date.isoformat(),
            # Demographics come from the Patient profile
            "id": patient.pk,
            "age": patient.age,
            "gender": patient.gender,
            "height": patient.height,
            "weight": patient.weight,
            "smoke": int(patient.smoke),
            "alco": int(patient.alco),
            "active": int(patient.active),
            # Per-record vitals
            "ap_hi": r.ap_hi,
            "ap_lo": r.ap_lo,
            "cholesterol": r.cholesterol,
            "gluc": r.gluc,
        })

    try:
        result = predict_from_records(records_payload)
    except ModelNotAvailableError as exc:
        logger.error("CVD model not available for patient %s: %s", pk, exc)
        return _err(
            "The prediction model is currently unavailable. "
            "Please ensure the model file is configured correctly.",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception:
        logger.exception("Unexpected prediction error for patient %s", pk)
        return _err(
            "An unexpected error occurred during prediction.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Persist the prediction
    prediction_obj = Prediction.objects.create(
        patient=patient,
        prediction=result["prediction"],
        probability=result["probability"],
        data_type_used=result["data_type_used"],
        shap_values=result.get("shap_values"),
        shap_warning=result.get("shap_warning", ""),
        records_provided=len(health_records),
        records_used=result.get("records_used", len(health_records)),
    )

    return _ok(PredictionSerializer(prediction_obj).data, status.HTTP_201_CREATED)


@api_view(["GET"])
def prediction_list(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    predictions = patient.predictions.all()
    serializer = PredictionSerializer(predictions, many=True)
    return _ok(serializer.data)
