import os
from pathlib import Path
from decouple import Config, RepositoryEnv, config as config_env

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# En local las credenciales vienen del .env de la raiz; en produccion,
# de las variables de entorno del servidor
_env_file = ROOT_DIR / '.env'
config = Config(RepositoryEnv(_env_file)) if _env_file.exists() else config_env

# En local apunta al contenedor de Docker; en produccion, al servicio
# de OSRM desplegado
OSRM_URL = config('OSRM_URL', default='http://127.0.0.1:5000')

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)


ALLOWED_HOSTS = ['*'] if DEBUG else ['127.0.0.1', 'localhost']

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    # Apps del proyecto
    'usuarios',
    'establecimientos',
    'visitas',
    'productos',
    'inventario',
    'rutas',
    'entregas',
    'reportes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ROOT_DIR / 'client' / 'templates'],
        'APP_DIRS': False,
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

WSGI_APPLICATION = 'config.wsgi.application'

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            # La base está en la nube y corre en UTC: se fija la zona de
            # Tijuana para que CURDATE() coincida con el día local
            'init_command': "SET time_zone = '-07:00'",
        },
    }
}

# Contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Tijuana'
USE_I18N = True
USE_TZ = False


MEDIA_URL = '/media/'
MEDIA_ROOT = ROOT_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# Desactiva la verificación de versión de MariaDB
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

# Desactiva la sintaxis RETURNING para MariaDB 10.4
DatabaseFeatures.can_return_columns_from_insert = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(ROOT_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(ROOT_DIR, 'client', 'static'),
]
# Sin manifiesto: los CSS de terceros (Leaflet, Boxicons) referencian
# imágenes y fuentes que no se descargaron, y el modo con manifiesto
# falla al no encontrarlas
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Railway asigna el dominio en tiempo de ejecución
CSRF_TRUSTED_ORIGINS = [
    'https://*.up.railway.app',
]