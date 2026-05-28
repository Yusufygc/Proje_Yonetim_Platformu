from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.idea import Idea
    from domain.models.project import Project


class ProjectIdea(Base, TimestampMixin):
    """Bir proje ile fikri ilişki tipiyle bağlar."""

    __tablename__ = "project_ideas"
    __table_args__ = (UniqueConstraint("project_id", "idea_id", "relation_type", name="uq_project_idea_relation"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    idea_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation_type: Mapped[str] = mapped_column(String(30), nullable=False, default="SOURCE")

    project: Mapped["Project"] = relationship("Project", back_populates="project_ideas")
    idea: Mapped["Idea"] = relationship("Idea", back_populates="project_links")
