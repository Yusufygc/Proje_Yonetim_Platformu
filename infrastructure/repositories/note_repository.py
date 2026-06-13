from domain.models.note import Note
from infrastructure.repositories.base_repository import ProjectScopedRepository


class NoteRepository(ProjectScopedRepository[Note]):
    """Proje Notları (Note) için veri erişim katmanı."""

    model = Note

    def _project_order(self) -> tuple:
        return (Note.created_at.desc(),)
