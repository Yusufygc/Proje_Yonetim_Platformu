"""
Dashboard Service - Ana ekran istatistiklerini hesaplar ve döner.
"""
import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.enums.priority import Priority
from domain.enums.project_status import ProjectStatus
from domain.enums.task_status import TaskStatus
from domain.models.idea import Idea
from domain.models.project import Project
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

_LIST_LIMIT = 10
_CLOSED_TASK_STATUSES = [TaskStatus.DONE.value, TaskStatus.CANCELLED.value]


def _count(sess: Session, model: type[Any], *conditions: Any) -> int:
    statement = select(func.count()).select_from(model)
    for condition in conditions:
        statement = statement.where(condition)
    return sess.scalar(statement) or 0


class DashboardService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_dashboard_stats(self) -> dict[str, Any]:
        """Dashboard'da gösterilecek sayaçları ve listeleri hazırlar."""
        with self._db.session() as sess:
            return {
                "total_ideas": _count(sess, Idea),
                "total_tasks": _count(sess, Task),
                "open_tasks": _count(sess, Task, Task.status.not_in(_CLOSED_TASK_STATUSES)),
                "active_projects": _count(sess, Project, Project.status == ProjectStatus.ACTIVE.value),
                "high_priority_tasks": self._high_priority_tasks(sess),
                "recent_ideas": self._recent_ideas(sess),
            }

    @staticmethod
    def _high_priority_tasks(sess: Session) -> list[dict[str, Any]]:
        statement = (
            select(Task, Project.title)
            .join(Project, Task.project_id == Project.id)
            .where(Task.priority.in_([Priority.HIGH.value, Priority.CRITICAL.value]))
            .where(Task.status.not_in(_CLOSED_TASK_STATUSES))
            .order_by(Task.priority.desc(), Task.updated_at.desc())
            .limit(_LIST_LIMIT)
        )
        return [
            {
                "id": task.id,
                "title": task.title,
                "project_name": project_name,
                "priority": task.priority,
                "status": task.status,
            }
            for task, project_name in sess.execute(statement)
        ]

    @staticmethod
    def _recent_ideas(sess: Session) -> list[dict[str, Any]]:
        statement = select(Idea).order_by(Idea.created_at.desc()).limit(_LIST_LIMIT)
        return [
            {"id": idea.id, "title": idea.title, "status": idea.status, "created_at": idea.created_at}
            for idea in sess.scalars(statement)
        ]
