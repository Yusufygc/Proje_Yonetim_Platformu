from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.project import Project


class ProjectTag(Base, TimestampMixin):
    """Projeye ait sınıflandırma etiketi."""

    __tablename__ = "project_tags"
    __table_args__ = (UniqueConstraint("project_id", "tag_name", name="uq_project_tag"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_name: Mapped[str] = mapped_column(String(80), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="tags")
