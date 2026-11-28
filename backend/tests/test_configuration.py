from __future__ import annotations

from datetime import timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from auth.dependencies import AuthenticatedUser, get_current_user, get_tenant_access
from auth.permissions import Role
from configuration.schemas import (
    PolicyRuleCreate,
    PolicyRuleUpdate,
    RiskWeights,
    TenantSettingsSchema,
)
from configuration.service import (
    ConfigurationRecordNotFound,
    TenantConfigurationService,
)
from db.models import AuditLog, Document, DocumentChunk, PolicyRule, TenantSettings
from db.session import get_db
from main import app


class TenantAccessStub:
    def __init__(self, tenant_id: UUID) -> None:
        self.tenant_id = tenant_id
        self.records: dict[type[object], dict[UUID, object]] = {}

    def get(self, model: type[object], record_id: UUID) -> object | None:
        record = self.records.get(model, {}).get(record_id)
        if record is None or getattr(record, "tenant_id", None) != self.tenant_id:
            return None
        return record

    def list(
        self,
        model: type[object],
        *conditions: object,
        limit: int | None = None,
    ) -> list[object]:
        records = [
            record
            for record in self.records.get(model, {}).values()
            if getattr(record, "tenant_id", None) == self.tenant_id
        ]
        for condition in conditions:
            field_name = condition.left.key
            expected = condition.right.value
            records = [
                record for record in records if getattr(record, field_name) == expected
            ]
        return records[:limit] if limit is not None else records

    def insert(self, model: type[object], values: dict[str, object]) -> object:
        record_values = {**values, "tenant_id": self.tenant_id}
        record = model(**record_values)
        record.id = uuid4()
        if isinstance(record, TenantSettings):
            record.id = record.tenant_id
        self.records.setdefault(model, {})[record.id] = record
        return record

    def update(
        self, model: type[object], record_id: UUID, values: dict[str, object]
    ) -> bool:
        record = self.get(model, record_id)
        if record is None:
            return False
        for field, value in values.items():
            setattr(record, field, value)
        return True


class SessionStub:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, _record: object) -> None:
        return None


@pytest.fixture
def configuration_client(monkeypatch: pytest.MonkeyPatch):
    tenant_id = uuid4()
    user_id = uuid4()
    role = {"value": Role.FINANCE_MANAGER}
    access = TenantAccessStub(tenant_id)
    session = SessionStub()

    def current_user() -> AuthenticatedUser:
        return AuthenticatedUser(
            id=user_id,
            tenant_id=tenant_id,
            name="Synthetic Manager",
            email="manager@example.test",
            role=role["value"],
        )

    monkeypatch.setitem(app.dependency_overrides, get_current_user, current_user)
    monkeypatch.setitem(app.dependency_overrides, get_tenant_access, lambda: access)
    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: session)
    with TestClient(app) as client:
        yield client, access, role, session, user_id, tenant_id


def _policy_payload(document_id: UUID) -> PolicyRuleCreate:
    return PolicyRuleCreate(
        name="Manager review",
        rule_type="review_required",
        condition={"days_overdue": {"gt": 30}},
        outcome={"requires_manager_review": True},
        source_document_id=document_id,
        source_section="§2.1",
    )


def _document(tenant_id: UUID) -> Document:
    document = Document(
        tenant_id=tenant_id,
        name="Synthetic policy",
        type="collection_policy",
        storage_path="synthetic/policy.md",
        uploaded_by=uuid4(),
    )
    document.id = uuid4()
    return document


def _chunk(tenant_id: UUID, document_id: UUID, section: str) -> DocumentChunk:
    chunk = DocumentChunk(
        tenant_id=tenant_id,
        document_id=document_id,
        policy_type="collection_policy",
        section=section,
        text=f"Synthetic section {section}",
    )
    chunk.id = uuid4()
    return chunk


def test_tenant_settings_schema_uses_prd_section_11_and_12_defaults() -> None:
    settings = TenantSettingsSchema()

    assert settings.risk_weights == RiskWeights(
        days_overdue=30,
        historical_payment_delay=25,
        broken_promises=25,
        recent_payment_behavior=20,
    )
    assert settings.risk_caps.model_dump() == {
        "days_overdue": 60,
        "historical_payment_delay": 45,
        "broken_promises": 3,
        "recent_payment_behavior": 30,
    }
    assert settings.min_history_invoices == 3
    assert settings.insufficient_history_ratio == 0.4
    assert settings.urgency.broken_promise_multiplier == 2.0
    assert settings.urgency.broken_promise_window_days == 7
    assert settings.urgency.escalation_crossing_multiplier == 2.0
    assert settings.urgency.escalation_crossing_window_days == 7
    assert settings.urgency.upcoming_promise_multiplier == 1.5
    assert settings.urgency.upcoming_promise_window_days == 3
    assert settings.urgency.no_contact_multiplier == 1.5
    assert settings.urgency.follow_up_interval_days == 7
    assert settings.urgency.default_multiplier == 1.0
    assert settings.escalation_trigger_days == (30, 60, 90)
    assert settings.promise_grace_days == 2
    assert settings.reminder_cap is None


@pytest.mark.parametrize(
    "values",
    [
        {"days_overdue": 29},
        {"days_overdue": -1, "historical_payment_delay": 26},
        {"days_overdue": 30, "historical_payment_delay": 25, "unknown": 25},
    ],
)
def test_risk_weight_validation_rejects_invalid_values(
    values: dict[str, int],
) -> None:
    with pytest.raises(ValidationError):
        RiskWeights(**values)


def test_settings_validation_rejects_invalid_thresholds_and_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TenantSettingsSchema(escalation_trigger_days=(30, 30, 90))
    with pytest.raises(ValidationError):
        TenantSettingsSchema(insufficient_history_ratio=1.1)
    with pytest.raises(ValidationError):
        TenantSettingsSchema(unreviewed_setting=10)


def test_policy_rule_requires_source_document_and_section() -> None:
    with pytest.raises(ValidationError):
        PolicyRuleCreate(
            name="Manager review",
            rule_type="review_required",
            condition={"days_overdue": {"gt": 30}},
            outcome={"requires_manager_review": True},
            source_document_id=uuid4(),
            source_section="  ",
        )
    with pytest.raises(ValidationError):
        PolicyRuleCreate(
            name="Manager review",
            rule_type="review_required",
            condition={"invalid": {1, 2}},
            outcome={"requires_manager_review": True},
            source_document_id=uuid4(),
            source_section="§2.1",
        )
    with pytest.raises(ValidationError, match="must be updated together"):
        PolicyRuleUpdate(source_document_id=uuid4())
    with pytest.raises(ValidationError, match="must be updated together"):
        PolicyRuleUpdate(source_section="§2.1")


def test_policy_rule_source_must_be_visible_in_authenticated_tenant() -> None:
    tenant_id = uuid4()
    other_tenant = uuid4()
    access = TenantAccessStub(tenant_id)
    document = _document(other_tenant)
    access.records.setdefault(Document, {})[document.id] = document

    with pytest.raises(ConfigurationRecordNotFound, match="Source document not found"):
        TenantConfigurationService(access).create_policy_rule(
            uuid4(), _policy_payload(document.id)
        )
    assert access.list(PolicyRule) == []


def test_policy_rule_create_rejects_a_section_missing_from_the_source_document() -> (
    None
):
    tenant_id = uuid4()
    access = TenantAccessStub(tenant_id)
    document = _document(tenant_id)
    access.records.setdefault(Document, {})[document.id] = document

    with pytest.raises(ValueError, match="Source section not found"):
        TenantConfigurationService(access).create_policy_rule(
            uuid4(),
            _policy_payload(document.id).model_copy(update={"source_section": "§9.9"}),
        )

    assert access.list(PolicyRule) == []
    assert access.list(AuditLog) == []


def test_policy_rule_create_accepts_an_existing_source_section() -> None:
    tenant_id = uuid4()
    actor_id = uuid4()
    access = TenantAccessStub(tenant_id)
    document = _document(tenant_id)
    access.records.setdefault(Document, {})[document.id] = document
    chunk = _chunk(tenant_id, document.id, "§2.1")
    access.records.setdefault(DocumentChunk, {})[chunk.id] = chunk

    created = TenantConfigurationService(access).create_policy_rule(
        actor_id,
        _policy_payload(document.id),
    )

    assert created.source_document_id == document.id
    assert created.source_section == "§2.1"
    assert created.active is False
    assert created.confirmed_by is None
    assert created.confirmed_at is None
    assert [entry.action for entry in access.list(AuditLog)] == ["policy_rule.create"]


def test_policy_rule_create_update_and_confirmation_are_audited() -> None:
    tenant_id = uuid4()
    actor_id = uuid4()
    access = TenantAccessStub(tenant_id)
    document = _document(tenant_id)
    access.records.setdefault(Document, {})[document.id] = document
    chunk = _chunk(tenant_id, document.id, "§2.1")
    access.records.setdefault(DocumentChunk, {})[chunk.id] = chunk
    service = TenantConfigurationService(access)

    created = service.create_policy_rule(actor_id, _policy_payload(document.id))
    assert created.source_document_id == document.id
    assert created.source_section == "§2.1"
    assert created.active is False
    assert created.confirmed_by is None
    assert created.confirmed_at is None

    confirmed = service.confirm_policy_rule(actor_id, created.id)
    assert confirmed.active is True
    assert confirmed.confirmed_by == actor_id
    assert confirmed.confirmed_at is not None
    assert confirmed.confirmed_at.tzinfo == timezone.utc

    updated = service.update_policy_rule(
        actor_id,
        created.id,
        PolicyRuleUpdate(outcome={"requires_manager_review": False}),
    )
    assert updated.outcome == {"requires_manager_review": False}
    assert updated.active is False
    assert updated.confirmed_by is None
    assert updated.confirmed_at is None

    audits = access.list(AuditLog)
    assert [entry.action for entry in audits] == [
        "policy_rule.create",
        "policy_rule.confirm",
        "policy_rule.update",
    ]
    assert audits[0].after["source_document_id"] == str(document.id)
    assert audits[0].after["active"] is False
    assert audits[1].before["confirmed_by"] is None
    assert audits[1].before["active"] is False
    assert audits[1].after["confirmed_by"] == str(actor_id)
    assert audits[1].after["active"] is True
    assert audits[2].before["outcome"] == {"requires_manager_review": True}
    assert audits[2].before["active"] is True
    assert audits[2].after["outcome"] == {"requires_manager_review": False}
    assert audits[2].after["active"] is False


def test_policy_rule_update_accepts_a_section_from_the_selected_document() -> None:
    tenant_id = uuid4()
    actor_id = uuid4()
    access = TenantAccessStub(tenant_id)
    original_document = _document(tenant_id)
    replacement_document = _document(tenant_id)
    access.records.setdefault(Document, {})[original_document.id] = original_document
    access.records[Document][replacement_document.id] = replacement_document
    original_chunk = _chunk(tenant_id, original_document.id, "§2.1")
    replacement_chunk = _chunk(tenant_id, replacement_document.id, "§3.1")
    access.records.setdefault(DocumentChunk, {})[original_chunk.id] = original_chunk
    access.records[DocumentChunk][replacement_chunk.id] = replacement_chunk
    service = TenantConfigurationService(access)
    rule = service.create_policy_rule(actor_id, _policy_payload(original_document.id))

    updated = service.update_policy_rule(
        actor_id,
        rule.id,
        PolicyRuleUpdate(
            source_document_id=replacement_document.id,
            source_section="§3.1",
        ),
    )

    assert updated.source_document_id == replacement_document.id
    assert updated.source_section == "§3.1"


def test_policy_rule_update_rejects_a_section_missing_from_the_selected_document() -> (
    None
):
    tenant_id = uuid4()
    actor_id = uuid4()
    access = TenantAccessStub(tenant_id)
    document = _document(tenant_id)
    access.records.setdefault(Document, {})[document.id] = document
    chunk = _chunk(tenant_id, document.id, "§2.1")
    access.records.setdefault(DocumentChunk, {})[chunk.id] = chunk
    service = TenantConfigurationService(access)
    rule = service.create_policy_rule(actor_id, _policy_payload(document.id))

    with pytest.raises(ValueError, match="Source section not found"):
        service.update_policy_rule(
            actor_id,
            rule.id,
            PolicyRuleUpdate(
                source_document_id=document.id,
                source_section="§9.9",
            ),
        )


def test_policy_rule_update_rejects_a_document_from_another_tenant() -> None:
    tenant_id = uuid4()
    actor_id = uuid4()
    access = TenantAccessStub(tenant_id)
    local_document = _document(tenant_id)
    other_tenant_document = _document(uuid4())
    access.records.setdefault(Document, {})[local_document.id] = local_document
    access.records[Document][other_tenant_document.id] = other_tenant_document
    local_chunk = _chunk(tenant_id, local_document.id, "§2.1")
    access.records.setdefault(DocumentChunk, {})[local_chunk.id] = local_chunk
    service = TenantConfigurationService(access)
    rule = service.create_policy_rule(actor_id, _policy_payload(local_document.id))

    with pytest.raises(ConfigurationRecordNotFound, match="Source document not found"):
        service.update_policy_rule(
            actor_id,
            rule.id,
            PolicyRuleUpdate(
                source_document_id=other_tenant_document.id,
                source_section="§3.1",
            ),
        )


def test_settings_updates_are_audited_with_before_and_after_values() -> None:
    tenant_id = uuid4()
    actor_id = uuid4()
    access = TenantAccessStub(tenant_id)
    service = TenantConfigurationService(access)

    created = service.put_settings(tenant_id, actor_id, TenantSettingsSchema())
    changed_settings = TenantSettingsSchema(
        risk_weights={
            "days_overdue": 35,
            "historical_payment_delay": 20,
            "broken_promises": 25,
            "recent_payment_behavior": 20,
        }
    )
    updated = service.put_settings(tenant_id, actor_id, changed_settings)

    audits = access.list(AuditLog)
    assert [entry.action for entry in audits] == [
        "tenant_settings.create",
        "tenant_settings.update",
    ]
    assert audits[0].before is None
    assert audits[0].after["risk_weights"]["days_overdue"] == 30
    assert audits[1].before["risk_weights"]["days_overdue"] == 30
    assert audits[1].after["risk_weights"]["days_overdue"] == 35
    assert created.tenant_id == updated.tenant_id == tenant_id


def test_settings_update_persists_updated_at() -> None:
    tenant_id = uuid4()
    actor_id = uuid4()
    access = TenantAccessStub(tenant_id)
    service = TenantConfigurationService(access)

    created = service.put_settings(tenant_id, actor_id, TenantSettingsSchema())
    first_updated_at = created.updated_at

    changed_settings = TenantSettingsSchema(
        risk_weights={
            "days_overdue": 35,
            "historical_payment_delay": 20,
            "broken_promises": 25,
            "recent_payment_behavior": 20,
        }
    )
    updated = service.put_settings(tenant_id, actor_id, changed_settings)

    assert updated.updated_at is not None
    assert updated.updated_at > first_updated_at


def test_settings_seed_is_idempotent_and_does_not_overwrite_changes() -> None:
    tenant_id = uuid4()
    actor_id = uuid4()
    access = TenantAccessStub(tenant_id)
    service = TenantConfigurationService(access)

    seeded = service.seed_default_settings(tenant_id, actor_id)
    seeded_at = seeded.updated_at
    changed = TenantSettingsSchema(
        risk_weights={
            "days_overdue": 35,
            "historical_payment_delay": 20,
            "broken_promises": 25,
            "recent_payment_behavior": 20,
        }
    )
    service.put_settings(tenant_id, actor_id, changed)
    second_seed = service.seed_default_settings(tenant_id, actor_id)

    assert second_seed.settings["risk_weights"]["days_overdue"] == 35
    assert second_seed.updated_at >= seeded_at
    assert [entry.action for entry in access.list(AuditLog)] == [
        "tenant_settings.seed",
        "tenant_settings.update",
    ]


def test_seeded_default_settings_omit_unspecified_prd_values() -> None:
    tenant_id = uuid4()
    access = TenantAccessStub(tenant_id)
    record = TenantConfigurationService(access).seed_default_settings(
        tenant_id, uuid4()
    )

    assert record.settings["promise_grace_days"] == 2
    assert "grace_period_days" not in record.settings
    assert "reminder_cap" not in record.settings
    assert "tone_defaults_by_tier" not in record.settings


def test_settings_api_is_manager_only_and_audits_changes(
    configuration_client: tuple[
        TestClient, TenantAccessStub, dict[str, Role], SessionStub, UUID, UUID
    ],
) -> None:
    client, access, role, session, user_id, tenant_id = configuration_client
    role["value"] = Role.COLLECTOR
    payload = TenantSettingsSchema().model_dump(mode="json")

    denied = client.put("/api/v1/settings", json=payload)
    assert denied.status_code == 403
    assert access.list(TenantSettings) == []

    role["value"] = Role.FINANCE_MANAGER
    created = client.put("/api/v1/settings", json=payload)
    assert created.status_code == 200
    assert created.json()["tenant_id"] == str(tenant_id)
    assert created.json()["updated_by"] == str(user_id)
    assert session.commits == 1
    assert [entry.action for entry in access.list(AuditLog)] == [
        "tenant_settings.create"
    ]


def test_policy_rule_api_requires_tenant_source_and_audits_confirmation(
    configuration_client: tuple[
        TestClient, TenantAccessStub, dict[str, Role], SessionStub, UUID, UUID
    ],
) -> None:
    client, access, _role, session, user_id, tenant_id = configuration_client
    other_tenant_document = _document(uuid4())
    access.records.setdefault(Document, {})[other_tenant_document.id] = (
        other_tenant_document
    )
    payload = _policy_payload(other_tenant_document.id).model_dump(mode="json")

    denied_source = client.post("/api/v1/policy-rules", json=payload)
    assert denied_source.status_code == 404
    assert access.list(PolicyRule) == []

    document = _document(tenant_id)
    access.records[Document][document.id] = document
    chunk = _chunk(tenant_id, document.id, "§2.1")
    access.records.setdefault(DocumentChunk, {})[chunk.id] = chunk
    payload["source_document_id"] = str(document.id)
    payload["active"] = True
    rejected_active = client.post("/api/v1/policy-rules", json=payload)
    assert rejected_active.status_code == 422
    assert access.list(PolicyRule) == []
    assert access.list(AuditLog) == []

    payload.pop("active")
    created = client.post("/api/v1/policy-rules", json=payload)
    assert created.status_code == 201
    rule = created.json()
    assert rule["source_document_id"] == str(document.id)
    assert rule["source_section"] == "§2.1"
    assert rule["active"] is False
    assert rule["confirmed_by"] is None
    assert rule["confirmed_at"] is None

    confirmed = client.post(
        f"/api/v1/policy-rules/{rule['id']}/confirm",
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["active"] is True
    assert confirmed.json()["confirmed_by"] == str(user_id)
    assert confirmed.json()["confirmed_at"] is not None

    rejected_patch = client.patch(
        f"/api/v1/policy-rules/{rule['id']}",
        json={"active": True},
    )
    assert rejected_patch.status_code == 422

    edited = client.patch(
        f"/api/v1/policy-rules/{rule['id']}",
        json={"active": False},
    )
    assert edited.status_code == 200
    assert edited.json()["active"] is False
    assert edited.json()["confirmed_by"] is None
    assert edited.json()["confirmed_at"] is None
    assert session.commits == 3
    assert [entry.action for entry in access.list(AuditLog)] == [
        "policy_rule.create",
        "policy_rule.confirm",
        "policy_rule.update",
    ]
    assert access.list(AuditLog)[1].after["active"] is True
    assert access.list(AuditLog)[2].before["active"] is True
    assert access.list(AuditLog)[2].after["active"] is False


def test_policy_rule_api_rejects_missing_source_section_without_writes(
    configuration_client: tuple[
        TestClient, TenantAccessStub, dict[str, Role], SessionStub, UUID, UUID
    ],
) -> None:
    client, access, _role, session, _user_id, tenant_id = configuration_client
    document = _document(tenant_id)
    access.records.setdefault(Document, {})[document.id] = document
    payload = _policy_payload(document.id).model_dump(mode="json")
    payload["source_section"] = "§9.9"

    response = client.post("/api/v1/policy-rules", json=payload)

    assert response.status_code == 422
    assert access.list(PolicyRule) == []
    assert access.list(AuditLog) == []
    assert session.commits == 0


@pytest.mark.parametrize(
    "patch",
    [
        {"source_document_id": str(uuid4())},
        {"source_section": "§3.1"},
    ],
)
def test_policy_rule_patch_rejects_partial_source_reference(
    configuration_client: tuple[
        TestClient, TenantAccessStub, dict[str, Role], SessionStub, UUID, UUID
    ],
    patch: dict[str, str],
) -> None:
    client, access, _role, _session, _user_id, _tenant_id = configuration_client

    response = client.patch(f"/api/v1/policy-rules/{uuid4()}", json=patch)

    assert response.status_code == 422
    assert access.list(PolicyRule) == []
