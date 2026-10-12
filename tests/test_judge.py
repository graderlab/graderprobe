from graderprobe import judge_profile


def test_judge_profile_mirrors_live_endpoint():
    profile = judge_profile()
    assert set(profile) == {"template", "documentedBiases", "whatCalibrationMeasures", "note"}
    assert set(profile["template"]) == {"systemPrompt", "fields", "output"}
    assert profile["template"]["fields"] == ["question", "candidate_answer"]
    names = {bias["name"] for bias in profile["documentedBiases"]}
    assert names == {
        "position bias",
        "verbosity bias",
        "self-preference",
        "prompt sensitivity",
    }
    for bias in profile["documentedBiases"]:
        assert set(bias) == {"name", "description"}
        assert bias["description"]
    assert "swap agreement" in profile["whatCalibrationMeasures"]
    assert profile["note"]


def test_judge_profile_returns_an_independent_copy():
    first = judge_profile()
    first["template"]["systemPrompt"] = "mutated"
    first["documentedBiases"][0]["name"] = "mutated"
    second = judge_profile()
    assert second["template"]["systemPrompt"] != "mutated"
    assert second["documentedBiases"][0]["name"] != "mutated"
