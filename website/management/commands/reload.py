import os
import sys
from pathlib import Path
from django.conf import settings

from django.core.management.base import BaseCommand

from .fetch_gravatar import Command as FetchGravatar
from .utils import get_run_with_expl, pipe_function, run_in_thread

BASE = settings.BASE_DIR


class Command(BaseCommand):
    @pipe_function
    def handle(self, pipe=False, outputs: list[str] | None = None, ok=True, *_args, **_options):
        print("Reloading script")
        print()

        run_with_expl = get_run_with_expl(BASE, pipe, (lambda proc: outputs.append(proc.stdout)) if outputs else None)
        run_with_expl_thread = run_in_thread(run_with_expl)

        manage = [sys.executable, str(BASE / "manage.py")]

        if not os.environ.get("VERCEL"):
            run_with_expl(
                ["python3", "-m", "pip", "install", "-r", str(BASE / "requirements.txt")], "installing requirements"
            )

        def compile_translations():
            if os.environ.get("VERCEL"):
                run_with_expl(["dnf", "install", "-y", "gettext"], "installing gettext")
            run_with_expl(
                [
                    *manage,
                    "compilemessages",
                    "--ignore",
                    "adminsortable2",
                    "--ignore",
                    "allauth",
                    "--ignore",
                    "debug_toolbar",
                    "--ignore",
                    "django",
                    "--ignore",
                    "django_comments",
                ],
                "compiling translations",
            )

        run_in_thread(compile_translations)()
        run_in_thread(FetchGravatar().handle)(reloading=True)
        run_with_expl_thread([*manage, "collectstatic", "--noinput", "--clear"], "collecting static files")

        if os.environ.get("PYTHONANYWHERE"):
            run_with_expl(["python3", "-m", "pip", "install", "mysqlclient~=2.2"], "installing MySQL")
        # we don't need to install psycopg if on Vercel (it's already installed by build.sh)
        run_with_expl_thread([*manage, "createcachetable"], "creating the cache tables")
        run_with_expl_thread([*manage, "migrate"], "migrating")

        wsgi_file = "/var/www/" + os.environ.get("HOST", "").replace(".", "_").lower().strip() + "_wsgi.py"
        if os.environ.get("PYTHONANYWHERE") and wsgi_file:
            print("Touching WSGI file")
            Path(wsgi_file).touch()

        if ok:
            print("OK")
