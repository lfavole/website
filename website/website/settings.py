"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from typing import Any, TypeVar

import custom_settings
import custom_settings_default
import custom_settings_test

_T = TypeVar("_T")

TEST = getattr(custom_settings, "TEST", False)


def get_custom_setting(key: str, default: _T = None) -> Any | _T:
    """
    Return the value of a custom setting.
    """
    ret = None
    if TEST:
        ret = getattr(custom_settings_test, key, default)
    else:
        ret = getattr(custom_settings, key, default)

    if ret is None:
        print(key, getattr(custom_settings_default, key, ret))
        return getattr(custom_settings_default, key, ret)
    print(key, ret)
    return ret


PYTHONANYWHERE = get_custom_setting("PYTHONANYWHERE")
OFFLINE = get_custom_setting("OFFLINE")
print(get_custom_setting("DB_HOST"))
print(getattr(custom_settings_default, "DB_HOST"))

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_custom_setting("SECRET_KEY") or "+jt!%+%erdp^y7h37v#68x31+u9ut6^8zryj@#zmu5p$_!u2)u"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_custom_setting("DEBUG")

if not DEBUG:
    CONN_MAX_AGE = 600
    ALLOWED_HOSTS = [get_custom_setting("HOST")]
    if PYTHONANYWHERE:
        CSRF_COOKIE_SECURE = True
        SESSION_COOKIE_SECURE = True
        SECURE_SSL_REDIRECT = True
else:
    ALLOWED_HOSTS = ["*"]

GITHUB_WEBHOOK_KEY = get_custom_setting("GITHUB_WEBHOOK_KEY")

# Application definition

INSTALLED_APPS = [
    # Django
    "admin_app",  # replaces django.contrib.admin
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # custom apps
    "adminsortable2",
    "django_cleanup",
    "easy_thumbnails",
    # apps with urls.py (automatic)
    *(dir.name for dir in BASE_DIR.glob("*") if (dir / "urls.py").exists()),
    # apps without urls.py
    "captcha",
    "users",
    "storage",
    # allauth (for template overridding)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "allauth_2fa",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "allauth_2fa.middleware.AllauthTwoFactorMiddleware",
    "website.middleware.RequireSuperuser2FAMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "website.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "website.context_processors.nav_links",
                "website.context_processors.now_variable",
                "website.context_processors.admin_permission",
            ],
        },
    },
]

WSGI_APPLICATION = "website.wsgi.application"

STORAGES = {
    "default": {
        "BACKEND": "storage.storages.CustomFileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = (
    {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    if get_custom_setting("USE_SQLITE")
    else {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": get_custom_setting("DB_NAME"),
            "USER": get_custom_setting("DB_USER"),
            "PASSWORD": get_custom_setting("DB_PASSWORD"),
            "HOST": get_custom_setting("DB_HOST"),
            "OPTIONS": {
                "init_command": 'SET sql_mode="STRICT_TRANS_TABLES"',
            },
        }
    }
)

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "allauth_2fa.adapter.OTPAdapter",
]

LOGIN_URL = "/accounts/login"
LOGIN_REDIRECT_URL = "/"

SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_SIGNUP_FORM_CLASS = "users.forms.AllAuthSignupForm"
# Set the allauth adapter to be the 2FA adapter.
ACCOUNT_ADAPTER = "allauth_2fa.adapter.OTPAdapter"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "github": {
        "SCOPE": [
            "user",
        ],
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "website.password_validation.PwnedPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True
USE_L10N = True
LOCALE_PATHS = [BASE_DIR / "locale"]

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "src/",
    BASE_DIR.parent / "data/static/",
]
STATIC_ROOT = BASE_DIR / "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# reCAPTCHA

RECAPTCHA_PUBLIC_KEY = get_custom_setting("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = get_custom_setting("RECAPTCHA_PRIVATE_KEY")
