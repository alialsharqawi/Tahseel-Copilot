from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import (
    AuthenticatedUser,
    get_tenant_access,
    require_permission,
)
from auth.permissions import Permission
from configuration.schemas import (
    PolicyRuleCreate,
    PolicyRuleResponse,
    PolicyRuleUpdate,
    TenantSettingsResponse,
    TenantSettingsSchema,
)
from configuration.service import (
    ConfigurationRecordNotFound,
    TenantConfigurationService,
)
from db.session import get_db
from db.tenant_access import TenantScopedDataAccess

router = APIRouter(tags=["tenant configuration"])


@router.get(
    "/settings",
    response_model=TenantSettingsResponse,
    summary="Get tenant settings",
)
def get_settings(
    user: AuthenticatedUser = Depends(
        require_permission(Permission.EDIT_TENANT_SETTINGS)
    ),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
) -> TenantSettingsResponse:
    try:
        record = TenantConfigurationService(access).get_settings(user.tenant_id)
    except ConfigurationRecordNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return TenantSettingsResponse.model_validate(record)


@router.put(
    "/settings",
    response_model=TenantSettingsResponse,
    summary="Create or update tenant settings",
)
def put_settings(
    payload: TenantSettingsSchema,
    user: AuthenticatedUser = Depends(
        require_permission(Permission.EDIT_TENANT_SETTINGS)
    ),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
    db: Session = Depends(get_db),
) -> TenantSettingsResponse:
    record = TenantConfigurationService(access).put_settings(
        user.tenant_id,
        user.id,
        payload,
    )
    db.commit()
    db.refresh(record)
    return TenantSettingsResponse.model_validate(record)


@router.get(
    "/policy-rules",
    response_model=list[PolicyRuleResponse],
    summary="List tenant policy rules",
)
def list_policy_rules(
    _user: AuthenticatedUser = Depends(
        require_permission(Permission.MANAGE_POLICY_RULES)
    ),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
) -> list[PolicyRuleResponse]:
    records = TenantConfigurationService(access).list_policy_rules()
    return [PolicyRuleResponse.model_validate(record) for record in records]


@router.post(
    "/policy-rules",
    response_model=PolicyRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tenant policy rule",
)
def create_policy_rule(
    payload: PolicyRuleCreate,
    user: AuthenticatedUser = Depends(
        require_permission(Permission.MANAGE_POLICY_RULES)
    ),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
    db: Session = Depends(get_db),
) -> PolicyRuleResponse:
    try:
        record = TenantConfigurationService(access).create_policy_rule(
            user.id,
            payload,
        )
    except ConfigurationRecordNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.commit()
    db.refresh(record)
    return PolicyRuleResponse.model_validate(record)


@router.patch(
    "/policy-rules/{rule_id}",
    response_model=PolicyRuleResponse,
    summary="Update a tenant policy rule",
)
def update_policy_rule(
    rule_id: UUID,
    payload: PolicyRuleUpdate,
    user: AuthenticatedUser = Depends(
        require_permission(Permission.MANAGE_POLICY_RULES)
    ),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
    db: Session = Depends(get_db),
) -> PolicyRuleResponse:
    try:
        record = TenantConfigurationService(access).update_policy_rule(
            user.id,
            rule_id,
            payload,
        )
    except ConfigurationRecordNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.commit()
    db.refresh(record)
    return PolicyRuleResponse.model_validate(record)


@router.post(
    "/policy-rules/{rule_id}/confirm",
    response_model=PolicyRuleResponse,
    summary="Confirm a tenant policy rule",
)
def confirm_policy_rule(
    rule_id: UUID,
    user: AuthenticatedUser = Depends(
        require_permission(Permission.MANAGE_POLICY_RULES)
    ),
    access: TenantScopedDataAccess = Depends(get_tenant_access),
    db: Session = Depends(get_db),
) -> PolicyRuleResponse:
    try:
        record = TenantConfigurationService(access).confirm_policy_rule(
            user.id, rule_id
        )
    except ConfigurationRecordNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    db.refresh(record)
    return PolicyRuleResponse.model_validate(record)
