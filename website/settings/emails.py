import os

ADMINS = [item.split(":", 1) for item in os.environ.get("ADMINS", "").split(",")]

DEFAULT_FROM_EMAIL = SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "") or os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
# 0 is OK cf. https://github.com/python/cpython/blob/024ac542/Lib/smtplib.py#L1016
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 0))
EMAIL_USE_TLS = bool(int(os.environ.get("EMAIL_USE_TLS", 0)))
EMAIL_USE_SSL = bool(int(os.environ.get("EMAIL_USE_SSL", 0)))
