"""Django settings for AutoLab project.

Generated for AutoLab automation educational platform.
"""

from pathlib import Path
from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="django-insecure-chave-de-desenvolvimento-local-autolab",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=Csv(),
)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config("DJANGO_CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
    if origin.strip()
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # AutoLab apps
    "core.apps.CoreConfig",
    "laboratorios.apps.LaboratoriosConfig",
    "exercicios.apps.ExerciciosConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database
# Default: SQLite in local environment
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "var" / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# AutoLab Specific Settings
RESULTS_ROOT = Path(config("RESULTS_ROOT", default=str(BASE_DIR / "var" / "results")))
RESULT_TTL_MINUTES = config("RESULT_TTL_MINUTES", default=30, cast=int)

# ZIP Upload & Processing limits
MAX_ZIP_UPLOAD_BYTES = config("MAX_ZIP_UPLOAD_BYTES", default=10 * 1024 * 1024, cast=int)  # 10 MiB
MAX_ZIP_ENTRIES = config("MAX_ZIP_ENTRIES", default=100, cast=int)
MAX_ZIP_UNCOMPRESSED_BYTES = config("MAX_ZIP_UNCOMPRESSED_BYTES", default=50 * 1024 * 1024, cast=int)  # 50 MiB
MAX_ZIP_ENTRY_BYTES = config("MAX_ZIP_ENTRY_BYTES", default=10 * 1024 * 1024, cast=int)  # 10 MiB

# Spreadsheet limits
MAX_SPREADSHEET_ROWS = config("MAX_SPREADSHEET_ROWS", default=10000, cast=int)
MAX_SPREADSHEET_COLUMNS = config("MAX_SPREADSHEET_COLUMNS", default=30, cast=int)
MAX_SPREADSHEET_UPLOAD_BYTES = config("MAX_SPREADSHEET_UPLOAD_BYTES", default=20 * 1024 * 1024, cast=int)  # 20 MiB

# AI Integration settings
LLM_ENABLED = config("LLM_ENABLED", default=False, cast=bool)
LLM_API_KEY = config("LLM_API_KEY", default="")
LLM_MODEL = config("LLM_MODEL", default="")
