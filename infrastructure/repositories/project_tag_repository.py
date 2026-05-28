"""ProjectTag veri erişim katmanı."""
from __future__ import annotations

from sqlalchemy import select

from domain.models.project_tag import ProjectTag
from infrastructure.database.db_manager import DatabaseManager


class ProjectTagRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def replace_for_project(self, project_id: int, tags: list[str]) -> list[ProjectTag]:
        cleaned = sorted({tag.strip() for tag in tags if tag and tag.strip()})
        with self._db.session() as sess:
            existing = list(sess.scalars(select(ProjectTag).where(ProjectTag.project_id == project_id)))
            for tag in existing:
                sess.delete(tag)
            created = [ProjectTag(project_id=project_id, tag_name=tag) for tag in cleaned]
            sess.add_all(created)
            sess.flush()
            for tag in created:
                sess.refresh(tag)
                sess.expunge(tag)
            return created

    def get_by_project(self, project_id: int) -> list[ProjectTag]:
        with self._db.session() as sess:
            stmt = select(ProjectTag).where(ProjectTag.project_id == project_id).order_by(ProjectTag.tag_name)
            return list(sess.scalars(stmt).all())
