from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from configuration.schemas import (
    PolicyRuleCreate,
    PolicyRuleUpdate,
    TenantSettingsSchema,
)
from db.models import AuditLog, Document, DocumentChunk, PolicyRule, TenantSettings
from db.tenant_access import TenantScopedDataAccess


class ConfigurationRecordNotFound(LookupError):
    """Raised when a configuration record is not visible in the tenant."""


def _settings_data(settings: TenantSettingsSchema) -> dict[str, Any]:
    return settings.model_dump(mode="json", exclude_none=True)


def _rule_data(rule: PolicyRule) -> dict[str, Any]:
    return {
        "name": rule.name,
        "rule_type": rule.rule_type,
        "condition": rule.condition,
        "outcome": rule.outcome,
        "source_document_id": str(rule.source_document_id),
        "source_section": rule.source_section,
        "confirmed_by": str(rule.confirmed_by) if rule.confirmed_by else None,
        "confirmed_at": rule.confirmed_at.isoformat() if rule.confirmed_at else None,
        "active": rule.active,
    }


class TenantConfigurationService:
    """Tenant-scoped configuration operations with append-only audit entries."""

    def __init__(self, access: TenantScopedDataAccess) -> None:
        self._access = access

    def get_settings(self, tenant_id: UUID) -> TenantSettings:
        settings = self._access.get(TenantSettings, tenant_id)
        if settings is None:
            raise ConfigurationRecordNotFound("Tenant settings not found.")
        TenantSettingsSchema.model_validate(settings.settings)
        return settings

    def put_settings(
        self,
        tenant_id: UUID,
        actor_id: UUID,
        settings: TenantSettingsSchema,
    ) -> TenantSettings:
        current = self._access.get(TenantSettings, tenant_id)
        before = current.settings if current is not None else None
        new_settings = _settings_data(settings)
        now = datetime.now(timezone.utc)

        if current is None:
            record = self._access.insert(
                TenantSettings,
                {
                    "settings": new_settings,
                    "updated_by": actor_id,
                    "updated_at": now,
                },
            )
            action = "tenant_settings.create"
        else:
            if not self._access.update(
                TenantSettings,
                tenant_id,
                {"settings": new_settings, "updated_by": actor_id, "updated_at": now},
            ):
                raise ConfigurationRecordNotFound("Tenant settings not found.")
            record = self.get_settings(tenant_id)
            action = "tenant_settings.update"

        self._audit(
            actor_id,
            action,
            "tenant_settings",
            str(tenant_id),
            before,
            new_settings,
        )
        return record

    def seed_default_settings(self, tenant_id: UUID, actor_id: UUID) -> TenantSettings:
        """Insert PRD defaults once without overwriting existing tenant configuration."""
        existing = self._access.get(TenantSettings, tenant_id)
        if existing is not None:
            TenantSettingsSchema.model_validate(existing.settings)
            return existing

        settings = TenantSettingsSchema()
        record = self._access.insert(
            TenantSettings,
            {
                "settings": _settings_data(settings),
                "updated_by": actor_id,
                "updated_at": datetime.now(timezone.utc),
            },
        )
        self._audit(
            actor_id,
            "tenant_settings.seed",
            "tenant_settings",
            str(tenant_id),
            None,
            record.settings,
        )
        return record

    def list_policy_rules(self) -> list[PolicyRule]:
        return self._access.list(PolicyRule)

    def create_policy_rule(
        self, actor_id: UUID, payload: PolicyRuleCreate
    ) -> PolicyRule:
        self._require_source_document(payload.source_document_id)
        self._require_source_section(
            payload.source_document_id,
            payload.source_section,
        )
        record = self._access.insert(
            PolicyRule,
            {
                **payload.model_dump(mode="json", exclude={"source_document_id"}),
                "source_document_id": payload.source_document_id,
                "confirmed_by": None,
                "confirmed_at": None,
            },
        )
        self._audit(
            actor_id,
            "policy_rule.create",
            "policy_rule",
            str(record.id),
            None,
            _rule_data(record),
        )
        return record

    def update_policy_rule(
        self,
        actor_id: UUID,
        rule_id: UUID,
        payload: PolicyRuleUpdate,
    ) -> PolicyRule:
        current = self._access.get(PolicyRule, rule_id)
        if current is None:
            raise ConfigurationRecordNotFound("Policy rule not found.")
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise ValueError("At least one policy-rule field must be updated.")
        if any(value is None for value in updates.values()):
            raise ValueError("Policy-rule fields must not be null.")
        source_document_id = updates.get("source_document_id")
        if source_document_id is not None:
            self._require_source_document(source_document_id)
            source_section = updates["source_section"]
            if not isinstance(source_section, str):
                raise ValueError(
                    "A source section is required with the source document."
                )
            self._require_source_section(source_document_id, source_section)

        before = _rule_data(current)
        updates["confirmed_by"] = None
        updates["confirmed_at"] = None
        if not self._access.update(PolicyRule, rule_id, updates):
            raise ConfigurationRecordNotFound("Policy rule not found.")
        updated = self._access.get(PolicyRule, rule_id)
        if updated is None:
            raise ConfigurationRecordNotFound("Policy rule not found.")
        self._audit(
            actor_id,
            "policy_rule.update",
            "policy_rule",
            str(rule_id),
            before,
            _rule_data(updated),
        )
        return updated

    def confirm_policy_rule(self, actor_id: UUID, rule_id: UUID) -> PolicyRule:
        current = self._access.get(PolicyRule, rule_id)
        if current is None:
            raise ConfigurationRecordNotFound("Policy rule not found.")
        before = _rule_data(current)
        confirmed_at = datetime.now(timezone.utc)
        if not self._access.update(
            PolicyRule,
            rule_id,
            {"confirmed_by": actor_id, "confirmed_at": confirmed_at},
        ):
            raise ConfigurationRecordNotFound("Policy rule not found.")
        confirmed = self._access.get(PolicyRule, rule_id)
        if confirmed is None:
            raise ConfigurationRecordNotFound("Policy rule not found.")
        self._audit(
            actor_id,
            "policy_rule.confirm",
            "policy_rule",
            str(rule_id),
            before,
            _rule_data(confirmed),
        )
        return confirmed

    def _require_source_document(self, document_id: UUID) -> Document:
        document = self._access.get(Document, document_id)
        if document is None:
            raise ConfigurationRecordNotFound("Source document not found.")
        return document

    def _require_source_section(self, document_id: UUID, section: str) -> None:
        chunks = self._access.list(
            DocumentChunk,
            DocumentChunk.document_id == document_id,
            DocumentChunk.section == section,
            limit=1,
        )
        if not chunks:
            raise ValueError("Source section not found in the selected document.")

    def _audit(
        self,
        actor_id: UUID,
        action: str,
        entity_type: str,
        entity_id: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> None:
        self._access.insert(
            AuditLog,
            {
                "user_id": actor_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "before": before,
                "after": after,
            },
        )
