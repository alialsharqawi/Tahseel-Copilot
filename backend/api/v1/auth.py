from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.v1.schemas import ErrorResponse, LoginRequest, TokenResponse, UserResponse
from auth.dependencies import AuthenticatedUser, get_current_user, get_tenant_access
from auth.permissions import Role
from auth.security import (
    create_access_token,
    verify_password,
    verify_password_constant_time,
)
from db.models import AuditLog, User
from db.session import get_db
from db.tenant_access import TenantContext, TenantScopedDataAccess

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Sign in",
    description=(
        "Authenticate with an email and password. Include tenant_id when the same "
        "email and password identify accounts in multiple tenants. The returned "
        "bearer token is required by protected endpoints."
    ),
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Email or password is invalid.",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid email or password."}
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Matching credentials exist in multiple tenants.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Multiple tenants match this account; specify tenant_id."
                    }
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "Application authentication configuration is invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Application configuration is invalid or incomplete."
                    }
                }
            },
        },
    },
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate a user by email/password and return a signed bearer token."""
    statement = select(User).where(func.lower(User.email) == payload.email)
    if payload.tenant_id is not None:
        statement = statement.where(User.tenant_id == payload.tenant_id)
    candidates = list(db.scalars(statement).all())

    if not candidates:
        verify_password_constant_time(payload.password)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    matched_users = [
        candidate
        for candidate in candidates
        if verify_password(payload.password, candidate.password_hash)
    ]
    if not matched_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if len(matched_users) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Multiple tenants match this account; specify tenant_id.",
        )

    user = matched_users[0]
    role = Role(user.role)
    access_token, expires_in = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=role,
    )

    scoped_access = TenantScopedDataAccess(db, TenantContext(user.tenant_id))
    scoped_access.insert(
        AuditLog,
        {
            "user_id": user.id,
            "action": "auth.login",
            "entity_type": "user",
            "entity_id": str(user.id),
            "before": None,
            "after": {"role": role.value},
        },
    )
    db.commit()

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user",
    description="Return the database-backed profile for the authenticated bearer token.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Bearer token is missing, invalid, expired, or inactive.",
            "content": {
                "application/json": {"example": {"detail": "Authentication required."}}
            },
        }
    },
)
def read_current_user(
    current_user: AuthenticatedUser = Depends(get_current_user),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
) -> UserResponse:
    """Return the authenticated user's profile from their tenant."""
    user = access.get(User, current_user.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is no longer active.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse.model_validate(user)
