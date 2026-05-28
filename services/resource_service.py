from typing import Any, Optional

from domain.models.resource import Resource
from infrastructure.repositories.resource_repository import ResourceRepository


class ResourceService:
    """Proje Kaynakları için iş kurallarını işleten servis."""

    def __init__(self, repository: ResourceRepository) -> None:
        self._repo = repository

    def create_resource(self, project_id: int, title: str, url: str, **kwargs: Any) -> Resource:
        if not url or not url.strip():
            raise ValueError("Kaynak URL boş olamaz.")
        cleaned_url = url.strip()
        cleaned_title = title.strip() if title and title.strip() else cleaned_url
            
        resource = Resource(
            project_id=project_id,
            title=cleaned_title,
            url=cleaned_url
        )
        
        for key, value in kwargs.items():
            if hasattr(resource, key):
                setattr(resource, key, value)
                
        return self._repo.create(resource)

    def update_resource(self, resource_id: int, **kwargs: Any) -> Resource:
        resource = self.get_resource(resource_id)
        if not resource:
            raise ValueError("Kaynak bulunamadı.")
            
        if "url" in kwargs and not str(kwargs["url"]).strip():
            raise ValueError("Kaynak URL boş olamaz.")
        if "title" in kwargs and not str(kwargs["title"]).strip():
            kwargs["title"] = kwargs.get("url", resource.url)
            
        for key, value in kwargs.items():
            if hasattr(resource, key):
                setattr(resource, key, value)
                
        return self._repo.update(resource)

    def delete_resource(self, resource_id: int) -> None:
        self._repo.delete(resource_id)

    def get_resource(self, resource_id: int) -> Optional[Resource]:
        return self._repo.get_by_id(resource_id)

    def get_project_resources(self, project_id: int) -> list[Resource]:
        return list(self._repo.get_by_project(project_id))
