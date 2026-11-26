from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from api.v1.schemas import CustomerSummaryResponse
from auth.dependencies import (
    AuthenticatedUser,
    get_accessible_customer,
    get_current_user,
    get_tenant_access,
    list_accessible_customers,
)
from db.tenant_access import TenantScopedDataAccess

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerSummaryResponse])
def list_customers(
    current_user: AuthenticatedUser = Depends(get_current_user),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
) -> list[CustomerSummaryResponse]:
    """List customers accessible to the current user (assigned-only for Collectors)."""
    customers = list_accessible_customers(access, current_user)
    return [CustomerSummaryResponse.model_validate(customer) for customer in customers]


@router.get("/{customer_id}", response_model=CustomerSummaryResponse)
def get_customer(
    customer_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
) -> CustomerSummaryResponse:
    """Fetch a single customer, enforcing tenant isolation and Collector assignment."""
    customer = get_accessible_customer(access, current_user, customer_id)
    return CustomerSummaryResponse.model_validate(customer)
