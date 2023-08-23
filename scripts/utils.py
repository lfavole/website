# type: ignore
# pylint: disable=C0413, E0401, E0611
import builtins
import io
import shlex
import subprocess as sp
import sys
from pathlib import Path
from typing import Any, Callable, TypeVar

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


def run(args: list[str] | str, pipe=False, capture=False, **kwargs) -> sp.CompletedProcess[str]:
    """
    Run the command specified by args. Return a `CompletedProcess[str]`.

    `pipe=True` wraps the input and output in pipes.

    `capture=True` adds the command before the output, that is captured.
    """
    # pylint: disable=W1510
    if isinstance(args, str):
        args = shlex.split(args)
    kwargs = {**kwargs, "encoding": "utf-8", "errors": "replace"}

    if pipe:
        kwargs["stdin"] = sp.PIPE
        kwargs["stdout"] = sp.PIPE
        kwargs["stderr"] = sp.PIPE
    if capture:
        kwargs["capture_output"] = True

    before_text = ""
    after_text = ""

    if not pipe or capture:
        before_text = "\n--- Command: " + " ".join(shlex.quote(arg) for arg in args) + " ---\n"
        if not capture:
            print(before_text, end="")

    ret = sp.run(args, **kwargs)

    if not pipe or capture:
        after_text = "--- End of command ---\n"
        if not capture:
            print(after_text, end="")

    if capture:
        ret.stdout = before_text + ret.stdout + after_text

    return ret


def get_run_with_expl(
    cwd: Path | None = None,
    pipe=False,
    callback: Callable[[sp.CompletedProcess[str]], None] | None = None,
):
    """
    Return a function that wraps the output of a command and writes a description before it.
    """

    def run_with_expl(cmd: str | list[str], expl: str):
        print(expl.capitalize())
        proc = run(cmd, capture=pipe, cwd=cwd)
        if callback:
            callback(proc)
        if proc.returncode != 0:
            print("Error while " + expl)

    return run_with_expl


def pipe(f):
    """
    Wraps a function and return all the printed text.

    The decorator passes an `outputs` argument that can be used to add text.
    """

    def wrapper(*args, pipe=False, outputs: list[str] | None = None, **kwargs):
        if pipe:
            if not isinstance(outputs, list):
                outputs: list[str] = []
            old_print = builtins.print

            def new_print(*args, file=None, **kwargs):
                if file in (sys.stdout, sys.stderr, None):
                    file = io.StringIO()
                    old_print(*args, **kwargs, file=file)
                    outputs.append(file.getvalue())
                else:
                    old_print(*args, **kwargs, file=file)

            builtins.print = new_print

            f(*args, pipe=pipe, outputs=outputs, **kwargs)

            builtins.print = old_print  # type: ignore
            return "".join(outputs)
        else:
            return f(*args, pipe=False, outputs=None, **kwargs)

    return wrapper
