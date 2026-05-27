"""
Tüm SQLAlchemy modellerinin türetileceği DeclarativeBase ve ortak sütun tanımları.
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Tüm ORM modellerinin türetildiği taban sınıf."""
    pass


class TimestampMixin:
    """
    created_at ve updated_at sütunlarını otomatik yöneten mixin.
    Her modelde tekrar yazılmasın diye ayrı tutuldu.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
