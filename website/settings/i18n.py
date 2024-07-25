from .env import BASE_DIR

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True
USE_L10N = True
LOCALE_PATHS = [BASE_DIR / "locale"]

USE_TZ = True
