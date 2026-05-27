from typing import Any, Optional

from domain.enums.idea_status import IdeaStatus
from domain.models.idea import Idea
from infrastructure.repositories.idea_repository import IdeaRepository
from services.project_service import ProjectService


class IdeaService:
    """Fikir Havuzu iş kurallarını işleten servis."""

    def __init__(self, repository: IdeaRepository, project_service: ProjectService) -> None:
        self._repo = repository
        self._project_service = project_service

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
        self._repo.delete(idea_id)

    def get_idea(self, idea_id: int) -> Optional[Idea]:
        return self._repo.get_by_id(idea_id)

    def get_all_ideas(self, include_converted: bool = False) -> list[Idea]:
        return list(self._repo.get_all(include_converted))

    def convert_idea_to_project(self, idea_id: int) -> int:
        """
        Fikri projeye dönüştürür.
        Fikrin detaylarını projenin açıklama, problem ve hedef alanlarına haritalar.
        """
        idea = self.get_idea(idea_id)
        if not idea:
            raise ValueError("Fikir bulunamadı.")
        
        if idea.status == IdeaStatus.CONVERTED.value:
            raise ValueError("Bu fikir zaten projeye dönüştürülmüş.")

        # Proje oluştur
        short_desc = idea.expected_value if idea.expected_value else idea.problem
        if short_desc and len(short_desc) > 500:
            short_desc = short_desc[:497] + "..."

        project_data = {
            "short_description": short_desc,
            "problem_statement": idea.problem,
            "full_description": idea.solution,
            "target_outcome": idea.expected_value,
        }
        
        if idea.source_link:
            project_data["docs_url"] = idea.source_link

        project = self._project_service.create_project(
            title=idea.title,
            **project_data
        )

        # Fikri güncelle
        idea.status = IdeaStatus.CONVERTED.value
        idea.converted_project_id = project.id
        self._repo.update(idea)

        return project.id
