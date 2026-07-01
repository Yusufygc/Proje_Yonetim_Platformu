from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums.note_type import NoteType
from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.project import Project


class Note(Base, TimestampMixin):
    """Proje notlarını saklayan ORM modeli."""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    note_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=NoteType.GENERAL.value
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # Kullanıcının sürükle-bırak ile belirlediği görüntüleme sırası.
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Optional bindings
    stage_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("project_stages.id", ondelete="SET NULL"), nullable=True
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )

    project: Mapped["Project"] = relationship("Project", back_populates="notes")

    def __repr__(self) -> str:
        return f"<Note id={self.id} title='{self.title}' type={self.note_type}>"
