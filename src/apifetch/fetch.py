"""Data fetching: single page and chunked retrieval."""

from __future__ import annotations

import math
import sys
from typing import Any, Optional

import httpx

from .api import Api
from .tokens import get_token

__all__ = ["fetch", "fetch_all", "ApiError"]


class ApiError(RuntimeError):
    """Raised when the API is unreachable or returns an HTTP error."""


def _log(verbosity: int, message: str) -> None:
    if verbosity > 0:
        print(message, file=sys.stderr)


def fetch(
    api: Api,
    name: str,
    limit: Optional[float] = None,
    offset: int = 0,
    query: Optional[dict] = None,
    verbosity: int = 0,
    client: Optional[httpx.Client] = None,
) -> list[dict[str, Any]]:
    """Fetch a single page from ``api`` and return it as a list of records.

    Args:
        api: An :class:`Api` profile.
        name: Token name to authenticate with (looked up via ``api.service``).
        limit: Maximum records to request. ``None``/``inf`` means no limit.
        offset: Starting record (omitted when ``0``).
        query: Extra query-string filters.
        verbosity: ``0`` silent, ``>=1`` progress messages.
        client: Optional pre-built ``httpx.Client`` (useful for testing or
            connection reuse). One is created and closed per call otherwise.

    Returns:
        The parsed JSON body as a list of dictionaries.
    """
    if not isinstance(api, Api):
        raise TypeError("api must be an Api instance (see apifetch.Api).")
    query = query or {}

    token = get_token(name, service=api.service)
    if token is None:
        raise ApiError(
            f"No token available for {name!r}; store one with apifetch.store_token()."
        )

    headers = {**api.auth.headers(token), **api.pagination.headers(limit, offset)}
    params = {**query, **api.auth.params(token), **api.pagination.params(limit, offset)}

    owns_client = client is None
    client = client or httpx.Client()
    try:
        try:
            resp = client.get(api.endpoint, headers=headers, params=params)
        except httpx.RequestError as exc:
            hint = f" {api.connect_hint}" if api.connect_hint else ""
            raise ApiError(
                f"Unable to connect to the API at {api.endpoint}. "
                f"Check your network connection.{hint} ({exc})"
            ) from exc
    finally:
        if owns_client:
            client.close()

    if resp.status_code >= 400:
        raise ApiError(
            f"The API returned an error (HTTP {resp.status_code} - {resp.reason_phrase}). "
            "Try again later, and check that the endpoint and token are valid."
        )

    data = resp.json()
    if isinstance(data, dict):
        data = [data]
    _log(verbosity, f"i Fetched {len(data)} records.")
    return data


def fetch_all(
    api: Api,
    name: str,
    total_limit: Optional[float] = None,
    chunk_size: int = 50_000,
    query: Optional[dict] = None,
    verbosity: int = 0,
    client: Optional[httpx.Client] = None,
) -> list[dict[str, Any]]:
    """Fetch every record by paging through ``api`` in chunks.

    Iteratively calls :func:`fetch` with an advancing ``offset`` until a chunk
    comes back empty or ``total_limit`` is reached. Columns listed in
    ``api.drop_cols`` are removed from each record.
    """
    if not isinstance(api, Api):
        raise TypeError("api must be an Api instance (see apifetch.Api).")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    total = math.inf if total_limit is None else total_limit
    offset = 0
    fetched = 0
    records: list[dict[str, Any]] = []

    owns_client = client is None
    client = client or httpx.Client()
    try:
        while True:
            current_limit = int(min(chunk_size, total - fetched))
            if current_limit <= 0:
                break

            chunk = fetch(
                api, name,
                limit=current_limit,
                offset=offset,
                query=query,
                verbosity=verbosity,
                client=client,
            )
            if api.drop_cols:
                chunk = [
                    {k: v for k, v in row.items() if k not in api.drop_cols}
                    for row in chunk
                ]
            if not chunk:
                break

            records.extend(chunk)
            fetched += len(chunk)
            offset += len(chunk)
            _log(verbosity, f"i Fetched {len(chunk)} records (total: {fetched}).")

            if fetched >= total:
                break
    finally:
        if owns_client:
            client.close()

    _log(verbosity, f"✓ Fetching complete: {len(records)} records retrieved.")
    return records
