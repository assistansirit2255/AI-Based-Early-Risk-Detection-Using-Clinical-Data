from rest_framework import serializers
from .models import Patient, HealthRecord


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = ["id", "patient", "date", "ap_hi", "ap_lo", "cholesterol", "gluc", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {"patient": {"required": False}}

    def create(self, validated_data):
        # patient is injected by the view via perform_create / save()
        return super().create(validated_data)


class PatientSerializer(serializers.ModelSerializer):
    records = HealthRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "name",
            "age",
            "gender",
            "height",
            "weight",
            "smoke",
            "alco",
            "active",
            "created_at",
            "records",
        ]
        read_only_fields = ["id", "created_at", "records"]
