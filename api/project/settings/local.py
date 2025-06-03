from .base import *  # noqa
from .base import DATABASES  # noqa: F401
import os


# * GENERAL
# ------------------------------------------------------------------------------
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'localhost:8000', 'http://localhost:8000', 'http://localhost']
ALLOWED_HOSTS = ['*']


# * DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES['default']['USER'] = os.environ.get('POSTGRES_USER', 'anomaly_detection_user')  # noqa: F405
DATABASES['default']['PASSWORD'] = os.environ.get(
    'POSTGRES_PASSWORD',
    'insecure_password_for_local_development')  # noqa: F405


# * Silk
INSTALLED_APPS += ["silk"]  # noqa: F405
MIDDLEWARE = ['silk.middleware.SilkyMiddleware'] + MIDDLEWARE  # noqa: F405
