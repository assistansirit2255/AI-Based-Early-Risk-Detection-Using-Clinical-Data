import logging

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HealthRecord, Patient
from .serializers import HealthRecordSerializer, PatientSerializer

logger = logging.getLogger(__name__)


class PatientCreateView(generics.CreateAPIView):
    """POST /api/patients/ — Register a new patient."""

    serializer_class = PatientSerializer
    queryset = Patient.objects.all()


class HealthRecordCreateView(generics.CreateAPIView):
    """POST /api/health-records/ — Add a health record for a patient."""

    serializer_class = HealthRecordSerializer
    queryset = HealthRecord.objects.all()


class PatientHistoryView(generics.ListAPIView):
    """GET /api/patients/<pk>/history/ — Paginated list of health records for a patient."""

    serializer_class = HealthRecordSerializer

    def get_queryset(self):
        patient_pk = self.kwargs['pk']
        if not Patient.objects.filter(pk=patient_pk).exists():
            return HealthRecord.objects.none()
        return HealthRecord.objects.filter(patient_id=patient_pk).order_by('recorded_on')

    def list(self, request, *args, **kwargs):
        patient_pk = self.kwargs['pk']
        if not Patient.objects.filter(pk=patient_pk).exists():
            return Response(
                {'error': f'Patient with id={patient_pk} does not exist.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().list(request, *args, **kwargs)


class CVDPredictView(APIView):
    """
    POST /api/patients/<pk>/predict/

    Run CVD risk prediction for the patient using all their stored health records.
    Returns prediction label, probability, and SHAP explanation.
    """

    def post(self, request, pk):
        # Validate patient exists
        try:
            patient = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return Response(
                {'error': f'Patient with id={pk} does not exist.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        records_qs = HealthRecord.objects.filter(patient=patient).order_by('recorded_on')
        if not records_qs.exists():
            return Response(
                {'error': 'No health records found for this patient. Add records before predicting.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serialize records into plain dicts, adding patient-level static fields
        serializer = HealthRecordSerializer(records_qs, many=True)
        records = serializer.data

        # Inject patient-level static features (gender, height, weight) into each record
        patient_static = {
            'gender': patient.gender,
            'height': patient.height,
            'weight': patient.weight,
        }
        enriched = []
        for rec in records:
            merged = dict(rec)
            merged.update(patient_static)
            enriched.append(merged)

        # Run ML prediction
        try:
            from ml_api.cvd_predictor import predict_from_records  # noqa: PLC0415

            result = predict_from_records(enriched)
        except FileNotFoundError as exc:
            logger.error('Model artifact missing: %s', exc)
            return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            logger.exception('Prediction error for patient %s', pk)
            return Response(
                {'error': f'Prediction failed: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        label = 'High Risk' if result['prediction'] == 1 else 'Low Risk'
        return Response(
            {
                'patient_id': pk,
                'patient_name': patient.name,
                'prediction': result['prediction'],
                'prediction_label': label,
                'probability': result['probability'],
                'shap_values': result['shap_values'],
            },
            status=status.HTTP_200_OK,
        )
