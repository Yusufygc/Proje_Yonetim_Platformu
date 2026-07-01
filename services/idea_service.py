from typing import Any, Optional

from domain.enums.idea_status import IdeaStatus
from domain.models.idea import Idea
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.idea_repository import IdeaRepository
from infrastructure.repositories.project_idea_repository import ProjectIdeaRepository
from services.project_service import ProjectService


class IdeaService:
    """Fikir Havuzu iş kurallarını işleten servis."""

    def __init__(
        self,
        repository: IdeaRepository,
        project_service: ProjectService,
        project_idea_repository: ProjectIdeaRepository | None = None,
        activity_log_repository: ActivityLogRepository | None = None,
    ) -> None:
        self._repo = repository
        self._project_service = project_service
        self._project_ideas = project_idea_repository
        self._activity_logs = activity_log_repository

    def create_idea(self, title: str, **kwargs: Any) -> Idea:
        if not title or not title.strip():
            raise ValueError("Fikir başlığı boş olamaz.")
        
        idea = Idea(title=title.strip())
        for key, value in kwargs.items():
            if hasattr(idea, key):
                setattr(idea, key, value)
        
        return self._repo.create(idea)

    def update_idea(self, idea_id: int, **kwargs: Any) -> Idea:
        idea = self.get_idea(idea_id)
        if not idea:
            raise ValueError("Fikir bulunamadı.")
            
        if "title" in kwargs and not str(kwargs["title"]).strip():
            raise ValueError("Fikir başlığı boş olamaz.")
            
        for key, value in kwargs.items():
            if hasattr(idea, key):
                setattr(idea, key, value)
                
        return self._repo.update(idea)

    def delete_idea(self, idea_id: int) -> None:
        idea = self.get_idea(idea_id)
        if idea and idea.status == IdeaStatus.REJECTED.value:
            raise ValueError("Reddedilen fikirler silinmemeli; gerekçe notu ile saklanmalıdır.")
        self._repo.delete(idea_id)

    def get_idea(self, idea_id: int) -> Optional[Idea]:
        return self._repo.get_by_id(idea_id)

    def get_all_ideas(self, include_converted: bool = False) -> list[Idea]:
        return list(self._repo.get_all(include_converted))

    def reorder(self, ordered_ids: list[int]) -> None:
        if not ordered_ids:
            return
        self._repo.reorder(ordered_ids)

    def convert_idea_to_project(self, idea_id: int, project_overrides: dict[str, Any] | None = None) -> int:
        """
        Fikri projeye dönüştürür.
        Fikrin detaylarını projenin açıklama, problem ve hedef alanlarına haritalar.
        """
        idea = self.get_idea(idea_id)
        if not idea:
            raise ValueError("Fikir bulunamadı.")
        
        if idea.status == IdeaStatus.CONVERTED.value:
            raise ValueError("Bu fikir zaten projeye dönüştürülmüş.")

        project_data = self.build_project_prefill_data(idea)
        if project_overrides:
            title = str(project_overrides.pop("title", idea.title))
            project_data.update(project_overrides)
        else:
            title = idea.title

        project = self._project_service.create_project(
            title=title,
            **project_data
        )
        if self._project_ideas is not None:
            self._project_ideas.create(project.id, idea.id, "SOURCE")

        # Fikri güncelle
        idea.status = IdeaStatus.CONVERTED.value
        idea.converted_project_id = project.id
        self._repo.update(idea)
        if self._activity_logs is not None:
            self._activity_logs.create(
                project_id=project.id,
                action="IDEA_CONVERTED",
                summary=f"{idea.title} fikri projeye dönüştürüldü.",
                entity_type="idea",
                entity_id=idea.id,
            )

        return project.id

    def build_project_prefill_data(self, idea: Idea) -> dict[str, Any]:
        short_desc = idea.problem or ""
        if len(short_desc) > 500:
            short_desc = short_desc[:497] + "..."

        project_data: dict[str, Any] = {
            "short_description": short_desc,
            "problem_statement": idea.problem,
        }
        if idea.source_link:
            project_data["docs_url"] = idea.source_link
        return project_data
