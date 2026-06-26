"""
Project tablosu üzerinde CRUD işlemlerini yürüten veri erişim katmanı.
Ham SQL yasaktır; tüm sorgular SQLAlchemy ORM ile yapılır (RULES.md).
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.models.project import Project
from infrastructure.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ProjectRepository(BaseRepository[Project]):
    """Proje varlıklarının veritabanı işlemlerini yönetir."""

    model = Project

    def _query_options(self) -> tuple:
        # Proje detayı her zaman aşama/görev/etiketleriyle birlikte tüketilir;
        # N+1 sorgu yerine selectinload ile tek seferde yüklenir.
        return (
            selectinload(Project.stages),
            selectinload(Project.tasks),
            selectinload(Project.tags),
        )

    def get_all(
        self,
        include_archived: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Project]:
        """Tüm projeleri döndürür; varsayılan olarak arşivlenenleri hariç tutar."""
        with self._db.session() as sess:
            stmt = select(Project).options(*self._query_options())
            if not include_archived:
                stmt = stmt.where(Project.is_archived.is_(False))
            stmt = stmt.order_by(Project.display_order, Project.created_at.asc())
            if offset:
                stmt = stmt.offset(max(0, offset))
            if limit is not None:
                stmt = stmt.limit(max(0, limit))
            return list(sess.scalars(stmt).all())

    def set_archived(self, project_id: int, archived: bool) -> None:
        with self._db.session() as sess:
            project = sess.get(Project, project_id)
            if project is not None:
                project.is_archived = archived
