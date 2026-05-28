"""ProjectIdea ilişki veri erişim katmanı."""
from __future__ import annotations

from sqlalchemy import select

from domain.models.project_idea import ProjectIdea
from infrastructure.database.db_manager import DatabaseManager


class ProjectIdeaRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, project_id: int, idea_id: int, relation_type: str = "SOURCE") -> ProjectIdea:
        link = ProjectIdea(project_id=project_id, idea_id=idea_id, relation_type=relation_type)
        with self._db.session() as sess:
            sess.add(link)
            sess.flush()
            sess.refresh(link)
            sess.expunge(link)
            return link

    def get_by_project(self, project_id: int) -> list[ProjectIdea]:
        with self._db.session() as sess:
            stmt = select(ProjectIdea).where(ProjectIdea.project_id == project_id)
            return list(sess.scalars(stmt).all())
