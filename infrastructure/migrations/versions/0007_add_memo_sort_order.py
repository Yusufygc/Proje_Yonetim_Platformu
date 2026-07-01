"""Notlarım (memo) listesine sürükle-bırak sıralaması için sort_order ekle.

Yeni kolon eklendiğinde tüm satırlar aynı varsayılanı (0) taşıyacağından,
önceki görsel sırayı (updated_at azalan — memo repository'nin mevcut ORDER BY'ı)
koruyacak şekilde backfill edilir.

Revision ID: 0007_add_memo_sort_order
Revises: 0006_add_list_sort_order
Create Date: 2026-07-01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0007_add_memo_sort_order"
down_revision = "0006_add_list_sort_order"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect, text

    conn = op.get_bind()
    existing = {col["name"] for col in inspect(conn).get_columns("memos")}
    if "sort_order" not in existing:
        op.add_column(
            "memos",
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        )

    rows = conn.execute(
        text("SELECT id FROM memos ORDER BY updated_at DESC, id DESC")
    ).fetchall()
    for index, row in enumerate(rows):
        conn.execute(
            text("UPDATE memos SET sort_order = :idx WHERE id = :row_id"),
            {"idx": index, "row_id": row[0]},
        )


def downgrade() -> None:
    with op.batch_alter_table("memos") as batch_op:
        batch_op.drop_column("sort_order")
