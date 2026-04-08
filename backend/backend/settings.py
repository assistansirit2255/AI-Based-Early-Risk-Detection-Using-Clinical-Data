"""
Django settings for backend project.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-me-in-production-use-env-var",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1").split()

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "corsheaders",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "backend.urls"

WSGI_APPLICATION = "backend.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# Allow React dev server during local development
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173 http://127.0.0.1:5173",
).split()

CORS_ALLOW_ALL_ORIGINS = DEBUG

# ML model paths (relative to repository root, one level up from this file)
REPO_ROOT = BASE_DIR.parent
CVD_MODEL_PATH = os.environ.get("CVD_MODEL_PATH", str(REPO_ROOT / "cvd" / "cvd_model.pkl"))
CVD_FEATURE_COLUMNS_PATH = os.environ.get(
    "CVD_FEATURE_COLUMNS_PATH", str(REPO_ROOT / "cvd" / "feature_columns.pkl")
)
CVD_BACKGROUND_CSV = os.environ.get(
    "CVD_BACKGROUND_CSV", str(REPO_ROOT / "cvd" / "cleaned_cardio_data.csv")
)
