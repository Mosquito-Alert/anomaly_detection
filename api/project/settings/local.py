from .base import *  # noqa


# * GENERAL
# ------------------------------------------------------------------------------
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'localhost:8000', 'http://localhost:8000', 'http://localhost']
ALLOWED_HOSTS = ['*']


# * Silk
INSTALLED_APPS += ["silk"]  # noqa: F405
MIDDLEWARE = ['silk.middleware.SilkyMiddleware'] + MIDDLEWARE  # noqa: F405
