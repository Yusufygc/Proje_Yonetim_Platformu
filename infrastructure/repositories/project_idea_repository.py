"""ProjectIdea ilişki veri erişim katmanı."""
from __future__ import annotations

from domain.models.project_idea import ProjectIdea
from infrastructure.repositories.base_repository import ProjectScopedRepository


class ProjectIdeaRepository(ProjectScopedRepository[ProjectIdea]):
    model = ProjectIdea

    def create(  # type: ignore[override] — ilişki kaydı id çiftinden kurulur
        self, project_id: int, idea_id: int, relation_type: str = "SOURCE"
    ) -> ProjectIdea:
        link = ProjectIdea(project_id=project_id, idea_id=idea_id, relation_type=relation_type)
        return super().create(link)
