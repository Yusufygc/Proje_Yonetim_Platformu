"""
Project tablosu üzerinde CRUD işlemlerini yürüten veri erişim katmanı.
Ham SQL yasaktır; tüm sorgular SQLAlchemy ORM ile yapılır (RULES.md).
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.models.project import Project
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ProjectRepository:
    """Proje varlıklarının veritabanı işlemlerini yönetir."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_all(
        self,
        include_archived: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Project]:
        """Tüm projeleri döndürür; varsayılan olarak arşivlenenleri hariç tutar."""
        with self._db.session() as sess:
            stmt = select(Project).options(
                selectinload(Project.stages),
                selectinload(Project.tasks),
                selectinload(Project.tags),
            )
            if not include_archived:
                stmt = stmt.where(Project.is_archived.is_(False))
            stmt = stmt.order_by(Project.display_order, Project.created_at.desc())
            if offset:
                stmt = stmt.offset(max(0, offset))
            if limit is not None:
                stmt = stmt.limit(max(0, limit))
            return list(sess.scalars(stmt).all())

    def get_by_id(self, project_id: int) -> Optional[Project]:
        with self._db.session() as sess:
            stmt = (
                select(Project)
                .options(
                    selectinload(Project.stages),
                    selectinload(Project.tasks),
                    selectinload(Project.tags),
                )
                .where(Project.id == project_id)
            )
            return sess.scalar(stmt)

    def create(self, project: Project) -> Project:
        with self._db.session() as sess:
            sess.add(project)
            sess.flush()
            sess.refresh(project)
            sess.expunge(project)
            return project

    def update(self, project: Project) -> Project:
        with self._db.session() as sess:
            merged = sess.merge(project)
            sess.flush()
            sess.refresh(merged)
            sess.expunge(merged)
            return merged

    def delete(self, project_id: int) -> None:
        with self._db.session() as sess:
            project = sess.get(Project, project_id)
            if project is not None:
                sess.delete(project)

    def set_archived(self, project_id: int, archived: bool) -> None:
        with self._db.session() as sess:
            project = sess.get(Project, project_id)
            if project is not None:
                project.is_archived = archived
