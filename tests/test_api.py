import math

import pytest

import apifetch as af


def test_auth_strategies():
    assert af.AuthRaw().headers("tok") == {"Authorization": "tok"}
    assert af.AuthBearer().headers("tok") == {"Authorization": "Bearer tok"}
    assert af.AuthHeader("X-API-Key").headers("tok") == {"X-API-Key": "tok"}
    assert af.AuthQuery("api_key").params("tok") == {"api_key": "tok"}


def test_pagination_offset_header():
    p = af.PaginateOffset(where="header")
    assert p.headers(10, 5) == {"limit": "10", "offset": "5"}  # headers are strings
    assert p.params(10, 5) == {}
    # inf / None / non-positive omitted
    assert p.headers(math.inf, 0) == {}
    assert p.headers(None, None) == {}


def test_pagination_offset_query():
    p = af.PaginateOffset(where="query")
    assert p.params(10, 0) == {"limit": 10}
    assert p.headers(10, 0) == {}


def test_api_validation():
    with pytest.raises(ValueError):
        af.Api("")
    with pytest.raises(TypeError):
        af.Api("https://x.test", auth="nope")
    with pytest.raises(TypeError):
        af.Api("https://x.test", pagination="nope")


def test_api_defaults():
    api = af.Api("https://x.test", service="S", drop_cols=("Mensagem",))
    assert isinstance(api.auth, af.AuthBearer)
    assert isinstance(api.pagination, af.PaginateOffset)
    assert api.drop_cols == ("Mensagem",)
