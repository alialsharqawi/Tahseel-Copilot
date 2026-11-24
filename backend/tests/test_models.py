from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
    inspect,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import configure_mappers
from pgvector.sqlalchemy import VECTOR

from alembic import command
from alembic.config import Config
from db.models import Base

BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_CONFIG = BACKEND_DIR / "alembic.ini"

EXPECTED_COLUMNS = {
    "tenants": {"id", "name", "industry", "created_at"},
    "users": {
        "id",
        "tenant_id",
        "name",
        "email",
        "password_hash",
        "role",
        "created_at",
    },
    "customers": {
        "id",
        "tenant_id",
        "name",
        "phone",
        "email",
        "credit_limit",
        "payment_terms",
        "tier",
        "sales_rep",
        "assigned_collector",
        "preferred_channel",
        "contact_person",
        "status",
        "created_at",
    },
    "invoices": {
        "id",
        "tenant_id",
        "customer_id",
        "invoice_number",
        "invoice_date",
        "due_date",
        "amount",
        "paid_amount",
        "status",
        "dispute_reason",
        "disputed_by",
        "disputed_at",
        "created_at",
    },
    "payments": {
        "id",
        "tenant_id",
        "customer_id",
        "invoice_id",
        "amount",
        "payment_date",
        "method",
        "created_at",
    },
    "promises_to_pay": {
        "id",
        "tenant_id",
        "customer_id",
        "invoice_id",
        "promised_amount",
        "promise_date",
        "status",
        "recorded_by",
        "created_at",
        "resolved_at",
    },
    "customer_notes": {
        "id",
        "tenant_id",
        "customer_id",
        "note_type",
        "text",
        "embedding",
        "author_id",
        "source",
        "created_at",
        "deleted_at",
    },
    "recommendations": {
        "id",
        "tenant_id",
        "customer_id",
        "agent_run_id",
        "action",
        "reasons",
        "citations",
        "requires_manager_review",
        "status",
        "decided_by",
        "decided_at",
        "decision_reason",
        "created_at",
    },
    "draft_versions": {
        "id",
        "tenant_id",
        "recommendation_id",
        "tone",
        "original_text",
        "edited_text",
        "edit_reason",
        "check_result",
        "created_by",
        "created_at",
    },
    "collection_tasks": {
        "id",
        "tenant_id",
        "customer_id",
        "recommendation_id",
        "assigned_to",
        "priority",
        "action",
        "due_at",
        "status",
        "notes",
        "created_by",
        "created_at",
    },
    "conversations": {
        "id",
        "tenant_id",
        "user_id",
        "customer_id",
        "created_at",
    },
    "messages": {
        "id",
        "tenant_id",
        "conversation_id",
        "role",
        "content",
        "tool_calls",
        "is_summary",
        "created_at",
    },
    "documents": {
        "id",
        "tenant_id",
        "name",
        "type",
        "storage_path",
        "uploaded_by",
        "effective_date",
        "created_at",
    },
    "document_chunks": {
        "id",
        "tenant_id",
        "document_id",
        "customer_id",
        "policy_type",
        "section",
        "page",
        "effective_date",
        "text",
        "embedding",
        "created_at",
    },
    "tenant_settings": {"tenant_id", "settings", "updated_by", "updated_at"},
    "policy_rules": {
        "id",
        "tenant_id",
        "name",
        "rule_type",
        "condition",
        "outcome",
        "source_document_id",
        "source_section",
        "confirmed_by",
        "confirmed_at",
        "active",
    },
    "risk_scores": {
        "id",
        "tenant_id",
        "customer_id",
        "score",
        "level",
        "factors",
        "calculated_at",
    },
    "agent_runs": {
        "id",
        "tenant_id",
        "user_id",
        "run_type",
        "input",
        "output",
        "tools_used",
        "status",
        "model",
        "prompt_tokens",
        "completion_tokens",
        "cost_estimate",
        "latency_ms",
        "created_at",
    },
    "audit_logs": {
        "id",
        "tenant_id",
        "user_id",
        "action",
        "entity_type",
        "entity_id",
        "before",
        "after",
        "created_at",
    },
}

EXPECTED_FOREIGN_KEYS = {
    "users": {"tenant_id": ("tenants", "id", False)},
    "customers": {
        "tenant_id": ("tenants", "id", False),
        "assigned_collector": ("users", "id", True),
    },
    "invoices": {
        "tenant_id": ("tenants", "id", False),
        "customer_id": ("customers", "id", False),
        "disputed_by": ("users", "id", True),
    },
    "payments": {
        "tenant_id": ("tenants", "id", False),
        "customer_id": ("customers", "id", False),
        "invoice_id": ("invoices", "id", False),
    },
    "promises_to_pay": {
        "tenant_id": ("tenants", "id", False),
        "customer_id": ("customers", "id", False),
        "invoice_id": ("invoices", "id", False),
        "recorded_by": ("users", "id", False),
    },
    "customer_notes": {
        "tenant_id": ("tenants", "id", False),
        "customer_id": ("customers", "id", False),
        "author_id": ("users", "id", False),
    },
    "recommendations": {
        "tenant_id": ("tenants", "id", False),
        "customer_id": ("customers", "id", False),
        "agent_run_id": ("agent_runs", "id", False),
        "decided_by": ("users", "id", True),
    },
    "draft_versions": {
        "tenant_id": ("tenants", "id", False),
        "recommendation_id": ("recommendations", "id", False),
        "created_by": ("users", "id", False),
    },
    "collection_tasks": {
        "tenant_id": ("tenants", "id", False),
        "customer_id": ("customers", "id", False),
        "recommendation_id": ("recommendations", "id", False),
        "assigned_to": ("users", "id", False),
        "created_by": ("users", "id", False),
    },
    "conversations": {
        "tenant_id": ("tenants", "id", False),
        "user_id": ("users", "id", False),
        "customer_id": ("customers", "id", True),
    },
    "messages": {
        "tenant_id": ("tenants", "id", False),
        "conversation_id": ("conversations", "id", False),
    },
    "documents": {
        "tenant_id": ("tenants", "id", False),
        "uploaded_by": ("users", "id", False),
    },
    "document_chunks": {
        "tenant_id": ("tenants", "id", False),
        "document_id": ("documents", "id", False),
        "customer_id": ("customers", "id", True),
    },
    "tenant_settings": {
        "tenant_id": ("tenants", "id", False),
        "updated_by": ("users", "id", True),
    },
    "policy_rules": {
        "tenant_id": ("tenants", "id", False),
        "source_document_id": ("documents", "id", False),
        "confirmed_by": ("users", "id", True),
    },
    "risk_scores": {
        "tenant_id": ("tenants", "id", False),
        "customer_id": ("customers", "id", False),
    },
    "agent_runs": {
        "tenant_id": ("tenants", "id", False),
        "user_id": ("users", "id", False),
    },
    "audit_logs": {
        "tenant_id": ("tenants", "id", False),
        "user_id": ("users", "id", False),
    },
}

EXPECTED_ENUMS = {
    "users": {"role": ("OWNER", "FINANCE_MANAGER", "COLLECTOR")},
    "customers": {
        "tier": ("strategic", "regular"),
        "preferred_channel": ("call", "whatsapp", "email"),
        "status": ("active", "inactive"),
    },
    "invoices": {"status": ("open", "paid", "disputed")},
    "promises_to_pay": {"status": ("pending", "kept", "broken")},
    "customer_notes": {
        "note_type": ("collector", "sales_rep", "call_outcome"),
        "source": ("ui", "import"),
    },
    "recommendations": {
        "action": (
            "CALL",
            "WHATSAPP",
            "EMAIL",
            "WAIT",
            "ESCALATE_TO_MANAGER",
            "TALK_TO_SALES_REP",
        ),
        "status": ("pending", "approved", "edited", "rejected"),
    },
    "draft_versions": {"tone": ("formal", "friendly", "firm")},
    "collection_tasks": {
        "priority": ("HIGH", "MEDIUM", "LOW"),
        "action": (
            "CALL",
            "WHATSAPP",
            "EMAIL",
            "WAIT",
            "ESCALATE_TO_MANAGER",
            "TALK_TO_SALES_REP",
        ),
        "status": ("pending", "done", "cancelled"),
    },
    "messages": {"role": ("user", "assistant", "tool")},
    "documents": {
        "type": (
            "credit_policy",
            "collection_policy",
            "payment_terms",
            "template",
            "contract",
            "other",
        )
    },
    "policy_rules": {
        "rule_type": ("escalation", "grace_period", "limit", "review_required")
    },
    "risk_scores": {"level": ("LOW", "MEDIUM", "HIGH", "CRITICAL")},
}

EXPECTED_INDEXES = {
    "invoices": {
        "ix_invoices_tenant_customer_due": ("tenant_id", "customer_id", "due_date")
    },
    "payments": {"ix_payments_tenant_invoice": ("tenant_id", "invoice_id")},
    "customer_notes": {"ix_customer_notes_tenant_id": ("tenant_id",)},
    "document_chunks": {"ix_document_chunks_tenant_id": ("tenant_id",)},
}

EXPECTED_NULLABLE_COLUMNS = {
    "customers": {
        "phone",
        "email",
        "credit_limit",
        "sales_rep",
        "assigned_collector",
        "preferred_channel",
        "contact_person",
    },
    "invoices": {"dispute_reason", "disputed_by", "disputed_at"},
    "promises_to_pay": {"resolved_at"},
    "customer_notes": {"embedding", "deleted_at"},
    "agent_runs": {
        "output",
        "model",
        "prompt_tokens",
        "completion_tokens",
        "cost_estimate",
        "latency_ms",
    },
    "recommendations": {"decided_by", "decided_at", "decision_reason"},
    "draft_versions": {"edited_text", "edit_reason"},
    "collection_tasks": {"notes"},
    "conversations": {"customer_id"},
    "messages": {"tool_calls"},
    "documents": {"effective_date"},
    "document_chunks": {
        "customer_id",
        "section",
        "page",
        "effective_date",
        "embedding",
    },
    "tenant_settings": {"updated_by"},
    "policy_rules": {"confirmed_by", "confirmed_at"},
    "audit_logs": {"before", "after"},
}

UUID_COLUMNS = {
    "id",
    "tenant_id",
    "assigned_collector",
    "customer_id",
    "disputed_by",
    "invoice_id",
    "recorded_by",
    "author_id",
    "agent_run_id",
    "decided_by",
    "recommendation_id",
    "created_by",
    "assigned_to",
    "user_id",
    "conversation_id",
    "uploaded_by",
    "document_id",
    "source_document_id",
    "confirmed_by",
    "updated_by",
}

DATE_COLUMNS = {
    ("invoices", "invoice_date"),
    ("invoices", "due_date"),
    ("payments", "payment_date"),
    ("promises_to_pay", "promise_date"),
    ("documents", "effective_date"),
    ("document_chunks", "effective_date"),
}

DATETIME_COLUMNS = {
    (table, column)
    for table, columns in {
        "tenants": ("created_at",),
        "users": ("created_at",),
        "customers": ("created_at",),
        "invoices": ("disputed_at", "created_at"),
        "payments": ("created_at",),
        "promises_to_pay": ("created_at", "resolved_at"),
        "customer_notes": ("created_at", "deleted_at"),
        "recommendations": ("decided_at", "created_at"),
        "draft_versions": ("created_at",),
        "collection_tasks": ("due_at", "created_at"),
        "conversations": ("created_at",),
        "messages": ("created_at",),
        "documents": ("created_at",),
        "document_chunks": ("created_at",),
        "tenant_settings": ("updated_at",),
        "policy_rules": ("confirmed_at",),
        "risk_scores": ("calculated_at",),
        "agent_runs": ("created_at",),
        "audit_logs": ("created_at",),
    }.items()
    for column in columns
}

JSONB_COLUMNS = {
    ("audit_logs", "before"),
    ("audit_logs", "after"),
    ("agent_runs", "input"),
    ("agent_runs", "output"),
    ("agent_runs", "tools_used"),
    ("recommendations", "reasons"),
    ("recommendations", "citations"),
    ("draft_versions", "check_result"),
    ("messages", "tool_calls"),
    ("tenant_settings", "settings"),
    ("policy_rules", "condition"),
    ("policy_rules", "outcome"),
    ("risk_scores", "factors"),
}


def test_all_documented_tables_and_columns_are_present() -> None:
    assert set(Base.metadata.tables) == set(EXPECTED_COLUMNS)
    assert len(Base.metadata.tables) == 19

    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        assert set(Base.metadata.tables[table_name].columns.keys()) == expected_columns

    for table_name in EXPECTED_COLUMNS.keys() - {"tenants"}:
        assert "tenant_id" in Base.metadata.tables[table_name].columns


def test_primary_and_foreign_keys_match_the_dictionary() -> None:
    for table_name, table in Base.metadata.tables.items():
        expected_primary_key = (
            {"tenant_id"} if table_name == "tenant_settings" else {"id"}
        )
        assert {
            column.name for column in table.primary_key.columns
        } == expected_primary_key
        assert all(not column.nullable for column in table.primary_key.columns)

        actual_foreign_keys = {
            column.name: (
                foreign_key.column.table.name,
                foreign_key.column.name,
                column.nullable,
            )
            for column in table.columns
            for foreign_key in column.foreign_keys
        }
        assert actual_foreign_keys == EXPECTED_FOREIGN_KEYS.get(table_name, {})


def test_nullability_and_server_defaults_are_explicit() -> None:
    timestamp_defaults = {
        "tenants": {"created_at"},
        "users": {"created_at"},
        "customers": {"created_at"},
        "invoices": {"created_at"},
        "payments": {"created_at"},
        "promises_to_pay": {"created_at"},
        "customer_notes": {"created_at"},
        "recommendations": {"created_at"},
        "draft_versions": {"created_at"},
        "collection_tasks": {"created_at"},
        "conversations": {"created_at"},
        "messages": {"created_at"},
        "documents": {"created_at"},
        "document_chunks": {"created_at"},
        "tenant_settings": {"updated_at"},
        "policy_rules": set(),
        "risk_scores": {"calculated_at"},
        "agent_runs": {"created_at"},
        "audit_logs": {"created_at"},
    }

    for table_name, table in Base.metadata.tables.items():
        expected_nullable = EXPECTED_NULLABLE_COLUMNS.get(table_name, set())
        expected_server_defaults = timestamp_defaults[table_name]
        for column in table.columns:
            assert column.nullable == (column.name in expected_nullable), (
                table_name,
                column.name,
            )
            has_expected_default = column.name in expected_server_defaults or (
                column.name == "id" and table_name != "tenant_settings"
            )
            assert (column.server_default is not None) == has_expected_default, (
                table_name,
                column.name,
            )


def test_documented_types_are_used() -> None:
    all_columns = {
        (table_name, column.name): column
        for table_name, table in Base.metadata.tables.items()
        for column in table.columns
    }

    for (table_name, column_name), column in all_columns.items():
        if column_name in UUID_COLUMNS:
            assert isinstance(column.type, PostgreSQLUUID), (table_name, column_name)
        elif (table_name, column_name) in DATE_COLUMNS:
            assert isinstance(column.type, Date), (table_name, column_name)
        elif (table_name, column_name) in DATETIME_COLUMNS:
            assert isinstance(column.type, DateTime), (table_name, column_name)
            assert column.type.timezone, (table_name, column_name)
        elif (table_name, column_name) in JSONB_COLUMNS:
            assert isinstance(column.type, JSONB), (table_name, column_name)
        elif (table_name, column_name) in {
            ("customers", "credit_limit"),
            ("invoices", "amount"),
            ("invoices", "paid_amount"),
            ("payments", "amount"),
            ("promises_to_pay", "promised_amount"),
            ("agent_runs", "cost_estimate"),
        }:
            assert isinstance(column.type, Numeric), (table_name, column_name)
            expected_precision = 10 if column_name == "cost_estimate" else 14
            expected_scale = 4 if column_name == "cost_estimate" else 2
            assert (column.type.precision, column.type.scale) == (
                expected_precision,
                expected_scale,
            )
        elif (table_name, column_name) == ("risk_scores", "score"):
            assert isinstance(column.type, SmallInteger)
        elif (table_name, column_name) in {
            ("document_chunks", "page"),
            ("agent_runs", "prompt_tokens"),
            ("agent_runs", "completion_tokens"),
            ("agent_runs", "latency_ms"),
        }:
            assert isinstance(column.type, Integer), (table_name, column_name)
        elif (table_name, column_name) in {
            ("recommendations", "requires_manager_review"),
            ("messages", "is_summary"),
            ("policy_rules", "active"),
        }:
            assert isinstance(column.type, Boolean), (table_name, column_name)
        elif (table_name, column_name) in {
            ("customer_notes", "embedding"),
            ("document_chunks", "embedding"),
        }:
            assert isinstance(column.type, VECTOR), (table_name, column_name)
            assert column.type.dim is None
        else:
            assert isinstance(column.type, Text), (table_name, column_name)


def test_documented_enum_checks_indexes_and_unique_constraint() -> None:
    for table_name, expected_columns in EXPECTED_ENUMS.items():
        checks = {
            constraint.name: constraint
            for constraint in Base.metadata.tables[table_name].constraints
            if isinstance(constraint, CheckConstraint)
        }
        assert len(checks) == len(expected_columns)
        for column_name, values in expected_columns.items():
            check = checks[f"ck_{table_name}_{column_name}_allowed_values"]
            allowed_values = ", ".join(f"'{value}'" for value in values)
            assert check.sqltext.text == f"{column_name} IN ({allowed_values})"

    for table_name, expected_indexes in EXPECTED_INDEXES.items():
        actual_indexes = {
            index.name: tuple(column.name for column in index.columns)
            for index in Base.metadata.tables[table_name].indexes
        }
        assert actual_indexes == expected_indexes

    invoice_unique_constraints = {
        constraint.name: tuple(column.name for column in constraint.columns)
        for constraint in Base.metadata.tables["invoices"].constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert invoice_unique_constraints == {
        "uq_invoices_tenant_invoice_number": ("tenant_id", "invoice_number")
    }


def test_all_foreign_keys_have_orm_relationships() -> None:
    configure_mappers()

    for table_name, table in Base.metadata.tables.items():
        model = next(
            mapper.class_
            for mapper in Base.registry.mappers
            if mapper.local_table is table
        )
        relationship_columns = {
            column
            for relationship_property in inspect(model).relationships
            for column in relationship_property.local_columns
        }
        foreign_key_columns = {foreign_key.parent for foreign_key in table.foreign_keys}
        assert foreign_key_columns <= relationship_columns


def test_initial_migration_renders_all_tables_and_unbounded_vectors() -> None:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/tahseel"
    )
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=BACKEND_DIR,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    for table_name in EXPECTED_COLUMNS:
        assert re.search(rf"CREATE TABLE {table_name}\s*\(", result.stdout)
    assert result.stdout.count("CREATE TABLE ") == 20
    assert result.stdout.count("VECTOR") == 2
    assert "VECTOR(" not in result.stdout
    assert "USING hnsw" not in result.stdout.lower()
    assert "USING ivfflat" not in result.stdout.lower()
    for table_name, expected_constraints in EXPECTED_ENUMS.items():
        for column_name in expected_constraints:
            constraint_name = f"ck_{table_name}_{column_name}_allowed_values"
            assert f"CONSTRAINT {constraint_name}" in result.stdout
    for indexes in EXPECTED_INDEXES.values():
        for index_name in indexes:
            assert f"CREATE INDEX {index_name}" in result.stdout
    assert "CONSTRAINT uq_invoices_tenant_invoice_number" in result.stdout


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="Set TEST_DATABASE_URL to run PostgreSQL migration integration tests.",
)
def test_migration_upgrade_and_downgrade_on_postgresql(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from sqlalchemy import create_engine, inspect as inspect_database
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    database_url = os.environ["TEST_DATABASE_URL"]
    monkeypatch.setenv("DATABASE_URL", database_url)
    alembic_config = Config(str(ALEMBIC_CONFIG))

    command.upgrade(alembic_config, "head")
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            inspector = inspect_database(connection)
            assert set(EXPECTED_COLUMNS) <= set(inspector.get_table_names())
            assert (
                compare_metadata(
                    MigrationContext.configure(connection),
                    Base.metadata,
                )
                == []
            )
        command.downgrade(alembic_config, "base")
        with engine.connect() as connection:
            assert not set(EXPECTED_COLUMNS) & set(
                inspect_database(connection).get_table_names()
            )
    finally:
        engine.dispose()
