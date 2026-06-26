import httpx
import pytest

import apifetch as af


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_sends_auth_and_pagination(monkeypatch):
    monkeypatch.delenv("T_ds", raising=False)
    af.store_token("ds", "secret", service="T")
    captured = {}

    def handler(request):
        captured["auth"] = request.headers.get("authorization")
        captured["limit"] = request.headers.get("limit")
        return httpx.Response(200, json=[{"a": 1}, {"a": 2}])

    api = af.Api(
        "https://x.test/api",
        service="T",
        auth=af.AuthRaw(),
        pagination=af.PaginateOffset(where="header"),
    )
    rows = af.fetch(api, "ds", limit=2, client=_client(handler))

    assert rows == [{"a": 1}, {"a": 2}]
    assert captured["auth"] == "secret"
    assert captured["limit"] == "2"
    af.remove_token("ds", service="T")


def test_fetch_all_pages_until_empty(monkeypatch):
    monkeypatch.delenv("T_ds", raising=False)
    af.store_token("ds", "secret", service="T")
    pages = [
        [{"x": 1, "Mensagem": "ok"}, {"x": 2, "Mensagem": "ok"}],
        [{"x": 3, "Mensagem": "ok"}],
        [],
    ]
    calls = {"n": 0}

    def handler(request):
        page = pages[calls["n"]]
        calls["n"] += 1
        return httpx.Response(200, json=page)

    api = af.Api(
        "https://x.test/api",
        service="T",
        auth=af.AuthRaw(),
        drop_cols=("Mensagem",),
    )
    rows = af.fetch_all(api, "ds", chunk_size=2, client=_client(handler))

    assert [r["x"] for r in rows] == [1, 2, 3]
    assert all("Mensagem" not in r for r in rows)  # drop_cols applied
    af.remove_token("ds", service="T")


def test_fetch_http_error_raises():
    af.store_token("ds", "secret", service="T")

    def handler(request):
        return httpx.Response(503, text="down")

    api = af.Api("https://x.test/api", service="T", auth=af.AuthRaw())
    with pytest.raises(af.ApiError):
        af.fetch(api, "ds", client=_client(handler))
    af.remove_token("ds", service="T")


def test_fetch_missing_token_raises():
    api = af.Api("https://x.test/api", service="Empty", auth=af.AuthRaw())
    with pytest.raises(af.ApiError):
        af.fetch(api, "absent")
