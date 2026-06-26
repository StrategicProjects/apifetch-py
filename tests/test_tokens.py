import apifetch as af


def test_round_trip(monkeypatch):
    monkeypatch.delenv("svc_alpha", raising=False)
    af.store_token("alpha", "tok-123", service="svc")
    assert af.get_token("alpha", service="svc") == "tok-123"
    assert "alpha" in af.list_tokens(service="svc")
    af.remove_token("alpha", service="svc")
    assert af.get_token("alpha", service="svc") is None


def test_no_overwrite(monkeypatch):
    monkeypatch.delenv("svc_beta", raising=False)
    af.store_token("beta", "first", service="svc")
    af.store_token("beta", "second", service="svc")  # refused
    assert af.get_token("beta", service="svc") == "first"


def test_accents_and_spaces(monkeypatch):
    af.store_token("São Paulo", "tok", service="svc")
    assert af.get_token("São Paulo", service="svc") == "tok"
    # env var name is sanitized
    import os
    assert "svc_Sao_Paulo" in os.environ


def test_missing_returns_none():
    assert af.get_token("nope", service="absent") is None


def test_invalid_inputs():
    import pytest
    with pytest.raises(ValueError):
        af.store_token("", "tok")
    with pytest.raises(ValueError):
        af.store_token("x", "")
