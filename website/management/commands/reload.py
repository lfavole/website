import os
import sys
from pathlib import Path
from django.conf import settings

from django.core.management import ManagementUtility
from django.core.management.base import BaseCommand

from .fetch_gravatar import Command as FetchGravatar
from .utils import get_run_with_expl, pipe_function

BASE = settings.BASE_DIR


class Command(BaseCommand):
    @pipe_function
    def handle(self, pipe=False, outputs: list[str] | None = None, ok=True, *_args, **_options):
        print("Reloading script")
        print()

        run_with_expl = get_run_with_expl(BASE, pipe, (lambda proc: outputs.append(proc.stdout)) if outputs else None)

        manage = [sys.executable, str(BASE / "manage.py")]

        run_with_expl(["python3", "-m", "pip", "install", "-r", str(BASE / "requirements.txt")], "installing requirements")
        if os.environ.get("PYTHONANYWHERE"):
            run_with_expl(["python3", "-m", "pip", "install", "mysqclient~=2.2"], "installing MySQL")
        if os.environ.get("VERCEL"):
            run_with_expl(["python3", "-m", "pip", "install", "psycopg[binary,pool]~=3.2"], "installing PostgreSQL")
        run_with_expl([*manage, "createcachetable"], "creating the cache tables")
        run_with_expl([*manage, "migrate"], "migrating")
        run_with_expl([*manage, "compilemessages"], "compiling translations")
        FetchGravatar().handle(reloading=True)
        run_with_expl([*manage, "collectstatic", "--noinput", "--clear"], "collecting static files")

        wsgi_file = "/var/www/" + os.environ.get("HOST", "").replace(".", "_").lower().strip() + "_wsgi.py"
        if os.environ.get("PYTHONANYWHERE") and wsgi_file:
            print("Touching WSGI file")
            Path(wsgi_file).touch()

        if ok:
            print("OK")
