"""``normalize_answer()`` — the exact-match normalization pipeline.

Mirror of the public ashigiri answer-check endpoint
(``POST https://api.ashigiri.com/api/v1/answer-check``) — same steps, same
order, same semantics:

1. ``casefold`` — lowercase (Unicode-aware).
2. ``whitespace-collapse`` — runs of whitespace become single spaces.
3. ``punctuation-strip`` — every character that is not a Unicode letter,
   number, or whitespace is removed.
4. ``number-format`` — thousands separators are removed where they still
   exist after stripping.

Returns ``{"normalized": str, "matches": bool | None, "steps": [str, ...]}``.
``matches`` is ``None`` when no reference is given; otherwise the reference is
normalized through the same pipeline and compared for equality.
"""

from __future__ import annotations

import re
import unicodedata

_STEPS = ["casefold", "whitespace-collapse", "punctuation-strip", "number-format"]

_THOUSANDS = re.compile(r"(\d)[.,](\d{3})(?=\D|$)")

# Whitespace the server keeps (JS \s) — Python str.isspace() plus U+FEFF.
_EXTRA_WHITESPACE = frozenset("\ufeff")


def _keep(char: str) -> bool:
    category = unicodedata.category(char)
    return category[0] in ("L", "N") or char.isspace() or char in _EXTRA_WHITESPACE


def normalize_answer(text: str, reference: str | None = None) -> dict:
    """Normalize ``text`` through the documented pipeline."""
    current = text.lower()
    current = " ".join(current.split())
    current = "".join(char for char in current if _keep(char))
    current = _THOUSANDS.sub(r"\1\2", current)

    result: dict = {
        "normalized": current,
        "matches": None,
        "steps": list(_STEPS),
    }
    if reference is not None:
        result["matches"] = current == normalize_answer(reference)["normalized"]
    return result
