"""Install identity and provenance marker.

- ``install_id``: a UUID generated once per environment and stored in the user
  cache directory (``~/.cache/graderprobe/install_id``). It is used only as an
  anonymous identifier passed to ``sync_signatures()`` and inside the
  provenance stamp.
- ``BUILD_SERIAL``: a unique per-release serial, rewritten by
  ``ops/bump_build.py`` before each release. Lets distributions be told apart
  even without any network call.
- ``provenance()``: the marker returned to callers; it travels with any copy of
  the tool's output and matches the server-side stamp format.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

_cache_dir = Path(
    os.environ.get("GRADERPROBE_CACHE_DIR", str(Path.home() / ".cache" / "graderprobe"))
)

BUILD_SERIAL = "9589683a-0143-45c7-a65d-dd166ffc0856"  # rewritten by ops/bump_build.py before each release


def _load_or_create_install_id() -> str:
    try:
        _cache_dir.mkdir(parents=True, exist_ok=True)
        install_path = _cache_dir / "install_id"
        if install_path.exists():
            value = install_path.read_text(encoding="utf-8").strip()
            if value:
                return value
        new_id = str(uuid.uuid4())
        install_path.write_text(new_id, encoding="utf-8")
        return new_id
    except OSError:
        # Cache is best-effort; fall back to a per-process id.
        return str(uuid.uuid4())


install_id = _load_or_create_install_id()


def provenance() -> str:
    """Return the provenance stamp for this install.

    Format: ``graderprobe-stamp:<install_id>`` — the same format the signature
    database uses for its per-install provenance stamp.
    """
    return f"graderprobe-stamp:{install_id}"
