"""
Proje aşaması ORM modeli.
Her proje oluşturulduğunda varsayılan aşamalar bu tabloya kopyalanır.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums.stage_status import StageStatus
from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.project import Project


class ProjectStage(Base, TimestampMixin):
    """Bir projeye ait tek bir süreç aşamasını temsil eder."""

    __tablename__ = "project_stages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), nullable=False, default="#6366F1")
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=StageStatus.PENDING.value
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    project: Mapped["Project"] = relationship("Project", back_populates="stages")

    def __repr__(self) -> str:
        return f"<ProjectStage id={self.id} name='{self.name}' status={self.status}>"
