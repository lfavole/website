# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

import os
import dj_database_url

from .env import PRODUCTION


DATABASES = {
    # POSTGRES_URL is put by Vercel
    "default": dj_database_url.config(default=os.environ.get("POSTGRES_URL")),
}

CACHES = {
    "default": {
        "BACKEND": (
            "django.core.cache.backends.db.DatabaseCache"
            if PRODUCTION
            else "django.core.cache.backends.locmem.LocMemCache"
        ),
        "LOCATION": "cache",
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
