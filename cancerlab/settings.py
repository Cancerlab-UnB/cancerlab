# cancerlab/settings.py
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# ---------------------------------------------------------------------------
# Deploy atrás de proxy HTTPS (Railway/Render/Heroku)
# ---------------------------------------------------------------------------
# Necessário para os formulários (login, agendamento, aprovação) não caírem em
# erro 403 de CSRF quando servidos via HTTPS no domínio do Railway.
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://*.railway.app,https://*.up.railway.app",
    cast=Csv(),
)
# O proxy do Railway encerra o TLS e encaminha via HTTP com este cabeçalho;
# isto faz o Django reconhecer a requisição como segura (HTTPS).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # apps do projeto
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

# ---------------------------------------------------------------------------
# Banco de dados – PostgreSQL (MESMA instância Railway do app Streamlit)
# ---------------------------------------------------------------------------
# O padrão aponta para o MESMO banco Railway usado pelo Streamlit, para que
# login interno, usuários externos e agendamentos compartilhem os dados.
# Pode ser sobrescrito via variável de ambiente DATABASE_URL.
_DEFAULT_RAILWAY_URL = (
    "postgresql+psycopg2://postgres:nDxPchIFBWnEZercIqUuEDwxTZsLNBcL"
    "@switchback.proxy.rlwy.net:37511/railway"
)
_DB_URL = config("DATABASE_URL", default=_DEFAULT_RAILWAY_URL)

if _DB_URL:
    # PostgreSQL remoto ou local configurado (Railway, Supabase, etc.)
    import re as _re
    _m = _re.match(
        r"(?:postgresql\+psycopg2|postgres(?:ql)?)://([^:]*):?([^@]*)@([^:/]+):?(\d*)/(.+)",
        _DB_URL,
    )
    if _m:
        _user, _pass, _host, _port, _dbname = _m.groups()
    else:
        _user, _pass, _host, _port, _dbname = "postgres", "", "localhost", "5432", "cancerlab"

    # SSL apenas para hosts remotos; localmente o PostgreSQL nao aceita SSL
    _is_local = _host in ("localhost", "127.0.0.1", "::1", "")
    _ssl_opts  = {} if _is_local else {"sslmode": "require"}

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _dbname,
            "USER": _user,
            "PASSWORD": _pass,
            "HOST": _host,
            "PORT": _port or "5432",
            "CONN_MAX_AGE": 600,
            "OPTIONS": _ssl_opts,
        }
    }
else:
    # Fallback: SQLite para testes locais sem PostgreSQL configurado
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Custom user model
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.InternalUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "apps.accounts.backends.CPFBackend",
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/interno/"
LOGOUT_REDIRECT_URL = "/"

# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Arquivos estáticos e de mídia
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Sessões
# ---------------------------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 8   # 8 horas
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# ---------------------------------------------------------------------------
# E-mail / SMTP
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("SMTP_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("SMTP_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("SMTP_USER", default="")
EMAIL_HOST_PASSWORD = config("SMTP_PASS", default="")
DEFAULT_FROM_EMAIL = f"CancerLab – No Reply <{EMAIL_HOST_USER}>"

ADMIN_EMAIL = config("ADMIN_EMAIL", default="victor.fleck906438@gmail.com")
LAB_EMAIL = config("LAB_EMAIL", default="cancerlab@unb.br")
APP_BASE_URL = config("APP_BASE_URL", default="http://localhost:8000")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Upload de arquivos TCLE
# ---------------------------------------------------------------------------
TCLE_UPLOAD_DIR = BASE_DIR / "media" / "tcle_uploads"
TCLE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Modelos que espelham tabelas já criadas pelo Streamlit no Railway.
# Em produção elas NÃO devem ser gerenciadas pelo Django (managed=False).
DB_MANAGED = config("DB_MANAGED", default=False, cast=bool)
