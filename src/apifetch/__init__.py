"""apifetch — a generic toolkit for token-authenticated REST API retrieval.

Quick start::

    import apifetch as af

    api = af.Api(
        endpoint="https://api.example.com/v1/search",
        service="Example",
        auth=af.AuthBearer(),
        pagination=af.PaginateOffset(where="query"),
    )
    af.store_token("reports", "my-secret-token", service="Example")
    rows = af.fetch_all(api, "reports", chunk_size=1000)

This is the Python sibling of the R package ``apifetch``.
"""

from __future__ import annotations

from .api import (
    Api,
    Auth,
    AuthBearer,
    AuthHeader,
    AuthQuery,
    AuthRaw,
    PaginateNone,
    PaginateOffset,
    Pagination,
)
from .fetch import ApiError, fetch, fetch_all
from .tokens import get_token, list_tokens, remove_token, store_token

__version__ = "0.1.0"

__all__ = [
    "Api",
    "Auth",
    "AuthRaw",
    "AuthBearer",
    "AuthHeader",
    "AuthQuery",
    "Pagination",
    "PaginateOffset",
    "PaginateNone",
    "fetch",
    "fetch_all",
    "ApiError",
    "store_token",
    "get_token",
    "remove_token",
    "list_tokens",
    "__version__",
]
