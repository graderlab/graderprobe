"""``judge_profile()`` — what a typical LLM judge template measures.

Mirror of the public ashigiri judge profile
(``GET https://api.ashigiri.com/api/v1/judge-profile``) — same keys, same
values. It describes documented, published behavior of LLM-as-a-judge setups;
nothing else. Keep in sync with that API.
"""

from __future__ import annotations

import copy

_JUDGE_PROFILE: dict = {
    "template": {
        "systemPrompt": "rubric + criteria + scale + output format",
        "fields": ["question", "candidate_answer"],
        "output": "verdict (score / pairwise choice / rubric form)",
    },
    "documentedBiases": [
        {
            "name": "position bias",
            "description": "Order of answers in pairwise comparisons moves the verdict.",
        },
        {
            "name": "verbosity bias",
            "description": "Longer answers score higher independent of content.",
        },
        {
            "name": "self-preference",
            "description": "Judges favour answers resembling their own style.",
        },
        {
            "name": "prompt sensitivity",
            "description": "Paraphrasing the rubric shifts the scores.",
        },
    ],
    "whatCalibrationMeasures": [
        "human agreement",
        "swap agreement",
        "correlation with anchored rubrics",
    ],
    "note": (
        "Every property above is documented in the calibration literature and is "
        "fixed on the evaluator side — not in the answer."
    ),
}


def judge_profile() -> dict:
    """Return the judge profile: template, documented biases, calibration measures.

    Read-only; returns a deep copy so callers can mutate their view safely.
    """
    return copy.deepcopy(_JUDGE_PROFILE)
