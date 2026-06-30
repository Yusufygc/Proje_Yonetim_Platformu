"""add drawing_data column to memos

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-30
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_add_memo_drawing_data"
down_revision = "0004_create_memos_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect
    conn = op.get_bind()
    cols = [c["name"] for c in inspect(conn).get_columns("memos")]
    if "drawing_data" not in cols:
        op.add_column("memos", sa.Column("drawing_data", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("memos", "drawing_data")
