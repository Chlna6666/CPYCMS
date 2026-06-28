# -*- coding: utf-8 -*-
"""CPYCMS - Django 配置。"""

from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[2]


def env_bool(name, default=False):
    """读取布尔环境变量。"""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() in {'1', 'true', 'yes', 'on'}


def env_int(name, default, min_value=None):
    """读取整数环境变量。"""
    try:
        value = int(os.environ.get(name, default))
    except (TypeError, ValueError):
        value = default
    if min_value is not None:
        value = max(min_value, value)
    return value


SECRET_KEY = os.environ.get('SECRET_KEY', 'cpycms-secret-key-change-me')
DEBUG = env_bool('CPYCMS_DEBUG', False)
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('CPYCMS_ALLOWED_HOSTS', '*').split(',') if host.strip()]
USE_X_FORWARDED_HOST = env_bool('CPYCMS_USE_X_FORWARDED_HOST', False)
if env_bool('CPYCMS_TRUST_PROXY_HEADERS', False):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'backend.apps.accounts.apps.AccountsConfig',
    'backend.apps.cms.apps.CmsConfig',
    'backend.apps.common.apps.CommonConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'backend.apps.common.csrf.DynamicCsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'backend.apps.common.middleware.RequestLogMiddleware',
]

ROOT_URLCONF = 'backend.config.urls'
WSGI_APPLICATION = 'backend.config.wsgi.application'
ASGI_APPLICATION = 'backend.config.asgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DEFAULT_DATABASE_FILE = BASE_DIR / 'cpycms.db'
FALLBACK_DATABASE_FILE = BASE_DIR / 'cpycms-django.db'
DATABASE_FILE = os.environ.get(
    'CPYCMS_DATABASE_FILE',
    str(FALLBACK_DATABASE_FILE if FALLBACK_DATABASE_FILE.exists() else DEFAULT_DATABASE_FILE),
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_FILE,
        'OPTIONS': {
            'timeout': max(1, env_int('CPYCMS_SQLITE_BUSY_TIMEOUT_MS', 5000, 1000) / 1000),
        },
    }
}

AUTH_USER_MODEL = 'accounts.User'
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = False
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
FRONTEND_DIR = Path(os.environ.get('CPYCMS_FRONTEND_DIR', str(BASE_DIR / 'frontend')))
FRONTEND_DIST = Path(os.environ.get('CPYCMS_FRONTEND_DIST', str(BASE_DIR / 'frontend' / 'dist')))
FRONTEND_DEV_SERVER_URL = os.environ.get('CPYCMS_FRONTEND_DEV_SERVER_URL', 'http://127.0.0.1:3000').rstrip('/')
USE_VITE_DEV_SERVER = DEBUG and env_bool('CPYCMS_USE_VITE_DEV_SERVER', True)
AUTO_START_VITE = DEBUG and env_bool('CPYCMS_AUTO_START_VITE', True)
VITE_STARTUP_TIMEOUT = env_int('CPYCMS_VITE_STARTUP_TIMEOUT', 20, 1)
MEDIA_URL = '/uploads/'
MEDIA_ROOT = Path(os.environ.get('CPYCMS_UPLOAD_FOLDER', str(BASE_DIR / 'uploads')))
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CPYCMS_CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1:3000,http://localhost:3000').split(',')
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'backend.apps.common.authentication.SafeSessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

MAX_UPLOAD_SIZE = 16 * 1024 * 1024
ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_RESOURCE_EXT = {'pdf', 'zip', 'rar', '7z', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md'}
SQLITE_CACHE_KB = env_int('CPYCMS_SQLITE_CACHE_KB', 20000, 1024)
REFRESH_SEARCH_INDEX_ON_STARTUP = env_bool('CPYCMS_REFRESH_SEARCH_INDEX_ON_STARTUP', False)
