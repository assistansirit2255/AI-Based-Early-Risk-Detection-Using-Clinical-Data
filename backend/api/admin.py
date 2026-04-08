from django.contrib import admin
from .models import Patient, HealthRecord, Prediction


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "age", "gender", "created_at"]
    search_fields = ["name"]


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "patient", "date", "ap_hi", "ap_lo", "cholesterol", "gluc"]
    list_filter = ["patient"]


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "patient", "prediction", "probability", "data_type_used", "created_at"
    ]
    list_filter = ["prediction", "data_type_used"]
