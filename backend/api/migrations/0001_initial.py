from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("age", models.PositiveIntegerField()),
                (
                    "gender",
                    models.IntegerField(
                        choices=[(0, "Female"), (1, "Male")],
                        help_text="0 = Female, 1 = Male",
                    ),
                ),
                ("height", models.FloatField(help_text="Height in cm")),
                ("weight", models.FloatField(help_text="Weight in kg")),
                ("smoke", models.IntegerField(choices=[(0, "No"), (1, "Yes")], default=0)),
                ("alco", models.IntegerField(choices=[(0, "No"), (1, "Yes")], default=0)),
                ("active", models.IntegerField(choices=[(0, "No"), (1, "Yes")], default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="HealthRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="records",
                        to="api.patient",
                    ),
                ),
                ("date", models.DateField()),
                ("ap_hi", models.FloatField(help_text="Systolic blood pressure")),
                ("ap_lo", models.FloatField(help_text="Diastolic blood pressure")),
                (
                    "cholesterol",
                    models.IntegerField(
                        choices=[(1, "Normal"), (2, "Above Normal"), (3, "Well Above Normal")],
                        help_text="1/2/3 level",
                    ),
                ),
                (
                    "gluc",
                    models.IntegerField(
                        choices=[(1, "Normal"), (2, "Above Normal"), (3, "Well Above Normal")],
                        help_text="1/2/3 level",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["date"]},
        ),
    ]
