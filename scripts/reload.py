import subprocess as sp
import sys
from pathlib import Path

from .fetch_gravatar import main as fetch_gravatar
from .utils import get_custom_setting, get_run_with_expl, pipe

FOLDER = Path(__file__).parent.parent
BASE = FOLDER / "website"


@pipe
def main(_args=None, pipe=False, outputs: list[str] | None = None, ok=True):
    print("Reloading script")
    print()

    run_with_expl = get_run_with_expl(FOLDER, pipe, (lambda proc: outputs.append(proc.stdout)) if outputs else None)

    manage = [sys.executable, str(BASE / "manage.py")]

    run_with_expl([*manage, "migrate"], "migrating")
    run_with_expl([*manage, "compilemessages"], "compiling translations")
    fetch_gravatar(reloading=True)
    run_with_expl([*manage, "collectstatic", "--noinput", "--link"], "collecting static files")

    wsgi_file = get_custom_setting("WSGI_FILE")
    if wsgi_file:
        print("Touching WSGI file")
        Path(wsgi_file).touch()

    if ok:
        print("OK")


def contribute_to_argparse(_parser):
    pass
