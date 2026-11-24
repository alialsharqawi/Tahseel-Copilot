from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    MetaData,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def _enum_check(column: str, values: tuple[str, ...]) -> CheckConstraint:
    allowed_values = ", ".join(f"'{value}'" for value in values)
    return CheckConstraint(
        f"{column} IN ({allowed_values})",
        name=f"{column}_allowed_values",
    )


class UUIDPrimaryKey:
    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )


class TenantScoped:
    tenant_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
    )

    @declared_attr
    def tenant(cls) -> Mapped[Tenant]:
        return relationship(foreign_keys=lambda: [cls.tenant_id])


class CreatedAt:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Tenant(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    industry: Mapped[str] = mapped_column(Text, nullable=False)


class User(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "users"
    __table_args__ = (
        _enum_check("role", ("OWNER", "FINANCE_MANAGER", "COLLECTOR")),
        UniqueConstraint("tenant_id", "id", name="uq_users_tenant_id"),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)


class Customer(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "customers"
    __table_args__ = (
        _enum_check("tier", ("strategic", "regular")),
        _enum_check("preferred_channel", ("call", "whatsapp", "email")),
        _enum_check("status", ("active", "inactive")),
        UniqueConstraint("tenant_id", "id", name="uq_customers_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "assigned_collector"],
            ["users.tenant_id", "users.id"],
            name="fk_customers_tenant_assigned_collector_users",
        ),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    credit_limit: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )
    payment_terms: Mapped[str] = mapped_column(Text, nullable=False)
    tier: Mapped[str] = mapped_column(Text, nullable=False)
    sales_rep: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_collector: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    preferred_channel: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_person: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)

    assigned_collector_user: Mapped[User | None] = relationship(
        foreign_keys=[assigned_collector]
    )


class Invoice(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "invoices"
    __table_args__ = (
        _enum_check("status", ("open", "paid", "disputed")),
        UniqueConstraint(
            "tenant_id",
            "invoice_number",
            name="uq_invoices_tenant_invoice_number",
        ),
        UniqueConstraint("tenant_id", "id", name="uq_invoices_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_invoices_tenant_customer_customers",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "disputed_by"],
            ["users.tenant_id", "users.id"],
            name="fk_invoices_tenant_disputed_by_users",
        ),
        Index(
            "ix_invoices_tenant_customer_due",
            "tenant_id",
            "customer_id",
            "due_date",
        ),
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )
    invoice_number: Mapped[str] = mapped_column(Text, nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    disputed_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    disputed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    customer: Mapped[Customer] = relationship(foreign_keys=[customer_id])
    disputed_by_user: Mapped[User | None] = relationship(foreign_keys=[disputed_by])


class Payment(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_tenant_invoice", "tenant_id", "invoice_id"),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_payments_tenant_customer_customers",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "invoice_id"],
            ["invoices.tenant_id", "invoices.id"],
            name="fk_payments_tenant_invoice_invoices",
        ),
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )
    invoice_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("invoices.id"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    method: Mapped[str] = mapped_column(Text, nullable=False)

    customer: Mapped[Customer] = relationship(foreign_keys=[customer_id])
    invoice: Mapped[Invoice] = relationship(foreign_keys=[invoice_id])


class PromiseToPay(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "promises_to_pay"
    __table_args__ = (
        _enum_check("status", ("pending", "kept", "broken")),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_promises_to_pay_tenant_customer_customers",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "invoice_id"],
            ["invoices.tenant_id", "invoices.id"],
            name="fk_promises_to_pay_tenant_invoice_invoices",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "recorded_by"],
            ["users.tenant_id", "users.id"],
            name="fk_promises_to_pay_tenant_recorded_by_users",
        ),
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )
    invoice_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("invoices.id"),
        nullable=False,
    )
    promised_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    promise_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    recorded_by: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    customer: Mapped[Customer] = relationship(foreign_keys=[customer_id])
    invoice: Mapped[Invoice] = relationship(foreign_keys=[invoice_id])
    recorded_by_user: Mapped[User] = relationship(foreign_keys=[recorded_by])


class CustomerNote(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "customer_notes"
    __table_args__ = (
        _enum_check("note_type", ("collector", "sales_rep", "call_outcome")),
        _enum_check("source", ("ui", "import")),
        Index("ix_customer_notes_tenant_id", "tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_customer_notes_tenant_customer_customers",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "author_id"],
            ["users.tenant_id", "users.id"],
            name="fk_customer_notes_tenant_author_users",
        ),
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )
    note_type: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(VECTOR(), nullable=True)
    author_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(Text, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    customer: Mapped[Customer] = relationship(foreign_keys=[customer_id])
    author: Mapped[User] = relationship(foreign_keys=[author_id])


class AgentRun(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_agent_runs_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["users.tenant_id", "users.id"],
            name="fk_agent_runs_tenant_user_users",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    run_type: Mapped[str] = mapped_column(Text, nullable=False)
    input: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    output: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    tools_used: Mapped[list[Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_estimate: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped[User] = relationship(foreign_keys=[user_id])


class Recommendation(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        _enum_check(
            "action",
            (
                "CALL",
                "WHATSAPP",
                "EMAIL",
                "WAIT",
                "ESCALATE_TO_MANAGER",
                "TALK_TO_SALES_REP",
            ),
        ),
        _enum_check("status", ("pending", "approved", "edited", "rejected")),
        UniqueConstraint("tenant_id", "id", name="uq_recommendations_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_recommendations_tenant_customer_customers",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "agent_run_id"],
            ["agent_runs.tenant_id", "agent_runs.id"],
            name="fk_recommendations_tenant_agent_run_agent_runs",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "decided_by"],
            ["users.tenant_id", "users.id"],
            name="fk_recommendations_tenant_decided_by_users",
        ),
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )
    agent_run_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("agent_runs.id"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    reasons: Mapped[list[Any]] = mapped_column(JSONB, nullable=False)
    citations: Mapped[list[Any]] = mapped_column(JSONB, nullable=False)
    requires_manager_review: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    decided_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(foreign_keys=[customer_id])
    agent_run: Mapped[AgentRun] = relationship(foreign_keys=[agent_run_id])
    decided_by_user: Mapped[User | None] = relationship(foreign_keys=[decided_by])


class DraftVersion(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "draft_versions"
    __table_args__ = (
        _enum_check("tone", ("formal", "friendly", "firm")),
        ForeignKeyConstraint(
            ["tenant_id", "recommendation_id"],
            ["recommendations.tenant_id", "recommendations.id"],
            name="fk_draft_versions_tenant_recommendation_recommendations",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "created_by"],
            ["users.tenant_id", "users.id"],
            name="fk_draft_versions_tenant_created_by_users",
        ),
    )

    recommendation_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recommendations.id"),
        nullable=False,
    )
    tone: Mapped[str] = mapped_column(Text, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    edited_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    edit_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    check_result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    recommendation: Mapped[Recommendation] = relationship(
        foreign_keys=[recommendation_id]
    )
    created_by_user: Mapped[User] = relationship(foreign_keys=[created_by])


class CollectionTask(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "collection_tasks"
    __table_args__ = (
        _enum_check("priority", ("HIGH", "MEDIUM", "LOW")),
        _enum_check(
            "action",
            (
                "CALL",
                "WHATSAPP",
                "EMAIL",
                "WAIT",
                "ESCALATE_TO_MANAGER",
                "TALK_TO_SALES_REP",
            ),
        ),
        _enum_check("status", ("pending", "done", "cancelled")),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_collection_tasks_tenant_customer_customers",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "recommendation_id"],
            ["recommendations.tenant_id", "recommendations.id"],
            name="fk_collection_tasks_tenant_recommendation_recommendations",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "assigned_to"],
            ["users.tenant_id", "users.id"],
            name="fk_collection_tasks_tenant_assigned_to_users",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "created_by"],
            ["users.tenant_id", "users.id"],
            name="fk_collection_tasks_tenant_created_by_users",
        ),
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )
    recommendation_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recommendations.id"),
        nullable=False,
    )
    assigned_to: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    priority: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    customer: Mapped[Customer] = relationship(foreign_keys=[customer_id])
    recommendation: Mapped[Recommendation] = relationship(
        foreign_keys=[recommendation_id]
    )
    assigned_to_user: Mapped[User] = relationship(foreign_keys=[assigned_to])
    created_by_user: Mapped[User] = relationship(foreign_keys=[created_by])


class Conversation(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_conversations_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["users.tenant_id", "users.id"],
            name="fk_conversations_tenant_user_users",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_conversations_tenant_customer_customers",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    customer_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=True,
    )

    user: Mapped[User] = relationship(foreign_keys=[user_id])
    customer: Mapped[Customer | None] = relationship(foreign_keys=[customer_id])


class Message(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "messages"
    __table_args__ = (
        _enum_check("role", ("user", "assistant", "tool")),
        ForeignKeyConstraint(
            ["tenant_id", "conversation_id"],
            ["conversations.tenant_id", "conversations.id"],
            name="fk_messages_tenant_conversation_conversations",
        ),
    )

    conversation_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("conversations.id"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    is_summary: Mapped[bool] = mapped_column(Boolean, nullable=False)

    conversation: Mapped[Conversation] = relationship(foreign_keys=[conversation_id])


class Document(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "documents"
    __table_args__ = (
        _enum_check(
            "type",
            (
                "credit_policy",
                "collection_policy",
                "payment_terms",
                "template",
                "contract",
                "other",
            ),
        ),
        UniqueConstraint("tenant_id", "id", name="uq_documents_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "uploaded_by"],
            ["users.tenant_id", "users.id"],
            name="fk_documents_tenant_uploaded_by_users",
        ),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_by: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    uploaded_by_user: Mapped[User] = relationship(foreign_keys=[uploaded_by])


class DocumentChunk(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("ix_document_chunks_tenant_id", "tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_document_chunks_tenant_document_documents",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_document_chunks_tenant_customer_customers",
        ),
    )

    document_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False,
    )
    customer_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=True,
    )
    policy_type: Mapped[str] = mapped_column(Text, nullable=False)
    section: Mapped[str | None] = mapped_column(Text, nullable=True)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(VECTOR(), nullable=True)

    document: Mapped[Document] = relationship(foreign_keys=[document_id])
    customer: Mapped[Customer | None] = relationship(foreign_keys=[customer_id])


class PolicyRule(UUIDPrimaryKey, TenantScoped, Base):
    __tablename__ = "policy_rules"
    __table_args__ = (
        _enum_check(
            "rule_type",
            ("escalation", "grace_period", "limit", "review_required"),
        ),
        ForeignKeyConstraint(
            ["tenant_id", "source_document_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_policy_rules_tenant_source_document_documents",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "confirmed_by"],
            ["users.tenant_id", "users.id"],
            name="fk_policy_rules_tenant_confirmed_by_users",
        ),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    rule_type: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    outcome: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source_document_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False,
    )
    source_section: Mapped[str] = mapped_column(Text, nullable=False)
    confirmed_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    source_document: Mapped[Document] = relationship(foreign_keys=[source_document_id])
    confirmed_by_user: Mapped[User | None] = relationship(foreign_keys=[confirmed_by])


class TenantSettings(TenantScoped, Base):
    __tablename__ = "tenant_settings"

    tenant_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("tenants.id"),
        primary_key=True,
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "updated_by"],
            ["users.tenant_id", "users.id"],
            name="fk_tenant_settings_tenant_updated_by_users",
        ),
    )
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_by: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    updated_by_user: Mapped[User | None] = relationship(foreign_keys=[updated_by])


class RiskScore(UUIDPrimaryKey, TenantScoped, Base):
    __tablename__ = "risk_scores"
    __table_args__ = (
        _enum_check("level", ("LOW", "MEDIUM", "HIGH", "CRITICAL")),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.id"],
            name="fk_risk_scores_tenant_customer_customers",
        ),
    )

    customer_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    level: Mapped[str] = mapped_column(Text, nullable=False)
    factors: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    customer: Mapped[Customer] = relationship(foreign_keys=[customer_id])


class AuditLog(UUIDPrimaryKey, TenantScoped, CreatedAt, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["users.tenant_id", "users.id"],
            name="fk_audit_logs_tenant_user_users",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False)
    before: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    after: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    user: Mapped[User] = relationship(foreign_keys=[user_id])
