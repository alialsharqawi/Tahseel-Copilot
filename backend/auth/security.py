from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from auth.permissions import Role
from core.config import get_access_token_ttl_minutes, get_auth_secret_key

JWT_ALGORITHM = "HS256"
TOKEN_TYPE = "access"
MIN_PASSWORD_LENGTH = 8

_password_hasher = PasswordHash.recommended()
# Pre-computed dummy hash keeps unknown-email login latency aligned with password verification.
_DUMMY_PASSWORD_HASH = _password_hasher.hash("dummy-timing-equalizer-secret")


class InvalidCredentialsError(Exception):
    """Raised when a bearer token is missing, malformed, expired, or invalid."""


@dataclass(frozen=True)
class TokenPayload:
    """Validated claims extracted from a signed access token."""

    user_id: UUID
    tenant_id: UUID
    role: Role
    expires_at: datetime


def validate_password_strength(password: str) -> None:
    """Enforce baseline password requirements before hashing."""
    if (
        not password
        or password.strip() != password
        or len(password) < MIN_PASSWORD_LENGTH
    ):
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters without leading or trailing spaces."
        )


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    validate_password_strength(password)
    return _password_hasher.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    if not plain_password or not password_hash:
        return False
    try:
        return _password_hasher.verify(plain_password, password_hash)
    except Exception:
        return False


def verify_password_constant_time(plain_password: str) -> None:
    """Run a dummy hash check when no user matches to limit timing side-channels."""
    verify_password(plain_password, _DUMMY_PASSWORD_HASH)


def create_access_token(
    *,
    user_id: UUID,
    tenant_id: UUID,
    role: Role,
    expires_delta: timedelta | None = None,
) -> tuple[str, int]:
    """Create a signed HS256 JWT access token and return (token, expires_in_seconds)."""
    now = datetime.now(timezone.utc)
    ttl = expires_delta or timedelta(minutes=get_access_token_ttl_minutes())
    expires_at = now + ttl
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "role": role.value,
        "type": TOKEN_TYPE,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": str(uuid4()),
    }
    token = jwt.encode(payload, get_auth_secret_key(), algorithm=JWT_ALGORITHM)
    return token, max(1, int(ttl.total_seconds()))


def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a bearer JWT access token."""
    if not token:
        raise InvalidCredentialsError("Missing access token.")
    try:
        raw_claims = jwt.decode(
            token,
            get_auth_secret_key(),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "tenant_id", "role", "exp", "iat", "type"]},
        )
    except InvalidTokenError as exc:
        raise InvalidCredentialsError("Invalid or expired access token.") from exc

    if raw_claims.get("type") != TOKEN_TYPE:
        raise InvalidCredentialsError("Invalid token type.")

    try:
        user_id = UUID(str(raw_claims["sub"]))
        tenant_id = UUID(str(raw_claims["tenant_id"]))
        role = Role(str(raw_claims["role"]))
        expires_at = datetime.fromtimestamp(int(raw_claims["exp"]), tz=timezone.utc)
    except (KeyError, ValueError, TypeError) as exc:
        raise InvalidCredentialsError("Malformed token claims.") from exc

    return TokenPayload(
        user_id=user_id,
        tenant_id=tenant_id,
        role=role,
        expires_at=expires_at,
    )
