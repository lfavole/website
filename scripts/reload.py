import subprocess as sp
import sys
from pathlib import Path

from .fetch_gravatar import main as fetch_gravatar
from .utils import get_custom_setting

BASE = Path(__file__).resolve().parent.parent / "website"


def main(_args=None):
    manage = [sys.executable, BASE / "manage.py"]

    print("Migrating")
    sp.run([*manage, "migrate"], check=True)
    print()

    print("Compiling translations")
    sp.run([*manage, "compilemessages"], check=True)
    print()

    fetch_gravatar(reloading=True)

    print("Collecting static files")
    sp.run([*manage, "collectstatic", "--noinput", "--link"], check=True)
    print()

    if get_custom_setting("PYTHONANYWHERE"):
        print("Touching WSGI file")
        Path(get_custom_setting("WSGI_FILE")).touch()


def contribute_to_argparse(_parser):
    pass
