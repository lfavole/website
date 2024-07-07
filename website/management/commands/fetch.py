from pathlib import Path

from django.core.management.base import BaseCommand

from .utils import get_run_with_expl, pipe_function

FOLDER = Path(__file__).parent.parent


class Command(BaseCommand):
    """
    Fetch changes with `git fetch` and migrate the apps.
    """

    @pipe_function
    def handle(self, pipe=False, outputs: list[str] | None = None, ok=True, **_options):
        print("Fetching script")
        print()

        run_with_expl = get_run_with_expl(FOLDER, pipe, (lambda proc: outputs.append(proc.stdout)) if outputs else None)

        run_with_expl("git init", "creating git repo")
        run_with_expl(["git", "pull"], "fetching changes")
        run_with_expl(["git", "stash"], "backing up changes")
        run_with_expl(["git", "reset", "--hard", "origin/main"], "resetting to server state")
        run_with_expl(["git", "pull"], "re-fetching changes")

        from .reload import Command as Reload

        Reload().handle(pipe=pipe, outputs=outputs, ok=False)

        if ok:
            print("OK")
