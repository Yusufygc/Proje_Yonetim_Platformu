"""Fikir modelinden kullanılmayan skor ve beklenen değer sütunlarını kaldır.

Revision ID: 0002_drop_idea_score_fields
Revises: 0001_current_schema
Create Date: 2026-06-24
"""
from __future__ import annotations

from alembic import op

revision = "0002_drop_idea_score_fields"
down_revision = "0001_current_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect
    conn = op.get_bind()
    existing = {col["name"] for col in inspect(conn).get_columns("ideas")}
    columns_to_drop = ["expected_value", "difficulty", "effort", "confidence"]
    cols_present = [c for c in columns_to_drop if c in existing]
    if not cols_present:
        return
    with op.batch_alter_table("ideas") as batch_op:
        for col in cols_present:
            batch_op.drop_column(col)


def downgrade() -> None:
    import sqlalchemy as sa

    with op.batch_alter_table("ideas") as batch_op:
        batch_op.add_column(sa.Column("expected_value", sa.Text, nullable=True))
        batch_op.add_column(sa.Column("difficulty", sa.Integer, nullable=True))
        batch_op.add_column(sa.Column("effort", sa.Integer, nullable=True))
        batch_op.add_column(sa.Column("confidence", sa.Integer, nullable=True))
