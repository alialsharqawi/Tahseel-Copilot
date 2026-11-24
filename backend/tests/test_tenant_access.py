from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import (
    AuditLog,
    Customer,
    CustomerNote,
    Document,
    DocumentChunk,
    Invoice,
    Tenant,
    User,
)
from db.tenant_access import TenantContext, TenantScopedDataAccess

BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_CONFIG = BACKEND_DIR / "alembic.ini"


@pytest.fixture
def database_session(monkeypatch: pytest.MonkeyPatch):
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run tenant-isolation integration tests.")

    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(Config(str(ALEMBIC_CONFIG)), "head")

    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            session = Session(
                bind=connection,
                join_transaction_mode="create_savepoint",
            )
            try:
                yield session
            finally:
                session.close()
                transaction.rollback()
    finally:
        engine.dispose()


def _tenant_access(
    session: Session,
) -> tuple[TenantScopedDataAccess, TenantScopedDataAccess, UUID, UUID]:
    tenant_a = Tenant(name="Synthetic Tenant A", industry="distribution")
    tenant_b = Tenant(name="Synthetic Tenant B", industry="distribution")
    session.add_all((tenant_a, tenant_b))
    session.flush()
    return (
        TenantScopedDataAccess(session, TenantContext(tenant_a.id)),
        TenantScopedDataAccess(session, TenantContext(tenant_b.id)),
        tenant_a.id,
        tenant_b.id,
    )


def _customer_values(name: str) -> dict[str, object]:
    return {
        "name": name,
        "payment_terms": "30 days",
        "tier": "regular",
        "status": "active",
    }


def _user_values(name: str, email: str) -> dict[str, object]:
    return {
        "name": name,
        "email": email,
        "password_hash": "synthetic-test-hash",
        "role": "OWNER",
    }


def test_tenant_scoped_crud_and_tenant_id_assignment(database_session: Session) -> None:
    access_a, access_b, tenant_a_id, tenant_b_id = _tenant_access(database_session)
    customer_a = access_a.insert(
        Customer,
        {**_customer_values("Synthetic A"), "tenant_id": tenant_b_id},
    )
    customer_b = access_b.insert(Customer, _customer_values("Synthetic B"))

    assert customer_a.tenant_id == tenant_a_id
    assert customer_b.tenant_id == tenant_b_id
    assert access_a.get(Customer, customer_b.id) is None
    assert access_a.list(Customer) == [customer_a]
    assert not access_a.update(Customer, customer_b.id, {"name": "Changed"})
    assert not access_a.delete(Customer, customer_b.id)

    assert access_a.update(Customer, customer_a.id, {"name": "Updated A"})
    assert access_a.get(Customer, customer_a.id).name == "Updated A"
    assert access_a.delete(Customer, customer_a.id)
    assert access_a.get(Customer, customer_a.id) is None
    assert access_b.get(Customer, customer_b.id) is customer_b


def test_access_layer_requires_explicit_trusted_context() -> None:
    with pytest.raises(TypeError, match="TenantContext"):
        TenantScopedDataAccess(None, None)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="validated tenant UUID"):
        TenantContext("untrusted request value")  # type: ignore[arg-type]


def test_access_layer_protects_tenant_fields() -> None:
    access_a = TenantScopedDataAccess(Mock(), TenantContext(uuid4()))
    with pytest.raises(ValueError, match="protected fields"):
        access_a.update(Customer, uuid4(), {"tenant_id": uuid4()})
    with pytest.raises(ValueError, match="soft deletion"):
        access_a.delete(CustomerNote, uuid4())
    with pytest.raises(ValueError, match="soft deletion"):
        access_a.update(CustomerNote, uuid4(), {"text": "Arbitrary edit"})
    with pytest.raises(ValueError, match="append-only"):
        access_a.update(AuditLog, uuid4(), {"action": "Changed"})
    with pytest.raises(ValueError, match="append-only"):
        access_a.delete(AuditLog, uuid4())
    with pytest.raises(TypeError, match="only for customer notes"):
        access_a.soft_delete(Customer, uuid4())


def test_soft_delete_builds_scoped_idempotent_utc_update() -> None:
    session = Mock()
    session.execute.return_value.rowcount = 1
    tenant_id = uuid4()
    record_id = uuid4()
    access = TenantScopedDataAccess(session, TenantContext(tenant_id))

    assert access.soft_delete(CustomerNote, record_id) is True
    statement = session.execute.call_args.args[0]
    compiled = statement.compile(dialect=postgresql.dialect())
    sql = str(compiled).lower()
    where_clause = sql.split("where", maxsplit=1)[1]
    assert "customer_notes.tenant_id" in where_clause
    assert "customer_notes.id" in where_clause
    assert "customer_notes.deleted_at is null" in where_clause

    timestamp = compiled.params["deleted_at"]
    assert timestamp.tzinfo is not None
    assert timestamp.utcoffset() == timezone.utc.utcoffset(timestamp)

    session.execute.return_value.rowcount = 0
    assert access.soft_delete(CustomerNote, record_id) is False


def test_composite_foreign_key_blocks_cross_tenant_relationships(
    database_session: Session,
) -> None:
    access_a, access_b, tenant_a_id, _ = _tenant_access(database_session)
    user_b = access_b.insert(User, _user_values("Synthetic B", "b@example.test"))
    customer_a = access_a.insert(Customer, _customer_values("Synthetic Customer A"))
    customer_b = access_b.insert(Customer, _customer_values("Synthetic Customer B"))

    invoice_a = access_a.insert(
        Invoice,
        {
            "customer_id": customer_a.id,
            "invoice_number": "SYN-A-001",
            "invoice_date": date(2026, 1, 1),
            "due_date": date(2026, 1, 31),
            "amount": Decimal("100.00"),
            "paid_amount": Decimal("0.00"),
            "status": "open",
        },
    )
    database_session.flush()
    assert invoice_a.tenant_id == tenant_a_id
    assert invoice_a.customer.id == customer_a.id

    with pytest.raises(IntegrityError):
        with database_session.begin_nested():
            access_a.insert(
                Invoice,
                {
                    "customer_id": customer_b.id,
                    "invoice_number": "SYN-A-002",
                    "invoice_date": date(2026, 1, 1),
                    "due_date": date(2026, 1, 31),
                    "amount": Decimal("100.00"),
                    "paid_amount": Decimal("0.00"),
                    "status": "open",
                },
            )

    with pytest.raises(IntegrityError):
        with database_session.begin_nested():
            access_a.insert(
                Customer,
                {
                    **_customer_values("Synthetic assigned collector mismatch"),
                    "assigned_collector": user_b.id,
                },
            )

    assert access_a.get(User, user_b.id) is None
    assert access_b.get(User, user_b.id) is user_b


def test_customer_note_soft_delete_is_tenant_scoped_and_excluded_from_search(
    database_session: Session,
) -> None:
    access_a, access_b, tenant_a_id, tenant_b_id = _tenant_access(database_session)
    user_a = access_a.insert(User, _user_values("Synthetic A", "a@example.test"))
    user_b = access_b.insert(User, _user_values("Synthetic B", "b@example.test"))
    customer_a = access_a.insert(Customer, _customer_values("Synthetic Customer A"))
    customer_b = access_b.insert(Customer, _customer_values("Synthetic Customer B"))
    note_a = access_a.insert(
        CustomerNote,
        {
            "customer_id": customer_a.id,
            "note_type": "collector",
            "text": "Synthetic note A",
            "embedding": [1.0, 0.0],
            "author_id": user_a.id,
            "source": "ui",
        },
    )
    note_b = access_b.insert(
        CustomerNote,
        {
            "customer_id": customer_b.id,
            "note_type": "collector",
            "text": "Synthetic note B",
            "embedding": [1.0, 0.0],
            "author_id": user_b.id,
            "source": "ui",
        },
    )

    assert access_a.get(CustomerNote, note_a.id) is note_a
    assert access_a.list(CustomerNote) == [note_a]
    assert access_b.get(CustomerNote, note_a.id) is None
    assert access_b.list(CustomerNote) == [note_b]

    update_statements: list[str] = []
    update_parameters: list[object] = []
    connection = database_session.connection()

    def capture_update(
        _conn: object,
        _cursor: object,
        statement: str,
        parameters: object,
        _context: object,
        _executemany: bool,
    ) -> None:
        if statement.lstrip().lower().startswith("update customer_notes"):
            update_statements.append(statement.lower())
            update_parameters.append(parameters)

    event.listen(connection, "before_cursor_execute", capture_update)
    try:
        assert access_a.soft_delete(CustomerNote, note_b.id) is False
        assert access_a.soft_delete(CustomerNote, note_a.id) is True
        assert access_a.soft_delete(CustomerNote, note_a.id) is False
    finally:
        event.remove(connection, "before_cursor_execute", capture_update)

    assert len(update_statements) == 3
    for statement in update_statements:
        where_position = statement.index("where")
        assert "tenant_id" in statement[where_position:]
        assert "customer_notes.id" in statement[where_position:]
        assert "deleted_at is null" in statement[where_position:]

    parameter_values = []
    for parameters in update_parameters:
        if isinstance(parameters, Mapping):
            parameter_values.extend(parameters.values())
        elif isinstance(parameters, Sequence) and not isinstance(
            parameters, (str, bytes, bytearray)
        ):
            parameter_values.extend(parameters)
    timestamps = [value for value in parameter_values if isinstance(value, datetime)]
    assert len(timestamps) == 3
    assert all(
        timestamp.tzinfo is not None
        and timestamp.utcoffset() == timezone.utc.utcoffset(timestamp)
        for timestamp in timestamps
    )
    database_session.expire(note_a, ["deleted_at"])
    database_session.refresh(note_a, attribute_names=["deleted_at"])
    assert note_a.deleted_at is not None
    assert note_a.deleted_at.tzinfo is not None
    assert access_a.get(CustomerNote, note_a.id) is None
    assert access_a.list(CustomerNote) == []
    assert access_b.get(CustomerNote, note_a.id) is None
    assert access_b.list(CustomerNote) == [note_b]
    assert access_b.soft_delete(CustomerNote, note_a.id) is False
    assert access_b.get(CustomerNote, note_b.id).deleted_at is None

    with pytest.raises(ValueError, match="soft deletion"):
        access_a.update(CustomerNote, note_a.id, {"text": "Arbitrary edit"})
    with pytest.raises(ValueError, match="soft deletion"):
        access_a.delete(CustomerNote, note_a.id)

    assert access_a.search_vectors(CustomerNote, [1.0, 0.0], limit=10) == []
    assert [
        note.id for note in access_b.search_vectors(CustomerNote, [1.0, 0.0], limit=10)
    ] == [note_b.id]
    assert note_a.tenant_id == tenant_a_id
    assert note_b.tenant_id == tenant_b_id


def test_vector_search_filters_tenant_before_ordering_and_limiting(
    database_session: Session,
) -> None:
    access_a, access_b, tenant_a_id, tenant_b_id = _tenant_access(database_session)
    user_a = access_a.insert(User, _user_values("Synthetic A", "a@example.test"))
    user_b = access_b.insert(User, _user_values("Synthetic B", "b@example.test"))
    document_a = access_a.insert(
        Document,
        {
            "name": "Synthetic policy A",
            "type": "credit_policy",
            "storage_path": "synthetic/a",
            "uploaded_by": user_a.id,
        },
    )
    document_b = access_b.insert(
        Document,
        {
            "name": "Synthetic policy B",
            "type": "credit_policy",
            "storage_path": "synthetic/b",
            "uploaded_by": user_b.id,
        },
    )
    customer_a = access_a.insert(Customer, _customer_values("Synthetic Customer A"))
    customer_b = access_b.insert(Customer, _customer_values("Synthetic Customer B"))
    chunk_a = access_a.insert(
        DocumentChunk,
        {
            "document_id": document_a.id,
            "policy_type": "credit_policy",
            "text": "Synthetic passage A",
            "embedding": [0.0, 1.0],
        },
    )
    chunk_b = access_b.insert(
        DocumentChunk,
        {
            "document_id": document_b.id,
            "policy_type": "credit_policy",
            "text": "Synthetic passage B",
            "embedding": [1.0, 0.0],
        },
    )
    note_a = access_a.insert(
        CustomerNote,
        {
            "customer_id": customer_a.id,
            "note_type": "collector",
            "text": "Synthetic note A",
            "embedding": [0.0, 1.0],
            "author_id": user_a.id,
            "source": "ui",
        },
    )
    note_b = access_b.insert(
        CustomerNote,
        {
            "customer_id": customer_b.id,
            "note_type": "collector",
            "text": "Synthetic note B",
            "embedding": [1.0, 0.0],
            "author_id": user_b.id,
            "source": "ui",
        },
    )

    statements: list[str] = []
    connection = database_session.connection()

    def capture_statement(
        conn: object,
        cursor: object,
        statement: str,
        parameters: object,
        context: object,
        executemany: bool,
    ) -> None:
        if "document_chunks" in statement or "customer_notes" in statement:
            statements.append(statement)

    event.listen(connection, "before_cursor_execute", capture_statement)
    try:
        results_a = access_a.search_vectors(
            DocumentChunk,
            [1.0, 0.0],
            limit=1,
        )
        results_b = access_b.search_vectors(
            DocumentChunk,
            [1.0, 0.0],
            limit=1,
        )
        notes_a = access_a.search_vectors(CustomerNote, [1.0, 0.0], limit=1)
        notes_b = access_b.search_vectors(CustomerNote, [1.0, 0.0], limit=1)
    finally:
        event.remove(connection, "before_cursor_execute", capture_statement)

    assert [chunk.id for chunk in results_a] == [chunk_a.id]
    assert [chunk.id for chunk in results_b] == [chunk_b.id]
    assert [note.id for note in notes_a] == [note_a.id]
    assert [note.id for note in notes_b] == [note_b.id]
    assert results_a[0].tenant_id == tenant_a_id
    assert results_b[0].tenant_id == tenant_b_id
    assert notes_a[0].tenant_id == tenant_a_id
    assert notes_b[0].tenant_id == tenant_b_id

    vector_queries = [
        statement.lower() for statement in statements if "order by" in statement.lower()
    ]
    assert len(vector_queries) == 4
    for statement in vector_queries:
        where_position = statement.index("where")
        tenant_position = statement.index("tenant_id", where_position)
        order_position = statement.index("order by")
        limit_position = statement.index("limit")
        assert where_position < tenant_position < order_position < limit_position
