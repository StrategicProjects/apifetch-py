"""Token management via environment variables.

Tokens are never written to disk; they live only in process environment
variables named ``<service>_<name>``. ``service`` acts as a namespace so a single
process can hold tokens for several different APIs without clashing.
"""

from __future__ import annotations

import os

from ._utils import sanitize_name, token_var

__all__ = ["store_token", "get_token", "remove_token", "list_tokens"]


def store_token(name: str, token: str, service: str = "apifetch") -> None:
    """Store ``token`` for ``name`` in an environment variable.

    Refuses to overwrite an existing, non-empty variable.
    """
    if not name:
        raise ValueError("name must be a non-empty string.")
    if not token:
        raise ValueError("token must be a non-empty string.")

    var = token_var(name, service)
    if os.environ.get(var):
        print(f"! {var} is already defined; not overwriting to avoid data loss.")
        return

    os.environ[var] = token
    print(f"✓ Token stored in environment variable: {var}")


def get_token(name: str, service: str = "apifetch") -> str | None:
    """Return the token stored for ``name``/``service``, or ``None`` if missing."""
    if not name:
        raise ValueError("name must be a non-empty string.")

    token = os.environ.get(token_var(name, service))
    if not token:
        print(f"! No token found for {name!r} (service {service!r}).")
        return None
    return token


def remove_token(name: str, service: str = "apifetch") -> None:
    """Remove the token stored for ``name``/``service`` if present."""
    if not name:
        raise ValueError("name must be a non-empty string.")

    var = token_var(name, service)
    if os.environ.get(var):
        del os.environ[var]
        print(f"✓ Token removed for {name!r} (service {service!r}).")
    else:
        print(f"! No token found for {name!r} (service {service!r}).")


def list_tokens(service: str = "apifetch") -> list[str]:
    """Return the names (without the ``service`` prefix) of stored tokens."""
    prefix = f"{sanitize_name(service)}_"
    names = [key[len(prefix):] for key in os.environ if key.startswith(prefix)]
    if not names:
        print(f"i No tokens found for service {service!r}.")
    return sorted(names)
