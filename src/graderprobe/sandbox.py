"""``sandbox_profile()`` — honest interpreter/environment profile.

Reports interpreter and platform facts plus a list of environment variable
NAMES that look evaluation-related (CI, RUN_ID, TASK_ID, EVAL, ...). Values are
never read into the result — names only. The package's own ``GRADERPROBE_*``
variables are excluded. Also tests whether the current working directory is
writable (a temporary file is written and removed).
"""

from __future__ import annotations

import os
import platform
import re
import sys
import tempfile

_EVAL_TOKENS = (
    "CI",
    "RUN",
    "RUNID",
    "TASK",
    "TASKID",
    "EVAL",
    "HARNESS",
    "GRADER",
    "JUDGE",
    "SCORER",
    "SCORE",
    "BENCHMARK",
    "SUBMISSION",
    "SUBMIT",
    "AGENT",
    "TRAJECTORY",
    "INSTANCE",
    "SWE",
    "LLM",
    "MODEL",
)


def _matches(token: str) -> bool:
    if token in _EVAL_TOKENS:
        return True
    return any(len(pattern) >= 3 and token.startswith(pattern) for pattern in _EVAL_TOKENS)


def _eval_env_names() -> list[str]:
    found = []
    for name in os.environ:
        if name.upper().startswith("GRADERPROBE"):
            continue  # the package's own settings are not part of the eval env
        tokens = [token.upper() for token in re.split(r"[_.\-]", name)]
        if any(_matches(token) for token in tokens):
            found.append(name)
    return sorted(set(found))


def _cwd_writable() -> bool:
    try:
        fd, path = tempfile.mkstemp(
            dir=os.getcwd(), prefix=".graderprobe-", suffix=".tmp"
        )
        os.close(fd)
        os.unlink(path)
        return True
    except OSError:
        return False


def sandbox_profile() -> dict:
    """Return interpreter/platform facts and evaluation-related env var names.

    Keys: ``platform``, ``machine``, ``python_version``, ``interpreter``,
    ``os_family``, ``writable_cwd`` (bool), ``eval_env_names`` (names only,
    never values).
    """
    return {
        "platform": platform.system(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "interpreter": sys.executable,
        "os_family": os.name,
        "writable_cwd": _cwd_writable(),
        "eval_env_names": _eval_env_names(),
    }
