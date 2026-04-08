from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.IntegerField(
        choices=[(0, "Female"), (1, "Male")],
        help_text="0 = Female, 1 = Male",
    )
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    smoke = models.IntegerField(default=0, choices=[(0, "No"), (1, "Yes")])
    alco = models.IntegerField(default=0, choices=[(0, "No"), (1, "Yes")])
    active = models.IntegerField(default=1, choices=[(0, "No"), (1, "Yes")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (id={self.pk})"


class HealthRecord(models.Model):
    CHOLESTEROL_CHOICES = [(1, "Normal"), (2, "Above Normal"), (3, "Well Above Normal")]
    GLUC_CHOICES = [(1, "Normal"), (2, "Above Normal"), (3, "Well Above Normal")]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="records")
    date = models.DateField()
    ap_hi = models.FloatField(help_text="Systolic blood pressure")
    ap_lo = models.FloatField(help_text="Diastolic blood pressure")
    cholesterol = models.IntegerField(choices=CHOLESTEROL_CHOICES, help_text="1/2/3 level")
    gluc = models.IntegerField(choices=GLUC_CHOICES, help_text="1/2/3 level")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"Record for patient {self.patient_id} on {self.date}"
