"""
Proje varlığı (SQLAlchemy ORM modeli).
05_VERI_MODELI.md'deki projects tablosunu karşılar.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums.priority import Priority
from domain.enums.project_status import ProjectStatus
from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.project_stage import ProjectStage
    from domain.models.task import Task


class Project(Base, TimestampMixin):
    """Bir projenin tüm meta verilerini ve durumunu tutan ana varlık."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    full_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    problem_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ProjectStatus.PLANNED.value
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=Priority.MEDIUM.value
    )
    health: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    docs_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    target_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    stages: Mapped[list["ProjectStage"]] = relationship(
        "ProjectStage", back_populates="project", cascade="all, delete-orphan"
    )

    # İlişkiler (diğer modeller eklendikçe aktif edilecek)
    # tags: Mapped[list["ProjectTag"]] = relationship("ProjectTag", back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project id={self.id} title='{self.title}' status={self.status}>"
