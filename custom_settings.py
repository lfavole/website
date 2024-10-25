"""
Default settings.

You will have to create a `custom_settings_overrides.py` file with the overrides.
"""

import os
import sys
from getpass import getuser
from types import ModuleType

# import now because we might remove the current directory from sys.path
try:
    import custom_settings_overrides as cs_overrides
except ImportError:
    cs_overrides = None
import custom_settings_test as cs_test
from captcha.constants import TEST_PRIVATE_KEY, TEST_PUBLIC_KEY

from website.utils.connectivity import internet

PA_SITE = os.environ.get("PYTHONANYWHERE_SITE", "")
PYTHONANYWHERE = bool(PA_SITE)
PRODUCTION = PYTHONANYWHERE
TEST = False
OFFLINE = False  # placeholder
USERNAME = getuser()

HOST = USERNAME + "." + PA_SITE if PYTHONANYWHERE else "*"
DEBUG = False
SECRET_KEY = ""

USE_SQLITE = not PYTHONANYWHERE
DB_HOST = USERNAME + ".mysql." + PA_SITE.replace("pythonanywhere.com", "pythonanywhere-services.com")
DB_NAME = ""  # placeholder
REAL_DB_NAME = "django"
DB_USER = USERNAME
DB_PASSWORD = ""  # placeholder

ADMINS = []
ADMIN_NAME = "lfavole"
GITHUB_REPO = "https://github.com/lfavole/website"
GITHUB_WEBHOOK_KEY = None
SENTRY_DSN = None
GOOGLE_DRIVE_FOLDERS = []

WSGI_FILE = "/var/www/" + HOST.replace(".", "_").lower().strip() + "_wsgi.py" if PYTHONANYWHERE else None

HCAPTCHA_PUBLIC_KEY = TEST_PUBLIC_KEY
HCAPTCHA_PRIVATE_KEY = TEST_PRIVATE_KEY


class CustomSettings(ModuleType):
    """
    Class for shadowing this module.
    It provides access to attributes that depend on other attributes for ease of use.
    """

    def __getattribute__(self, name):
        if name[:2] == "__" and name[-2:] == "__":
            # short-circuit cf. https://github.com/django/django/blob/f6ed2c3/django/utils/autoreload.py#L118 and l.133
            return super().__getattribute__(name)

        if name == "OFFLINE":
            if PYTHONANYWHERE:
                return False
            # return the current value of OFFLINE
            return not internet()

        if cs_overrides is not None:
            try:
                if getattr(cs_overrides, "TEST", False):
                    return getattr(cs_test, name)

                return getattr(cs_overrides, name)
            except AttributeError:
                pass

        if name == "DB_NAME":
            try:
                ret = super().__getattribute__(name)
                if ret:
                    return ret
            except AttributeError:
                pass
            return USERNAME + "$" + self.REAL_DB_NAME  # type: ignore

        return super().__getattribute__(name)


sys.modules[__name__].__class__ = CustomSettings  # type: ignore
