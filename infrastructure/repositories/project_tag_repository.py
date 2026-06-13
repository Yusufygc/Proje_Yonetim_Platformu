"""ProjectTag veri erişim katmanı."""
from __future__ import annotations

from sqlalchemy import select

from domain.models.project_tag import ProjectTag
from infrastructure.repositories.base_repository import ProjectScopedRepository


class ProjectTagRepository(ProjectScopedRepository[ProjectTag]):
    model = ProjectTag

    def _project_order(self) -> tuple:
        return (ProjectTag.tag_name,)

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
