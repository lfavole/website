"""
Default settings.

You will have to create a `custom_settings.py` file with the overrides.
"""

import os
import sys
from getpass import getuser

from website.utils.connectivity import internet

PA_SITE = os.environ.get("PYTHONANYWHERE_SITE", "")
PYTHONANYWHERE = bool(PA_SITE)
USERNAME = getuser()

APP_NAME = "website"
HOST = USERNAME + "." + PA_SITE if PYTHONANYWHERE else "*"
DEBUG = False
SECRET_KEY = ""

USE_SQLITE = True

GITHUB_REPO = "https://github.com/lfavole/website"
GITHUB_WEBHOOK_KEY = None


class CustomSettings:
    """
    Class for shadowing this module.
    The only purpose of this is to dynamically provide the value of `OFFLINE`.
    """

    def __getattr__(self, name):
        if name == "OFFLINE":
            # return the current value of OFFLINE
            return not internet()
        return super().__getattribute__(name)


sys.modules[__name__] = CustomSettings()  # type: ignore
