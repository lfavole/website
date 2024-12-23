import os
import re
from urllib.parse import quote, urlparse

from django.core.files.storage import default_storage
from django.utils.functional import lazy
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
        "https://cdn.tiny.cloud",
        # https://docs.hcaptcha.com/#content-security-policy-settings
        "https://hcaptcha.com",
        "https://*.hcaptcha.com",
    ],
    "frame-src": [
        "self",
        # https://docs.hcaptcha.com/#content-security-policy-settings
        "https://hcaptcha.com",
        "https://*.hcaptcha.com",
        "https://www.youtube.com",
        "https://www.youtube-nocookie.com",
    ],
    "img-src": [
        "self",
        lazy(lambda: getattr(default_storage, "_prefix", ""), str)(),
    ],
    "style-src": [
        "self",
        "https://cdn.jsdelivr.net",
        "https://cdn.tiny.cloud",
        # https://docs.hcaptcha.com/#content-security-policy-settings
        "https://hcaptcha.com",
        "https://*.hcaptcha.com",
    ],
    "connect-src": [
        "self",
        # https://docs.hcaptcha.com/#content-security-policy-settings
        "https://hcaptcha.com",
        "https://*.hcaptcha.com",
    ],
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

# hCaptcha

HCAPTCHA_PUBLIC_KEY = os.environ.get("HCAPTCHA_PUBLIC_KEY")
HCAPTCHA_PRIVATE_KEY = os.environ.get("HCAPTCHA_PRIVATE_KEY")
