"""Notlar/Fikirler listelerine sürükle-bırak sıralaması için sort_order ekle.

Projects tablosu zaten display_order kolonuna sahip; burada yalnızca eski
DB'lerde eksik kalmış olma ihtimaline karşı savunmacı olarak eklenir.
Yeni kolon eklendiğinde tüm satırlar aynı varsayılanı (0) taşıyacağından,
önceki görsel sırayı (created_at azalan) koruyacak şekilde backfill edilir.

Revision ID: 0006_add_list_sort_order
Revises: 0005_add_memo_drawing_data
Create Date: 2026-07-01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0006_add_list_sort_order"
down_revision = "0005_add_memo_drawing_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect, text

    conn = op.get_bind()
    _add_column_if_missing(conn, "notes", "sort_order")
    _add_column_if_missing(conn, "ideas", "sort_order")
    _add_column_if_missing(conn, "projects", "display_order")
    _backfill(conn, "notes", "sort_order")
    _backfill(conn, "ideas", "sort_order")


def _add_column_if_missing(conn, table_name: str, column_name: str) -> None:
    from sqlalchemy import inspect

    existing = {col["name"] for col in inspect(conn).get_columns(table_name)}
    if column_name in existing:
        return
    op.add_column(
        table_name,
        sa.Column(column_name, sa.Integer(), nullable=False, server_default="0"),
    )


def _backfill(conn, table_name: str, column_name: str) -> None:
    from sqlalchemy import text

    rows = conn.execute(
        text(f"SELECT id FROM {table_name} ORDER BY created_at DESC, id DESC")
    ).fetchall()
    for index, row in enumerate(rows):
        conn.execute(
            text(f"UPDATE {table_name} SET {column_name} = :idx WHERE id = :row_id"),
            {"idx": index, "row_id": row[0]},
        )


def downgrade() -> None:
    with op.batch_alter_table("notes") as batch_op:
        batch_op.drop_column("sort_order")
    with op.batch_alter_table("ideas") as batch_op:
        batch_op.drop_column("sort_order")
