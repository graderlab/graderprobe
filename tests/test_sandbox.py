import json
import os

from graderprobe.sandbox import sandbox_profile


def test_profile_shape():
    profile = sandbox_profile()
    assert set(profile) == {
        "platform",
        "machine",
        "python_version",
        "interpreter",
        "os_family",
        "writable_cwd",
        "eval_env_names",
    }
    assert isinstance(profile["writable_cwd"], bool)
    assert isinstance(profile["eval_env_names"], list)


def test_eval_env_names_are_real_sorted_unique_names():
    profile = sandbox_profile()
    names = profile["eval_env_names"]
    assert names == sorted(set(names))
    for name in names:
        assert name in os.environ
        assert "=" not in name


def test_eval_style_names_detected(monkeypatch):
    monkeypatch.setenv("RUN_ID", "x")
    monkeypatch.setenv("TASK_ID", "x")
    profile = sandbox_profile()
    assert "RUN_ID" in profile["eval_env_names"]
    assert "TASK_ID" in profile["eval_env_names"]


def test_no_value_leak(monkeypatch):
    marker = "unique-secret-marker-9f2c"
    monkeypatch.setenv("RUN_ID", marker)
    profile = sandbox_profile()
    assert "RUN_ID" in profile["eval_env_names"]
    assert marker not in json.dumps(profile, sort_keys=True)


def test_deterministic_within_process():
    first = sandbox_profile()
    second = sandbox_profile()
    assert first["platform"] == second["platform"]
    assert first["eval_env_names"] == second["eval_env_names"]
