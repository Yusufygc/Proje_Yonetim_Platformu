from typing import Any, Optional

from domain.models.note import Note
from infrastructure.repositories.note_repository import NoteRepository


class NoteService:
    """Proje Notları için iş kurallarını işleten servis."""

    def __init__(self, repository: NoteRepository) -> None:
        self._repo = repository

    def create_note(self, project_id: int, title: str, body: str, **kwargs: Any) -> Note:
        if not title or not title.strip():
            raise ValueError("Not başlığı boş olamaz.")
        if not body or not body.strip():
            raise ValueError("Not içeriği boş olamaz.")
            
        note = Note(
            project_id=project_id,
            title=title.strip(),
            body=body.strip()
        )
        
        for key, value in kwargs.items():
            if hasattr(note, key):
                setattr(note, key, value)
                
        return self._repo.create(note)

    def update_note(self, note_id: int, **kwargs: Any) -> Note:
        note = self.get_note(note_id)
        if not note:
            raise ValueError("Not bulunamadı.")
            
        if "title" in kwargs and not str(kwargs["title"]).strip():
            raise ValueError("Not başlığı boş olamaz.")
        if "body" in kwargs and not str(kwargs["body"]).strip():
            raise ValueError("Not içeriği boş olamaz.")
            
        for key, value in kwargs.items():
            if hasattr(note, key):
                setattr(note, key, value)
                
        return self._repo.update(note)

    def delete_note(self, note_id: int) -> None:
        self._repo.delete(note_id)

    def get_note(self, note_id: int) -> Optional[Note]:
        return self._repo.get_by_id(note_id)

    def get_project_notes(self, project_id: int) -> list[Note]:
        return list(self._repo.get_by_project(project_id))

    def reorder(self, ordered_ids: list[int]) -> None:
        if not ordered_ids:
            return
        self._repo.reorder(ordered_ids)
