"""
Search Service - Tüm sistemde global arama yapar (Projeler, Görevler, Fikirler).
"""
import logging
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from core.text_normalization import LIKE_ESCAPE, SQL_FOLD_FUNCTION, escape_like, normalize_search_text
from domain.models.idea import Idea
from domain.models.project import Project
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

_MIN_QUERY_LENGTH = 2
_RESULT_LIMIT = 20


def _matches_any(columns: list[InstrumentedAttribute[Any]], pattern: str) -> Any:
    """Kolonları Türkçe uyumlu katlayıp LIKE ile karşılaştırır (SQLite LIKE yalnızca ASCII'de duyarsızdır)."""
    fold = getattr(func, SQL_FOLD_FUNCTION)
    return or_(*(fold(column).like(pattern, escape=LIKE_ESCAPE) for column in columns))


class SearchService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def search_all(self, query: str) -> dict[str, list[dict[str, Any]]]:
        """Tüm tablolarda arama yapar ve formatlanmış sonuçları döner."""
        if not query or len(query.strip()) < _MIN_QUERY_LENGTH:
            return {"projects": [], "tasks": [], "ideas": []}

        pattern = f"%{escape_like(normalize_search_text(query.strip()))}%"
        with self._db.session() as sess:
            return {
                "projects": self._search_projects(sess, pattern),
                "tasks": self._search_tasks(sess, pattern),
                "ideas": self._search_ideas(sess, pattern),
            }

    def _search_projects(self, sess: Session, pattern: str) -> list[dict[str, Any]]:
        stmt = select(Project).where(
            _matches_any([Project.title, Project.short_description], pattern)
        ).limit(_RESULT_LIMIT)
        return [
            {"id": p.id, "title": p.title, "description": p.short_description or "", "type": "project"}
            for p in sess.scalars(stmt)
        ]

    def _search_tasks(self, sess: Session, pattern: str) -> list[dict[str, Any]]:
        stmt = select(Task).where(
            _matches_any([Task.title, Task.description], pattern)
        ).limit(_RESULT_LIMIT)
        return [
            {
                "id": t.id,
                "project_id": t.project_id,
                "title": t.title,
                "description": t.description or "",
                "type": "task",
            }
            for t in sess.scalars(stmt)
        ]

    def _search_ideas(self, sess: Session, pattern: str) -> list[dict[str, Any]]:
        stmt = select(Idea).where(
            _matches_any([Idea.title, Idea.problem, Idea.solution, Idea.notes], pattern)
        ).limit(_RESULT_LIMIT)
        return [
            {
                "id": i.id,
                "title": i.title,
                "description": i.problem or i.solution or i.notes or "",
                "type": "idea",
            }
            for i in sess.scalars(stmt)
        ]
