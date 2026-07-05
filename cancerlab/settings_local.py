"""
settings_local.py — Ambiente de DESENVOLVIMENTO LOCAL
Usa SQLite (sem PostgreSQL) e e-mail no console.
Não precisa de .env nem de nenhuma variável de ambiente configurada.

Uso:
  python manage.py runserver --settings=cancerlab.settings_local
  python manage.py migrate  --settings=cancerlab.settings_local

Ou exporte uma vez no terminal:
  export DJANGO_SETTINGS_MODULE=cancerlab.settings_local
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "local-dev-secret-key-nao-usar-em-producao"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.public",
    "apps.accounts",
    "apps.bookings",
    "apps.internal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cancerlab.urls"

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
                "apps.public.context_processors.navbar_context",
            ],
        },
    },
]

WSGI_APPLICATION = "cancerlab.wsgi.application"

# ── BANCO: SQLite local — zero configuração ──────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_local.sqlite3",   # arquivo separado do de produção
    }
}

# ── Auth ─────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.InternalUser"
AUTHENTICATION_BACKENDS = ["apps.accounts.backends.CPFBackend"]
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/interno/"
LOGOUT_REDIRECT_URL = "/"

AUTH_PASSWORD_VALIDATORS = []   # sem validação de senha em dev

# ── I18n ─────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ── Arquivos estáticos ────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Em dev use o storage simples (sem hash de manifesto — mais rápido)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Sessões ───────────────────────────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 8

# ── E-MAIL: imprime no terminal em vez de enviar ──────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ADMIN_EMAIL = "admin@local.dev"
LAB_EMAIL = "lab@local.dev"
APP_BASE_URL = "http://localhost:8000"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Upload TCLE ───────────────────────────────────────────────────────────────
TCLE_UPLOAD_DIR = BASE_DIR / "media" / "tcle_uploads"
TCLE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# No SQLite local, criamos as tabelas via migrations para poder testar.
DB_MANAGED = True
