"""Create the initial Tahseel database schema.

Revision ID: 0001_initial_schema
Revises:
"""

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute(
        """
        CREATE TABLE tenants (
            name TEXT NOT NULL,
            industry TEXT NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_tenants PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE users (
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_users PRIMARY KEY (id),
            CONSTRAINT ck_users_role_allowed_values
                CHECK (role IN ('OWNER', 'FINANCE_MANAGER', 'COLLECTOR')),
            CONSTRAINT fk_users_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE agent_runs (
            user_id UUID NOT NULL,
            run_type TEXT NOT NULL,
            input JSONB NOT NULL,
            output JSONB,
            tools_used JSONB NOT NULL,
            status TEXT NOT NULL,
            model TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            cost_estimate NUMERIC(10, 4),
            latency_ms INTEGER,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_agent_runs PRIMARY KEY (id),
            CONSTRAINT fk_agent_runs_user_id_users
                FOREIGN KEY (user_id) REFERENCES users (id),
            CONSTRAINT fk_agent_runs_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE audit_logs (
            user_id UUID NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            before JSONB,
            after JSONB,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_audit_logs PRIMARY KEY (id),
            CONSTRAINT fk_audit_logs_user_id_users
                FOREIGN KEY (user_id) REFERENCES users (id),
            CONSTRAINT fk_audit_logs_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE customers (
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            credit_limit NUMERIC(14, 2),
            payment_terms TEXT NOT NULL,
            tier TEXT NOT NULL,
            sales_rep TEXT,
            assigned_collector UUID,
            preferred_channel TEXT,
            contact_person TEXT,
            status TEXT NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_customers PRIMARY KEY (id),
            CONSTRAINT ck_customers_tier_allowed_values
                CHECK (tier IN ('strategic', 'regular')),
            CONSTRAINT ck_customers_preferred_channel_allowed_values
                CHECK (preferred_channel IN ('call', 'whatsapp', 'email')),
            CONSTRAINT ck_customers_status_allowed_values
                CHECK (status IN ('active', 'inactive')),
            CONSTRAINT fk_customers_assigned_collector_users
                FOREIGN KEY (assigned_collector) REFERENCES users (id),
            CONSTRAINT fk_customers_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE documents (
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            storage_path TEXT NOT NULL,
            uploaded_by UUID NOT NULL,
            effective_date DATE,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_documents PRIMARY KEY (id),
            CONSTRAINT ck_documents_type_allowed_values
                CHECK (type IN (
                    'credit_policy', 'collection_policy', 'payment_terms',
                    'template', 'contract', 'other'
                )),
            CONSTRAINT fk_documents_uploaded_by_users
                FOREIGN KEY (uploaded_by) REFERENCES users (id),
            CONSTRAINT fk_documents_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE tenant_settings (
            tenant_id UUID NOT NULL,
            settings JSONB NOT NULL,
            updated_by UUID,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_tenant_settings PRIMARY KEY (tenant_id),
            CONSTRAINT fk_tenant_settings_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id),
            CONSTRAINT fk_tenant_settings_updated_by_users
                FOREIGN KEY (updated_by) REFERENCES users (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE conversations (
            user_id UUID NOT NULL,
            customer_id UUID,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_conversations PRIMARY KEY (id),
            CONSTRAINT fk_conversations_user_id_users
                FOREIGN KEY (user_id) REFERENCES users (id),
            CONSTRAINT fk_conversations_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_conversations_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE customer_notes (
            customer_id UUID NOT NULL,
            note_type TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding VECTOR,
            author_id UUID NOT NULL,
            source TEXT NOT NULL,
            deleted_at TIMESTAMP WITH TIME ZONE,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_customer_notes PRIMARY KEY (id),
            CONSTRAINT ck_customer_notes_note_type_allowed_values
                CHECK (note_type IN ('collector', 'sales_rep', 'call_outcome')),
            CONSTRAINT ck_customer_notes_source_allowed_values
                CHECK (source IN ('ui', 'import')),
            CONSTRAINT fk_customer_notes_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_customer_notes_author_id_users
                FOREIGN KEY (author_id) REFERENCES users (id),
            CONSTRAINT fk_customer_notes_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute("CREATE INDEX ix_customer_notes_tenant_id ON customer_notes (tenant_id)")
    op.execute(
        """
        CREATE TABLE document_chunks (
            document_id UUID NOT NULL,
            customer_id UUID,
            policy_type TEXT NOT NULL,
            section TEXT,
            page INTEGER,
            effective_date DATE,
            text TEXT NOT NULL,
            embedding VECTOR,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_document_chunks PRIMARY KEY (id),
            CONSTRAINT fk_document_chunks_document_id_documents
                FOREIGN KEY (document_id) REFERENCES documents (id),
            CONSTRAINT fk_document_chunks_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_document_chunks_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_tenant_id ON document_chunks (tenant_id)"
    )
    op.execute(
        """
        CREATE TABLE invoices (
            customer_id UUID NOT NULL,
            invoice_number TEXT NOT NULL,
            invoice_date DATE NOT NULL,
            due_date DATE NOT NULL,
            amount NUMERIC(14, 2) NOT NULL,
            paid_amount NUMERIC(14, 2) NOT NULL,
            status TEXT NOT NULL,
            dispute_reason TEXT,
            disputed_by UUID,
            disputed_at TIMESTAMP WITH TIME ZONE,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_invoices PRIMARY KEY (id),
            CONSTRAINT ck_invoices_status_allowed_values
                CHECK (status IN ('open', 'paid', 'disputed')),
            CONSTRAINT uq_invoices_tenant_invoice_number
                UNIQUE (tenant_id, invoice_number),
            CONSTRAINT fk_invoices_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_invoices_disputed_by_users
                FOREIGN KEY (disputed_by) REFERENCES users (id),
            CONSTRAINT fk_invoices_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_invoices_tenant_customer_due
        ON invoices (tenant_id, customer_id, due_date)
        """
    )
    op.execute(
        """
        CREATE TABLE policy_rules (
            name TEXT NOT NULL,
            rule_type TEXT NOT NULL,
            condition JSONB NOT NULL,
            outcome JSONB NOT NULL,
            source_document_id UUID NOT NULL,
            source_section TEXT NOT NULL,
            confirmed_by UUID,
            confirmed_at TIMESTAMP WITH TIME ZONE,
            active BOOLEAN NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            CONSTRAINT pk_policy_rules PRIMARY KEY (id),
            CONSTRAINT ck_policy_rules_rule_type_allowed_values
                CHECK (rule_type IN (
                    'escalation', 'grace_period', 'limit', 'review_required'
                )),
            CONSTRAINT fk_policy_rules_source_document_id_documents
                FOREIGN KEY (source_document_id) REFERENCES documents (id),
            CONSTRAINT fk_policy_rules_confirmed_by_users
                FOREIGN KEY (confirmed_by) REFERENCES users (id),
            CONSTRAINT fk_policy_rules_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE recommendations (
            customer_id UUID NOT NULL,
            agent_run_id UUID NOT NULL,
            action TEXT NOT NULL,
            reasons JSONB NOT NULL,
            citations JSONB NOT NULL,
            requires_manager_review BOOLEAN NOT NULL,
            status TEXT NOT NULL,
            decided_by UUID,
            decided_at TIMESTAMP WITH TIME ZONE,
            decision_reason TEXT,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_recommendations PRIMARY KEY (id),
            CONSTRAINT ck_recommendations_action_allowed_values
                CHECK (action IN (
                    'CALL', 'WHATSAPP', 'EMAIL', 'WAIT',
                    'ESCALATE_TO_MANAGER', 'TALK_TO_SALES_REP'
                )),
            CONSTRAINT ck_recommendations_status_allowed_values
                CHECK (status IN ('pending', 'approved', 'edited', 'rejected')),
            CONSTRAINT fk_recommendations_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_recommendations_agent_run_id_agent_runs
                FOREIGN KEY (agent_run_id) REFERENCES agent_runs (id),
            CONSTRAINT fk_recommendations_decided_by_users
                FOREIGN KEY (decided_by) REFERENCES users (id),
            CONSTRAINT fk_recommendations_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE risk_scores (
            customer_id UUID NOT NULL,
            score SMALLINT NOT NULL,
            level TEXT NOT NULL,
            factors JSONB NOT NULL,
            calculated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            CONSTRAINT pk_risk_scores PRIMARY KEY (id),
            CONSTRAINT ck_risk_scores_level_allowed_values
                CHECK (level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
            CONSTRAINT fk_risk_scores_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_risk_scores_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE collection_tasks (
            customer_id UUID NOT NULL,
            recommendation_id UUID NOT NULL,
            assigned_to UUID NOT NULL,
            priority TEXT NOT NULL,
            action TEXT NOT NULL,
            due_at TIMESTAMP WITH TIME ZONE NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            created_by UUID NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_collection_tasks PRIMARY KEY (id),
            CONSTRAINT ck_collection_tasks_priority_allowed_values
                CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
            CONSTRAINT ck_collection_tasks_action_allowed_values
                CHECK (action IN (
                    'CALL', 'WHATSAPP', 'EMAIL', 'WAIT',
                    'ESCALATE_TO_MANAGER', 'TALK_TO_SALES_REP'
                )),
            CONSTRAINT ck_collection_tasks_status_allowed_values
                CHECK (status IN ('pending', 'done', 'cancelled')),
            CONSTRAINT fk_collection_tasks_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_collection_tasks_recommendation_id_recommendations
                FOREIGN KEY (recommendation_id) REFERENCES recommendations (id),
            CONSTRAINT fk_collection_tasks_assigned_to_users
                FOREIGN KEY (assigned_to) REFERENCES users (id),
            CONSTRAINT fk_collection_tasks_created_by_users
                FOREIGN KEY (created_by) REFERENCES users (id),
            CONSTRAINT fk_collection_tasks_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE draft_versions (
            recommendation_id UUID NOT NULL,
            tone TEXT NOT NULL,
            original_text TEXT NOT NULL,
            edited_text TEXT,
            edit_reason TEXT,
            check_result JSONB NOT NULL,
            created_by UUID NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_draft_versions PRIMARY KEY (id),
            CONSTRAINT ck_draft_versions_tone_allowed_values
                CHECK (tone IN ('formal', 'friendly', 'firm')),
            CONSTRAINT fk_draft_versions_recommendation_id_recommendations
                FOREIGN KEY (recommendation_id) REFERENCES recommendations (id),
            CONSTRAINT fk_draft_versions_created_by_users
                FOREIGN KEY (created_by) REFERENCES users (id),
            CONSTRAINT fk_draft_versions_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE messages (
            conversation_id UUID NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            tool_calls JSONB,
            is_summary BOOLEAN NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_messages PRIMARY KEY (id),
            CONSTRAINT ck_messages_role_allowed_values
                CHECK (role IN ('user', 'assistant', 'tool')),
            CONSTRAINT fk_messages_conversation_id_conversations
                FOREIGN KEY (conversation_id) REFERENCES conversations (id),
            CONSTRAINT fk_messages_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE payments (
            customer_id UUID NOT NULL,
            invoice_id UUID NOT NULL,
            amount NUMERIC(14, 2) NOT NULL,
            payment_date DATE NOT NULL,
            method TEXT NOT NULL,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_payments PRIMARY KEY (id),
            CONSTRAINT fk_payments_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_payments_invoice_id_invoices
                FOREIGN KEY (invoice_id) REFERENCES invoices (id),
            CONSTRAINT fk_payments_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_payments_tenant_invoice ON payments (tenant_id, invoice_id)"
    )
    op.execute(
        """
        CREATE TABLE promises_to_pay (
            customer_id UUID NOT NULL,
            invoice_id UUID NOT NULL,
            promised_amount NUMERIC(14, 2) NOT NULL,
            promise_date DATE NOT NULL,
            status TEXT NOT NULL,
            recorded_by UUID NOT NULL,
            resolved_at TIMESTAMP WITH TIME ZONE,
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            CONSTRAINT pk_promises_to_pay PRIMARY KEY (id),
            CONSTRAINT ck_promises_to_pay_status_allowed_values
                CHECK (status IN ('pending', 'kept', 'broken')),
            CONSTRAINT fk_promises_to_pay_customer_id_customers
                FOREIGN KEY (customer_id) REFERENCES customers (id),
            CONSTRAINT fk_promises_to_pay_invoice_id_invoices
                FOREIGN KEY (invoice_id) REFERENCES invoices (id),
            CONSTRAINT fk_promises_to_pay_recorded_by_users
                FOREIGN KEY (recorded_by) REFERENCES users (id),
            CONSTRAINT fk_promises_to_pay_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
    )


def downgrade() -> None:
    for table_name in (
        "promises_to_pay",
        "payments",
        "messages",
        "draft_versions",
        "collection_tasks",
        "risk_scores",
        "recommendations",
        "policy_rules",
        "invoices",
        "document_chunks",
        "customer_notes",
        "conversations",
        "tenant_settings",
        "documents",
        "customers",
        "audit_logs",
        "agent_runs",
        "users",
        "tenants",
    ):
        op.drop_table(table_name)
