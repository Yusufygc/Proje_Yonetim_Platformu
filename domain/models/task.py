"""
Görev ORM modeli.
Bir projeye bağlı iş birimini temsil eder; isteğe bağlı olarak aşamaya da bağlanabilir.
"""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums.priority import Priority
from domain.enums.task_status import TaskStatus
from domain.enums.task_type import TaskType
from infrastructure.database.base_model import Base, TimestampMixin

if TYPE_CHECKING:
    from domain.models.checklist_item import ChecklistItem
    from domain.models.project import Project
    from domain.models.project_stage import ProjectStage


class Task(Base, TimestampMixin):
    """Bir projeye ait tek bir görevi temsil eder."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("project_stages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_task_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=TaskStatus.TODO.value
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=Priority.MEDIUM.value
    )
    task_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default=TaskType.TASK.value
    )
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    stage: Mapped[Optional["ProjectStage"]] = relationship("ProjectStage")
    parent_task: Mapped[Optional["Task"]] = relationship(
        "Task",
        remote_side=[id],
        back_populates="subtasks",
    )
    subtasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="parent_task",
        cascade="all, delete-orphan",
        order_by="Task.order_index",
    )
    checklist_items: Mapped[list["ChecklistItem"]] = relationship(
        "ChecklistItem",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="ChecklistItem.order_index",
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title='{self.title}' status={self.status}>"
