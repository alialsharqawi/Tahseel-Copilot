"""Enforce same-tenant foreign-key relationships.

Revision ID: 0002_tenant_scoped_foreign_keys
Revises: 0001_initial_schema
"""

from alembic import op

revision = "0002_tenant_scoped_foreign_keys"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

TENANT_KEY_CONSTRAINTS = (
    ("users", "uq_users_tenant_id"),
    ("customers", "uq_customers_tenant_id"),
    ("invoices", "uq_invoices_tenant_id"),
    ("agent_runs", "uq_agent_runs_tenant_id"),
    ("recommendations", "uq_recommendations_tenant_id"),
    ("conversations", "uq_conversations_tenant_id"),
    ("documents", "uq_documents_tenant_id"),
)

TENANT_FOREIGN_KEYS = (
    (
        "fk_customers_tenant_assigned_collector_users",
        "customers",
        "users",
        ["tenant_id", "assigned_collector"],
    ),
    (
        "fk_invoices_tenant_customer_customers",
        "invoices",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_invoices_tenant_disputed_by_users",
        "invoices",
        "users",
        ["tenant_id", "disputed_by"],
    ),
    (
        "fk_payments_tenant_customer_customers",
        "payments",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_payments_tenant_invoice_invoices",
        "payments",
        "invoices",
        ["tenant_id", "invoice_id"],
    ),
    (
        "fk_promises_to_pay_tenant_customer_customers",
        "promises_to_pay",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_promises_to_pay_tenant_invoice_invoices",
        "promises_to_pay",
        "invoices",
        ["tenant_id", "invoice_id"],
    ),
    (
        "fk_promises_to_pay_tenant_recorded_by_users",
        "promises_to_pay",
        "users",
        ["tenant_id", "recorded_by"],
    ),
    (
        "fk_customer_notes_tenant_customer_customers",
        "customer_notes",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_customer_notes_tenant_author_users",
        "customer_notes",
        "users",
        ["tenant_id", "author_id"],
    ),
    (
        "fk_agent_runs_tenant_user_users",
        "agent_runs",
        "users",
        ["tenant_id", "user_id"],
    ),
    (
        "fk_recommendations_tenant_customer_customers",
        "recommendations",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_recommendations_tenant_agent_run_agent_runs",
        "recommendations",
        "agent_runs",
        ["tenant_id", "agent_run_id"],
    ),
    (
        "fk_recommendations_tenant_decided_by_users",
        "recommendations",
        "users",
        ["tenant_id", "decided_by"],
    ),
    (
        "fk_draft_versions_tenant_recommendation_recommendations",
        "draft_versions",
        "recommendations",
        ["tenant_id", "recommendation_id"],
    ),
    (
        "fk_draft_versions_tenant_created_by_users",
        "draft_versions",
        "users",
        ["tenant_id", "created_by"],
    ),
    (
        "fk_collection_tasks_tenant_customer_customers",
        "collection_tasks",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_collection_tasks_tenant_recommendation_recommendations",
        "collection_tasks",
        "recommendations",
        ["tenant_id", "recommendation_id"],
    ),
    (
        "fk_collection_tasks_tenant_assigned_to_users",
        "collection_tasks",
        "users",
        ["tenant_id", "assigned_to"],
    ),
    (
        "fk_collection_tasks_tenant_created_by_users",
        "collection_tasks",
        "users",
        ["tenant_id", "created_by"],
    ),
    (
        "fk_conversations_tenant_user_users",
        "conversations",
        "users",
        ["tenant_id", "user_id"],
    ),
    (
        "fk_conversations_tenant_customer_customers",
        "conversations",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_messages_tenant_conversation_conversations",
        "messages",
        "conversations",
        ["tenant_id", "conversation_id"],
    ),
    (
        "fk_documents_tenant_uploaded_by_users",
        "documents",
        "users",
        ["tenant_id", "uploaded_by"],
    ),
    (
        "fk_document_chunks_tenant_document_documents",
        "document_chunks",
        "documents",
        ["tenant_id", "document_id"],
    ),
    (
        "fk_document_chunks_tenant_customer_customers",
        "document_chunks",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_tenant_settings_tenant_updated_by_users",
        "tenant_settings",
        "users",
        ["tenant_id", "updated_by"],
    ),
    (
        "fk_policy_rules_tenant_source_document_documents",
        "policy_rules",
        "documents",
        ["tenant_id", "source_document_id"],
    ),
    (
        "fk_policy_rules_tenant_confirmed_by_users",
        "policy_rules",
        "users",
        ["tenant_id", "confirmed_by"],
    ),
    (
        "fk_risk_scores_tenant_customer_customers",
        "risk_scores",
        "customers",
        ["tenant_id", "customer_id"],
    ),
    (
        "fk_audit_logs_tenant_user_users",
        "audit_logs",
        "users",
        ["tenant_id", "user_id"],
    ),
)


def upgrade() -> None:
    for table_name, constraint_name in TENANT_KEY_CONSTRAINTS:
        op.create_unique_constraint(
            constraint_name,
            table_name,
            ["tenant_id", "id"],
        )

    for (
        constraint_name,
        table_name,
        referred_table,
        local_columns,
    ) in TENANT_FOREIGN_KEYS:
        op.create_foreign_key(
            constraint_name,
            table_name,
            referred_table,
            local_columns,
            ["tenant_id", "id"],
        )


def downgrade() -> None:
    for constraint_name, table_name, _, _ in reversed(TENANT_FOREIGN_KEYS):
        op.drop_constraint(constraint_name, table_name, type_="foreignkey")

    for table_name, constraint_name in reversed(TENANT_KEY_CONSTRAINTS):
        op.drop_constraint(constraint_name, table_name, type_="unique")
