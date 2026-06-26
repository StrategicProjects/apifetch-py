"""Internal helpers shared across the package."""

from __future__ import annotations

import math
import unicodedata


def sanitize_name(value: str) -> str:
    """Transliterate to ASCII (dropping accents) and turn spaces into underscores.

    This matches the contract shared by every token function so that the same
    environment-variable name is computed everywhere.
    """
    nfkd = unicodedata.normalize("NFKD", value)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    return ascii_only.replace(" ", "_")


def token_var(name: str, service: str) -> str:
    """Build the environment-variable name for a token: ``<service>_<name>``."""
    return f"{sanitize_name(service)}_{sanitize_name(name)}"


def is_unset(value) -> bool:
    """True for values that mean "no pagination bound": ``None``, ``<= 0``, ``inf``."""
    if value is None:
        return True
    if isinstance(value, float) and math.isinf(value):
        return True
    return value <= 0
