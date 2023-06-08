# type: ignore
# pylint: disable=C0413, E0401, E0611
import sys
from pathlib import Path
from typing import Any, TypeVar

BASE = Path(__file__).resolve().parent.parent

# setup to avoid errors later
CUSTOM_SETTINGS_PATH = BASE / "website/custom_settings.py"
CUSTOM_SETTINGS_PATH.touch()

(BASE / "website/static").mkdir(exist_ok=True)

_T = TypeVar("_T")

TEST = None

sys.path.insert(0, str(BASE / "website"))
import custom_settings  # noqa
import custom_settings_default  # noqa
import custom_settings_test  # noqa

sys.path.pop(0)

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
        return getattr(custom_settings_default, key, ret)
    return ret
