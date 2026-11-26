from __future__ import annotations

import os

MIN_SECRET_KEY_BYTES = 32
DEFAULT_ACCESS_TOKEN_TTL_MINUTES = 60


class AuthConfigurationError(RuntimeError):
    """Raised when required authentication or database configuration is invalid."""


def get_database_url() -> str:
    """Return the configured SQLAlchemy database URL or fail closed."""
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url or not database_url.strip():
        raise AuthConfigurationError(
            "DATABASE_URL must be set for database operations."
        )
    return database_url.strip()


def get_auth_secret_key() -> str:
    """Return the signing key for bearer tokens without altering secret characters."""
    secret_key = os.getenv("APP_SECRET_KEY", "")
    if not secret_key or not secret_key.strip():
        raise AuthConfigurationError(
            "APP_SECRET_KEY must be set and cannot be empty or whitespace-only."
        )
    if len(secret_key.encode("utf-8")) < MIN_SECRET_KEY_BYTES:
        raise AuthConfigurationError(
            f"APP_SECRET_KEY must be at least {MIN_SECRET_KEY_BYTES} bytes."
        )
    return secret_key


def get_access_token_ttl_minutes() -> int:
    """Return the access-token lifetime in minutes."""
    raw = os.getenv("ACCESS_TOKEN_TTL_MINUTES", "").strip()
    if not raw:
        return DEFAULT_ACCESS_TOKEN_TTL_MINUTES
    try:
        ttl = int(raw)
    except ValueError as exc:
        raise AuthConfigurationError(
            "ACCESS_TOKEN_TTL_MINUTES must be an integer."
        ) from exc
    if ttl < 1:
        raise AuthConfigurationError("ACCESS_TOKEN_TTL_MINUTES must be at least 1.")
    return ttl
