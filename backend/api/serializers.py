"""DRF serializers for Patient, HealthRecord, and Prediction models."""

from rest_framework import serializers
from .models import Patient, HealthRecord, Prediction, DiabetesRecord, DiabetesPrediction


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id", "name", "age", "gender", "height", "weight",
            "smoke", "alco", "active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_age(self, value):
        if value < 1 or value > 120:
            raise serializers.ValidationError("Age must be between 1 and 120.")
        return value

    def validate_gender(self, value):
        if value not in (1, 2):
            raise serializers.ValidationError("Gender must be 1 (Male) or 2 (Female).")
        return value

    def validate_height(self, value):
        if value < 50 or value > 250:
            raise serializers.ValidationError("Height must be between 50 and 250 cm.")
        return value

    def validate_weight(self, value):
        if value < 10 or value > 400:
            raise serializers.ValidationError("Weight must be between 10 and 400 kg.")
        return value


class HealthRecordSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = HealthRecord
        fields = [
            "id", "patient_id", "date", "ap_hi", "ap_lo",
            "cholesterol", "gluc", "created_at",
        ]
        read_only_fields = ["id", "patient_id", "created_at"]

    def validate_ap_hi(self, value):
        if value < 60 or value > 300:
            raise serializers.ValidationError(
                "Systolic BP (ap_hi) must be between 60 and 300 mmHg."
            )
        return value

    def validate_ap_lo(self, value):
        if value < 40 or value > 200:
            raise serializers.ValidationError(
                "Diastolic BP (ap_lo) must be between 40 and 200 mmHg."
            )
        return value

    def validate_cholesterol(self, value):
        if value not in (1, 2, 3):
            raise serializers.ValidationError("Cholesterol must be 1, 2, or 3.")
        return value

    def validate_gluc(self, value):
        if value not in (1, 2, 3):
            raise serializers.ValidationError("Glucose (gluc) must be 1, 2, or 3.")
        return value

    def validate(self, data):
        ap_hi = data.get("ap_hi")
        ap_lo = data.get("ap_lo")
        if ap_hi is not None and ap_lo is not None and ap_lo >= ap_hi:
            raise serializers.ValidationError(
                "Diastolic BP (ap_lo) must be less than systolic BP (ap_hi)."
            )
        return data


class PredictionSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(read_only=True)
    risk_label = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = [
            "id", "patient_id", "prediction", "risk_label", "probability",
            "data_type_used", "shap_values", "shap_warning",
            "records_used", "records_provided", "created_at",
        ]
        read_only_fields = fields

    def get_risk_label(self, obj):
        return "High Risk" if obj.prediction == 1 else "Low Risk"


class DiabetesRecordSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = DiabetesRecord
        fields = [
            "id", "patient_id", "date", "pregnancies", "glucose",
            "blood_pressure", "skin_thickness", "insulin", "bmi",
            "diabetes_pedigree_function", "age", "created_at",
        ]
        read_only_fields = ["id", "patient_id", "created_at"]

    def validate_pregnancies(self, value):
        if value < 0 or value > 20:
            raise serializers.ValidationError("Pregnancies must be between 0 and 20.")
        return value

    def validate_glucose(self, value):
        if value < 40 or value > 400:
            raise serializers.ValidationError("Glucose must be between 40 and 400.")
        return value

    def validate_blood_pressure(self, value):
        if value < 40 or value > 200:
            raise serializers.ValidationError("Blood pressure must be between 40 and 200.")
        return value

    def validate_skin_thickness(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Skin thickness must be between 0 and 100.")
        return value

    def validate_insulin(self, value):
        if value < 0 or value > 1000:
            raise serializers.ValidationError("Insulin must be between 0 and 1000.")
        return value

    def validate_bmi(self, value):
        if value < 10 or value > 70:
            raise serializers.ValidationError("BMI must be between 10 and 70.")
        return value

    def validate_diabetes_pedigree_function(self, value):
        if value < 0 or value > 3:
            raise serializers.ValidationError("Diabetes pedigree function must be between 0 and 3.")
        return value

    def validate_age(self, value):
        if value < 1 or value > 120:
            raise serializers.ValidationError("Age must be between 1 and 120.")
        return value


class DiabetesPredictionSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(read_only=True)
    record_id = serializers.IntegerField(read_only=True)
    risk_label = serializers.SerializerMethodField()

    class Meta:
        model = DiabetesPrediction
        fields = [
            "id", "patient_id", "record_id", "prediction", "risk_label",
            "probability", "shap_values", "shap_warning", "created_at",
        ]
        read_only_fields = fields

    def get_risk_label(self, obj):
        return "High Risk" if obj.prediction == 1 else "Low Risk"
