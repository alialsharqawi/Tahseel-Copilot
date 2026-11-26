from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.v1.schemas import (
    ErrorResponse,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from auth.dependencies import AuthenticatedUser, get_tenant_access, require_roles
from auth.permissions import Role
from auth.security import hash_password
from db.models import AuditLog, User
from db.session import get_db
from db.tenant_access import TenantScopedDataAccess

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List users",
    description="List users in the authenticated Owner's tenant. Owner-only.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Bearer token is missing, invalid, expired, or inactive.",
        },
        403: {
            "model": ErrorResponse,
            "description": "The authenticated user is not an Owner.",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient role permissions."}
                }
            },
        },
    },
)
def list_users(
    _owner: AuthenticatedUser = Depends(require_roles(Role.OWNER)),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
) -> list[UserResponse]:
    """List users in the Owner's tenant."""
    users = access.list(User)
    return [UserResponse.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user",
    description="Fetch one user from the authenticated Owner's tenant. Owner-only.",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Bearer token is missing, invalid, expired, or inactive.",
        },
        403: {
            "model": ErrorResponse,
            "description": "The authenticated user is not an Owner.",
        },
        404: {
            "model": ErrorResponse,
            "description": "No user with this ID exists in the Owner's tenant.",
            "content": {"application/json": {"example": {"detail": "User not found."}}},
        },
    },
)
def get_user(
    user_id: UUID,
    _owner: AuthenticatedUser = Depends(require_roles(Role.OWNER)),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
) -> UserResponse:
    """Fetch a single user in the Owner's tenant."""
    user = access.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return UserResponse.model_validate(user)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    description=(
        "Create a user in the authenticated Owner's tenant. The tenant_id is "
        "assigned by the server; clients cannot choose another tenant. Owner-only."
    ),
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Bearer token is missing, invalid, expired, or inactive.",
        },
        403: {
            "model": ErrorResponse,
            "description": "The authenticated user is not an Owner.",
        },
        409: {
            "model": ErrorResponse,
            "description": "A user with this email already exists in the tenant.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "A user with this email already exists in the tenant."
                    }
                }
            },
        },
    },
)
def create_user(
    payload: UserCreateRequest,
    owner: AuthenticatedUser = Depends(require_roles(Role.OWNER)),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Create a user in the Owner's tenant (Owner-only)."""
    existing = access.list(User, func.lower(User.email) == payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists in the tenant.",
        )

    try:
        created = access.insert(
            User,
            {
                "name": payload.name,
                "email": payload.email,
                "password_hash": hash_password(payload.password),
                "role": payload.role.value,
            },
        )
        access.insert(
            AuditLog,
            {
                "user_id": owner.id,
                "action": "user.create",
                "entity_type": "user",
                "entity_id": str(created.id),
                "before": None,
                "after": {
                    "name": created.name,
                    "email": created.email,
                    "role": created.role,
                },
            },
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists in the tenant.",
        ) from exc
    db.refresh(created)
    return UserResponse.model_validate(created)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    description=(
        "Update one or more of name, email, role, or password in the Owner's tenant. "
        "At least one field is required. The last Owner cannot be demoted. Owner-only."
    ),
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Bearer token is missing, invalid, expired, or inactive.",
        },
        403: {
            "model": ErrorResponse,
            "description": "The authenticated user is not an Owner.",
        },
        404: {
            "model": ErrorResponse,
            "description": "No user with this ID exists in the Owner's tenant.",
            "content": {"application/json": {"example": {"detail": "User not found."}}},
        },
        409: {
            "model": ErrorResponse,
            "description": "Email conflicts with another user or this is the last Owner.",
            "content": {
                "application/json": {
                    "example": {"detail": "Cannot demote the last Owner in the tenant."}
                }
            },
        },
    },
)
def update_user(
    user_id: UUID,
    payload: UserUpdateRequest,
    owner: AuthenticatedUser = Depends(require_roles(Role.OWNER)),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update a user's profile, role, or password within the Owner's tenant."""
    target = access.get(User, user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    updates: dict[str, object] = {}
    if payload.name is not None:
        updates["name"] = payload.name
    if payload.email is not None:
        if payload.email != target.email.lower():
            duplicates = access.list(
                User,
                func.lower(User.email) == payload.email,
                User.id != target.id,
            )
            if duplicates:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists in the tenant.",
                )
        updates["email"] = payload.email
    if payload.role is not None:
        if target.role == Role.OWNER.value and payload.role != Role.OWNER:
            # Lock OWNER rows in the tenant so concurrent demotions serialize cleanly.
            owners = access.list(User, User.role == Role.OWNER.value, for_update=True)
            if len(owners) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot demote the last Owner in the tenant.",
                )
        updates["role"] = payload.role.value
    if payload.password is not None:
        updates["password_hash"] = hash_password(payload.password)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided to update.",
        )

    before_snapshot = {
        "name": target.name,
        "email": target.email,
        "role": target.role,
    }
    try:
        access.update(User, target.id, updates)
        updated = access.get(User, target.id)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        access.insert(
            AuditLog,
            {
                "user_id": owner.id,
                "action": "user.update",
                "entity_type": "user",
                "entity_id": str(updated.id),
                "before": before_snapshot,
                "after": {
                    "name": updated.name,
                    "email": updated.email,
                    "role": updated.role,
                    "password_updated": payload.password is not None,
                },
            },
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists in the tenant.",
        ) from exc
    return UserResponse.model_validate(updated)
