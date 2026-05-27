from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums.decision_status import DecisionStatus
from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.project import Project


class DecisionRecord(Base, TimestampMixin):
    """Proje kararlarını saklayan ORM modeli."""

    __tablename__ = "decision_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    alternatives: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=DecisionStatus.DRAFT.value
    )

    # Optional bindings (For MVP, just project is enough, but adding columns for future)
    stage_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    task_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    project: Mapped["Project"] = relationship("Project")

    def __repr__(self) -> str:
        return f"<DecisionRecord id={self.id} title='{self.title}' status={self.status}>"
