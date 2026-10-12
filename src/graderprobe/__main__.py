"""CLI: ``python -m graderprobe`` — judge profile, sandbox profile, provenance."""

from __future__ import annotations

import sys

from . import __version__
from ._provenance import BUILD_SERIAL, provenance
from .judge import judge_profile
from .sandbox import sandbox_profile


def main(argv: list[str] | None = None) -> int:
    """Print the full report and return 0."""
    del argv  # no arguments; kept for console-script compatibility
    judge = judge_profile()
    box = sandbox_profile()
    out = sys.stdout

    out.write(f"graderprobe {__version__} — eval infrastructure profile\n")
    out.write(f"build: {BUILD_SERIAL}\n\n")

    template = judge["template"]
    out.write("JUDGE PROFILE\n")
    out.write(f"  systemPrompt: {template['systemPrompt']}\n")
    out.write(f"  fields:       {', '.join(template['fields'])}\n")
    out.write(f"  output:       {template['output']}\n")
    biases = ", ".join(b["name"] for b in judge["documentedBiases"])
    out.write(f"  documented biases: {biases}\n")
    calibration = ", ".join(judge["whatCalibrationMeasures"])
    out.write(f"  calibration measures: {calibration}\n\n")

    out.write("SANDBOX PROFILE\n")
    out.write(f"  platform:     {box['platform']}\n")
    out.write(f"  python:       {box['python_version']}\n")
    out.write(f"  interpreter:  {box['interpreter']}\n")
    out.write(f"  os_family:    {box['os_family']}\n")
    out.write(f"  writable_cwd: {str(box['writable_cwd']).lower()}\n")
    eval_names = ", ".join(box["eval_env_names"]) or "(none detected)"
    out.write(f"  eval_env:     {eval_names}   (names only, never values)\n\n")

    out.write("PROVENANCE\n")
    out.write(f"  {provenance()}\n\n")

    out.write("SIGNATURES\n")
    out.write("  run graderprobe.sync_signatures() to fetch the current signature database\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
