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
    "easy_thumbnails",
    # my apps
    "blog",
    "calendrier_avent_2023",
    "calendrier_avent_2024",
    "captcha",
    "cookies",
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
    "django_comments",
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
    "allauth.usersessions.middleware.UserSessionsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "website.middleware.CSPMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
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
                "website.context_processors.globals",
                "globals.context_processors.nav_links",
                "cookies.context_processors.cookies",
            ],
        },
    },
]

WSGI_APPLICATION = "website.wsgi.application"
