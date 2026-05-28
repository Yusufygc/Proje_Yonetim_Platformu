"""
Dashboard Service - Ana ekran istatistiklerini hesaplar ve döner.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select

from domain.enums.priority import Priority
from domain.enums.project_health import ProjectHealth
from domain.enums.project_status import ProjectStatus
from domain.enums.task_status import TaskStatus
from domain.models.idea import Idea
from domain.models.project import Project
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_dashboard_stats(self) -> dict[str, Any]:
        """Dashboard'da gösterilecek metrikleri ve listeleri hazırlar."""
        stats = {
            "total_projects": 0,
            "total_ideas": 0,
            "total_tasks": 0,
            "active_projects": 0,
            "completed_projects": 0,
            "updated_this_week": 0,
            "blocked_projects": [],
            "recent_tasks": [],
            "high_priority_tasks": [],
            "recent_ideas": [],
        }

        with self._db.session() as sess:
            # Counts
            stats["total_projects"] = sess.scalar(select(func.count()).select_from(Project)) or 0
            stats["total_ideas"] = sess.scalar(select(func.count()).select_from(Idea)) or 0
            stats["total_tasks"] = sess.scalar(select(func.count()).select_from(Task)) or 0
            stats["active_projects"] = sess.scalar(
                select(func.count()).select_from(Project).where(Project.status == ProjectStatus.ACTIVE.value)
            ) or 0
            stats["completed_projects"] = sess.scalar(
                select(func.count()).select_from(Project).where(Project.status == ProjectStatus.COMPLETED.value)
            ) or 0
            week_start = datetime.now(timezone.utc) - timedelta(days=7)
            stats["updated_this_week"] = sess.scalar(
                select(func.count()).select_from(Project).where(Project.updated_at >= week_start)
            ) or 0

            # Blocked / At Risk Projects
            stmt_p = select(Project).where(
                (Project.status == ProjectStatus.BLOCKED.value)
                | (Project.health == ProjectHealth.AT_RISK.value)
                | (Project.health == ProjectHealth.BLOCKED.value)
            ).limit(5)
            for p in sess.scalars(stmt_p):
                stats["blocked_projects"].append({
                    "id": p.id,
                    "name": p.title,
                    "status": p.status
                })

            # Recent Tasks (Son güncellenen görevler)
            stmt_t = select(Task, Project.title).join(Project, Task.project_id == Project.id).order_by(Task.updated_at.desc()).limit(10)
            for row in sess.execute(stmt_t):
                task = row[0]
                project_name = row[1]
                stats["recent_tasks"].append({
                    "id": task.id,
                    "title": task.title,
                    "project_name": project_name,
                    "status": task.status,
                    "updated_at": task.updated_at
                })

            stmt_hp = (
                select(Task, Project.title)
                .join(Project, Task.project_id == Project.id)
                .where(Task.priority.in_([Priority.HIGH.value, Priority.CRITICAL.value]))
                .where(Task.status.not_in([TaskStatus.DONE.value, TaskStatus.CANCELLED.value]))
                .order_by(Task.priority.desc(), Task.updated_at.desc())
                .limit(10)
            )
            for task, project_name in sess.execute(stmt_hp):
                stats["high_priority_tasks"].append({
                    "id": task.id,
                    "title": task.title,
                    "project_name": project_name,
                    "priority": task.priority,
                    "status": task.status,
                })

            stmt_i = select(Idea).order_by(Idea.created_at.desc()).limit(10)
            for idea in sess.scalars(stmt_i):
                stats["recent_ideas"].append({
                    "id": idea.id,
                    "title": idea.title,
                    "status": idea.status,
                })

        return stats
