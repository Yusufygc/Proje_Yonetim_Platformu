"""
Search Service - Tüm sistemde global arama yapar (Projeler, Görevler, Fikirler).
"""
import logging
from typing import Any

from sqlalchemy import or_, select

from domain.models.idea import Idea
from domain.models.project import Project
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def search_all(self, query: str) -> dict[str, list[dict[str, Any]]]:
        """Tüm tablolarda arama yapar ve formatlanmış sonuçları döner."""
        if not query or len(query.strip()) < 2:
            return {"projects": [], "tasks": [], "ideas": []}

        term = f"%{query.strip().lower()}%"
        results = {"projects": [], "tasks": [], "ideas": []}

        with self._db.session() as sess:
            # Projelerde Arama
            stmt_p = select(Project).where(
                or_(
                    Project.title.ilike(term),
                    Project.short_description.ilike(term)
                )
            ).limit(20)
            for p in sess.scalars(stmt_p):
                results["projects"].append({
                    "id": p.id,
                    "title": p.title,
                    "description": p.short_description or "",
                    "type": "project"
                })

            # Görevlerde Arama
            stmt_t = select(Task).where(
                or_(
                    Task.title.ilike(term),
                    Task.description.ilike(term)
                )
            ).limit(20)
            for t in sess.scalars(stmt_t):
                results["tasks"].append({
                    "id": t.id,
                    "project_id": t.project_id,
                    "title": t.title,
                    "description": t.description or "",
                    "type": "task"
                })

            # Fikirlerde Arama
            stmt_i = select(Idea).where(
                or_(
                    Idea.title.ilike(term),
                    Idea.problem.ilike(term),
                    Idea.solution.ilike(term),
                    Idea.expected_value.ilike(term),
                    Idea.notes.ilike(term),
                )
            ).limit(20)
            for i in sess.scalars(stmt_i):
                description = i.problem or i.solution or i.expected_value or i.notes or ""
                results["ideas"].append({
                    "id": i.id,
                    "title": i.title,
                    "description": description,
                    "type": "idea"
                })

        return results
