from typing import Any, Optional

from domain.models.decision_record import DecisionRecord
from infrastructure.repositories.decision_repository import DecisionRepository


class DecisionService:
    """Proje Kararları için iş kurallarını işleten servis."""

    def __init__(self, repository: DecisionRepository) -> None:
        self._repo = repository

    def create_decision(self, project_id: int, title: str, decision: str, **kwargs: Any) -> DecisionRecord:
        if not title or not title.strip():
            raise ValueError("Karar başlığı boş olamaz.")
        if not decision or not decision.strip():
            raise ValueError("Karar metni boş olamaz.")
            
        record = DecisionRecord(
            project_id=project_id,
            title=title.strip(),
            decision=decision.strip()
        )
        
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
                
        return self._repo.create(record)

    def update_decision(self, decision_id: int, **kwargs: Any) -> DecisionRecord:
        record = self.get_decision(decision_id)
        if not record:
            raise ValueError("Karar bulunamadı.")
            
        if "title" in kwargs and not str(kwargs["title"]).strip():
            raise ValueError("Karar başlığı boş olamaz.")
        if "decision" in kwargs and not str(kwargs["decision"]).strip():
            raise ValueError("Karar metni boş olamaz.")
            
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
                
        return self._repo.update(record)

    def delete_decision(self, decision_id: int) -> None:
        self._repo.delete(decision_id)

    def get_decision(self, decision_id: int) -> Optional[DecisionRecord]:
        return self._repo.get_by_id(decision_id)

    def get_project_decisions(self, project_id: int) -> list[DecisionRecord]:
        return list(self._repo.get_by_project(project_id))
