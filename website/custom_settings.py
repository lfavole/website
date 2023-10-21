"""
Default settings.

You will have to create a `custom_settings.py` file with the overrides.
"""

import os
import sys
from getpass import getuser
from types import ModuleType

# import now because we might remove the current directory from sys.path
import custom_settings_overrides as cs_overrides
import custom_settings_test as cs_test
from captcha.constants import TEST_PRIVATE_KEY, TEST_PUBLIC_KEY

from website.utils.connectivity import internet

PA_SITE = os.environ.get("PYTHONANYWHERE_SITE", "")
PYTHONANYWHERE = bool(PA_SITE)
USERNAME = getuser()

HOST = USERNAME + "." + PA_SITE if PYTHONANYWHERE else "*"
DEBUG = False
SECRET_KEY = ""

USE_SQLITE = not PYTHONANYWHERE
DB_HOST = USERNAME + ".mysql." + PA_SITE.replace("pythonanywhere.com", "pythonanywhere-services.com")
REAL_DB_NAME = "django"
DB_USER = USERNAME

GITHUB_REPO = "https://github.com/lfavole/website"
GITHUB_WEBHOOK_KEY = None

WSGI_FILE = "/var/www/" + HOST.replace(".", "_").lower().strip() + "_wsgi.py" if PYTHONANYWHERE else None

RECAPTCHA_PUBLIC_KEY = TEST_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY = TEST_PRIVATE_KEY


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

        try:
            if getattr(cs_overrides, "TEST", False):
                return getattr(cs_test, name)

            return getattr(cs_overrides, name)
        except AttributeError:
            pass

        if name == "TEST":
            return False  # True will be returned from CS_OVERRIDES

        if name == "DB_NAME":
            try:
                return super().__getattribute__(name)
            except AttributeError:
                return USERNAME + "$" + super().__getattribute__("REAL_DB_NAME")

        return super().__getattribute__(name)


sys.modules[__name__].__class__ = CustomSettings  # type: ignore
