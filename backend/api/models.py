"""
Database models for the clinical API.

Patient     – demographic profile of a patient
HealthRecord – time-series clinical measurement for a patient
Prediction   – stored result of an ML prediction run
"""

from django.db import models


class Patient(models.Model):
    GENDER_CHOICES = [(1, "Male"), (2, "Female")]

    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(help_text="Age in years")
    gender = models.IntegerField(choices=GENDER_CHOICES, help_text="1=Male, 2=Female")
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    smoke = models.BooleanField(default=False, help_text="Smoker?")
    alco = models.BooleanField(default=False, help_text="Alcohol consumer?")
    active = models.BooleanField(default=True, help_text="Physically active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Patient #{self.pk} – {self.name}"


class HealthRecord(models.Model):
    CHOLESTEROL_CHOICES = [
        (1, "Normal"),
        (2, "Above Normal"),
        (3, "Well Above Normal"),
    ]
    GLUCOSE_CHOICES = [
        (1, "Normal"),
        (2, "Above Normal"),
        (3, "Well Above Normal"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="health_records"
    )
    date = models.DateField(help_text="Date of measurement")
    ap_hi = models.FloatField(
        help_text="Systolic blood pressure (mmHg)"
    )
    ap_lo = models.FloatField(
        help_text="Diastolic blood pressure (mmHg)"
    )
    cholesterol = models.IntegerField(
        choices=CHOLESTEROL_CHOICES,
        default=1,
        help_text="Cholesterol level: 1=Normal, 2=Above Normal, 3=Well Above Normal",
    )
    gluc = models.IntegerField(
        choices=GLUCOSE_CHOICES,
        default=1,
        help_text="Glucose level: 1=Normal, 2=Above Normal, 3=Well Above Normal",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"Record [{self.date}] for Patient #{self.patient_id}"


class Prediction(models.Model):
    DATA_TYPE_CHOICES = [("real", "Real"), ("hybrid", "Hybrid")]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="predictions"
    )
    prediction = models.IntegerField(help_text="0=Low Risk, 1=High Risk")
    probability = models.FloatField(help_text="Probability of high risk (0–1)")
    data_type_used = models.CharField(
        max_length=10,
        choices=DATA_TYPE_CHOICES,
        default="real",
        help_text="Whether real or hybrid (synthetic) data was used",
    )
    shap_values = models.JSONField(
        null=True, blank=True, help_text="SHAP feature attributions dict or null"
    )
    shap_warning = models.TextField(
        blank=True, default="", help_text="Warning message if SHAP could not be computed"
    )
    records_used = models.IntegerField(
        default=0, help_text="Number of records used (after normalization)"
    )
    records_provided = models.IntegerField(
        default=0, help_text="Number of records originally provided"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = "High Risk" if self.prediction == 1 else "Low Risk"
        return f"Prediction [{label}] for Patient #{self.patient_id}"


class DiabetesRecord(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="diabetes_records"
    )
    date = models.DateField(help_text="Date of measurement")
    pregnancies = models.IntegerField(default=0, help_text="Number of pregnancies")
    glucose = models.FloatField(help_text="Glucose level (mg/dL)")
    blood_pressure = models.FloatField(help_text="Blood pressure (mmHg)")
    skin_thickness = models.FloatField(help_text="Skin thickness (mm)")
    insulin = models.FloatField(help_text="Insulin level")
    bmi = models.FloatField(help_text="Body Mass Index")
    diabetes_pedigree_function = models.FloatField(help_text="Diabetes pedigree function")
    age = models.IntegerField(help_text="Age in years")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Diabetes Record [{self.date}] for Patient #{self.patient_id}"


class DiabetesPrediction(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="diabetes_predictions"
    )
    record = models.ForeignKey(
        DiabetesRecord, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="predictions"
    )
    prediction = models.IntegerField(help_text="0=Low Risk, 1=High Risk")
    probability = models.FloatField(help_text="Probability of high risk (0-1)")
    shap_values = models.JSONField(
        null=True, blank=True, help_text="SHAP feature attributions dict or null"
    )
    shap_warning = models.TextField(
        blank=True, default="", help_text="Warning message if SHAP could not be computed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = "High Risk" if self.prediction == 1 else "Low Risk"
        return f"Diabetes Prediction [{label}] for Patient #{self.patient_id}"
