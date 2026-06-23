"""Proje modelinden kullanılmayan alanları kaldır.

full_description diyalogda tek açıklama alanıyla birleştirildi;
demo_url, target_end_date ve is_featured UI'dan çıkarıldığı için
veritabanı temizleniyor.

Revision ID: 0003_drop_project_unused_fields
Revises: 0002_drop_idea_score_fields
Create Date: 2026-06-24
"""
from __future__ import annotations

from alembic import op

revision = "0003_drop_project_unused_fields"
down_revision = "0002_drop_idea_score_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("projects") as batch_op:
        batch_op.drop_column("full_description")
        batch_op.drop_column("demo_url")
        batch_op.drop_column("target_end_date")
        batch_op.drop_column("is_featured")


def downgrade() -> None:
    import sqlalchemy as sa

    with op.batch_alter_table("projects") as batch_op:
        batch_op.add_column(sa.Column("full_description", sa.Text, nullable=True))
        batch_op.add_column(sa.Column("demo_url", sa.String(500), nullable=True))
        batch_op.add_column(sa.Column("target_end_date", sa.Date, nullable=True))
        batch_op.add_column(sa.Column("is_featured", sa.Boolean, nullable=False, server_default="0"))
