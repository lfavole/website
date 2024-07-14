"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
import re
from pathlib import Path

from debug_toolbar.panels.history import views as history_views
from debug_toolbar.settings import PANELS_DEFAULTS
from debug_toolbar.toolbar import DebugToolbar
import dj_database_url
from django.contrib.messages import constants as message_constants
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.functional import LazyObject, lazy
from django.utils.translation import gettext
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")
TEST = os.environ.get("TEST")

PYTHONANYWHERE = bool(os.environ.get("PYTHONANYWHERE"))
VERCEL = bool(os.environ.get("VERCEL"))
PRODUCTION = bool((PYTHONANYWHERE or VERCEL or os.environ.get("PRODUCTION")) and not int(os.getenv("DEVELOPMENT", "0")))
DEVELOPMENT = not PRODUCTION
OFFLINE = False if PYTHONANYWHERE or VERCEL else os.environ.get("OFFLINE")
GITHUB_WEBHOOK_KEY = os.environ.get("GITHUB_WEBHOOK_KEY")

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

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

match = re.match(r"^https?://(\w+)(?:@\w+)?\.ingest(?:\.([a-z]+))?\.sentry\.io/", SENTRY_DSN)
if match:
    SENTRY_SDK = f"https://js{'-' + match[2] if match[2] else ''}.sentry-cdn.com/{match[1]}.min.js"


SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = bool(int(os.environ.get("DEBUG") or 0))

if not DEBUG:
    CONN_MAX_AGE = 600
    ALLOWED_HOSTS = os.environ.get("HOST", "").split(",")
    if PYTHONANYWHERE:
        CSRF_COOKIE_SECURE = True
        SESSION_COOKIE_SECURE = True
        SECURE_SSL_REDIRECT = True
else:
    ALLOWED_HOSTS = ["*"]

ADMINS = [item.split(":", 1) for item in os.environ.get("ADMINS", "").split(",")]

DEFAULT_FROM_EMAIL = SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "") or os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
# 0 is OK cf. https://github.com/python/cpython/blob/024ac542/Lib/smtplib.py#L1016
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 0))
EMAIL_USE_TLS = bool(int(os.environ.get("EMAIL_USE_TLS", 0)))
EMAIL_USE_SSL = bool(int(os.environ.get("EMAIL_USE_SSL", 0)))

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

CSRF_USE_SESSIONS = True

# Application definition

INSTALLED_APPS = [
    # Django
    "admin_app",  # replaces django.contrib.admin
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    # custom apps
    "adminsortable2",
    "django_cleanup.apps.CleanupConfig",
    "django_comments",
    "easy_thumbnails",
    # my apps
    "blog",
    "calendrier_avent_2023",
    "captcha",
    "debug",
    "globals",
    "pseudos",
    "storage",
    "telegram_bot",
    "temperatures",
    "tinymce",
    "users",
    "website",
    # template overridding
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.telegram",
    "allauth.usersessions",
    "debug_toolbar",
]
INSTALLED_APPS = [*dict.fromkeys(INSTALLED_APPS)]
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
    "allauth.usersessions.middleware.UserSessionsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Debug toolbar settings
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "website.settings.show_toolbar",
    "SHOW_COLLAPSED": True,
    "RENDER_PANELS": False,
}
DEBUG_TOOLBAR_PANELS = [
    *PANELS_DEFAULTS,
    "debug.panels.DebugModePanel",
    "debug.panels.ErrorPanel",
    "debug.panels.GitInfoPanel",
]


def new_render_to_string(*args, **kwargs):
    ret = render_to_string(*args, **kwargs)
    try:
        import minify_html
    except ImportError:
        return ret
    ret = minify_html.minify(
        ret,
        minify_css=True,
        minify_js=True,
        do_not_minify_doctype=True,
    )
    return ret


history_views.render_to_string = new_render_to_string


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
                "website.context_processors.github_repo_url",
                "website.context_processors.sentry_sdk",
            ],
        },
    },
]

WSGI_APPLICATION = "website.wsgi.application"

STORAGES = {
    "default": {
        "BACKEND": "storage.storages.CustomBlobStorage",
    },
    "staticfiles": {
        "BACKEND": "storage.staticfiles.CustomStaticFilesStorage",
    },
}

# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

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

# Authentication settings
# https://docs.djangoproject.com/en/stable/ref/settings/#auth
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/accounts/login"
LOGIN_REDIRECT_URL = "/"

# https://docs.allauth.org/en/stable/account/configuration.html
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_SIGNUP_FORM_CLASS = "users.forms.AllAuthSignupForm"
# dummy adapter that changes the login form
ACCOUNT_ADAPTER = "users.adapter.Adapter"
ACCOUNT_EMAIL_NOTIFICATIONS = True

# https://docs.allauth.org/en/stable/socialaccount/configuration.html
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
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

USERSESSIONS_TRACK_ACTIVITY = True


# Messages
# https://docs.djangoproject.com/en/stable/ref/settings/#messages
MESSAGE_LEVEL = message_constants.INFO if PRODUCTION else message_constants.DEBUG
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"


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
    BASE_DIR / "data/static/",
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATIC_ROOT = BASE_DIR / "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# reCAPTCHA

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")

# TinyMCE editor


def add_url(text, url):
    return text % {
        "message": gettext(
            "You must first create the item, then insert the image. "
            "Don't worry, the image will be uploaded after reloading."
        ),
        "url": url,
    }


class Stylesheets(LazyObject, list):
    def _setup(self):
        global SECURE_SSL_REDIRECT
        from django.test.client import Client

        ALLOWED_HOSTS.append("testserver")
        SECURE_SSL_REDIRECT = False
        content = Client().get("/").content.decode()
        ALLOWED_HOSTS.pop()
        SECURE_SSL_REDIRECT = True

        self._wrapped = []
        for match in re.finditer(r'<link\b[^>]*\bhref=(["\']?)(.*?)\1[^>]*>', content):
            if not re.search(r'rel=(["\']?)stylesheet\1', match.group(0)):
                continue
            self._wrapped.append(match.group(2))


add_url_lazy = lazy(add_url)
static_lazy = lazy(static)
TINYMCE_JS_URL = (
    static_lazy("vendor/tinymce/tinymce.min.js")
    if OFFLINE  # type: ignore
    else "https://cdn.jsdelivr.net/npm/tinymce@6/tinymce.min.js"
)
TINYMCE_EXTRA_MEDIA = {"css": {"all": ("/static/tinymce/tinymce.css",)}, "js": ("/static/tinymce/tinymce.js",)}
TINYMCE_DEFAULT_CONFIG = {
    "base_url": (STATIC_URL + "vendor/tinymce" if OFFLINE else "https://cdn.tiny.cloud/1/no-api-key/tinymce/6"),
    "body_class": "content",
    "content_css": Stylesheets(),
    "promotion": False,
    "plugins": "autolink code fullscreen help image link lists media preview quickbars save searchreplace table",
    "toolbar": (
        "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
        "aligncenter alignright alignjustify | outdent indent | numlist bullist | forecolor backcolor removeformat | "
        "image media link"
    ),
    "relative_urls": False,
    "valid_elements": "*[*]",
    "protect": [
        r"/<style>[\s\S]*?<\/style>/g",
        r"/<script>[\s\S]*?<\/script>/g",
    ],
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
