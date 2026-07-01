"""Memo — proje bağımsız serbest not defteri modeli."""
from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base_model import Base, TimestampMixin


class Memo(Base, TimestampMixin):
    __tablename__ = "memos"

    id:           Mapped[int]       = mapped_column(Integer, primary_key=True, autoincrement=True)
    title:        Mapped[str]       = mapped_column(String(255), nullable=False)
    body:         Mapped[str]       = mapped_column(Text, nullable=False, default="")
    drawing_data: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    # Kullanıcının sürükle-bırak ile belirlediği görüntüleme sırası.
    sort_order:   Mapped[int]       = mapped_column(Integer, nullable=False, default=0)
