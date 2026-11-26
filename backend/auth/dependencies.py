from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from auth.permissions import Permission, Role, has_permission
from auth.security import InvalidCredentialsError, decode_access_token
from db.models import Customer, User
from db.session import get_db
from db.tenant_access import TenantContext, TenantScopedDataAccess

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    """Server-verified user identity loaded from the database."""

    id: UUID
    tenant_id: UUID
    name: str
    email: str
    role: Role


def _unauthorized(detail: str = "Could not validate credentials.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """Authenticate the bearer token and load authoritative user state from DB."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Authentication required.")

    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidCredentialsError as exc:
        raise _unauthorized(str(exc)) from exc

    # Re-read the user inside the token's tenant so deleted users or role updates apply immediately.
    scoped_access = TenantScopedDataAccess(db, TenantContext(payload.tenant_id))
    user = scoped_access.get(User, payload.user_id)
    if user is None:
        raise _unauthorized("User account is no longer active.")

    try:
        authoritative_role = Role(user.role)
    except ValueError as exc:
        raise _unauthorized("User role is invalid.") from exc

    return AuthenticatedUser(
        id=user.id,
        tenant_id=user.tenant_id,
        name=user.name,
        email=user.email,
        role=authoritative_role,
    )


def get_tenant_access(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenantScopedDataAccess:
    """Return a TenantScopedDataAccess bound strictly to the authenticated user's tenant."""
    return TenantScopedDataAccess(db, TenantContext(current_user.tenant_id))


def require_roles(
    *allowed_roles: Role,
) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """Dependency enforcing that the authenticated user holds one of the allowed roles."""
    allowed = frozenset(allowed_roles)

    def _check_role(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions.",
            )
        return current_user

    return _check_role


def require_permission(
    permission: Permission,
) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """Dependency enforcing a named permission from Decision Log D15/D30."""

    def _check_permission(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation.",
            )
        return current_user

    return _check_permission


def enforce_recommendation_approval_role(
    access: TenantScopedDataAccess,
    current_user: AuthenticatedUser,
    customer_id: UUID,
    *,
    requires_manager_review: bool,
) -> Customer:
    """Enforce AC-014 and D15: customer assignment and manager-review rules."""
    customer = get_accessible_customer(access, current_user, customer_id)
    required_permission = (
        Permission.APPROVE_MANAGER_REVIEW_RECOMMENDATION
        if requires_manager_review
        else Permission.APPROVE_ROUTINE_RECOMMENDATION
    )
    if not has_permission(current_user.role, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager role is required to approve flagged recommendations.",
        )
    return customer


def list_accessible_customers(
    access: TenantScopedDataAccess,
    current_user: AuthenticatedUser,
) -> list[Customer]:
    """List customers in the tenant, restricted to assigned customers for Collectors."""
    if has_permission(current_user.role, Permission.VIEW_ALL_CUSTOMERS):
        return access.list(Customer)
    return access.list(Customer, Customer.assigned_collector == current_user.id)


def get_accessible_customer(
    access: TenantScopedDataAccess,
    current_user: AuthenticatedUser,
    customer_id: UUID,
) -> Customer:
    """Fetch a tenant-scoped customer, blocking Collectors from unassigned records."""
    customer = access.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )
    if (
        not has_permission(current_user.role, Permission.VIEW_ALL_CUSTOMERS)
        and customer.assigned_collector != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Collectors can only access assigned customers.",
        )
    return customer
