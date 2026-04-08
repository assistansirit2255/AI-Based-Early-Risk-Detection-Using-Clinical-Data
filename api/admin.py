from django.contrib import admin

from .models import HealthRecord, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date_of_birth', 'gender', 'height', 'weight', 'created_at']
    search_fields = ['name']


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'recorded_on', 'age', 'ap_hi', 'ap_lo', 'cholesterol']
    list_filter = ['cholesterol', 'smoke', 'alco', 'active']
    search_fields = ['patient__name']
