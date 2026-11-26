from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    """Application roles defined in Decision Log D15 and D30."""

    OWNER = "OWNER"
    FINANCE_MANAGER = "FINANCE_MANAGER"
    COLLECTOR = "COLLECTOR"


class Permission(str, Enum):
    """Capabilities from the D15/D30 permissions matrix."""

    IMPORT_DATA_AND_POLICIES = "import_data_and_policies"
    VIEW_ALL_CUSTOMERS = "view_all_customers"
    VIEW_ASSIGNED_CUSTOMERS = "view_assigned_customers"
    APPROVE_ROUTINE_RECOMMENDATION = "approve_routine_recommendation"
    APPROVE_MANAGER_REVIEW_RECOMMENDATION = "approve_manager_review_recommendation"
    ASSIGN_TASKS = "assign_tasks"
    VIEW_AUDIT_LOG = "view_audit_log"
    RECORD_CUSTOMER_MEMORY = "record_customer_memory"
    DISPUTE_INVOICE = "dispute_invoice"
    CLEAR_DISPUTE = "clear_dispute"
    OVERRIDE_REMINDER_CAP = "override_reminder_cap"
    MANAGE_POLICY_RULES = "manage_policy_rules"
    EDIT_TENANT_SETTINGS = "edit_tenant_settings"
    SOFT_DELETE_MEMORY = "soft_delete_memory"
    VIEW_EXECUTIVE_DASHBOARD = "view_executive_dashboard"
    MANAGE_USERS = "manage_users"


_MANAGER_ROLES: frozenset[Role] = frozenset({Role.OWNER, Role.FINANCE_MANAGER})
_ALL_ROLES: frozenset[Role] = frozenset(Role)

ROLE_PERMISSIONS: dict[Permission, frozenset[Role]] = {
    Permission.IMPORT_DATA_AND_POLICIES: _MANAGER_ROLES,
    Permission.VIEW_ALL_CUSTOMERS: _MANAGER_ROLES,
    Permission.VIEW_ASSIGNED_CUSTOMERS: _ALL_ROLES,
    Permission.APPROVE_ROUTINE_RECOMMENDATION: _ALL_ROLES,
    Permission.APPROVE_MANAGER_REVIEW_RECOMMENDATION: _MANAGER_ROLES,
    Permission.ASSIGN_TASKS: _MANAGER_ROLES,
    Permission.VIEW_AUDIT_LOG: _MANAGER_ROLES,
    Permission.RECORD_CUSTOMER_MEMORY: _ALL_ROLES,
    Permission.DISPUTE_INVOICE: _ALL_ROLES,
    Permission.CLEAR_DISPUTE: _MANAGER_ROLES,
    Permission.OVERRIDE_REMINDER_CAP: _MANAGER_ROLES,
    Permission.MANAGE_POLICY_RULES: _MANAGER_ROLES,
    Permission.EDIT_TENANT_SETTINGS: _MANAGER_ROLES,
    Permission.SOFT_DELETE_MEMORY: _MANAGER_ROLES,
    Permission.VIEW_EXECUTIVE_DASHBOARD: _MANAGER_ROLES,
    Permission.MANAGE_USERS: frozenset({Role.OWNER}),
}


def has_permission(role: Role, permission: Permission) -> bool:
    """Return True if the given role holds the requested D15/D30 permission."""
    return role in ROLE_PERMISSIONS[permission]
