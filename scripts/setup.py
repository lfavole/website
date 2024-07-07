import argparse
import subprocess as sp

from .utils import BASE, DOTENV_PATH


def main(args):
    if args.test:
        with DOTENV_PATH.open("w") as f:
            f.write("TEST=1")

    sp.run(["pip", "install", "-r", BASE / "requirements.txt"], check=True)

    if args.dev or args.linting:
        sp.run(["pip", "install", "-r", BASE / "requirements-dev.txt"], check=True)

    if args.reload and not args.linting:
        from .reload import main as reload

        reload()


def contribute_to_argparse(parser: argparse.ArgumentParser):
    parser.add_argument("--test", action="store_true", help="setup a test environment")
    parser.add_argument("--dev", action="store_true", help="setup a development environment")
    parser.add_argument("--no-reload", action="store_false", dest="reload", help="don't run the reload script")
    parser.add_argument("--linting", action="store_true", help="setup a linting environment")
