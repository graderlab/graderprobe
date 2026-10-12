"""graderprobe — field tooling for eval-infrastructure security.

Profiles the evaluation harness your submission will be scored in: the LLM
judge, the sandbox, and the scoring pipeline. Read-only and stdlib-only;
contains no scoring logic of its own and makes NO network calls on import —
the only network surface is the explicit ``sync_signatures()`` call.
"""

__version__ = "0.1.0"

from .judge import judge_profile
from .normalize import normalize_answer
from .sandbox import sandbox_profile
from .signatures import sync_signatures
from ._provenance import provenance

__all__ = [
    "judge_profile",
    "normalize_answer",
    "sandbox_profile",
    "sync_signatures",
    "provenance",
    "__version__",
]
