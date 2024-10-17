import os

# Authentication settings
# https://docs.djangoproject.com/en/stable/ref/settings/#auth
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/accounts/login"
LOGIN_REDIRECT_URL = "/"

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "website.password_validation.PwnedPasswordValidator"},
]

# Allauth settings
# https://docs.allauth.org/en/stable/account/configuration.html
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_SIGNUP_FORM_CLASS = "users.forms.AllAuthSignupForm"
# we set the adapter to an adapter that changes the login form
ACCOUNT_ADAPTER = "users.adapter.Adapter"
ACCOUNT_EMAIL_NOTIFICATIONS = True

# https://docs.allauth.org/en/stable/socialaccount/configuration.html
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # the address that comes from Google (Gmail) is always verified,
        # so we can log in with it without prior linking
        "EMAIL_AUTHENTICATION": True,
        "APPS": [
            {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "secret": os.getenv("GOOGLE_SECRET"),
            },
        ],
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "offline",
        },
    },
    "github": {
        "APPS": [
            {
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "secret": os.getenv("GITHUB_SECRET"),
            },
        ],
        "SCOPE": [
            "user",
        ],
    },
    "telegram": {
        "APPS": [
            {
                "client_id": os.getenv("BOT_TOKEN", "").split(":")[0],
                "secret": os.getenv("BOT_TOKEN"),
            },
        ],
        "AUTH_PARAMS": {"auth_date_validity": 30},
    },
}

# https://docs.allauth.org/en/latest/mfa/configuration.html
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_SUPPORTED_TYPES = ["recovery_codes", "totp", "webauthn"]
WEBAUTHN_ALLOW_INSECURE_ORIGIN = True

USERSESSIONS_TRACK_ACTIVITY = True
