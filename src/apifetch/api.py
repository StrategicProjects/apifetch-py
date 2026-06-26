"""API profiles: authentication and pagination strategies.

An :class:`Api` describes *where* to call, *how* to authenticate, and *how* to
paginate. Auth and pagination are pluggable strategy objects, so the same fetch
functions work against APIs with different conventions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ._utils import is_unset

__all__ = [
    "Auth",
    "AuthRaw",
    "AuthBearer",
    "AuthHeader",
    "AuthQuery",
    "Pagination",
    "PaginateOffset",
    "PaginateNone",
    "Api",
]


# ---- Authentication strategies -------------------------------------------


class Auth:
    """Base authentication strategy.

    Subclasses contribute to a request's headers and/or query parameters.
    """

    def headers(self, token: str) -> dict:
        return {}

    def params(self, token: str) -> dict:
        return {}


@dataclass
class AuthRaw(Auth):
    """Send the token verbatim in a header (default ``Authorization``).

    This is what the Big Data PE API expects.
    """

    header: str = "Authorization"

    def headers(self, token: str) -> dict:
        return {self.header: token}


@dataclass
class AuthBearer(Auth):
    """Send ``"<prefix><token>"`` in a header (default ``Authorization: Bearer``)."""

    header: str = "Authorization"
    prefix: str = "Bearer "

    def headers(self, token: str) -> dict:
        return {self.header: f"{self.prefix}{token}"}


@dataclass
class AuthHeader(Auth):
    """Send the token in an arbitrary header (e.g. ``X-API-Key``)."""

    header: str = "X-API-Key"

    def headers(self, token: str) -> dict:
        return {self.header: token}


@dataclass
class AuthQuery(Auth):
    """Send the token as a URL query parameter."""

    param: str = "api_key"

    def params(self, token: str) -> dict:
        return {self.param: token}


# ---- Pagination strategies -----------------------------------------------


class Pagination:
    """Base pagination strategy."""

    def headers(self, limit, offset) -> dict:
        return {}

    def params(self, limit, offset) -> dict:
        return {}


@dataclass
class PaginateOffset(Pagination):
    """Send ``limit``/``offset`` as HTTP headers (default) or query parameters.

    Non-positive, ``None`` and infinite values are omitted.
    """

    where: str = "header"  # "header" or "query"
    limit_param: str = "limit"
    offset_param: str = "offset"

    def _values(self, limit, offset) -> dict:
        vals = {}
        if not is_unset(limit):
            vals[self.limit_param] = int(limit)
        if not is_unset(offset):
            vals[self.offset_param] = int(offset)
        return vals

    def headers(self, limit, offset) -> dict:
        # HTTP header values must be strings.
        if self.where != "header":
            return {}
        return {k: str(v) for k, v in self._values(limit, offset).items()}

    def params(self, limit, offset) -> dict:
        return self._values(limit, offset) if self.where == "query" else {}


@dataclass
class PaginateNone(Pagination):
    """Send no pagination parameters."""


# ---- API profile ----------------------------------------------------------


@dataclass
class Api:
    """Describe an API endpoint together with its auth and pagination strategies.

    Args:
        endpoint: The base API URL.
        service: Namespace used to look up the token (see :func:`get_token`).
        auth: An :class:`Auth` strategy. Defaults to bearer-token auth.
        pagination: A :class:`Pagination` strategy. Defaults to offset paging
            sent as HTTP headers.
        drop_cols: Keys to drop from each record after parsing (e.g. a status
            column).
        connect_hint: Optional extra line shown on a connection error (e.g. a
            VPN requirement).
    """

    endpoint: str
    service: str = "apifetch"
    auth: Auth = field(default_factory=AuthBearer)
    pagination: Pagination = field(default_factory=PaginateOffset)
    drop_cols: tuple[str, ...] = ()
    connect_hint: str | None = None

    def __post_init__(self):
        if not self.endpoint:
            raise ValueError("endpoint must be a non-empty string.")
        if not isinstance(self.auth, Auth):
            raise TypeError("auth must be an Auth instance (e.g. AuthBearer()).")
        if not isinstance(self.pagination, Pagination):
            raise TypeError(
                "pagination must be a Pagination instance (e.g. PaginateOffset())."
            )
