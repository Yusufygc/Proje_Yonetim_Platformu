"""
Checklist öğesi ORM modeli.
Bir göreve ait tamamlanabilir alt maddeyi temsil eder.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.task import Task


class ChecklistItem(Base, TimestampMixin):
    """Bir göreve ait tek bir checklist maddesini temsil eder."""

    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    task: Mapped["Task"] = relationship("Task", back_populates="checklist_items")

    def __repr__(self) -> str:
        return f"<ChecklistItem id={self.id} text='{self.text[:20]}' is_done={self.is_done}>"
