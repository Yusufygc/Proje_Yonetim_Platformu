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
    with op.batch_alter_table("ideas") as batch_op:
        batch_op.drop_column("expected_value")
        batch_op.drop_column("difficulty")
        batch_op.drop_column("effort")
        batch_op.drop_column("confidence")


def downgrade() -> None:
    import sqlalchemy as sa

    with op.batch_alter_table("ideas") as batch_op:
        batch_op.add_column(sa.Column("expected_value", sa.Text, nullable=True))
        batch_op.add_column(sa.Column("difficulty", sa.Integer, nullable=True))
        batch_op.add_column(sa.Column("effort", sa.Integer, nullable=True))
        batch_op.add_column(sa.Column("confidence", sa.Integer, nullable=True))
