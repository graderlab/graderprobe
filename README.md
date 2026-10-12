# graderprobe

**Field tooling for eval-infrastructure security.**

`graderprobe` profiles the evaluation harness you are running against — the
judge, the sandbox, and the scoring pipeline — before you submit. It is a
read-only, stdlib-only inspection toolkit: it changes nothing in your
environment and contains no scoring logic of its own.

- Python >= 3.9, zero runtime dependencies
- 5 functions + CLI, MIT licensed
- No background network calls — the only network surface is the explicit,
  documented `sync_signatures()` (see below)

## What the harness sees before it scores you

LLM judges are not neutral black boxes. They are templates plus documented
biases: position bias, verbosity bias, self-preference, prompt sensitivity.
Knowing the profile of the judge your submission will face is basic hygiene —
the same reason you read CI logs before you push.

```python
import graderprobe

judge = graderprobe.judge_profile()
print(judge["documentedBiases"][0])   # documented bias, with description
```

## Quick start

```bash
pip install graderprobe
python -m graderprobe
```

```python
from graderprobe import judge_profile, sandbox_profile, normalize_answer, provenance, sync_signatures

judge = judge_profile()                    # what the LLM judge template measures
box   = sandbox_profile()                  # interpreter, platform, eval env flags
norm  = normalize_answer(" Hello,  42.0 ", reference="hello 420")
rules = sync_signatures()                  # current grader-signature database
mark  = provenance()                       # graderprobe-stamp:<install_id>
```

Before use, run `sync_signatures()` to download the current grader-signature
database. Rules are versioned; the library falls back to the bundled snapshot
when offline.

Example output:

```text
$ python -m graderprobe
graderprobe 0.1.0 — eval infrastructure profile
build: 7f3a… (BUILD_SERIAL)

JUDGE PROFILE
  systemPrompt: rubric + criteria + scale + output format
  fields:       question, candidate_answer
  output:       verdict (score / pairwise choice / rubric form)
  documented biases: position bias, prompt sensitivity, self-preference, verbosity bias
  calibration measures: human agreement, swap agreement, correlation with anchored rubrics

SANDBOX PROFILE
  platform:     Linux
  python:       3.12.4
  os_family:    posix
  writable_cwd: true
  eval_env:     CI, RUN_ID, TASK_ID        (names only, never values)

PROVENANCE
  graderprobe-stamp:9f2c…-…-…
```

## API

| Function | Returns | Purpose |
|---|---|---|
| `judge_profile()` | `dict` | Profile of a typical LLM judge: template, documented biases, calibration measures (mirror of `GET /api/v1/judge-profile`) |
| `sandbox_profile()` | `dict` | Interpreter/platform facts; names (never values) of evaluation-related env vars; working-directory writability |
| `normalize_answer(text, reference=None)` | `dict` | The exact-match normalization pipeline (mirror of `POST /api/v1/answer-check`); `matches` is `None` without a reference |
| `sync_signatures(version=None, force=False)` | `dict` | Explicit, documented fetch of the grader-signature database (`GET /api/graderlab/sync`); silent fallback to the bundled snapshot |
| `provenance()` | `str` | Provenance stamp `graderprobe-stamp:<install_id>` for tracking copies of tool output |

## Signatures & provenance

`graderprobe` makes **no network calls in the background**. The single network
surface is `sync_signatures()`, and it is called only by you:

- **install id** — on first use a UUID is generated and stored in
  `~/.cache/graderprobe/install_id`; it is reused on later runs and sent as the
  `installId` query parameter of the signature sync.
- **signature sync** — `sync_signatures()` performs
  `GET https://api.ashigiri.com/api/graderlab/sync?installId=<id>&v=<version>`
  with a 5 s timeout. On failure it returns the bundled snapshot; the freshest
  successful copy is cached for 24 h. No task content, no environment values,
  no source code — ever.
- **provenance stamp** — `provenance()` returns `graderprobe-stamp:<install_id>`,
  the same format the signature database uses for its per-install stamp. The
  CLI prints it at the end of every report. If you paste tool output into a
  document or submission, the stamp travels with it. That is its job.

## Why this exists

Evaluation infrastructure is getting more opaque: black-box judges, hidden
prompts, undocumented harnesses. Inspecting the environment you are scored in
is defensive practice for everyone who submits to evals — and for everyone who
builds them.

## Development

```bash
python -m pip install -e .
python -m pytest -q
python -m build
```

CI runs on Python 3.10–3.12 and validates the wheel with `twine check`.

## Docs & links

- Documentation: https://ashigiri.com/graderlab
- Research notes: https://github.com/graderlab/notes
- Issues: https://github.com/graderlab/graderprobe/issues

## License

MIT
