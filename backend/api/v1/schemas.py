from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from auth.permissions import Role
from auth.security import validate_password_strength

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if not _EMAIL_PATTERN.match(normalized):
        raise ValueError("Invalid email address format.")
    return normalized


def _normalize_name(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Name must not be empty.")
    return normalized


class LoginRequest(BaseModel):
    """Credentials payload for POST /api/v1/auth/login."""

    email: str
    password: str = Field(min_length=1)
    tenant_id: UUID | None = None

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        return _normalize_email(value)


class UserResponse(BaseModel):
    """Public user representation; never includes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    email: str
    role: Role
    created_at: datetime


class TokenResponse(BaseModel):
    """Bearer token response returned on successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserCreateRequest(BaseModel):
    """Owner-only payload to create a user inside the current tenant."""

    name: str
    email: str
    password: str
    role: Role

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return _normalize_name(value)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        return _normalize_email(value)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class UserUpdateRequest(BaseModel):
    """Owner-only payload to update user attributes or role inside the current tenant."""

    name: str | None = None
    email: str | None = None
    role: Role | None = None
    password: str | None = None

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_name(value)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_email(value)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return None
        validate_password_strength(value)
        return value


class CustomerSummaryResponse(BaseModel):
    """Tenant- and role-scoped customer record."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    phone: str | None
    email: str | None
    credit_limit: Decimal | None
    payment_terms: str
    tier: str
    sales_rep: str | None
    assigned_collector: UUID | None
    preferred_channel: str | None
    contact_person: str | None
    status: str
    created_at: datetime
