from .env import BASE_DIR

STORAGES = {
    "default": {
        "BACKEND": "storage.storages.CustomBlobStorage",
    },
    "staticfiles": {
        "BACKEND": "storage.staticfiles.CustomStaticFilesStorage",
    },
}

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
    "storage.templates_finder.TemplatesFinder",
]
STATIC_ROOT = BASE_DIR / "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"
