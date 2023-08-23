from pathlib import Path

from .utils import get_run_with_expl, pipe

FOLDER = Path(__file__).parent.parent


@pipe
def main(_args=None, pipe=False, outputs: list[str] | None = None, ok=True):
    """
    Fetch changes with `git fetch` and migrate the apps.
    """
    print("Fetching script")
    print()

    run_with_expl = get_run_with_expl(FOLDER, pipe, (lambda proc: outputs.append(proc.stdout)) if outputs else None)

    run_with_expl("git init", "creating git repo")
    run_with_expl(["git", "pull"], "fetching changes")
    run_with_expl(["git", "stash"], "backing up changes")
    run_with_expl(["git", "reset", "--hard", "origin/main"], "resetting to server state")
    run_with_expl(["git", "pull"], "re-fetching changes")

    from .reload import main as reload

    reload(pipe=pipe, outputs=outputs, ok=False)

    if ok:
        print("OK")


def contribute_to_argparse(_parser):
    pass
