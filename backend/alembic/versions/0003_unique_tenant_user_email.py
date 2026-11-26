"""Enforce tenant-scoped case-insensitive uniqueness for user emails.

Revision ID: 0003_unique_tenant_user_email
Revises: 0002_tenant_scoped_foreign_keys
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_unique_tenant_user_email"
down_revision = "0002_tenant_scoped_foreign_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_users_tenant_lower_email",
        "users",
        ["tenant_id", sa.literal_column("lower(email)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_users_tenant_lower_email", table_name="users")
