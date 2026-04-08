"""
Django settings for backend project.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

_DEFAULT_SECRET = "django-insecure-change-me-in-production-use-env-var"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", _DEFAULT_SECRET)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# Fail fast in production if the default insecure key is still in use
if not DEBUG and SECRET_KEY == _DEFAULT_SECRET:
    raise RuntimeError(
        "DJANGO_SECRET_KEY environment variable must be set to a secure value in production."
    )

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

# CORS: always use an explicit allowlist; never blanket-allow all origins
_default_cors = "http://localhost:5173 http://127.0.0.1:5173"
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", _default_cors).split()

# ML model paths (relative to repository root, one level up from this file)
REPO_ROOT = BASE_DIR.parent
CVD_MODEL_PATH = os.environ.get("CVD_MODEL_PATH", str(REPO_ROOT / "cvd" / "cvd_model.pkl"))
CVD_FEATURE_COLUMNS_PATH = os.environ.get(
    "CVD_FEATURE_COLUMNS_PATH", str(REPO_ROOT / "cvd" / "feature_columns.pkl")
)
CVD_BACKGROUND_CSV = os.environ.get(
    "CVD_BACKGROUND_CSV", str(REPO_ROOT / "cvd" / "cleaned_cardio_data.csv")
)
