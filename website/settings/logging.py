import os

from .env import SENTRY_DSN, PRODUCTION, BASE_DIR

LOGGING = {
    "version": 1,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
    },
}

if SENTRY_DSN:
    # Load Sentry at the start to capture as many errors as possible
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment="production" if PRODUCTION else "development",
        integrations=[DjangoIntegration()],
        send_default_pii=False,
        traces_sample_rate=0.1 if PRODUCTION else 1.0,
        profiles_sample_rate=0.1 if PRODUCTION else 1.0,
        project_root=str(BASE_DIR),
    )
