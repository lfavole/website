"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import re

import custom_settings
from debug_toolbar.settings import PANELS_DEFAULTS
from debug_toolbar.toolbar import DebugToolbar
from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.functional import lazy
from django.utils.translation import gettext

TEST = custom_settings.TEST

PYTHONANYWHERE = custom_settings.PYTHONANYWHERE
OFFLINE = custom_settings.OFFLINE

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = custom_settings.SECRET_KEY or "+jt!%+%erdp^y7h37v#68x31+u9ut6^8zryj@#zmu5p$_!u2)u"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = custom_settings.DEBUG

if not DEBUG:
    CONN_MAX_AGE = 600
    ALLOWED_HOSTS = [custom_settings.HOST]
    if PYTHONANYWHERE:
        CSRF_COOKIE_SECURE = True
        SESSION_COOKIE_SECURE = True
        SECURE_SSL_REDIRECT = True
else:
    ALLOWED_HOSTS = ["*"]

GITHUB_WEBHOOK_KEY = custom_settings.GITHUB_WEBHOOK_KEY

# Application definition

INSTALLED_APPS = [
    # Django
    "admin_app",  # replaces django.contrib.admin
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    # custom apps
    "adminsortable2",
    "compressor",
    "debug_toolbar",
    "django_cleanup.apps.CleanupConfig",
    "django_comments",
    "easy_thumbnails",
    "tinymce",
    # apps with urls.py (automatic)
    *(dir.name for dir in BASE_DIR.glob("*") if (dir / "urls.py").exists()),
    # apps without urls.py
    "captcha",
    "users",
    "storage",
    # allauth (for template overridding)
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.telegram",
]
SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "website.middleware.MinifyHtmlMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "website.settings.show_toolbar",
    "SHOW_COLLAPSED": True,
    "RENDER_PANELS": False,
    "OBSERVE_REQUEST_CALLBACK": "website.settings.observe_request",
}
DEBUG_TOOLBAR_PANELS = [
    *PANELS_DEFAULTS,
    "debug.panels.ErrorPanel",
    "debug.panels.GitInfoPanel",
]


def show_toolbar(request: HttpRequest):
    """
    Should we show the toolbar?
    """
    return request.user.is_authenticated and request.user.has_perm("users.can_see_debug_toolbar")  # type: ignore


def observe_request(request: HttpRequest):
    """
    Should we observe the request with the toolbar?
    """
    if DebugToolbar.is_toolbar_request(request):
        return False
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return False
    return True


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
                "website.context_processors.offline",
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
    if custom_settings.USE_SQLITE
    else {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": custom_settings.DB_NAME,
            "USER": custom_settings.DB_USER,
            "PASSWORD": custom_settings.DB_PASSWORD,
            "HOST": custom_settings.DB_HOST,
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
SOCIALACCOUNT_STORE_TOKENS = True
# Set the allauth adapter to be the 2FA adapter.
ACCOUNT_ADAPTER = "users.adapter.Adapter"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "offline",
        },
    },
    "github": {
        "SCOPE": [
            "user",
        ],
    },
    "telegram": {
        "AUTH_PARAMS": {"auth_date_validity": 30},
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
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]
COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)
STATIC_ROOT = BASE_DIR / "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# reCAPTCHA

RECAPTCHA_PUBLIC_KEY = custom_settings.RECAPTCHA_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY = custom_settings.RECAPTCHA_PRIVATE_KEY

# TinyMCE editor


def add_url(text, url):
    return text % {
        "message": gettext(
            "You must first create the item, then insert the image. "
            "Don't worry, the image will be uploaded after reloading."
        ),
        "url": url,
    }


add_url_lazy = lazy(add_url)
static_lazy = lazy(static)
TINYMCE_JS_URL = (
    static_lazy("vendor/tinymce/tinymce.min.js")
    if custom_settings.OFFLINE  # type: ignore
    else "https://cdn.jsdelivr.net/npm/tinymce@6/tinymce.min.js"
)
TINYMCE_EXTRA_MEDIA = {"css": {"all": ("/static/tinymce/tinymce.css",)}, "js": ("/static/tinymce/tinymce.js",)}
TINYMCE_DEFAULT_CONFIG = {
    "language": "fr",
    "language_url": static_lazy("tinymce/langs/fr_FR.js"),
    "content_css": [
        "https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,700;1,400;1,700&display=swap",
        static_lazy("global/global.css"),
    ],
    "content_style": "body{padding:8px}",
    "promotion": False,
    "plugins": "autolink code fullscreen help image link lists media preview quickbars save searchreplace table",
    "toolbar": (
        "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
        "aligncenter alignright alignjustify | outdent indent | numlist bullist | forecolor backcolor removeformat | "
        "image media link"
    ),
    "relative_urls": False,
    "extended_valid_elements": "*[*],+i[class=fa-*]",  # allow all elements, keep Font Awesome icons
    "image_advtab": True,
    # pylint: disable=C0209
    "images_upload_handler": add_url_lazy(
        """\
(blobInfo, progress) => new Promise((success, failure) => {
    var parts = location.pathname.split("/");
    if(parts[4] == "add" && parts[5] == "") {
        failure("%(message)s");
        return;
    }
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "%(url)s");
    xhr.withCredentials = true;
    xhr.upload.onprogress = e => {
        progress(e.loaded / e.total * 100);
    };
    xhr.onerror = () => {
        failure("Image upload failed due to a XHR Transport error. Code: " + xhr.status);
    };
    xhr.onload = () => {
        if(xhr.status < 200 || xhr.status >= 300) {
            failure("HTTP Error: " + xhr.status);
            return;
        }
        var json = JSON.parse(xhr.responseText);
        if(!json || !json.location) {
            failure("Invalid JSON: " + xhr.responseText);
            return;
        }
        success(json.location);
    };
    var formData = new FormData();
    formData.append("file", blobInfo.blob(), blobInfo.filename());
    formData.append("csrfmiddlewaretoken", django.jQuery("#content-main form").get(0).csrfmiddlewaretoken.value);
    xhr.send(formData);
})
""",
        reverse_lazy("tinymce-upload-image"),
    ),
}
