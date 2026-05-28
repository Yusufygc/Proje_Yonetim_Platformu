from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base_model import Base, TimestampMixin


class Setting(Base, TimestampMixin):
    """Uygulama ayarları için anahtar/değer kaydı."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
