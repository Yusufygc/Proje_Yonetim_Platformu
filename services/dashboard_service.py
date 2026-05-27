"""
Dashboard Service - Ana ekran istatistiklerini hesaplar ve döner.
"""
import logging
from typing import Any

from sqlalchemy import func, select

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
            "blocked_projects": [],
            "recent_tasks": []
        }

        with self._db.session() as sess:
            # Counts
            stats["total_projects"] = sess.scalar(select(func.count()).select_from(Project)) or 0
            stats["total_ideas"] = sess.scalar(select(func.count()).select_from(Idea)) or 0
            stats["total_tasks"] = sess.scalar(select(func.count()).select_from(Task)) or 0

            # Blocked / At Risk Projects
            stmt_p = select(Project).where(
                Project.status.in_(["BLOCKED", "AT_RISK"])
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

        return stats
