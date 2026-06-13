"""Proje aşaması veri erişim katmanı."""
from __future__ import annotations

from domain.models.project_stage import ProjectStage
from infrastructure.repositories.base_repository import ProjectScopedRepository


class StageRepository(ProjectScopedRepository[ProjectStage]):
    """ProjectStage kayıtları üzerinde CRUD işlemlerini yönetir."""

    model = ProjectStage

    def _project_order(self) -> tuple:
        return (ProjectStage.order_index,)
