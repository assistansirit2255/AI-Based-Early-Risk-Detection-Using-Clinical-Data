from django.urls import path
from .views import PatientListCreateView, HealthRecordListCreateView, predict_view

urlpatterns = [
    path("patients/", PatientListCreateView.as_view(), name="patient-list-create"),
    path(
        "patients/<int:patient_id>/records/",
        HealthRecordListCreateView.as_view(),
        name="health-record-list-create",
    ),
    path("patients/<int:patient_id>/predict/", predict_view, name="predict"),
]
