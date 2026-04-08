"""URL patterns for the api app."""

from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path("health/", views.health_check, name="health-check"),

    # Patients
    path("patients/", views.patient_list, name="patient-list"),
    path("patients/<int:pk>/", views.patient_detail, name="patient-detail"),

    # Health Records
    path("patients/<int:pk>/records/", views.record_list, name="record-list"),
    path("patients/<int:pk>/records/<int:rid>/", views.record_detail, name="record-detail"),

    # Predictions
    path("patients/<int:pk>/predict/", views.predict, name="predict"),
    path("patients/<int:pk>/predictions/", views.prediction_list, name="prediction-list"),
]
