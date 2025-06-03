import os
from .base import *  # noqa


# * GENERAL
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "labs.mosquitoalert.com").split(",")  # noqa: F405


# * API Settings
# -------------------------------------------------------------------------------

# Spectacular settings
SPECTACULAR_SETTINGS["SERVERS"] = [  # noqa: F405
    {"url": "https://labs.mosquitoalert.com/anomaly_detection", "description": "Production server"}
]
