"""create memos table

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-30
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_create_memos_table"
down_revision = "0003_drop_project_unused_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect
    conn = op.get_bind()
    if inspect(conn).has_table("memos"):
        return
    op.create_table(
        "memos",
        sa.Column("id",         sa.Integer(),              primary_key=True, autoincrement=True),
        sa.Column("title",      sa.String(255),            nullable=False),
        sa.Column("body",       sa.Text(),                 nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("memos")
