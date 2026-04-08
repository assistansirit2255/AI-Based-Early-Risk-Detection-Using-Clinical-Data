from django.db import models


class Patient(models.Model):
    """Represents a patient in the system."""

    GENDER_CHOICES = [
        (0, 'Female'),
        (1, 'Male'),
    ]

    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.IntegerField(choices=GENDER_CHOICES)
    height = models.FloatField(help_text='Height in centimetres')
    weight = models.FloatField(help_text='Weight in kilograms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} (id={self.pk})'


class HealthRecord(models.Model):
    """A single clinical measurement snapshot linked to a Patient."""

    CHOLESTEROL_CHOICES = [
        (1, 'Normal'),
        (2, 'Above normal'),
        (3, 'Well above normal'),
    ]
    GLUCOSE_CHOICES = [
        (1, 'Normal'),
        (2, 'Above normal'),
        (3, 'Well above normal'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='health_records')
    recorded_on = models.DateField(help_text='Date of clinical measurement')
    age = models.IntegerField(help_text='Patient age at time of measurement (years)')
    ap_hi = models.IntegerField(help_text='Systolic blood pressure (mmHg)')
    ap_lo = models.IntegerField(help_text='Diastolic blood pressure (mmHg)')
    cholesterol = models.IntegerField(choices=CHOLESTEROL_CHOICES, default=1)
    gluc = models.IntegerField(choices=GLUCOSE_CHOICES, default=1)
    smoke = models.BooleanField(default=False)
    alco = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['recorded_on']

    def __str__(self):
        return f'Record for {self.patient.name} on {self.recorded_on}'
