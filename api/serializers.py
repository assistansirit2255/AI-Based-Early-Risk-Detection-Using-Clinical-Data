from rest_framework import serializers

from .models import HealthRecord, Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'date_of_birth', 'gender', 'height', 'weight', 'created_at']
        read_only_fields = ['id', 'created_at']


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = [
            'id',
            'patient',
            'recorded_on',
            'age',
            'ap_hi',
            'ap_lo',
            'cholesterol',
            'gluc',
            'smoke',
            'alco',
            'active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        if attrs.get('ap_hi', 0) <= attrs.get('ap_lo', 0):
            raise serializers.ValidationError(
                'Systolic blood pressure (ap_hi) must be greater than diastolic blood pressure (ap_lo).'
            )
        return attrs
