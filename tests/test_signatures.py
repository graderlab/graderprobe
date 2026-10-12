from graderprobe import signatures
from graderprobe._provenance import install_id


def test_bundled_fallback_shape(monkeypatch):
    def offline(url, timeout):
        raise OSError("offline")

    monkeypatch.setattr(signatures, "_http_get", offline)
    payload = signatures.sync_signatures(version="0.1.0", force=True)
    assert set(payload) == {
        "pkg",
        "signatureVersion",
        "updatedAt",
        "rules",
        "note",
        "stamp",
    }
    assert payload["signatureVersion"] == 3
    assert len(payload["rules"]) == 10
    assert payload["stamp"] == f"graderprobe-stamp:{install_id}"
    rule_ids = {rule["id"] for rule in payload["rules"]}
    assert {"position-bias", "canary-hygiene", "judge-template"} <= rule_ids
    for rule in payload["rules"]:
        assert set(rule) == {"id", "title", "summary", "reference"}
        assert rule["reference"].startswith("/blog/")


def test_url_contains_install_id_and_version(monkeypatch):
    seen = {}

    def capture(url, timeout):
        seen["url"] = url
        raise OSError("offline")

    monkeypatch.setattr(signatures, "_http_get", capture)
    signatures.sync_signatures(version="9.9.9", force=True)
    assert "/api/graderlab/sync" in seen["url"]
    assert "installId=" in seen["url"]
    assert "v=9.9.9" in seen["url"]


def test_live_payload_returned_untouched(monkeypatch):
    live = {
        "pkg": "graderprobe",
        "signatureVersion": 3,
        "updatedAt": "2026-01-01T00:00:00Z",
        "rules": [],
        "note": "n",
        "stamp": "graderprobe-stamp:xyz",
    }
    monkeypatch.setattr(signatures, "_http_get", lambda url, timeout: live)
    assert signatures.sync_signatures(force=True) == live


def test_cached_payload_reused_without_network(monkeypatch, tmp_path):
    payload = {
        "pkg": "graderprobe",
        "signatureVersion": 3,
        "updatedAt": "2026-01-01T00:00:00Z",
        "rules": [],
        "note": "n",
        "stamp": "graderprobe-stamp:xyz",
    }
    monkeypatch.setattr(signatures, "_cache_dir", tmp_path)
    signatures._save_cache(payload)
    monkeypatch.setattr(signatures, "_http_get", lambda url, timeout: (_ for _ in ()).throw(OSError("offline")))
    assert signatures.sync_signatures(force=False) == payload
