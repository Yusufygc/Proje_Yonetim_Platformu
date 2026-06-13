from domain.models.resource import Resource
from infrastructure.repositories.base_repository import ProjectScopedRepository


class ResourceRepository(ProjectScopedRepository[Resource]):
    """Proje Kaynakları (Resource) için veri erişim katmanı."""

    model = Resource

    def _project_order(self) -> tuple:
        return (Resource.created_at.desc(),)
