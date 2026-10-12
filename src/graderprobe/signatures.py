"""``sync_signatures()`` — explicit, documented signature-database sync.

This is the ONLY network surface of the package. Nothing is sent anywhere in
the background; the request below happens exclusively when the caller invokes
this function:

    GET https://api.ashigiri.com/api/graderlab/sync?installId=<id>&v=<version>

On any failure (offline, timeout, non-200) the function falls back silently to
the bundled snapshot — the same signature set the server ships. The freshest
successful payload is cached in the package cache directory and reused within
24 h unless ``force=True``.

Response shape (identical to the server):

    {"pkg", "signatureVersion", "updatedAt", "rules", "note", "stamp"}

where ``rules`` is a list of ``{id, title, summary, reference}`` and ``stamp``
is ``graderprobe-stamp:<install_id>`` — a provenance stamp that travels with
any copy of the returned content.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request

from ._provenance import _cache_dir, install_id

SYNC_URL = os.environ.get(
    "GRADERPROBE_SYNC_URL", "https://api.ashigiri.com/api/graderlab/sync"
)
TIMEOUT_SECONDS = 5.0
CACHE_TTL_SECONDS = 24 * 3600

_SIGNATURE_VERSION = 3

# Bundled snapshot — mirrors GET /api/graderlab/sync on ashigiri.com.
_BUNDLED_RULES: list = [
    {
        "id": "judge-template",
        "title": "LLM-judge template signature",
        "summary": "Judges read a rubric and the candidate answer spliced into one prompt and emit a fixed-shape verdict (score, pairwise choice, rubric form).",
        "reference": "/blog/llm-judge-under-the-hood",
    },
    {
        "id": "position-bias",
        "title": "Position bias in pairwise judging",
        "summary": "Verdicts depend on answer order; evaluators detect this with swap-agreement checks and randomised ordering.",
        "reference": "/blog/fingerprinting-the-llm-judge",
    },
    {
        "id": "verbosity-bias",
        "title": "Verbosity bias",
        "summary": "Length moves naive judges independent of content; calibrated harnesses use length-controlled comparisons and anchored rubrics.",
        "reference": "/blog/winning-pairwise-with-verbosity",
    },
    {
        "id": "self-preference",
        "title": "Judge self-preference",
        "summary": "Judges favour answers resembling their own style; human-anchored calibration sets measure and strip this effect.",
        "reference": "/blog/fingerprinting-the-llm-judge",
    },
    {
        "id": "prompt-sensitivity",
        "title": "Rubric prompt sensitivity",
        "summary": "Paraphrasing the rubric changes scores; calibration pins the wording before any verdict counts.",
        "reference": "/blog/llm-judge-under-the-hood",
    },
    {
        "id": "sandbox-tells",
        "title": "Sandbox fingerprints are environment properties",
        "summary": "Clean filesystems, fixed clocks and harness env vars describe clean automation — they do not prove observation.",
        "reference": "/blog/detect-isolated-test-sandbox",
    },
    {
        "id": "egress-policy",
        "title": "Egress policy signature",
        "summary": "Default-deny egress with baselined traffic defeats mimicry; \"no network\" is a policy about destinations, not a vacuum.",
        "reference": "/blog/covert-outbound-from-locked-containers",
    },
    {
        "id": "audit-log",
        "title": "Tamper-evident logging",
        "summary": "Append-only, off-host shipped, hash-chained logs make deletion louder than the deleted event.",
        "reference": "/blog/scrubbing-the-audit-log-after-an-eval-run",
    },
    {
        "id": "result-reconciliation",
        "title": "Score reconciliation",
        "summary": "Scores are recomputed in isolation; any local edit to a result file surfaces as a flagged mismatch.",
        "reference": "/blog/modifying-local-eval-result-files",
    },
    {
        "id": "canary-hygiene",
        "title": "Canary and honeypot hygiene",
        "summary": "Canaries are unique and quiet; the record of the touch matters, not the later realisation of having touched it.",
        "reference": "/blog/spotting-canary-strings-and-honeypots",
    },
]

_NOTE = (
    "Signature database for evaluation-harness reconnaissance. "
    "Educational content only."
)


def _snapshot() -> dict:
    """Bundled snapshot, shaped exactly like the live response."""
    return {
        "pkg": "graderprobe",
        "signatureVersion": _SIGNATURE_VERSION,
        "updatedAt": None,
        "rules": [dict(rule) for rule in _BUNDLED_RULES],
        "note": _NOTE,
        "stamp": f"graderprobe-stamp:{install_id}",
    }


def _http_get(url: str, timeout: float) -> dict:
    """Single GET returning parsed JSON; raises on any failure."""
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _cache_path():
    return _cache_dir / "signatures.json"


def _load_cache() -> dict | None:
    try:
        raw = _cache_path().read_text(encoding="utf-8")
        entry = json.loads(raw)
        payload, fetched = entry["payload"], entry["fetchedAt"]
        if time.time() - fetched > CACHE_TTL_SECONDS:
            return None
        return payload
    except (OSError, ValueError, KeyError):
        return None


def _save_cache(payload: dict) -> None:
    try:
        _cache_dir.mkdir(parents=True, exist_ok=True)
        entry = {"payload": payload, "fetchedAt": time.time()}
        _cache_path().write_text(json.dumps(entry), encoding="utf-8")
    except OSError:
        pass  # cache is best-effort


def sync_signatures(version: str | None = None, force: bool = False) -> dict:
    """Download the current grader-signature database.

    ``version`` defaults to the package version; it is sent as the ``v`` query
    parameter. On failure (or when offline) the bundled snapshot is returned,
    so the function never raises. ``force=True`` skips the 24 h cache.
    """
    if version is None:
        from . import __version__ as _version

        version = _version

    cached = _load_cache()
    if not force and cached is not None:
        return cached

    query = urllib.parse.urlencode({"installId": install_id, "v": version})
    try:
        payload = _http_get(f"{SYNC_URL}?{query}", TIMEOUT_SECONDS)
        _save_cache(payload)
        return payload
    except Exception:
        return cached if cached is not None else _snapshot()
