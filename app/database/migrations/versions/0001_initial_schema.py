"""initial schema with tenant isolation (RLS)

Revision ID: 0001
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

APP_ROLE = "bizops_app"
TENANT_TABLES = ("users", "business_policies", "tasks")
_CTX = "NULLIF(current_setting('app.current_business_id', true), '')::uuid"


def _id() -> sa.Column:
    return sa.Column(
        "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
    )


def _business_id() -> sa.Column:
    return sa.Column("business_id", sa.Uuid(), nullable=False)


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(),
                  nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(),
                  nullable=False),
    ]


def _fk(table: str) -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint(
        ["business_id"], ["businesses.id"], name=op.f(f"fk_{table}_business_id_businesses")
    )


def _enable_rls(table: str, column: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {table} "
        f"USING ({column} = {_CTX}) WITH CHECK ({column} = {_CTX})"
    )


def upgrade() -> None:
    # Tables created below (by the owner role) are readable/writable by the app role.
    # No DELETE on purpose: add it per table when a feature needs it.
    op.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"GRANT SELECT, INSERT, UPDATE ON TABLES TO {APP_ROLE}"
    )

    op.create_table(
        "businesses",
        _id(),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("timezone", sa.String(64), server_default="UTC", nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_businesses")),
    )

    op.create_table(
        "users",
        _id(),
        _business_id(),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        _fk("users"),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.CheckConstraint("role IN ('owner', 'manager')", name=op.f("ck_users_user_role")),
        sa.CheckConstraint("email = lower(email)", name=op.f("ck_users_email_lowercase")),
    )
    op.create_index(op.f("ix_users_business_id"), "users", ["business_id"])

    op.create_table(
        "business_policies",
        _id(),
        _business_id(),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_business_policies")),
        _fk("business_policies"),
        sa.UniqueConstraint("business_id", "key",
                            name=op.f("uq_business_policies_business_id_key")),
        sa.CheckConstraint(
            "source IN ('user_stated', 'system_default', 'ai_suggested')",
            name=op.f("ck_business_policies_policy_source"),
        ),
    )

    op.create_table(
        "tasks",
        _id(),
        _business_id(),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
        _fk("tasks"),
        sa.CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')",
            name=op.f("ck_tasks_task_status"),
        ),
    )
    op.create_index(op.f("ix_tasks_business_id"), "tasks", ["business_id"])

    # Tenant isolation. FORCE makes it apply to the table owner too (superusers still bypass).
    for table in TENANT_TABLES:
        _enable_rls(table, "business_id")
    _enable_rls("businesses", "id")


def downgrade() -> None:
    for table in ("tasks", "business_policies", "users", "businesses"):
        op.drop_table(table)  # policies and indexes are dropped with the table
    op.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"REVOKE SELECT, INSERT, UPDATE ON TABLES FROM {APP_ROLE}"
    )