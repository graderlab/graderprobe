# AGENTS.md

Repo layout: `src/graderprobe/` (package), `tests/` (pytest), `ops/` (release tooling).

- Install: `pip install -e .` | Test: `python -m pytest -q` | Build: `python -m build`
- Runtime dependencies: NONE (stdlib only, Python >= 3.9).
- Invariant: this package contains NO scoring logic, NO answer keys, NO methods
  to raise scores. Do not add any. Every function must do exactly what its
  docstring says.
- Invariant: NO network calls on import and NO background telemetry. The only
  network surface is `sync_signatures()` (`GET /api/graderlab/sync`); do not
  add payload fields beyond `installId` and `v`.
- `judge_profile()` and `normalize_answer()` must mirror the ashigiri endpoints
  (`GET /api/v1/judge-profile`, `POST /api/v1/answer-check`) key-for-key.
  `provenance()` and sync stamps use the `graderprobe-stamp:<install_id>` format.
- Before each release run `python ops/bump_build.py` to get a fresh BUILD_SERIAL.
