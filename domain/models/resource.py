from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums.resource_type import ResourceType
from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.project import Project


class Resource(Base, TimestampMixin):
    """Proje kaynaklarını (link/doküman) saklayan ORM modeli."""

    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    resource_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ResourceType.DOCUMENT.value
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Optional bindings
    idea_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ideas.id", ondelete="SET NULL"), nullable=True
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )

    project: Mapped["Project"] = relationship("Project", back_populates="resources")

    def __repr__(self) -> str:
        return f"<Resource id={self.id} title='{self.title}' type={self.resource_type}>"
