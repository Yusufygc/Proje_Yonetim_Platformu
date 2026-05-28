from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.project import Project


class Attachment(Base, TimestampMixin):
    """Projeye, göreve veya karara bağlı yerel dosya/çıktı referansı."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )
    decision_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("decision_records.id", ondelete="SET NULL"), nullable=True
    )
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    attachment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="OUTPUT")
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="attachments")
