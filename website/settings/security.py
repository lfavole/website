import os
import re
from urllib.parse import quote, urlparse

from django.utils.translation import gettext_lazy as _

from .env import DEBUG, PRODUCTION, SENTRY_DSN, SENTRY_SDK

SECRET_KEY = os.environ.get("SECRET_KEY")

if not DEBUG:
    CONN_MAX_AGE = 600
    ALLOWED_HOSTS = os.environ.get("HOST", "").split(",")
    if PRODUCTION:
        CSRF_COOKIE_SECURE = True
        SESSION_COOKIE_SECURE = True
        SECURE_SSL_REDIRECT = True
else:
    ALLOWED_HOSTS = ["*"]

CSRF_USE_SESSIONS = True

# Content Security Policy
CONTENT_SECURITY_POLICY = {
    "block-all-mixed-content": True,
    "script-src": [
        "self",
        "unsafe-eval",
        "https://cdn.jsdelivr.net",
        "https://fonts.googleapis.com",
        "https://browser.sentry-cdn.com",
    ],
    "style-src": ["self", "https://cdn.jsdelivr.net"],
    "worker-src": ["self", "blob:"],
    "report-threshold": 0.1,
}

if SENTRY_SDK:
    parts = urlparse(SENTRY_SDK)
    CONTENT_SECURITY_POLICY["script-src"].append(f"{parts.scheme}://{parts.hostname}")

SENTRY_PUBLIC_KEY = os.getenv("SENTRY_PUBLIC_KEY")
if SENTRY_PUBLIC_KEY and SENTRY_DSN:
    match = re.match(r"^(https?://)(?:\w+@)?(\w+\.ingest(?:\.[a-z]+)?\.sentry\.io)/(\d+)", SENTRY_DSN)
    if match:
        CONTENT_SECURITY_POLICY["report-uri"] = (
            f"{match[1]}{match[2]}/api/{match[3]}/security/?sentry_key={quote(SENTRY_PUBLIC_KEY)}"
        )

COOKIE_TYPES = {
    "essential": (_("Essential"), True),
    "performance": (_("Performance"), False),
}

# reCAPTCHA

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
