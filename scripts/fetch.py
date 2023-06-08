import subprocess as sp

from .utils import BASE, get_custom_setting


def main(_args=None):
    print("Creating git repo")
    sp.run("git init", cwd=BASE, check=True)
    print()

    print("Fetching changes")
    sp.run(["git", "fetch", get_custom_setting("GITHUB_REPO", "") + ".git"], cwd=BASE, check=True)
    print()

    print("Merging changes")
    sp.run(
        [
            "git",
            "merge",
            "FETCH_HEAD",
            "main",
            "--allow-unrelated-histories",
            "--strategy-option",
            "theirs",
            "-m",
            "Merging remote changes",
        ],
        cwd=BASE,
        check=True,
    )
    print()

    from .reload import main as reload

    reload()


def contribute_to_argparse(_parser):
    pass
