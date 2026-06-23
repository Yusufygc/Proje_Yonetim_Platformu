"""
Proje varlığı (SQLAlchemy ORM modeli).
05_VERI_MODELI.md'deki projects tablosunu karşılar.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums.priority import Priority
from domain.enums.project_health import ProjectHealth
from domain.enums.project_status import ProjectStatus
from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.activity_log import ActivityLog
    from domain.models.attachment import Attachment
    from domain.models.decision_record import DecisionRecord
    from domain.models.note import Note
    from domain.models.project_idea import ProjectIdea
    from domain.models.project_stage import ProjectStage
    from domain.models.project_tag import ProjectTag
    from domain.models.resource import Resource
    from domain.models.task import Task


class Project(Base, TimestampMixin):
    """Bir projenin tüm meta verilerini ve durumunu tutan ana varlık."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    problem_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(ProjectStatus, native_enum=False), nullable=False, default=ProjectStatus.PLANNED.value
    )
    priority: Mapped[str] = mapped_column(
        SAEnum(Priority, native_enum=False), nullable=False, default=Priority.MEDIUM.value
    )
    health: Mapped[str] = mapped_column(
        SAEnum(ProjectHealth, native_enum=False), nullable=False, default=ProjectHealth.UNKNOWN.value
    )
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    manual_progress_percent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    docs_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    stages: Mapped[list["ProjectStage"]] = relationship(
        "ProjectStage", back_populates="project", cascade="all, delete-orphan"
    )

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    tags: Mapped[list["ProjectTag"]] = relationship(
        "ProjectTag", back_populates="project", cascade="all, delete-orphan"
    )
    project_ideas: Mapped[list["ProjectIdea"]] = relationship(
        "ProjectIdea", back_populates="project", cascade="all, delete-orphan"
    )
    decisions: Mapped[list["DecisionRecord"]] = relationship(
        "DecisionRecord", back_populates="project", cascade="all, delete-orphan"
    )
    notes: Mapped[list["Note"]] = relationship(
        "Note", back_populates="project", cascade="all, delete-orphan"
    )
    resources: Mapped[list["Resource"]] = relationship(
        "Resource", back_populates="project", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment", back_populates="project", cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} title='{self.title}' status={self.status}>"
