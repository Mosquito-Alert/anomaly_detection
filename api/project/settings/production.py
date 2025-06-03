import os
from .base import *  # noqa
from .base import DATABASES  # noqa: F401


# * GENERAL
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "api.mosquitoalert.com").split(",")  # noqa: F405
DEBUG = False

# * DATABASES
# ------------------------------------------------------------------------------
DATABASES['default']['USER'] = os.environ.get('POSTGRES_USER')  # noqa: F405
DATABASES['default']['PASSWORD'] = os.environ.get('POSTGRES_PASSWORD')  # noqa: F405

# * LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}

# * API Settings
# -------------------------------------------------------------------------------

# Spectacular settings
SPECTACULAR_SETTINGS["SERVERS"] = [  # noqa: F405
    {"url": "https://api.mosquitoalert.com/v1/anomaly_detection", "description": "Production server"}
]
