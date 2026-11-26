from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, TypeVar
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from db.models import AuditLog, CustomerNote, DocumentChunk, TenantScoped

TenantModel = TypeVar("TenantModel", bound=TenantScoped)
VectorModel = TypeVar("VectorModel", CustomerNote, DocumentChunk)


@dataclass(frozen=True)
class TenantContext:
    """Tenant identity established by a trusted authentication boundary."""

    tenant_id: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_id, UUID):
            raise TypeError("TenantContext requires a validated tenant UUID.")


class TenantScopedDataAccess:
    """Database operations that always constrain tenant-owned rows."""

    def __init__(self, session: Session, context: TenantContext) -> None:
        if not isinstance(context, TenantContext):
            raise TypeError("A trusted TenantContext is required.")
        self._session = session
        self._tenant_id = context.tenant_id

    def get(self, model: type[TenantModel], record_id: UUID) -> TenantModel | None:
        model = self._tenant_model(model)
        identity_column = self._identity_column(model)
        statement = select(model).where(
            model.tenant_id == self._tenant_id,
            identity_column == record_id,
            *self._active_record_conditions(model),
        )
        return self._session.scalar(statement)

    def list(
        self,
        model: type[TenantModel],
        *conditions: Any,
        limit: int | None = None,
        for_update: bool = False,
    ) -> list[TenantModel]:
        model = self._tenant_model(model)
        if limit is not None and limit < 1:
            raise ValueError("limit must be a positive integer.")
        statement = select(model).where(
            model.tenant_id == self._tenant_id,
            *self._active_record_conditions(model),
            *conditions,
        )
        if for_update:
            statement = statement.with_for_update()
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

    def insert(
        self,
        model: type[TenantModel],
        values: Mapping[str, Any],
    ) -> TenantModel:
        model = self._tenant_model(model)
        payload = dict(values)
        payload["tenant_id"] = self._tenant_id
        record = model(**payload)
        self._session.add(record)
        self._session.flush()
        return record

    def update(
        self,
        model: type[TenantModel],
        record_id: UUID,
        values: Mapping[str, Any],
    ) -> bool:
        model = self._tenant_model(model)
        self._ensure_mutable(model)
        self._ensure_mutable_fields(values)
        if not values:
            raise ValueError("At least one field must be updated.")
        identity_column = self._identity_column(model)
        statement = (
            update(model)
            .where(
                model.tenant_id == self._tenant_id,
                identity_column == record_id,
            )
            .values(**dict(values))
            .execution_options(synchronize_session="fetch")
        )
        result = self._session.execute(statement)
        return result.rowcount == 1

    def delete(self, model: type[TenantModel], record_id: UUID) -> bool:
        model = self._tenant_model(model)
        self._ensure_mutable(model)
        identity_column = self._identity_column(model)
        statement = delete(model).where(
            model.tenant_id == self._tenant_id,
            identity_column == record_id,
        )
        result = self._session.execute(statement)
        return result.rowcount == 1

    def soft_delete(self, model: type[TenantModel], record_id: UUID) -> bool:
        if model is not CustomerNote:
            raise TypeError("Soft deletion is supported only for customer notes.")

        statement = (
            update(CustomerNote)
            .where(
                CustomerNote.tenant_id == self._tenant_id,
                CustomerNote.id == record_id,
                CustomerNote.deleted_at.is_(None),
            )
            .values(deleted_at=datetime.now(timezone.utc))
            .execution_options(synchronize_session="fetch")
        )
        result = self._session.execute(statement)
        return result.rowcount == 1

    def search_vectors(
        self,
        model: type[VectorModel],
        embedding: list[float],
        *,
        limit: int,
    ) -> list[VectorModel]:
        if model not in (CustomerNote, DocumentChunk):
            raise TypeError("Vector search is supported for notes and document chunks.")
        if limit < 1:
            raise ValueError("limit must be a positive integer.")

        distance = model.embedding.cosine_distance(embedding)
        conditions = [
            model.tenant_id == self._tenant_id,
            model.embedding.is_not(None),
        ]
        if model is CustomerNote:
            conditions.append(model.deleted_at.is_(None))
        statement = select(model).where(*conditions).order_by(distance).limit(limit)
        return list(self._session.scalars(statement).all())

    @staticmethod
    def _tenant_model(model: type[TenantModel]) -> type[TenantModel]:
        if not isinstance(model, type) or not issubclass(model, TenantScoped):
            raise TypeError("Only tenant-scoped models are supported.")
        return model

    @staticmethod
    def _identity_column(model: type[TenantModel]) -> Any:
        primary_key = model.__mapper__.primary_key
        if len(primary_key) != 1:
            raise TypeError("Tenant-scoped records must have a single-column key.")
        return primary_key[0]

    @staticmethod
    def _ensure_mutable(model: type[TenantModel]) -> None:
        if model is AuditLog:
            raise ValueError("Audit logs are append-only.")
        if model is CustomerNote:
            raise ValueError("Customer notes must use soft deletion.")

    @staticmethod
    def _ensure_mutable_fields(values: Mapping[str, Any]) -> None:
        protected = {"id", "tenant_id"}.intersection(values)
        if protected:
            raise ValueError(
                f"Cannot update protected fields: {', '.join(sorted(protected))}."
            )

    @staticmethod
    def _active_record_conditions(model: type[TenantModel]) -> tuple[Any, ...]:
        if model is CustomerNote:
            return (CustomerNote.deleted_at.is_(None),)
        return ()
