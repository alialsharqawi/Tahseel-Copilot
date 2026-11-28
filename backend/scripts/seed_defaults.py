from __future__ import annotations

import argparse
from uuid import UUID

from auth.permissions import Permission, Role, has_permission
from configuration.service import TenantConfigurationService
from db.models import Tenant, User
from db.session import get_session_factory
from db.tenant_access import TenantContext, TenantScopedDataAccess


def seed_tenant_settings(tenant_id: UUID, actor_id: UUID) -> None:
    """Seed exact PRD §11–12 settings for an existing tenant, without overwriting."""
    with get_session_factory()() as session:
        if session.get(Tenant, tenant_id) is None:
            raise ValueError(f"Tenant {tenant_id} does not exist.")

        access = TenantScopedDataAccess(session, TenantContext(tenant_id))
        actor = access.get(User, actor_id)
        if actor is None:
            raise ValueError(f"User {actor_id} does not belong to tenant {tenant_id}.")
        if not has_permission(Role(actor.role), Permission.EDIT_TENANT_SETTINGS):
            raise ValueError("The seed actor must be an Owner or Finance Manager.")

        TenantConfigurationService(access).seed_default_settings(tenant_id, actor_id)
        session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Seed exact PRD section 11 and 12 tenant settings. Policy-rule seeding "
            "is deferred until T-021 provides approved source documents."
        )
    )
    parser.add_argument("--tenant-id", required=True, type=UUID)
    parser.add_argument("--actor-id", required=True, type=UUID)
    arguments = parser.parse_args()
    seed_tenant_settings(arguments.tenant_id, arguments.actor_id)
    print(f"Tenant settings seeding completed for {arguments.tenant_id}.")


if __name__ == "__main__":
    main()
